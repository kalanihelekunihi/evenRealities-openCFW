#!/usr/bin/env python3
"""Actual compiled-C/native privacy reset, flash erase, and ten-row effects.
Logger-disabled only; logger paths remain qualified by static native ABI evidence.
"""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_privacy_erase_all.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_privacy_rows[2000];uint8_t audio_ble_flash_staging_200636a0[256];
volatile uint16_t audio_ble_bond_flash_bytes_20004524;uint8_t audio_ble_privacy_nvm_records[2560];
void audio_ble_privacy_cache_maintenance(const void*p,uint8_t x){(void)p;(void)x;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
uint32_t g2_gpio_critical_save(void){return 0;}
uint32_t audio_ble_nvm_write_words(uint32_t k,const uint8_t*s,uint8_t*d,uint32_t n){(void)k;(void)s;(void)d;(void)n;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_privacy_reset_local',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names={'cache':('audio_ble_privacy_cache_maintenance',0x475014),'zero':('audio_uart_buffer_zero',0x43c0e4),'crit':('g2_gpio_critical_save',0x473940),'nvm':('audio_ble_nvm_write_words',0x4d0a2c),'flags':('audio_log_level',0x43d0ce),'ext':('audio_log_extended',0x43d574),'compact':('compressed_log_output',0x43ce9e)}
 def run(compiled,result,size,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  row=sy['audio_ble_privacy_rows'] if compiled else 0x20067a30
  stage=sy['audio_ble_flash_staging_200636a0'] if compiled else 0x200636a0
  length=sy['audio_ble_bond_flash_bytes_20004524'] if compiled else 0x20004524
  dest=sy['audio_ble_privacy_nvm_records'] if compiled else 0x7ff000
  u.mem_write(row,bytes([0xa5]*2000));u.mem_write(stage,bytes([0x66]*256));u.mem_write(length,struct.pack('<H',size))
  trace=[]
  for name,(cs,ns) in names.items():
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0,r1,r2,r3=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='cache':trace.append(('cache',r0,r1))
    elif name=='zero':
     trace.append(('zero','stage' if r0==stage else (r0-row)//200,r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
    elif name=='crit':trace.append(('crit',));uc.reg_write(UC_ARM_REG_R0,0)
    elif name=='nvm':trace.append(('nvm',r0,r1==stage,r2==dest,r3));uc.reg_write(UC_ARM_REG_R0,result)
    elif name=='flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,flags)
    elif name=='ext':trace.append(('ext',r0,r2!=0,r3!=0,struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]));
    elif name=='compact':
     payload=bytes(uc.mem_read(r3,128)).split(b'\0')[0] if r3>=0x100000 and r3<0x800000 else r3
     trace.append(('compact',r0,r1!=0,r2!=0,payload))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(0x1111,0x2222,0x3333,0x4444)):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  a=(sy['audio_ble_privacy_reset_local'] if compiled else 0x47acf8)
  u.emu_start(a|1,0x600000,count=20000)
  return trace,bytes(u.mem_read(row,2000)),bytes(u.mem_read(stage,256))
 cases=0
 for result in (0,0x08000140):
  for size in (0,64,128,252):
   for flags in (0,1,2,4,7):
    a,b=run(False,result,size,flags),run(True,result,size,flags)
    assert a==b,(result,size,flags,a[0],b[0])
    cases+=1
 print('PASS_PRIVACY_ERASE_ALL_NATIVE',cases)
