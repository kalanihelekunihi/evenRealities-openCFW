"""Compiled-C/native target, auth, and delayed scheduler children."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_master_target_address[6];char audio_ble_master_target_name[15];
volatile uint8_t audio_ble_master_auth_mode,audio_ble_master_connect_state;
void audio_ble_master_connect_event(void){}
void audio_ble_master_cancel_retry(void){}
void audio_event_loop_push_delayed(void(*a)(void),uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_set_target',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_master_connect_children.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind,arg in [('target',0),('target',1),('auth',0),('auth',1),('auth',0x5a),('schedule',0),('schedule',1)]:
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   address=syms['audio_ble_master_target_address'] if compiled else 0x200003c0
   name=syms['audio_ble_master_target_name'] if compiled else 0x200003c8
   mode=syms['audio_ble_master_auth_mode'] if compiled else 0x20074f80
   state=syms['audio_ble_master_connect_state'] if compiled else 0x20074f87
   u.mem_write(address,b'\xaa'*6);u.mem_write(name,b'\xaa'*15);u.mem_write(mode,b'\x02');u.mem_write(state,b'\x00')
   u.mem_write(0x20090000,b'ABCDEF');u.mem_write(0x20090100,b'EVEN R1\0ringMa\0')
   cuts={syms['audio_log_level']&~1:'level',syms['audio_queue_copy_bytes']&~1:'copy',syms['audio_uart_buffer_zero']&~1:'zero',syms['audio_ble_master_cancel_retry']&~1:'cancel',syms['audio_event_loop_push_delayed']&~1:'delayed'} if compiled else {0x43d0ce:'level',0x439be4:'copy',0x43c0e4:'zero',0x4a17f4:'cancel',0x47697e:'delayed'}
   events=[]
   def hook(uc,a,size,_):
    t=cuts.get(a)
    if not t:return
    r0,r1,r2=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
    if t=='level':uc.reg_write(UC_ARM_REG_R0,0)
    elif t=='copy':events.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
    elif t=='zero':events.append(('zero',r1,r2));uc.mem_write(r0,bytes([r2&0xff])*r1)
    elif t=='cancel':events.append(('cancel',))
    elif t=='delayed':events.append(('delayed',r1,r2,r0==((syms['audio_ble_master_connect_event'] if compiled else 0x4a1b60)|1)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   if kind=='target':
    start=syms['audio_ble_master_set_target'] if compiled else 0x4a2068
    u.reg_write(UC_ARM_REG_R0,0 if arg else 0x20090000);u.reg_write(UC_ARM_REG_R1,0x20090100);u.reg_write(UC_ARM_REG_R2,15)
   elif kind=='auth':
    start=syms['audio_ble_master_auth_mode_set'] if compiled else 0x4a2168
    u.reg_write(UC_ARM_REG_R0,arg)
   else:
    start=syms['audio_ble_master_schedule_connect'] if compiled else 0x4a2618
    u.reg_write(UC_ARM_REG_R0,2000);u.reg_write(UC_ARM_REG_R1,arg)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start(start|1,0x600000,count=2000)
   observations.append((u.reg_read(UC_ARM_REG_R0) if kind=='auth' else None,events,bytes(u.mem_read(address,6)) if kind=='target' else None,bytes(u.mem_read(name,15)) if kind=='target' else None,u.mem_read(mode,1)[0] if kind=='auth' else None,u.mem_read(state,1)[0] if kind=='schedule' else None))
  assert observations[0]==observations[1],(kind,arg,observations)
  print('PASS master child',kind,arg)
