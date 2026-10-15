#!/usr/bin/env python3
"""Differential execution of native registry and NFC discovery contracts."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/'r1/research/source-build/i2c5'
HEAD=0x20007680;STATE=0x20006838;ADC=STATE+28;STOP=0x20000100
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'registry-bootstrap-verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
    assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'report.json').read_text());obj=BASE/'st25-i2c5-registry.o'
    assert sha(obj)==report['relocatable_sha256']
    for row in report['units']:assert sha(ROOT/row['source'])==row['source_sha256']
    for path,expected in report['headers'].items():assert sha(ROOT/path)==expected
    lib=ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc.a'
    roots={'r1_stock_registry_find':0x85ce0,'r1_stock_registry_register':0x85d58,'r1_vnfc_rect_adc_handle_cache':0x50d3c,'r1_i2c5_nfc_resource_registration':0x50464,**{'r1_stock_i2c'+str(i+2)+'_register':address for i,address in enumerate((0x56508,0x56520,0x56538,0x56550))}}
    counts={k:0 for k in roots}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin'
        ld.write_text('SECTIONS { .text 0x01000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.i2c5.state 0x20006838 (NOLOAD) : { *(.r1.i2c5.state) } .r1.vnfc.adc 0x20006854 (NOLOAD) : { *(.r1.vnfc.adc) } .r1.twi.records 0x20007400 (NOLOAD) : { *(.r1.twi.records) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_stock_registry_find',*['--undefined='+k for k in roots],str(obj),str(lib),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        assert syms['r1_stock_twi_records']==0x20007400
        assert syms['r1_stock_registry_head']==HEAD and syms['r1_vnfc_rect_adc_device']==ADC
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);traces={id(stock):[],id(candidate):[]}
        stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
        for uc in (stock,candidate):
            uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
            uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:traces[id(u)].append((p,s,v)),begin=0x50000000,end=0x50000fff)
        candidate.mem_write(0x1000000,binary.read_bytes())
        def put(uc,p,v):uc.mem_write(p,struct.pack('<I',v))
        names=[b'nfc_gpo_irq',b'i2c_5',b'vnfc_rect_adc',b'other',b'I2C_5']
        def setup(indices,cached=False):
            for uc in (stock,candidate):
                uc.mem_write(0x20001000,bytes(0x7000))
                for i,n in enumerate(names):uc.mem_write(0x20003000+i*64,n+b'\0')
                for i in range(5):uc.mem_write(0x20002000+i*64,struct.pack('<6I',0x20003000+i*64,0x20004000,0,0,0,0xdeadbeef))
                put(uc,HEAD,0x20002000+indices[0]*64 if indices else 0)
                for j,i in enumerate(indices):put(uc,0x20002000+i*64+20,0x20002000+indices[j+1]*64 if j+1<len(indices) else 0)
                if cached:put(uc,STATE,0x20002500);put(uc,STATE+4,0x20002600)
                put(uc,ADC,0x20002700)
        def compare(name,arg=0):
            results=[]
            for uc,entry in ((stock,roots[name]),(candidate,syms[name])):
                traces[id(uc)].clear();uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,STOP|1);uc.reg_write(UC_ARM_REG_R0,arg)
                uc.emu_start(entry|1,STOP,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==STOP
                results.append((uc.reg_read(UC_ARM_REG_R0) if (name in ('r1_stock_registry_find','r1_stock_registry_register') or name.endswith('_register')) else None,bytes(uc.mem_read(0x20002000,320)),bytes(uc.mem_read(STATE,32)),bytes(uc.mem_read(HEAD,4)),list(traces[id(uc)]),bytes(uc.mem_read(0x20007400,448))))
            assert results[0]==results[1],(name,arg,results);counts[name]+=1
        for indices in ([],[0],[0,1,2],[3,2,1,0]):
            for i in range(5):setup(indices);compare('r1_stock_registry_find',0x20003000+i*64)
            for cached in (False,True):
                setup(indices,cached);compare('r1_i2c5_nfc_resource_registration');compare('r1_i2c5_nfc_resource_registration')
                for uc in (stock,candidate):put(uc,HEAD,0)
                compare('r1_i2c5_nfc_resource_registration')
            setup(indices);compare('r1_vnfc_rect_adc_handle_cache')
            for target in (0,0x200020c0,0x20002040):setup(indices);compare('r1_stock_registry_register',target)
        for field in (0,4):
            setup([])
            for uc in (stock,candidate):put(uc,0x200020c0+field,0)
            compare('r1_stock_registry_register',0x200020c0)
        for initial in ([],[0],[0,1,2]):
            for order in ((0,1,2,3),(3,2,1,0)):
                setup(initial)
                for uc in (stock,candidate):
                    uc.mem_write(0x20007400,bytes((i*29+3)&255 for i in range(448)))
                    for i in range(4):
                        name=0x20003200+i*32;uc.mem_write(name,('i2c_'+str(i+2)).encode()+b'\0');put(uc,0x20007400+i*112,name)
                for i in (*order,*order):compare('r1_stock_i2c'+str(i+2)+'_register')
    result=dict(application_sha256=sha(app),integration_report_sha256=sha(BASE/'report.json'),relocatable_sha256=sha(obj),runtime_archive=str(lib.relative_to(ROOT)),runtime_archive_sha256=sha(lib),comparisons=sum(counts.values()),comparisons_by_entry=counts,scope='Original Thumb versus compiled registry lookup, registration and NFC discovery; actual pinned newlib strcmp executes in candidate',limitations=['Runtime archive is an attributable binary test dependency, not C-only runtime closure.','Invalid NULL name with nonempty list is excluded; stock strcmp fault contract remains unresolved.','Native TWI record registration is tested with injected authenticated-layout fixtures. Initial scatter values, operation bodies/GPIO installation, electrical behavior and full application link remain open.'],application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(counts)
if __name__=='__main__':main()
