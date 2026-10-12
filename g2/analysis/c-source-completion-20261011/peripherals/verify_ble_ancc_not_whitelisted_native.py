#!/usr/bin/env python3
"""Actual C/native protobuf encoder allocation, packet, and return effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_not_whitelisted.c'
SHIM='''#include <stdint.h>
struct pb_ostream_candidate{void*callback;void*state;uint32_t max_size;uint32_t bytes_written;const char*errmsg;};
const uint8_t audio_ble_ancc_not_whitelisted_pb_descriptor[16]={0};
void *file_heap_allocate(uint32_t a){(void)a;return 0;}
void file_heap_free(void*a){(void)a;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
uint32_t g2_log_module_length(const char*a){(void)a;return 0;}
uint32_t g2_flashdb_candidate_tick(void){return 0;}
void audio_pb_ostream_from_buffer(struct pb_ostream_candidate*a,void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_pb_encode(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_settings_notify_ble(uint8_t a,uint8_t b,const void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'enc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_not_whitelisted_4d71bc',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 stock={'audio_ble_ancc_not_whitelisted_4d71bc':0x4d71bc,'file_heap_allocate':0x474cd2,'file_heap_free':0x474d16,
        'audio_uart_buffer_zero':0x43c0e4,'audio_queue_copy_bytes':0x439be4,'g2_log_module_length':0x44a43c,
        'g2_flashdb_candidate_tick':0x4490cc,'audio_pb_ostream_from_buffer':0x4905f4,'audio_pb_encode':0x490c32,
        'audio_settings_notify_ble':0x475c1a,'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
 def run(c,alloc,encode,send,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_write(0x20081000,b'com.app\0');u.mem_write(0x20081100,b'App Name\0')
  effects=[];addr={((sy[k]&~1) if c else v):k for k,v in stock.items()}
  def hook(uc,a,size,user):
   k=addr.get(a)
   if not k:return
   r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   if k=='file_heap_allocate':effects.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,0x20090000 if alloc else 0)
   elif k=='file_heap_free':effects.append(('free',r0==0x20090000))
   elif k=='audio_uart_buffer_zero':uc.mem_write(r0,bytes(r1))
   elif k=='audio_queue_copy_bytes':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
   elif k=='g2_log_module_length':uc.reg_write(UC_ARM_REG_R0,len(bytes(uc.mem_read(r0,100)).split(b'\0')[0]))
   elif k=='g2_flashdb_candidate_tick':uc.reg_write(UC_ARM_REG_R0,0x1234)
   elif k=='audio_pb_ostream_from_buffer':uc.mem_write(r0,struct.pack('<5I',0x11111111,r1,r2,0,0))
   elif k=='audio_pb_encode':
    effects.append(('encode',r1==((sy['audio_ble_ancc_not_whitelisted_pb_descriptor'] if c else 0x7799f4)),r2==0x2009004e))
    uc.mem_write(r0+12,struct.pack('<I',13));uc.mem_write(r0+16,struct.pack('<I',0));uc.reg_write(UC_ARM_REG_R0,encode)
   elif k=='audio_settings_notify_ble':effects.append(('send',r0,r1,r2==0x20090000,r3,bytes(uc.mem_read(r2,0x9c))));uc.reg_write(UC_ARM_REG_R0,send)
   elif k=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='audio_log_extended':effects.append(('log',r0))
   elif k=='compressed_log_output':effects.append(('compact',r0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_R0,0x20081000);u.reg_write(UC_ARM_REG_R1,0x20081100);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start(((sy['audio_ble_ancc_not_whitelisted_4d71bc']&~1) if c else 0x4d71bc)|1,0x600000,count=40000)
  return u.reg_read(UC_ARM_REG_R0),effects,bytes(u.mem_read(0x20090000,0x9c))
 cases=0
 for alloc,encode,send in ((0,1,0),(1,0,0),(1,1,0),(1,1,1)):
  for flags in (0,1,2,4,7):
   a=run(False,alloc,encode,send,flags);b=run(True,alloc,encode,send,flags)
   assert a==b,(alloc,encode,send,flags,a[0],b[0],a[1],b[1],[(i,x,y) for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y][:10])
   cases+=1
 print('PASS_BLE_ANCC_NOT_WHITELISTED_NATIVE',cases)
