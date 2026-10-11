"""Compiled C/native immediate event queue message and failure paths."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_event_loop_thread_handle,*audio_event_loop_queue;
volatile uint32_t calls,arg_value,callback_value,put_result;
int32_t audio_cmsis_queue_put(void *q,const void *p,uint8_t pr,uint32_t t){(void)q;(void)pr;(void)t;const uint32_t *a=p;calls++;arg_value=a[0];callback_value=a[1];return put_result;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_event_loop_push',str(ROOT/'components/audio/uart_thread_source_candidate/display_event_loop_push.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,thread,queue,put_result):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        wr(syms['audio_event_loop_thread_handle'],0x20082000 if thread else 0);wr(syms['audio_event_loop_queue'],0x20083000 if queue else 0);wr(syms['put_result'],put_result)
        wr(0x200745f0,0x20082000 if thread else 0);wr(0x200745ec,0x20083000 if queue else 0)
        u.reg_write(UC_ARM_REG_R0,0x20085001);u.reg_write(UC_ARM_REG_R1,163);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                result=None
                if a==0x43d0ce:result=0
                elif a==0x449abe:
                    p=uc.reg_read(UC_ARM_REG_R1);wr(syms['calls'],rd(syms['calls'])+1);wr(syms['arg_value'],rd(p));wr(syms['callback_value'],rd(p+4));result=put_result
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_event_loop_push'] if c else 0x4766ec)|1,0x600000,count=3000)
        return tuple(rd(syms[n]) for n in ['calls','arg_value','callback_value'])
    for case in [(False,True,0),(True,False,0),(True,True,0),(True,True,1)]:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
        print('PASS event push',case)
