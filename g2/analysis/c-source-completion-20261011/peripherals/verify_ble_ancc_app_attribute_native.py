#!/usr/bin/env python3
"""Actual compiled-C/native ANCC app attribute and sync result effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_app_attribute.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ancc_state[0x600];
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,...){(void)a;(void)b;return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
void audio_ble_attc_write_request(uint8_t a,uint16_t b,uint16_t c,const uint8_t*d){(void)a;(void)b;(void)c;(void)d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'app.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_get_app_attribute_4bebc4',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 stock={'audio_ble_ancc_get_app_attribute_4bebc4':0x4bebc4,'audio_ble_ancc_rx_sync_callback_4bed0e':0x4bed0e,
        'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,
        'audio_queue_copy_bytes':0x439be4,'audio_ble_attc_write_request':0x4b579c}
 def run(c,which,length,handle,flags,status):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_ancc_state'] if c else 0x200695c8
  u.mem_write(state,bytes((3,))+bytes(0x5ff))
  u.mem_write(0x20083000,bytes((0,0,0,0,handle,0,0,0)))
  u.mem_write(0x20081000,b'a'*length+b'\0')
  effects=[];addr={((sy[k]&~1) if c else v):k for k,v in stock.items()}
  def hook(uc,a,size,user):
   k=addr.get(a)
   if not k:return
   r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   if k=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='audio_log_extended':effects.append(('log',r0))
   elif k=='compressed_log_output':effects.append(('compact',r0))
   elif k=='audio_queue_copy_bytes':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
   elif k=='audio_ble_attc_write_request':effects.append(('att',r0,r1,r2,bytes(uc.mem_read(r3,r2))))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.mem_write(0x200fef80,bytes((i*37+11)&255 for i in range(128)))
  u.reg_write(UC_ARM_REG_R0,0x20083000 if which=='app' else status)
  u.reg_write(UC_ARM_REG_R1,0x20081000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  entry='audio_ble_ancc_get_app_attribute_4bebc4' if which=='app' else 'audio_ble_ancc_rx_sync_callback_4bed0e'
  u.emu_start(((sy[entry]&~1) if c else stock[entry])|1,0x600000,count=30000)
  return effects,u.reg_read(UC_ARM_REG_R0) if which=='sync' else None
 cases=0
 for length in (0,1,10,61,62,63,64,70,73):
  for handle in (0,8):
   a=run(False,'app',length,handle,0,0);b=run(True,'app',length,handle,0,0)
   assert a==b,('app',length,handle,a,b)
   cases+=1
 for status in (0,5):
  for flags in (0,1,2,4,7):
   a=run(False,'sync',0,0,flags,status);b=run(True,'sync',0,0,flags,status)
   assert a==b,('sync',status,flags,a,b)
   cases+=1
 print('PASS_BLE_ANCC_APP_ATTRIBUTE_NATIVE',cases)
