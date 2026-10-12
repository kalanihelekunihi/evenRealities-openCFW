#!/usr/bin/env python3
"""Compiled-C/native whitelist behavior on authenticated product RAM."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_whitelist.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ancc_service_state[8],audio_ble_whitelist_info[0x100];
uint32_t g2_log_module_length(const char*p){(void)p;return 0;}
int32_t audio_l2c_strncmp(const char*a,const char*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'w.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_whitelist_type_4d67b8',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 stock={'audio_ble_ancc_whitelist_type_4d67b8':0x4d67b8,'g2_log_module_length':0x44a43c,'audio_l2c_strncmp':0x44b610,
        'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
 def run(c,kind,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_ancc_service_state'] if c else 0x200036c8
  info=sy['audio_ble_whitelist_info'] if c else 0x20054718
  u.mem_write(state+4,bytes((1 if kind=='disabled' else 0,)))
  row=bytearray(0x100);row[0]=0x10;row[1]=1;row[2:2+8]=b'com.test';u.mem_write(info,bytes(row))
  s=({'null':None,'long':b'x'*64,'vendor1':b'com.even.sg','vendor2':b'com.even.g1','listed':b'com.test.app','blocked':b'other.app','disabled':b'other.app'})[kind]
  if s is not None:u.mem_write(0x20081000,s+b'\0')
  effects=[];addr={((sy[k]&~1) if c else v):k for k,v in stock.items()}
  def string(p):
   if p==0:return b''
   return bytes(uc.mem_read(p+i,1)[0] for i in range(80)) if False else bytes(u.mem_read(p,80)).split(b'\0')[0]
  def hook(uc,a,size,user):
   k=addr.get(a)
   if not k:return
   r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   if k=='g2_log_module_length':uc.reg_write(UC_ARM_REG_R0,len(string(r0)))
   elif k=='audio_l2c_strncmp':uc.reg_write(UC_ARM_REG_R0,0 if bytes(uc.mem_read(r0,r2))==bytes(uc.mem_read(r1,r2)) else 1)
   elif k=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='audio_log_extended':effects.append(('log',r0))
   elif k=='compressed_log_output':effects.append(('compact',r0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_R0,0 if s is None else 0x20081000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start(((sy['audio_ble_ancc_whitelist_type_4d67b8']&~1) if c else 0x4d67b8)|1,0x600000,count=30000)
  return u.reg_read(UC_ARM_REG_R0),effects
 cases=0
 for kind in ('disabled','null','long','vendor1','vendor2','listed','blocked'):
  for flags in (0,1,2,4,7):
   a=run(False,kind,flags);b=run(True,kind,flags)
   assert a==b,(kind,flags,a,b)
   cases+=1
 print('PASS_BLE_ANCC_WHITELIST_NATIVE',cases)
