"""Compiled C/native event-loop constructor order and authenticated attr ABI."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_event_loop_queue,*audio_event_loop_timer,*audio_event_loop_mutex,*audio_event_loop_thread_handle;
uint8_t audio_event_loop_queue_cb[80],audio_event_loop_queue_storage[120],audio_event_loop_timer_cb[44],audio_event_loop_mutex_cb[80],audio_event_loop_thread_cb[112],audio_event_loop_thread_stack[3072];
void *audio_queue_new(uint32_t c,uint32_t s,const void *a){(void)c;(void)s;(void)a;return (void *)0x20083000;}
void *audio_uart_timer_new(void (*f)(void *),uint32_t t,void *x,const void *a){(void)f;(void)t;(void)x;(void)a;return (void *)0x20084000;}
void *audio_uart_mutex_new(const void *a){(void)a;return (void *)0x20085000;}
int32_t audio_thread_terminate_peer(void *t){(void)t;return 0;}
void *audio_thread_new(void (*f)(void *),void *x,const void *a){(void)f;(void)x;(void)a;return (void *)0x20086000;}
int32_t audio_event_loop_queue_get(void *q,void *m,uint8_t *p,uint32_t t){(void)q;(void)m;(void)p;(void)t;return -1;}
void audio_event_loop_timer_callback(uint32_t a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_event_loop_initialize',str(ROOT/'components/audio/uart_thread_source_candidate/display_event_loop_init_task.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,existing):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x400000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        native={'audio_event_loop_queue':0x200745ec,'audio_event_loop_timer':0x200745f8,'audio_event_loop_mutex':0x200745f4,'audio_event_loop_thread_handle':0x200745f0}
        if existing:
            for n,v in [('audio_event_loop_queue',0x20083000),('audio_event_loop_timer',0x20084000),('audio_event_loop_mutex',0x20085000),('audio_event_loop_thread_handle',0x20087000)]:wr(syms[n],v);wr(native[n],v)
        calls=[];u.reg_write(UC_ARM_REG_SP,0x203ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        mapping={syms['audio_queue_new'] if c else 0x449a32:('queue',0x20083000),
                 syms['audio_uart_timer_new'] if c else 0x4493b0:('timer',0x20084000),
                 syms['audio_uart_mutex_new'] if c else 0x44971c:('mutex',0x20085000),
                 syms['audio_thread_terminate_peer'] if c else 0x4491fe:('terminate',0),
                 syms['audio_thread_new'] if c else 0x4490e2:('thread',0x20086000)}
        def attrs(ptr,count):
            fields=[rd(ptr+i*4) for i in range(count)]
            name=bytes(u.mem_read(fields[0],80)).split(b'\0')[0] if fields[0] else b''
            return (name,fields[1],*[fields[i] for i in range(count) if i in [3,5,6]])
        def cut(uc,a,size,_):
            if not c and a==0x43d0ce:
                uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if a not in mapping:return
            kind,result=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
            if kind=='queue':calls.append((kind,r0,uc.reg_read(UC_ARM_REG_R1),attrs(r2,6)))
            elif kind=='timer':calls.append((kind,bool(r0),uc.reg_read(UC_ARM_REG_R1),attrs(r3,4)))
            elif kind=='mutex':calls.append((kind,attrs(r0,4)))
            elif kind=='thread':calls.append((kind,bool(r0),attrs(r2,9)))
            else:calls.append((kind,r0))
            uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_event_loop_initialize'] if c else 0x4764e0)|1,0x600000,count=10000)
        return calls,tuple(rd(syms[n] if c else native[n]) for n in native)
    for existing in [False,True]:
        a=run(False,existing);b=run(True,existing);assert a==b,(existing,a,b)
        print('PASS event init',existing)
