"""Compiled C/native connect parameter decision and WSF dispatch paths."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t conn[64],cached[64],msg[12];uint8_t *audio_ble_cached_conn_params=cached;
volatile uint8_t audio_ble_connect_request_pending,audio_ble_current_conn_mode,audio_ble_requested_conn_mode,audio_ble_connect_event_handler;
volatile uint32_t conn_present,slow_status,fast_status,alloc_fail,sends,handler,removed,pushed,push_mode,push_delay;
void *audio_ble_dm_conn_params(void){return conn_present?conn:0;}
uint32_t audio_ble_is_conn_params_slow(const void *p){(void)p;return slow_status;}
uint32_t audio_ble_is_conn_params_fast(const void *p){(void)p;return fast_status;}
uint32_t audio_event_loop_remove_delayed(void (*p)(void)){(void)p;removed++;return 1;}
void audio_event_loop_push_delayed(void (*p)(void),uint32_t m,uint32_t d){(void)p;pushed++;push_mode=m;push_delay=d;}
void audio_ble_connect_param_request(uint8_t m){(void)m;}
void *audio_wsf_msg_alloc(uint32_t n){(void)n;return alloc_fail?0:msg;}
void audio_wsf_msg_send(uint8_t h,void *m){(void)m;sends++;handler=h;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_connect_param_request_impl',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_connect_request_impl.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,mode,connid,pending,requested,current,slow,fast,alloc_fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        present=int(connid>=0);actual_connid=max(connid,0)
        u.mem_write(syms['conn']+4,bytes([actual_connid]));u.mem_write(0x20083004,bytes([actual_connid]))
        for base in [syms['cached'],0x20084000]:
            u.mem_write(base+24,struct.pack('<HHH',24,3,100))
        wr(syms['audio_ble_cached_conn_params'],syms['cached']);wr(0x2007433c,0x20084000)
        for n,v in [('conn_present',present),('slow_status',slow),('fast_status',fast),('alloc_fail',alloc_fail)]:wr(syms[n],v)
        for n,v in [('audio_ble_connect_request_pending',pending),('audio_ble_current_conn_mode',current),('audio_ble_requested_conn_mode',requested),('audio_ble_connect_event_handler',7)]:u.mem_write(syms[n],bytes([v]))
        for a,v in [(0x20074f91,pending),(0x20004542,current),(0x20004541,requested),(0x20074f8e,7)]:u.mem_write(a,bytes([v]))
        u.reg_write(UC_ARM_REG_R0,mode);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);result=None
                if a==0x43d0ce:result=0
                elif a==0x46efcc:result=0x20083000 if present else 0
                elif a==0x476fe2:result=slow
                elif a==0x476db8:result=fast
                elif a==0x476ace:wr(syms['removed'],rd(syms['removed'])+1);result=1
                elif a==0x47697e:wr(syms['pushed'],rd(syms['pushed'])+1);wr(syms['push_mode'],r1);wr(syms['push_delay'],r2);result=0
                elif a==0x4bf99e:result=0 if alloc_fail else 0x20085000
                elif a==0x4bf9ba:wr(syms['sends'],rd(syms['sends'])+1);wr(syms['handler'],r0);result=0
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_ble_connect_param_request_impl'] if c else 0x47720c)|1,0x600000,count=12000)
        cell=lambda n,a:bytes(u.mem_read(syms[n] if c else a,1))
        return (cell('audio_ble_connect_request_pending',0x20074f91),cell('audio_ble_current_conn_mode',0x20004542),
                bytes(u.mem_read(syms['msg'] if c else 0x20085000,12)),tuple(rd(syms[n]) for n in ['sends','handler','removed','pushed','push_mode','push_delay']))
    cases=[(0xa3,-1,0,0xa3,0,0,0,0),(0xa3,0,0,0xa3,0,0,0,0),(0xa3,4,0,0xa3,0,0,0,0),
           (0xa3,1,0,0xa3,0,0,0xa3,0),(0xa4,1,0,0xa4,0,0xa4,0,0),(0xa3,1,1,0xa3,0,0,0,0),
           (0xa3,1,0,0xa4,0,0,0,0),(0xa3,1,0,0xa4,0,0,0,1)]
    for case in cases:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
        print('PASS BLE connect impl',case)
