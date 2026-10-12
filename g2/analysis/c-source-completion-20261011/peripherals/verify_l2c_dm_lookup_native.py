#!/usr/bin/env python3
"""Stock/C DM CCB lookup, three-row bound, and miss diagnostics."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
uint8_t audio_dm_connection_records[0x90];volatile uint8_t audio_l2c_log_enabled_cell;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_hci_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'lookup.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_dm_conn_ccb_by_handle_4b601c',str(D/'l2c_dm_conn_lookup.c'),str(D/'l2c_log_helpers.c'),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,index,enabled,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_dm_connection_records'] if c else 0x200712a4
  for i in range(3):
   u.mem_write(base+i*0x30+0xc,struct.pack('<H',0x100+i))
   u.mem_write(base+i*0x30+0x16,b'\x01' if i!=1 else b'\x00')
  en=(sy['audio_ble_hci_vendor_log_enabled_4c9c50']&~1) if c else 0x4c9c50
  lf=(sy['audio_log_flags']&~1) if c else 0x43d0ce
  lg=(sy['audio_log_extended']&~1) if c else 0x43d574
  tr=(sy['audio_ble_hci_wsf_trace']&~1) if c else 0x52a63c
  effects=[]
  def txt(p):return bytes(u.mem_read(p,160)).split(b'\0')[0].decode('ascii')
  def hook(uc,addr,size,user):
   if addr==en:uc.reg_write(UC_ARM_REG_R0,enabled)
   elif addr==lf:uc.reg_write(UC_ARM_REG_R0,flags)
   elif addr==lg:
    sp=uc.reg_read(UC_ARM_REG_SP);a=struct.unpack('<III',bytes(uc.mem_read(sp,12)))
    effects.append(('log',uc.reg_read(UC_ARM_REG_R0),a[0],txt(a[1]),a[2]))
   elif addr==tr:effects.append(('trace',txt(uc.reg_read(UC_ARM_REG_R0)),txt(uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2)))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_R0,0x100+index);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  entry=(sy['audio_ble_dm_conn_ccb_by_handle_4b601c']&~1) if c else 0x4b601c
  u.emu_start(entry|1,0x600000,count=100000)
  ret=u.reg_read(UC_ARM_REG_R0)
  return (ret-base if ret else None),effects
 cases=0
 for index in range(4):
  for enabled in (0,1):
   for flags in (0,2):
    a=run(False,index,enabled,flags);b=run(True,index,enabled,flags)
    assert a==b,(index,enabled,flags,a,b)
    cases+=1
 print('PASS_L2C_DM_LOOKUP_NATIVE',cases)
