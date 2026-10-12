#!/usr/bin/env python3
"""Native/C diagnostic call sequence for settings dump 0x46b458."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/settings_dump_config.c'
SHIM='''#include <stdint.h>
uint8_t audio_settings_config_live[64];
uint32_t audio_log_flags(void){return 7;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'dump.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SVC_Settings_DumpSettingConfig',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,record,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for addr,data in seg:u.mem_write(addr,data)
  u.mem_write(sy['audio_settings_config_live'] if is_c else 0x20072da8,record)
  faddr=(sy['audio_log_flags']&~1) if is_c else 0x43d0ce
  eaddr=(sy['audio_log_extended']&~1) if is_c else 0x43d574
  caddr=(sy['compressed_log_output']&~1) if is_c else 0x43ce9e
  calls=[]
  def txt(ptr):return bytes(u.mem_read(ptr,160)).split(b'\0')[0].decode('ascii')
  def hook(uc,addr,size,user):
   if addr==faddr:uc.reg_write(UC_ARM_REG_R0,flags)
   elif addr==eaddr:
    sp=uc.reg_read(UC_ARM_REG_SP);line,fmt,val=struct.unpack('<III',bytes(uc.mem_read(sp,12)))
    s=txt(fmt);calls.append(('e',uc.reg_read(UC_ARM_REG_R0),line,s,val if '%' in s else None))
   elif addr==caddr:
    s=txt(uc.reg_read(UC_ARM_REG_R1));calls.append(('c',uc.reg_read(UC_ARM_REG_R0),s,uc.reg_read(UC_ARM_REG_R3) if '%' in s else None))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['SVC_Settings_DumpSettingConfig'] if is_c else 0x46b458)|1,0x600000,count=100000)
  return calls
 cases=0
 for flags in (0,1,2,4,7):
  for seed in (0,37):
   p=bytes((i*17+seed)&255 for i in range(64))
   a=run(False,p,flags);b=run(True,p,flags)
   assert a==b,(flags,seed,a,b)
   cases+=1
 print('PASS_SETTINGS_DUMP_NATIVE',cases)
