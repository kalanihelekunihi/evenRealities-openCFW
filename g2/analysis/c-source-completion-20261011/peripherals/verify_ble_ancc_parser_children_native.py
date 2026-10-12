#!/usr/bin/env python3
"""Compiled-C/native ANCC complete, action packet, and attribute callback."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_parser_children.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ancc_state[0x600],audio_ble_ancc_cache[0x400];
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,...){(void)a;(void)b;return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
uint32_t g2_log_module_length(const char*a){(void)a;return 0;}
int32_t audio_ble_send_status_message(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_ble_ancc_rx_sync_callback_4bed0e(uint32_t a){(void)a;}
void audio_ble_ancc_get_app_attribute_4bebc4(uint32_t a,const char*b){(void)a;(void)b;}
void audio_ble_attc_write_request(uint8_t a,uint16_t b,uint16_t c,const uint8_t*d){(void)a;(void)b;(void)c;(void)d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'children.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_attr_callback_4bf06c',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 stock={'audio_ble_ancc_send_complete_4bedac':0x4bedac,'audio_ble_ancc_perform_action_4beb82':0x4beb82,'audio_ble_ancc_attr_callback_4bf06c':0x4bf06c,
        'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,'audio_queue_copy_bytes':0x439be4,
        'g2_log_module_length':0x44a43c,'audio_ble_send_status_message':0x464d1c,'audio_ble_ancc_get_app_attribute_4bebc4':0x4bebc4,'audio_ble_attc_write_request':0x4b579c}
 def run(c,which,mode,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_ancc_state'] if c else 0x200695c8;cache=sy['audio_ble_ancc_cache'] if c else 0x2006ddd4
  s=bytearray(0x600);s[0]=3;s[4:8]=struct.pack('<I',0x20083000);s[8:10]=struct.pack('<H',2)
  s[0x1c+2*12:0x20+2*12]=bytes((5,1,6,7));s[0x35c+8:0x35c+12]=b'app\0';s[0x35c+6:0x35c+8]=struct.pack('<H',4)
  s[0x12]=mode if which=='attr' else 0
  s[0x10:0x12]=struct.pack('<H',4);s[0xe:0x10]=struct.pack('<H',8)
  u.mem_write(state,bytes(s));u.mem_write(cache,bytes(0x400))
  u.mem_write(0x20083000,bytes((7,0,0,0,8 if mode else 0,0,9,0)))
  u.mem_write(0x20081000,b'payload'+bytes(16))
  effects=[];addr={((sy[k]&~1) if c else v):k for k,v in stock.items() if k in sy}
  callback=(sy['audio_ble_ancc_rx_sync_callback_4bed0e']&~1) if c else 0x4bed0e
  def hook(uc,a,size,user):
   k=addr.get(a)
   if not k:return
   r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   if k=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='audio_log_extended':effects.append(('log',r0))
   elif k=='compressed_log_output':effects.append(('compact',r0))
   elif k=='audio_queue_copy_bytes':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
   elif k=='g2_log_module_length':uc.reg_write(UC_ARM_REG_R0,len(bytes(uc.mem_read(r0,96)).split(b'\0')[0]))
   elif k=='audio_ble_send_status_message':effects.append(('sendcomplete',r0,r1==0x20081000,r2,r3==callback))
   elif k=='audio_ble_ancc_get_app_attribute_4bebc4':effects.append(('getapp',r0,bytes(uc.mem_read(r1,32)).split(b'\0')[0]))
   elif k=='audio_ble_attc_write_request':effects.append(('att',r0,r1,r2,bytes(uc.mem_read(r3,r2))))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  if which=='complete':r0,r1=0x20081000,0x2fc
  elif which=='action':r0,r1=0x20083000,0x12345678
  else:r0,r1=state+8,0
  for reg,val in ((UC_ARM_REG_R0,r0),(UC_ARM_REG_R1,r1),(UC_ARM_REG_R2,1),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start(((sy[stock_inv[which]]&~1) if c else stock[stock_inv[which]])|1,0x600000,count=30000)
  return bytes(u.mem_read(state,0x600)),bytes(u.mem_read(cache,0x400)),effects
 stock_inv={'complete':'audio_ble_ancc_send_complete_4bedac','action':'audio_ble_ancc_perform_action_4beb82','attr':'audio_ble_ancc_attr_callback_4bf06c'}
 cases=0
 for which,mode in [('complete',0),('action',0),('action',1)]+[('attr',i) for i in (0,1,2,3,5,6,7,9)]:
  for flags in (0,1,2,4):
   a=run(False,which,mode,flags);b=run(True,which,mode,flags)
   assert a==b,(which,mode,flags,a[2],b[2],[(i,x,y) for i,(x,y) in enumerate(zip(a[0],b[0])) if x!=y][:8],[(i,x,y) for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:8])
   cases+=1
 print('PASS_BLE_ANCC_PARSER_CHILDREN_NATIVE',cases)
