"""Actual compiled-C/native follow-up touch and delayed restart cases."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
uint8_t *audio_ble_profile_connection_context;
int32_t audio_uart_ring_task_msg_send(uint32_t a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_event_loop_remove_delayed(void(*a)(void)){(void)a;return 0;}void audio_event_loop_push_delayed(void(*a)(void),uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_ble_phone_advertising_restart(void){}uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_followup_delayed',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_master_touch_followup.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for connection in (0,3):
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(syms['audio_ble_profile_connection_context'] if compiled else 0x2007432c,struct.pack('<I',0x20002000));u.mem_write(0x20002054,bytes([connection]));calls=[]
   cuts={(syms[n]&~1 if compiled else a):n for n,a in [('audio_log_level',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e),('audio_uart_ring_task_msg_send',0x4c549c),('audio_event_loop_remove_delayed',0x476ace),('audio_event_loop_push_delayed',0x47697e)]}
   def hook(uc,a,size,_):
    n=cuts.get(a)
    if n is None:return
    if n=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,0)
    elif n=='audio_uart_ring_task_msg_send':calls.append(('send',uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1)),uc.reg_read(UC_ARM_REG_R2)));uc.reg_write(UC_ARM_REG_R0,0)
    elif n=='audio_event_loop_remove_delayed':calls.append(('remove',))
    elif n=='audio_event_loop_push_delayed':calls.append(('push',uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_master_followup_delayed'] if compiled else 0x4c4ee4)|1,0x600000,count=500)
   obs.append(calls)
  assert obs[0]==obs[1],(connection,obs)
  print('PASS touch followup',connection)
