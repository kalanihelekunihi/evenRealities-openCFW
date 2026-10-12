#!/usr/bin/env python3
"""Actual C/native DmReadRemoteFeatures CCB and callback packet effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/app_remote_features.c'
STUB='''#include <stdint.h>
uint8_t audio_dm_connection_records[0xb0];
uint8_t *dmConnCcbById(uint8_t x){(void)x;return 0;}
void HciLeReadRemoteFeatCmd(uint16_t x){(void)x;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'remote.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmReadRemoteFeatures',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names=[('ccb','dmConnCcbById',0x4b62a8),('cmd','HciLeReadRemoteFeatCmd',0x52b352),('zero','audio_uart_buffer_zero',0x43c0e4)]
 def run(compiled,exists,feature_ready):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_dm_connection_records'] if compiled else 0x200712a4
  ccb=0x20081000;data=bytearray(0x30);data[0xc:0xe]=struct.pack('<H',0x4567);data[0x10]=3;data[0x28:0x2c]=struct.pack('<I',0xa1b2c3d4);data[0x2c]=feature_ready;u.mem_write(ccb,bytes(data))
  u.mem_write(base+0x9c,struct.pack('<I',0x2008a001));trace=[]
  for name,cname,stock in names:
   addr=(sy[cname]&~1) if compiled else stock
   def hook(uc,pc,size,user,name=name):
    a,b,c,d=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='ccb':trace.append(('ccb',a));uc.reg_write(UC_ARM_REG_R0,ccb if exists else 0)
    elif name=='cmd':trace.append(('cmd',a))
    else:trace.append(('zero',b,c));uc.mem_write(a,bytes(b))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
  def callback(uc,pc,size,user):trace.append(('callback',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),16))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,callback,begin=0x2008a000,end=0x2008a000)
  for r,v in ((UC_ARM_REG_R0,3),(UC_ARM_REG_R1,0x7777),(UC_ARM_REG_R2,0x8888),(UC_ARM_REG_R3,0x9999),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  entry=(sy['DmReadRemoteFeatures']&~1) if compiled else 0x4b6cb0
  u.emu_start(entry|1,0x600000,count=30000)
  return u.reg_read(UC_ARM_REG_R0),trace
 cases=0
 for exists in (0,1):
  for ready in (0,1):
   a=run(False,exists,ready);b=run(True,exists,ready)
   assert a==b,(exists,ready,a,b)
   cases+=1
 print('PASS_APP_REMOTE_FEATURES_NATIVE',cases)
