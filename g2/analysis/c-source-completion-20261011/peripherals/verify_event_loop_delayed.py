"""Compiled C/native bounded delayed-slot insertion and removal."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_event_loop_thread_handle,*audio_event_loop_mutex,*audio_event_loop_timer;
uint32_t audio_event_loop_base_tick,audio_event_loop_delayed_slots[192];
volatile uint32_t tick,timer_stops,callback_arg,pushes,push_arg,push_timeout;
uint32_t audio_delay(uint32_t n){return n;}
uint32_t g2_flashdb_candidate_tick(void){return tick;}
int32_t audio_file_mutex_acquire(void *p,uint32_t t){(void)p;(void)t;return 0;}
int32_t audio_file_mutex_release(void *p){(void)p;return 0;}
int32_t audio_timer_stop(void *p){(void)p;timer_stops++;return 0;}
uint32_t audio_event_loop_push(void (*p)(void),uint32_t arg,uint32_t timeout){(void)p;pushes++;push_arg=arg;push_timeout=timeout;return 0;}
void audio_event_loop_timer_callback(uint32_t t){callback_arg=t;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_event_loop_push_delayed',str(ROOT/'components/audio/uart_thread_source_candidate/display_event_loop_delayed.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,remove,delay,existing):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        for n,v in [('audio_event_loop_thread_handle',0x20082000),('audio_event_loop_mutex',0x20083000),('audio_event_loop_timer',0x20084000),('audio_event_loop_base_tick',100),('tick',150)]:wr(syms[n],v)
        for a,v in [(0x200745f0,0x20082000),(0x200745f4,0x20083000),(0x200745f8,0x20084000),(0x200745fc,100)]:wr(a,v)
        cb=0x20085001
        if existing:
            wr(syms['audio_event_loop_delayed_slots'],cb);wr(0x2006dad4,cb)
        u.reg_write(UC_ARM_REG_R0,cb);u.reg_write(UC_ARM_REG_R1,163);u.reg_write(UC_ARM_REG_R2,delay)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);result=None
                if a==0x43d0ce:result=0
                elif a==0x4497b6 or a==0x44981c:result=0
                elif a==0x4490cc:result=150
                elif a==0x4494d8:wr(syms['timer_stops'],rd(syms['timer_stops'])+1);result=0
                elif a==0x4767a8:wr(syms['callback_arg'],r0);result=0
                elif a==0x4766ec:wr(syms['pushes'],rd(syms['pushes'])+1);wr(syms['push_arg'],r1);wr(syms['push_timeout'],r2);result=0
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        start=(syms['audio_event_loop_remove_delayed' if remove else 'audio_event_loop_push_delayed'] if c else (0x476ace if remove else 0x47697e))
        u.emu_start(start|1,0x600000,count=10000)
        base=syms['audio_event_loop_delayed_slots'] if c else 0x2006dad4
        return bytes(u.mem_read(base,772)),tuple(rd(syms[n]) for n in ['timer_stops','callback_arg','pushes','push_arg','push_timeout'])
    for case in [(False,0,False),(False,100,False),(False,100,True),(True,0,False),(True,0,True)]:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a[1],b[1],a[0][:12],b[0][:12])
        print('PASS event delayed',case)
