#!/usr/bin/env python3
"""Compare compiled ANCC notification/list source to native RAM and calls."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ancc_state[0x600];
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,...){(void)a;(void)b;return 0;}
void audio_event_loop_push_delayed(void (*a)(void),uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_ble_ancc_attr_handler_4bf228(const uint8_t*a,uint16_t b){(void)a;(void)b;return 0;}
void audio_ble_ancc_get_next_delayed_4bea7a(uint32_t a){(void)a;}
void audio_ble_ancc_reset_state_machine(void){}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'ancc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_notification_value_update_4bee5a',str(D/'display_ble_ancc_notification.c'),str(D/'display_ble_ancc_state_children.c'),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 stock={'audio_ble_ancc_notification_value_update_4bee5a':0x4bee5a,'audio_ble_ancc_action_push_4bec20':0x4bec20,
        'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,'audio_event_loop_push_delayed':0x47697e,'audio_ble_ancc_attr_handler_4bf228':0x4bf228}
 def run(c,kind,full=False,duplicate=False,connected=True,flags=0):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_ancc_state'] if c else 0x200695c8
  data=bytearray(0x600);data[0]=3 if connected else 0;data[1]=0x42
  if full:
   for i in range(64):data[0x24+12*i]=1
  if duplicate:
   data[0x24+12*3]=1;data[0x20+12*3:0x24+12*3]=struct.pack('<I',0x12345678)
  u.mem_write(state,bytes(data))
  u.mem_write(0x20082000,bytes((2 if kind=='remove' else 1,0,4,0))+struct.pack('<I',0x12345678))
  handle=7 if kind in ('push','remove','direct') else 9 if kind=='attr' else 10
  u.mem_write(0x20081000,bytes(4)+struct.pack('<I',0x20082000)+struct.pack('<H',8)+struct.pack('<H',handle)+bytes(8))
  u.mem_write(0x20083000,struct.pack('<H',7)+bytes(4)+struct.pack('<H',9))
  effects=[]
  callback=(sy['audio_ble_ancc_get_next_delayed_4bea7a']&~1) if c else 0x4bea7a
  addr={((sy[k]&~1) if c else v):k for k,v in stock.items() if k in sy}
  def hook(uc,a,size,user):
   k=addr.get(a)
   if not k:return
   r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   if k=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='audio_log_extended':effects.append(('log',r0))
   elif k=='compressed_log_output':effects.append(('compact',r0))
   elif k=='audio_event_loop_push_delayed':effects.append(('delay',r0==callback,r1,r2))
   elif k=='audio_ble_ancc_attr_handler_4bf228':effects.append(('attr',r0==0x20082000,r1));uc.reg_write(UC_ARM_REG_R0,0)
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_R0,0x20083000);u.reg_write(UC_ARM_REG_R1,0x20081000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start(((sy['audio_ble_ancc_notification_value_update_4bee5a']&~1) if c else 0x4bee5a)|1,0x600000,count=60000)
  return bytes(u.mem_read(state,0x600)),effects
 cases=0
 for kind,full,duplicate,connected,flags in [('push',0,0,1,0),('push',0,0,0,0),('push',1,0,1,0),('push',0,1,1,0),('remove',0,0,1,0),('attr',0,0,1,0),('other',0,0,1,0)]+[(k,0,0,1,f) for k in ('push','remove','attr') for f in (1,2,4,7)]:
  a=run(False,kind,full,duplicate,connected,flags);b=run(True,kind,full,duplicate,connected,flags)
  assert a==b,(kind,full,duplicate,connected,flags,a[1],b[1],[(i,x,y) for i,(x,y) in enumerate(zip(a[0],b[0])) if x!=y][:10])
  cases+=1
 print('PASS_BLE_ANCC_NOTIFICATION_NATIVE',cases)
