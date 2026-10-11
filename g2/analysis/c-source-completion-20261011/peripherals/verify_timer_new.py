"""Bounded actual C/native osTimerNew construction branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
uint32_t irq,alloc,create_result;volatile uint32_t calls[8];
uint32_t audio_irq_context(void){return irq;}
void *pvPortMalloc(uint32_t n){calls[0]++;calls[1]=n;return (void *)alloc;}
void vPortFree(void *p){calls[2]++;calls[3]=(uint32_t)p;}
void *audio_freertos_timer_create_dynamic(const char *name,uint32_t period,uint32_t auto_reload,uintptr_t id,void (*cb)(void *)){(void)name;(void)period;(void)cb;calls[4]++;calls[5]=auto_reload;calls[6]=id;return (void *)create_result;}
void *audio_freertos_timer_create_static(const char *name,uint32_t period,uint32_t auto_reload,uintptr_t id,void (*cb)(void *),void *storage){(void)name;(void)period;(void)cb;(void)storage;calls[4]++;calls[5]=auto_reload;calls[6]=id;return (void *)create_result;}
uintptr_t audio_freertos_timer_get_id(void *p){return (uintptr_t)p;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_timer_new',str(ROOT/'components/audio/uart_thread_source_candidate/cmsis_timer_new.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,irq,callback,attr,cbsize,alloc,created):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        wr(symbols['irq'],irq);wr(symbols['alloc'],alloc);wr(symbols['create_result'],created)
        u.mem_write(0x20070000,struct.pack('<IIII',0,0,0x20071000 if attr else 0,cbsize))
        for reg,value in [(UC_ARM_REG_R0,0x100801 if callback else 0),(UC_ARM_REG_R1,1),(UC_ARM_REG_R2,0x20073000),(UC_ARM_REG_R3,0x20070000 if attr else 0),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,value)
        if not candidate:
            def cut(uc,address,size,_):
                out=symbols['calls']
                get=lambda i:struct.unpack('<I',uc.mem_read(out+4*i,4))[0]
                put=lambda i,v:wr(out+4*i,v)
                if address==0x44900e:result=irq
                elif address==0x456110:put(0,get(0)+1);put(1,uc.reg_read(UC_ARM_REG_R0));result=alloc
                elif address==0x456210:put(2,get(2)+1);put(3,uc.reg_read(UC_ARM_REG_R0));result=0
                elif address in (0x47e6dc,0x47e712):
                    put(4,get(4)+1);put(5,uc.reg_read(UC_ARM_REG_R2));put(6,uc.reg_read(UC_ARM_REG_R3));result=created
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_uart_timer_new'] if candidate else 0x4493b0)|1,0x600000,count=1000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(symbols['calls'],28))
    cases=[(1,1,0,0,0,0),(0,0,0,0,0,0),(0,1,0,0,0,0),
           (0,1,0,0,0x20072000,0x20075000),(0,1,0,0,0x20072000,0),
           (0,1,1,52,0,0x20075000),(0,1,1,44,0x20072000,0x20075000),
           (0,1,1,2,0x20072000,0x20075000)]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS timer',case)
