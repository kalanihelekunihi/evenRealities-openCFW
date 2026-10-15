#!/usr/bin/env python3
"""Verify typed native initialization and execute its real provider tables."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'gpio/verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'gpio/report.json').read_text());obj=BASE/'gpio/stock_named_gpio.o';assert sha(obj)==report['units'][0]['object_sha256']
    assert sha(ROOT/report['units'][0]['source'])==report['units'][0]['source_sha256']
    for path,digest in report['headers'].items():assert sha(ROOT/path)==digest
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    ghidra=json.loads((BASE/'gpio/ghidra-mcp-irq-bytes.json').read_text())
    assert bytes(ghidra['data'])==app.read_bytes()[0x6ed94-0x27000:0x6edc8-0x27000]
    integrated=BASE/'i2c5/st25-i2c5-registry.o';integration=json.loads((BASE/'i2c5/report.json').read_text());assert sha(integrated)==integration['relocatable_sha256']
    lib=ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc.a'
    roots={'r1_named_gpio_register_all':0x54c24,'r1_named_gpio_callback':0x54afc,'r1_named_gpio_read':0x54ed0,'r1_named_gpio_close':0x54b40,'r1_named_gpio_open':0x54b90,'r1_named_gpio_irq_dispatch':0x6ed94}
    comparisons=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';text=tmp/'text.bin';data=tmp/'records.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.gpio.records 0x200070c0 : { *(.r1.gpio.records) } .r1.gpio.ops 0x200071f4 : { *(.r1.gpio.ops) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+next(iter(roots)),*['--undefined='+n for n in roots],'--defsym=nrfx_gpiote_in_event_disable=0x100e001','--defsym=nrfx_gpiote_in_uninit=0x100e011','--defsym=nrfx_gpiote_is_init=0x100e021','--defsym=nrfx_gpiote_init=0x100e031','--defsym=nrfx_gpiote_in_init=0x100e041','--defsym=nrfx_gpiote_in_event_enable=0x100e051',str(obj),str(integrated),str(lib),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.gpio.records='+str(data),str(elf)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        candidate.mem_write(0x1000000,text.read_bytes());candidate.mem_write(0x200070c0,data.read_bytes());assert len(data.read_bytes())==308
        ops=tmp/'ops.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.gpio.ops='+str(ops),str(elf)],check=True);candidate.mem_write(0x200071f4,ops.read_bytes())
        def normalize(uc):
            result=bytearray(uc.mem_read(0x200070c0,308))
            for i in range(7):
                for off in (0,16):result[i*44+off:i*44+off+4]=bytes(4)
            return bytes(result)
        assert normalize(stock)==normalize(candidate)
        from unicorn import UC_HOOK_CODE
        init_state=[0,0,0]
        provider_map={0x7a73c:'disable',0x7a8ec:'uninit',0x7aa18:'is_init',0x7a94c:'init',0x7a81c:'in_init',0x7a784:'enable',0x100e000:'disable',0x100e010:'uninit',0x100e020:'is_init',0x100e030:'init',0x100e040:'in_init',0x100e050:'enable'}
        def providers(uc,address,size,data):
            if address in provider_map:
                name=provider_map[address];value=0
                if name=='in_init':
                    configuration=bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),4))
                    assert uc.reg_read(UC_ARM_REG_R2)==(0x6ed95 if uc is stock else syms['r1_named_gpio_irq_dispatch']|1)
                    events[id(uc)].append((name,uc.reg_read(UC_ARM_REG_R0),configuration));value=init_state[2]
                elif name=='enable':events[id(uc)].append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
                elif name in ('is_init','init'):
                    events[id(uc)].append((name,));value=init_state[0 if name=='is_init' else 1]
                else:events[id(uc)].append((name,uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            elif address in (0x100e100,0x100e110):
                events[id(uc)].append(('user_callback',address,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        for uc in (stock,candidate):
            uc.hook_add(UC_HOOK_CODE,providers)
            uc.mem_write(0x20002500,bytes(24));uc.mem_write(0x50000000,bytes(4096))
        def compare(name,args):
            nonlocal comparisons
            results=[]
            for uc,entry in ((stock,roots[name]),(candidate,syms[name])):
                events[id(uc)].clear();uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(reg,value)
                uc.emu_start(entry|1,0x20000100,count=2000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                results.append((None if name=='r1_named_gpio_irq_dispatch' else uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),normalize(uc),bytes(uc.mem_read(0x20007680,4)),bytes(uc.mem_read(0x20003000,16)),bytes(uc.mem_read(0x50000000,4096))))
            assert results[0]==results[1],(name,args,results);comparisons+=1
        for _ in range(2):compare('r1_named_gpio_register_all',[0,0,0,0])
        names=['acc_int_1','ppg_int','touch_rdy_in','mcu_reset_irq','pmic_irq','nfc_gpo_irq','device_stacmd_irq','missing']
        for i,name in enumerate(names):
            for uc in (stock,candidate):
                uc.mem_write(0x20002600,name.encode()+b'\0');uc.mem_write(0x20002500,struct.pack('<I',0x20002600))
            for value in (0,0x12345679,0xffffffff):compare('r1_named_gpio_callback',[0x20002500,0,value,0])
            for pattern in (0,0xffffffff,0x55555555):
                for uc in (stock,candidate):uc.mem_write(0x50000000,struct.pack('<I',pattern)*1024)
                compare('r1_named_gpio_read',[0x20002500,0,0x20003000,0])
            for flag in (0,1,255):
                if i<7:
                    for uc in (stock,candidate):uc.mem_write(0x200070c4+i*44,bytes([flag]))
                compare('r1_named_gpio_close',[0x20002500,0,0,0])
        for i,name in enumerate(names):
            for uc in (stock,candidate):uc.mem_write(0x20002600,name.encode()+b'\0');uc.mem_write(0x20002500,struct.pack('<I',0x20002600))
            for opened in (0,1,255):
                for state in ((0,0,0),(1,0,0),(0,8,7),(1,0,7)):
                    init_state[:]=state
                    if i<7:
                        for uc in (stock,candidate):uc.mem_write(0x200070c4+i*44,bytes([opened]))
                    compare('r1_named_gpio_open',[0x20002500,0,0,0])
        for uc in (stock,candidate):
            for i in range(7):uc.mem_write(0x200070c0+i*44+40,struct.pack('<I',0 if i==1 else (0x100e101 if i%2 else 0x100e111)))
        for pin in (0,3,15,17,18,21,33,47):
            for action in (0,1,2,3):compare('r1_named_gpio_irq_dispatch',[pin,action,0,0])
    result=dict(application_sha256=sha(app),gpio_report_sha256=sha(BASE/'gpio/report.json'),integration_report_sha256=sha(BASE/'i2c5/report.json'),object_sha256=sha(obj),comparisons=comparisons,initialized_record_bytes=308,runtime_archive_sha256=sha(lib),scope='Typed records, registration, callback storage, compiled GPIO reads, open configuration/error handling, close ordering and shared-pin IRQ callback dispatch compared with stock',limitations=['Open/close nrfx calls are intercepted at SDK seams; SDK internals remain untested by this oracle.','nrfx disable/uninit are intercepted only at the final SDK seam; their internal behavior is not tested here.','Newlib strcmp is a binary test dependency.','Electrical behavior, interrupts and complete application startup remain unproven.'],application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'308 GPIO record bytes verified; {comparisons} named-GPIO comparisons passed')
if __name__=='__main__':main()
