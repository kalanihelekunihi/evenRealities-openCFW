#!/usr/bin/env python3
"""Stock/C L2CAP default callback diagnostic/trace effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
volatile uint8_t audio_l2c_log_enabled_cell;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_hci_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'d.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_l2c_default_data_530538',str(D/'l2c_default_callbacks.c'),str(D/'l2c_log_helpers.c'),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,cid,sequence,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  enable=(sy['audio_ble_hci_vendor_log_enabled_4c9c50']&~1) if c else 0x4c9c50
  logf=(sy['audio_log_flags']&~1) if c else 0x43d0ce
  ext=(sy['audio_log_extended']&~1) if c else 0x43d574
  trace=(sy['audio_ble_hci_wsf_trace']&~1) if c else 0x52a63c
  effects=[];idx=[0]
  def txt(ptr):return bytes(u.mem_read(ptr,160)).split(b'\0')[0].decode('ascii')
  def hook(uc,addr,size,user):
   if addr==enable:
    i=idx[0];idx[0]+=1;uc.reg_write(UC_ARM_REG_R0,sequence[min(i,len(sequence)-1)])
   elif addr==logf:uc.reg_write(UC_ARM_REG_R0,flags)
   elif addr==ext:
    sp=uc.reg_read(UC_ARM_REG_SP);line,fmt,val=struct.unpack('<III',bytes(uc.mem_read(sp,12)))
    s=txt(fmt);effects.append(('ext',uc.reg_read(UC_ARM_REG_R0),line,s,val if '%' in s else None))
   elif addr==trace:
    s=txt(uc.reg_read(UC_ARM_REG_R1));effects.append(('trace',txt(uc.reg_read(UC_ARM_REG_R0)),s,uc.reg_read(UC_ARM_REG_R2) if '%' in s else None))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((UC_ARM_REG_R0,0x1111),(UC_ARM_REG_R1,cid or 0),(UC_ARM_REG_R2,0x2222),(UC_ARM_REG_R3,0x3333),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  entry=(sy['audio_ble_l2c_default_cid_530640'] if cid is not None else sy['audio_ble_l2c_default_data_530538']) if c else (0x530640 if cid is not None else 0x530538)
  u.emu_start(entry|1,0x600000,count=100000)
  return effects,idx[0]
 sequences=((0,),(1,),(0,1),(1,0,1),(1,0,0,1),(1,0,0,0,0),(0,0,0,0,1))
 cases=0
 for cid in (None,0,0x1234):
  for seq in sequences:
   for flags in (0,2):
    a=run(False,cid,seq,flags);b=run(True,cid,seq,flags)
    assert a==b,(cid,seq,flags,a,b)
    cases+=1
 print('PASS_L2C_DEFAULT_NATIVE',cases)
