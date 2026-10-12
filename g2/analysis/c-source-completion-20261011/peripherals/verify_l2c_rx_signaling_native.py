#!/usr/bin/env python3
"""Stock/C comparison for L2CAP signaling role dispatch and failure effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
uint8_t audio_ble_l2c_state[0x30];volatile uint8_t audio_l2c_log_enabled_cell;
uint8_t DmConnIdByHandle(uint16_t h){(void)h;return 0;}
uint8_t DmConnRole(uint8_t c){(void)c;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_hci_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'signal.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_l2c_rx_signaling_53076e',str(D/'l2c_rx_signaling.c'),str(D/'l2c_log_helpers.c'),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,length,conn,role,cbmask,enabled,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_l2c_state'] if c else 0x200737d8
  for off,bit,addr in ((24,1,0x20090001),(28,2,0x20090101)):
   u.mem_write(state+off,struct.pack('<I',addr if cbmask&bit else 0))
  dm=(sy['DmConnIdByHandle']&~1) if c else 0x4b6e96
  dr=(sy['DmConnRole']&~1) if c else 0x4b73c4
  en=(sy['audio_ble_hci_vendor_log_enabled_4c9c50']&~1) if c else 0x4c9c50
  lf=(sy['audio_log_flags']&~1) if c else 0x43d0ce
  lg=(sy['audio_log_extended']&~1) if c else 0x43d574
  tr=(sy['audio_ble_hci_wsf_trace']&~1) if c else 0x52a63c
  effects=[]
  def txt(p):return bytes(u.mem_read(p,160)).split(b'\0')[0].decode('ascii')
  def hook(uc,addr,size,user):
   if addr==dm:effects.append(('dm',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,conn)
   elif addr==dr:effects.append(('role',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,role)
   elif addr==en:uc.reg_write(UC_ARM_REG_R0,enabled)
   elif addr==lf:uc.reg_write(UC_ARM_REG_R0,flags)
   elif addr==lg:
    sp=uc.reg_read(UC_ARM_REG_SP);a=struct.unpack('<III',bytes(uc.mem_read(sp,12)))
    effects.append(('log',uc.reg_read(UC_ARM_REG_R0),a[0],txt(a[1]),a[2]))
   elif addr==tr:effects.append(('trace',txt(uc.reg_read(UC_ARM_REG_R0)),txt(uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2)))
   elif addr in (0x20090000,0x20090100):effects.append(('cb',addr,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((UC_ARM_REG_R0,0x1234),(UC_ARM_REG_R1,length),(UC_ARM_REG_R2,0x20080000),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start(((sy['audio_ble_l2c_rx_signaling_53076e'] if c else 0x53076e)|1),0x600000,count=100000)
  return effects
 cases=0
 for length,conn,role,cbmask in ((3,1,0,3),(4,0,0,3),(4,1,0,3),(5,2,1,3),(6,2,2,3),(6,2,0,0),(6,2,1,0)):
  for enabled in (0,1):
   for flags in (0,2):
    a=run(False,length,conn,role,cbmask,enabled,flags);b=run(True,length,conn,role,cbmask,enabled,flags)
    assert a==b,(length,conn,role,cbmask,enabled,flags,a,b)
    cases+=1
 print('PASS_L2C_RX_SIGNALING_NATIVE',cases)
