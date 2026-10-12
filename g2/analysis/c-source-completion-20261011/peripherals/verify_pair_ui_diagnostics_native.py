#!/usr/bin/env python3
"""Actual C/native passkey and confirm diagnostics, logging, callback, ABI."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_ui_diagnostics.c'
STUB='''#include <stdint.h>
uintptr_t audio_ble_ui_callback_cells[4];
uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
int32_t audio_l2c_strncmp(const char*a,const char*b,uint32_t n){(void)a;(void)b;(void)n;return 1;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'ui.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_passkey_trace',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names={'enabled':('audio_ble_hci_vendor_log_enabled_4c9c50',0x4c9c50),'cmp':('audio_l2c_strncmp',0x44b610),'mask':('audio_log_level',0x43d0ce),'ext':('audio_log_extended',0x43d574),'trace':('audio_ble_wsf_trace',0x52a63c)}
 def run(compiled,which,enabled,level,mask,callback):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  def string(p):
   return bytes(u.mem_read(p,128)).split(b'\0')[0]
  base=sy['audio_ble_ui_callback_cells'] if compiled else 0x20073f60
  u.mem_write(base+4,struct.pack('<I',0x2008a001 if callback else 0));trace=[]
  for name,(cs,ns) in names.items():
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='enabled':trace.append(('enabled',));uc.reg_write(UC_ARM_REG_R0,enabled)
    elif name=='cmp':
     left,right=string(r0),string(r1);trace.append(('cmp',left,right,r2))
     uc.reg_write(UC_ARM_REG_R0,0 if (level==1 and right==b'ERR') or (level==2 and right==b'WARN') or (level==3 and left==right==b'INFO') else 1)
    elif name=='mask':trace.append(('mask',));uc.reg_write(UC_ARM_REG_R0,mask)
    elif name=='ext':
     sp=uc.reg_read(UC_ARM_REG_SP);line,msg,val,ambient=struct.unpack('<4I',bytes(uc.mem_read(sp,16)))
     trace.append(('ext',r0,string(r1),string(r2),string(r3),line,string(msg),val,ambient if r0==1 else None))
    else:trace.append(('trace',string(r0),string(r1),r2))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  def cb(uc,pc,n,user):trace.append(('callback',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cb,begin=0x2008a000,end=0x2008a000)
  for r,v in ((UC_ARM_REG_R0,123456),(UC_ARM_REG_R1,0x22222222),(UC_ARM_REG_R2,0x33333333),(UC_ARM_REG_R3,0x44444444),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  symbol='audio_ble_pair_passkey_trace' if which=='passkey' else 'audio_ble_pair_compare_trace'
  native=0x4bd7fa if which=='passkey' else 0x4bd91e
  u.emu_start((sy[symbol] if compiled else native)|1,0x600000,count=10000)
  regs=tuple(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
  if regs[1]>=0x100000 and regs[1]<0x800000 and regs[1]!=0x22222222:regs=(regs[0],string(regs[1]),regs[2],regs[3])
  return trace,regs
 cases=0
 for which in ('passkey','confirm'):
  for enabled in (0,1):
   for level in (0,1,2,3,4):
    for mask in (0,2):
     for callback in (0,1):
      a,b=run(False,which,enabled,level,mask,callback),run(True,which,enabled,level,mask,callback)
      assert a==b,(which,enabled,level,mask,callback,a,b)
      cases+=1
 print('PASS_PAIR_UI_DIAGNOSTICS_NATIVE',cases)
