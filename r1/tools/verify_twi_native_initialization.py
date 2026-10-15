#!/usr/bin/env python3
"""Verify typed native initialization and execute its real provider tables."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'software-twi/native-initialization-verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'i2c5/report.json').read_text());obj=BASE/'i2c5/st25-i2c5-registry.o';assert sha(obj)==report['relocatable_sha256']
    for row in report['units']:assert sha(ROOT/row['source'])==row['source_sha256']
    for path,digest in report['headers'].items():assert sha(ROOT/path)==digest
    lib=ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc.a'
    roots={**{'r1_stock_i2c'+str(i+2)+'_register':a for i,a in enumerate((0x56508,0x56520,0x56538,0x56550))},'r1_stock_dispatch_08':0x85d1a,'r1_stock_dispatch_0c':0x85cba,'r1_stock_dispatch_10':0x85d2c,'r1_stock_dispatch_14':0x85da8}
    comparisons=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';text=tmp/'text.bin';data=tmp/'records.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.twi.records 0x20007400 : { *(.r1.twi.records) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+next(iter(roots)),*['--undefined='+n for n in roots],str(obj),str(lib),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.twi.records='+str(data),str(elf)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        candidate.mem_write(0x1000000,text.read_bytes());candidate.mem_write(0x20007400,data.read_bytes());assert len(data.read_bytes())==448
        initial=json.loads((BASE/'software-twi/stock-initialization.json').read_text())
        pointer_offsets=(0,20,24,28,32,40,44,48,84,88,92,96)
        callback_names={20:'r1_twi_gpio_low',24:'r1_twi_gpio_high',28:'r1_twi_gpio_output',32:'r1_twi_gpio_input',44:'r1_twi_gpio_read',48:'r1_twi_gpio_release'}
        for i in range(4):
            original=bytearray(stock.mem_read(0x20007400+i*112,112));compiled=bytearray(candidate.mem_read(0x20007400+i*112,112))
            for offset in pointer_offsets:
                a=struct.unpack_from('<I',original,offset)[0];b=struct.unpack_from('<I',compiled,offset)[0]
                if offset==0:assert bytes(stock.mem_read(a,6))==bytes(candidate.mem_read(b,6))
                else:
                    name=callback_names.get(offset)
                    if offset==40:name='r1_twi_delay_busy' if i<2 else 'r1_twi_delay_noop'
                    if offset>=84:name='r1_stock_i2c'+str(i+2)+'_'+{84:'open',88:'close',92:'read',96:'write'}[offset]
                    assert b==syms[name]|1,(i,offset,name,b)
                original[offset:offset+4]=compiled[offset:offset+4]=bytes(4)
            assert original==compiled,(i,original,compiled)
        def normalize(uc):
            data=bytearray(uc.mem_read(0x20007400,448))
            for i in range(4):
                for offset in (*pointer_offsets,52,56):data[i*112+offset:i*112+offset+4]=bytes(4)
            return bytes(data)
        for uc in (stock,candidate):
            uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events[id(u)].append((p,s,v)),begin=0x50000000,end=0x50000fff)
            uc.mem_write(0x50000000,bytes(4096))
        def compare(name,args):
            nonlocal comparisons
            results=[]
            for uc,entry in ((stock,roots[name]),(candidate,syms[name])):
                events[id(uc)].clear();uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(reg,value)
                uc.emu_start(entry|1,0x20000100,count=2000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                results.append((uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),normalize(uc),bytes(uc.mem_read(0x20007680,4)),bytes(uc.mem_read(0x20003000,16)),bytes(uc.mem_read(0x50000000,4096))))
            assert results[0]==results[1],(name,args,results);comparisons+=1
        for i in range(4):compare('r1_stock_i2c'+str(i+2)+'_register',[0,0,0,0])
        for i in range(4):
            device=0x20007434+i*112
            for _ in range(2):compare('r1_stock_dispatch_08',[device,0,0,0])
            for length in (0,1,2):
                for uc in (stock,candidate):
                    uc.mem_write(0x20002500,struct.pack('<BBHIHHIHH',0xa6,0,0x12ab,0x20003000,length,0,0x20003000,length,0));uc.mem_write(0x20003000,bytes(range(16)))
                compare('r1_stock_dispatch_10',[device,0,0x20002500,0]);compare('r1_stock_dispatch_14',[device,0,0x20002500,0])
            for _ in range(2):compare('r1_stock_dispatch_0c',[device,0,0,0])
    result=dict(application_sha256=sha(app),integration_report_sha256=sha(BASE/'i2c5/report.json'),relocatable_sha256=sha(obj),runtime_archive_sha256=sha(lib),compiled_initialized_bytes=448,record_comparisons=4,registry_lifecycle_transfer_comparisons=comparisons,scope='Compiled typed record scalars and callback bindings match stock after explicit relocations; real registry dispatch, native lifecycle/transfers, GPIO and delay bodies execute without intercepted callbacks',limitations=['Newlib strcmp is an attributable binary test dependency; C-only runtime closure remains open.','GPIO peripheral semantics and wire inputs are emulated, with zero IN values supplying ACK/zero payload.','Source delay cycles differ; physical timing and electrical effects remain unproven.','This component test is not complete application startup/link or instruction identity.'],application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'448 source-initialized bytes verified; {comparisons} full native registry/lifecycle/transfer comparisons passed')
if __name__=='__main__':main()
