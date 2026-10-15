#!/usr/bin/env python3
"""Execute source-linked GPIO/nrfx bodies without provider interception."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'adc/sdk-execution.json';receipt.unlink(missing_ok=True)
    report=json.loads((BASE/'adc/integration-report.json').read_text());obj=BASE/'adc/adc-native-integration.o';assert sha(obj)==report['relocatable_sha256']
    lib=ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc.a'
    roots=['r1_named_adc_register_all','r1_named_adc_open','r1_named_adc_close']
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';text=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.adc.state 0x20006ef4 : { *(.r1.adc.state) } .r1.adc.ops 0x20006f70 : { *(.r1.adc.ops) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .bss 0x2002c250 (NOLOAD) : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+roots[0],*['--undefined='+n for n in roots],'--defsym=r1_adc_error=0x100e001',str(obj),str(lib),'-o',str(elf)],check=True,capture_output=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);uc.mem_map(0x1000000,0x10000);uc.mem_write(0x1000000,text.read_bytes());uc.mem_map(0x20000000,0x40000);uc.mem_map(0x40000000,0x100000);uc.mem_map(0x50000000,0x1000);uc.mem_map(0xe0000000,0x100000)
        for section,address in (('.r1.adc.state',0x20006ef4),('.r1.adc.ops',0x20006f70)):
            data=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(data),str(elf)],check=True);uc.mem_write(address,data.read_bytes())
        events=[];history=[]
        uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events.append((p,s,v)),begin=0x40000000,end=0x50000fff)
        uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events.append((p,s,v)),begin=0xe0000000,end=0xe00fffff)
        from unicorn import UC_HOOK_CODE
        def fatal(uc,address,size,data):
            if address==0x100e000:raise AssertionError('Unimplemented fatal ADC error path was reached')
        uc.hook_add(UC_HOOK_CODE,fatal)
        def normalize_control(data,pointer=0):return bytes(data)
        def call(name,arg):
            uc.reg_write(UC_ARM_REG_R0,arg);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);start=len(events);uc.emu_start(syms[name]|1,0x20000100,count=1000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
            history.append((name,arg,uc.reg_read(UC_ARM_REG_R0),list(events[start:]),bytes(uc.mem_read(syms['m_cb'],48))))
            return uc.reg_read(UC_ARM_REG_R0)
        assert call('r1_named_adc_register_all',0)==1
        states=[]
        for i in range(3):
            device=0x20006f08+i*40;assert call('r1_named_adc_open',device)==0
            assert bytes(uc.mem_read(0x20006efc+i*40,1))==b'\1'
            control=bytes(uc.mem_read(syms['m_cb'],48));assert control[44]==1
            before=len(events);assert call('r1_named_adc_open',device)==0;assert len(events)==before
            states.append(dict(index=i,input=uc.mem_read(0x20006efd+i*40,1)[0],active_channels=control[45]))
        for i in (0,1,2):
            assert call('r1_named_adc_close',0x20006f08+i*40)==0
            assert bytes(uc.mem_read(0x20006efc+i*40,1))==b'\0'
        assert bytes(uc.mem_read(syms['m_cb']+44,1))==b'\0'
        app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
        assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
        stock.mem_map(0x20000000,0x40000);stock.mem_map(0x40000000,0x100000);stock.mem_map(0x50000000,0x1000);stock.mem_map(0xe0000000,0x100000)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        stock_events=[]
        for begin,end in ((0x40000000,0x50000fff),(0xe0000000,0xe00fffff)):
            stock.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:stock_events.append((p,s,v)),begin=begin,end=end)
        original={'r1_named_adc_register_all':0x5493c,'r1_named_adc_open':0x54864,'r1_named_adc_close':0x547f4}
        for name,arg,value,trace,control in history:
            stock_events.clear();stock.reg_write(UC_ARM_REG_R0,arg);stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.reg_write(UC_ARM_REG_LR,0x20000101)
            stock.emu_start(original[name]|1,0x20000100,count=1000000);assert stock.reg_read(UC_ARM_REG_PC)==0x20000100
            actual_control=bytes(stock.mem_read(0x2002c250,48))
            assert stock.reg_read(UC_ARM_REG_R0)==value,(name,'status')
            assert stock_events==trace,(name,'MMIO',stock_events,trace)
            assert actual_control==control,(name,'nrfx control',actual_control.hex(),control.hex())
        result=dict(application_sha256=sha(app),stock_differential_calls=len(history),integration_report_sha256=sha(BASE/'adc/integration-report.json'),relocatable_sha256=sha(obj),runtime_archive_sha256=sha(lib),executable_sha256=sha(elf),undefined_symbols=[],test_only_bindings=["r1_adc_error: trap if reached"],open_records=3,close_records=3,open_states=states,peripheral_writes=len(events),nrfx_callbacks_intercepted=False,scope='Actual compiled SAADC init/channel-init/channel-uninit/uninit and native adapters execute against stock; statuses, ordered MMIO/core writes and 48-byte control block match',limitations=['Only successful initialization/channel setup and bounded STOP-event timeout are exercised.','No analog samples, DMA buffers or asynchronous interrupts are simulated.','Fatal error seam traps if reached; its production body remains unresolved.','Newlib strcmp is a binary test dependency.','Settling cycles and physical timing remain unproven.'],application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'Actual SAADC executed: {len(history)} stock differential calls, {len(events)} peripheral/core writes; no provider interception')
if __name__=='__main__':main()
