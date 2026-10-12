#!/usr/bin/env python3
"""Bounded compiled-C/stock RING_ConnectPolicyNotifyConnectSuccessSoon."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_policy_success.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_ring_policy_pending_2007500b;
void audio_ble_ring_policy_delayed(void){}
uint32_t audio_ble_master_success_delayed(uint32_t x){return x;}
uint32_t audio_event_loop_remove_delayed(void (*f)(void)){(void)f;return 0;}
void audio_event_loop_push_delayed(void (*f)(void),uint32_t a,uint32_t d){(void)f;(void)a;(void)d;}
uint32_t audio_uart_ring_active(void){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ring_policy_notify_success_49f646',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for owner in (0,1):
  for level in (0,7):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    state=sym['audio_ble_ring_policy_pending_2007500b'] if is_c else 0x2007500b;u.mem_write(state,b'\x01')
    cb_timeout=sym['audio_ble_ring_policy_delayed'] if is_c else 0x49f501
    cb_success=sym['audio_ble_master_success_delayed'] if is_c else 0x4bc419
    def cb(x):return 'timeout' if x in (cb_timeout,cb_timeout&~1) else 'success' if x in (cb_success,cb_success&~1) else hex(x)
    trace=[]
    hooks=[('audio_event_loop_remove_delayed',0x476ace),('audio_event_loop_push_delayed',0x47697e),('audio_uart_ring_active',0x4a2914),('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
    for n,a in hooks:
     addr=sym[n] if is_c else a
     def hook(uc,address,size,user_data,n=n):
      r0=uc.reg_read(UC_ARM_REG_R0)
      if n=='audio_event_loop_remove_delayed':trace.append(('remove',cb(r0)))
      elif n=='audio_event_loop_push_delayed':trace.append(('push',cb(r0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
      elif n=='audio_uart_ring_active':trace.append(('owner',));uc.reg_write(UC_ARM_REG_R0,owner)
      elif n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
      elif n=='audio_log_extended':trace.append(('extended',r0))
      else:trace.append(('compressed',r0))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sym['audio_ble_ring_policy_notify_success_49f646'] if is_c else 0x49f646)|1,0x600000,count=2000)
    pair.append((trace,u.mem_read(state,1)[0]))
   assert pair[0]==pair[1],(owner,level,pair)
 print('PASS_RING_POLICY_SUCCESS_NATIVE',4)
