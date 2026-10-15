#!/usr/bin/env python3
"""Execute source-linked GPIO/nrfx bodies without provider interception."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'gpio/sdk-execution.json';receipt.unlink(missing_ok=True)
    report=json.loads((BASE/'gpio/integration-report.json').read_text());obj=BASE/'gpio/gpio-native-integration.o';assert sha(obj)==report['relocatable_sha256']
    lib=ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc.a'
    roots=['r1_named_gpio_register_all','r1_named_gpio_open','r1_named_gpio_close','nrfx_gpiote_is_init']
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';text=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.gpio.records 0x200070c0 : { *(.r1.gpio.records) } .r1.gpio.ops 0x200071f4 : { *(.r1.gpio.ops) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .bss 0x2002c168 (NOLOAD) : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+roots[0],*['--undefined='+n for n in roots],str(obj),str(lib),'-o',str(elf)],check=True,capture_output=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);uc.mem_map(0x1000000,0x10000);uc.mem_write(0x1000000,text.read_bytes());uc.mem_map(0x20000000,0x40000);uc.mem_map(0x40000000,0x100000);uc.mem_map(0x50000000,0x1000);uc.mem_map(0xe0000000,0x100000)
        for section,address in (('.r1.gpio.records',0x200070c0),('.r1.gpio.ops',0x200071f4)):
            data=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(data),str(elf)],check=True);uc.mem_write(address,data.read_bytes())
        events=[];history=[]
        uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events.append((p,s,v)),begin=0x40000000,end=0x50000fff)
        uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events.append((p,s,v)),begin=0xe0000000,end=0xe00fffff)
        def normalize_control(data,pointer):
            block=bytearray(data)
            for off in range(0,64,4):
                if struct.unpack_from('<I',block,off)[0]==pointer:struct.pack_into('<I',block,off,1)
            return bytes(block)
        def call(name,arg):
            uc.reg_write(UC_ARM_REG_R0,arg);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);start=len(events);uc.emu_start(syms[name]|1,0x20000100,count=1000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
            history.append((name,arg,uc.reg_read(UC_ARM_REG_R0),list(events[start:]),normalize_control(bytes(uc.mem_read(syms['m_cb'],128)),syms['r1_named_gpio_irq_dispatch']|1)))
            return uc.reg_read(UC_ARM_REG_R0)
        assert call('nrfx_gpiote_is_init',0)==0;assert call('r1_named_gpio_register_all',0)==1
        pins=[15,21,17,18,33,3,33];states=[]
        for i,pin in enumerate(pins):
            device=0x200070d0+i*44;assert call('r1_named_gpio_open',device)==0;assert call('nrfx_gpiote_is_init',0)==1
            assert bytes(uc.mem_read(0x200070c4+i*44,1))==b'\1'
            control=bytes(uc.mem_read(syms['m_cb'],128));assignment=struct.unpack('<b',control[64+pin:65+pin])[0]
            assert 8<=assignment<16,(pin,assignment)
            before=len(events);assert call('r1_named_gpio_open',device)==0;assert len(events)==before
            states.append(dict(pin=pin,slot=assignment,state=control[126]))
        assert states[4]['slot']==states[6]['slot']
        # Close unique pins only: the duplicate descriptor's lifecycle coherence is a separate gate.
        for i in (5,4,3,2,1,0):
            assert call('r1_named_gpio_close',0x200070d0+i*44)==0
            assert bytes(uc.mem_read(0x200070c4+i*44,1))==b'\0'
        app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
        assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
        stock.mem_map(0x20000000,0x40000);stock.mem_map(0x40000000,0x100000);stock.mem_map(0x50000000,0x1000);stock.mem_map(0xe0000000,0x100000)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        stock_events=[]
        for begin,end in ((0x40000000,0x50000fff),(0xe0000000,0xe00fffff)):
            stock.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:stock_events.append((p,s,v)),begin=begin,end=end)
        original={'nrfx_gpiote_is_init':0x7aa18,'r1_named_gpio_register_all':0x54c24,'r1_named_gpio_open':0x54b90,'r1_named_gpio_close':0x54b40}
        for name,arg,value,trace,control in history:
            stock_events.clear();stock.reg_write(UC_ARM_REG_R0,arg);stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.reg_write(UC_ARM_REG_LR,0x20000101)
            stock.emu_start(original[name]|1,0x20000100,count=1000000);assert stock.reg_read(UC_ARM_REG_PC)==0x20000100
            actual_control=normalize_control(bytes(stock.mem_read(0x2002c168,128)),0x6ed95)
            assert stock.reg_read(UC_ARM_REG_R0)==value,(name,'status')
            assert stock_events==trace,(name,'MMIO',stock_events,trace)
            assert actual_control==control,(name,'nrfx control',actual_control.hex(),control.hex())
        result=dict(application_sha256=sha(app),stock_differential_calls=len(history),integration_report_sha256=sha(BASE/'gpio/integration-report.json'),relocatable_sha256=sha(obj),runtime_archive_sha256=sha(lib),executable_sha256=sha(elf),undefined_symbols=[],open_records=7,unique_close_records=6,open_states=states,peripheral_writes=len(events),nrfx_callbacks_intercepted=False,scope='Source-linked native GPIO plus actual nrfx init/in-init/enable/disable/uninit execute in Unicorn with populated tables; initialized state, low-power allocation and repeated-open idempotence checked',limitations=['Newlib memory/string runtime is a binary test dependency.','Peripheral registers are emulated, without asynchronous interrupts or electrical line models.','Shared-pin duplicate close coherence is not tested.','Stock differential covers statuses, ordered peripheral/core writes and relocated nrfx control state; physical hardware remains unproven.'],application_linked=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'Actual nrfx executed: 7 opens, 6 unique closes, {len(events)} peripheral writes; no provider interception')
if __name__=='__main__':main()
