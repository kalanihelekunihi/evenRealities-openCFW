"""Actual compiled C/native four-layout BLE TX and ownership comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
struct ble_msgtx_manager {uint8_t reserved[8];void *thread;void *queue;};
struct ble_msgtx_manager audio_ble_msgtx_manager;
uint8_t block[128]; volatile uint32_t count_value,capacity_value,queue_result,alloc_fail,freed,flagged,put_calls;
void *codec_allocate(uint32_t n){(void)n;return alloc_fail?0:block;}
void audio_file_heap_free(void *p){(void)p;freed++;}
void *audio_queue_copy_bytes(void *d,const void *s,uint32_t n){uint8_t *a=d;const uint8_t *b=s;for(uint32_t i=0;i<n;i++)a[i]=b[i];return d;}
uint32_t audio_cmsis_queue_get_count(void *q){(void)q;return count_value;}
uint32_t audio_cmsis_queue_get_capacity(void *q){(void)q;return capacity_value;}
int32_t audio_cmsis_queue_put(void *q,const void *p,uint8_t pr,uint32_t timeout){(void)q;(void)p;(void)pr;(void)timeout;put_calls++;return queue_result;}
uint32_t audio_thread_flags_set(void *t,uint32_t f){(void)t;flagged=f;return f;}
uint32_t audio_ble_is_connected(void){return 1;}
void audio_ble_set_fast_mode(void){}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_msg_tx',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_msg_tx.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f: segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,piping,nonnull,queue,count,capacity,put):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        wr(syms['audio_ble_msgtx_manager']+8,0x20082000);wr(syms['audio_ble_msgtx_manager']+12,0x20083000 if queue else 0)
        wr(0x20004028,0x20082000);wr(0x2000402c,0x20083000 if queue else 0)
        for n,v in [('count_value',count),('capacity_value',capacity),('queue_result',put)]:wr(syms[n],v)
        u.mem_write(0x20081000,b'\x11\x22\x33\x44')
        u.reg_write(UC_ARM_REG_R0,piping);u.reg_write(UC_ARM_REG_R1,3);u.reg_write(UC_ARM_REG_R2,9);u.reg_write(UC_ARM_REG_R3,7)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        wr(0x200ff000,0x20081000 if nonnull else 0);wr(0x200ff004,4)
        if not c:
            def cut(uc,a,size,_):
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);result=None
                if a==0x43d0ce:result=0
                elif a==0x4780f8:result=1
                elif a==0x478160:result=0
                elif a==0x474cd2:result=0x20085000
                elif a==0x474d16:wr(syms['freed'],rd(syms['freed'])+1);result=0
                elif a==0x439be4:
                    uc.mem_write(r0,bytes(uc.mem_read(r1,uc.reg_read(UC_ARM_REG_R2))));result=r0
                elif a==0x449bc8:result=count
                elif a==0x449bbc:result=capacity
                elif a==0x449abe:wr(syms['put_calls'],rd(syms['put_calls'])+1);result=put
                elif a==0x449238:wr(syms['flagged'],r1);result=r1
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_ble_msg_tx'] if c else 0x47564e)|1,0x600000,count=10000)
        block=bytes(u.mem_read(syms['block'] if c else 0x20085000,24))
        return u.reg_read(UC_ARM_REG_R0),block,tuple(rd(syms[n]) for n in ['freed','flagged','put_calls'])
    for case in [(0,False,True,0,8,0),(0,True,False,0,8,0),(0,True,True,0,8,0),(1,True,True,0,8,0),(2,True,True,0,8,0),(3,True,True,0,8,0),(1,True,True,4,8,0),(0,True,True,0,8,1)]:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS BLE TX',case)
