#!/usr/bin/env python3
"""Controlled stock/C ANCC attribute parser state and lower-effect comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_attr_parser.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ancc_state[0x600],audio_ble_ancc_cache[0x400];
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,...){(void)a;(void)b;return 0;}
uint8_t audio_ble_ancc_whitelist_type_4d67b8(const uint8_t*a){(void)a;return 0;}
void audio_ble_ancc_not_whitelisted_4d71bc(const uint8_t*a,const uint8_t*b){(void)a;(void)b;}
void audio_ble_ancc_send_complete_4bedac(const uint8_t*a,uint32_t b){(void)a;(void)b;}
void audio_ble_ancc_reset_state_machine(void){}
void audio_ble_ancc_attr_callback_4bf06c(uint8_t*a){(void)a;}
void audio_ble_ancc_perform_action_4beb82(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'parser.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_attr_handler_4bf228',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 stock={'audio_ble_ancc_attr_handler_4bf228':0x4bf228,'audio_uart_buffer_zero':0x43c0e4,'audio_queue_copy_bytes':0x439be4,
        'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,
        'audio_ble_ancc_whitelist_type_4d67b8':0x4d67b8,'audio_ble_ancc_not_whitelisted_4d71bc':0x4d71bc,
        'audio_ble_ancc_send_complete_4bedac':0x4bedac,'audio_ble_ancc_reset_state_machine':0x4bf6c4,
        'audio_ble_ancc_attr_callback_4bf06c':0x4bf06c,'audio_ble_ancc_perform_action_4beb82':0x4beb82}
 def run(c,kind,whitelist=0,flags=0):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_ancc_state'] if c else 0x200695c8
  cache=sy['audio_ble_ancc_cache'] if c else 0x2006ddd4
  s=bytearray(0x600);q=bytearray(0x400);s[0]=3
  if kind=='badstate':s[10]=3;payload=b'abc'
  elif kind=='append':s[10]=2;s[12:14]=struct.pack('<H',10);payload=b'abcd'
  elif kind=='overflow':s[10]=2;s[12:14]=struct.pack('<H',510);payload=b'abcd'
  elif kind=='short':s[10]=1;s[12:14]=struct.pack('<H',5);s[14:16]=struct.pack('<H',4);payload=b''
  elif kind in ('attr','attr_done','attr_incomplete'):
   s[10]=1;s[12:14]=struct.pack('<H',6)
   s[0x14:0x16]=struct.pack('<H',7 if kind=='attr_done' else 0)
   s[0x35c:0x362]=b'\x02'+struct.pack('<H',4 if kind=='attr_incomplete' else 0)+b'abc'
   payload=b''
  elif kind=='uid':payload=b'\x00\x78\x56\x34\x12'
  else:payload=b'\x01A\x00\x00\x02\x00BC\x00\x00'
  u.mem_write(state,bytes(s));u.mem_write(cache,bytes(q));u.mem_write(0x20081000,payload+bytes(64))
  effects=[];addr={((sy[k]&~1) if c else v):k for k,v in stock.items() if k in sy}
  def hook(uc,a,size,user):
   k=addr.get(a)
   if not k:return
   r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   if k=='audio_uart_buffer_zero':uc.mem_write(r0,bytes(r1))
   elif k=='audio_queue_copy_bytes':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
   elif k=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='audio_log_extended':effects.append(('log',r0))
   elif k=='compressed_log_output':effects.append(('compact',r0))
   elif k=='audio_ble_ancc_whitelist_type_4d67b8':effects.append('whitelist');uc.reg_write(UC_ARM_REG_R0,whitelist)
   elif k=='audio_ble_ancc_not_whitelisted_4d71bc':effects.append('notwhitelisted')
   elif k=='audio_ble_ancc_send_complete_4bedac':effects.append(('complete',r1))
   elif k=='audio_ble_ancc_reset_state_machine':effects.append('reset')
   elif k=='audio_ble_ancc_attr_callback_4bf06c':effects.append('callback')
   elif k=='audio_ble_ancc_perform_action_4beb82':effects.append(('action',r1,r2))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_R0,0x20081000);u.reg_write(UC_ARM_REG_R1,len(payload));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start(((sy['audio_ble_ancc_attr_handler_4bf228']&~1) if c else 0x4bf228)|1,0x600000,count=60000)
  return bytes(u.mem_read(state,0x600)),bytes(u.mem_read(cache,0x400)),effects,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for kind,whitelist,flags in [(k,0,0) for k in ('badstate','append','overflow','short','attr','attr_done','attr_incomplete','uid')]+[('appid',v,0) for v in (0,1,2,3)]+[(k,v,f) for k,v in [('attr_done',0)]+[('appid',v) for v in (0,1,2,3)] for f in (1,2,4,7)]:
  a=run(False,kind,whitelist,flags);b=run(True,kind,whitelist,flags)
  assert a==b,(kind,whitelist,flags,a[2:],b[2:],[(i,x,y) for i,(x,y) in enumerate(zip(a[0],b[0])) if x!=y][:10],[(i,x,y) for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:10])
  cases+=1
 print('PASS_BLE_ANCC_ATTR_PARSER_NATIVE',cases)
