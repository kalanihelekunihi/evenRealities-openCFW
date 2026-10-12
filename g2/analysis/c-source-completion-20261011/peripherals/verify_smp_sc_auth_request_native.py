#!/usr/bin/env python3
"""Actual compiled-C/native SMP SC auth routing and ambient stack frame."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sc_auth_request.c'
STUB='''#include <stdint.h>
void DmSmpCbackExec(void *e){(void)e;}
void smpSmExecute(uint8_t *c,const uint8_t *e){(void)c;(void)e;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'sc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_smp_sc_callback_5e2aba',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,context0,context1,auth):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  ccb=0x20080000;sc=0x20080100;data=bytearray(0x60);data[0x3d]=7;data[0x40]=auth;data[0x48:0x4c]=struct.pack('<I',sc);u.mem_write(ccb,bytes(data));u.mem_write(sc,bytes([context0,context1])+bytes(30))
  u.mem_write(0x200fef00,bytes([0xa5]*256));trace=[]
  for name,cs,ns in [('callback','DmSmpCbackExec',0x4d24a8),('execute','smpSmExecute',0x56ee62)]:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    p=uc.reg_read(UC_ARM_REG_R0) if name=='callback' else uc.reg_read(UC_ARM_REG_R1)
    trace.append((name,bytes(uc.mem_read(p,24)),uc.reg_read(UC_ARM_REG_R0)==ccb if name=='execute' else True))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  for r,v in ((UC_ARM_REG_R0,ccb),(UC_ARM_REG_R1,0x1234),(UC_ARM_REG_R2,0xabcd),(UC_ARM_REG_R3,0x9876),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  a=sy['audio_ble_smp_sc_callback_5e2aba'] if compiled else 0x5e2aba
  u.emu_start(a|1,0x600000,count=1000)
  return trace
 cases=0
 for c0 in (0,1):
  for c1 in (0,2,3):
   for auth in (0,4):
    a,b=run(False,c0,c1,auth),run(True,c0,c1,auth)
    assert a==b,(c0,c1,auth,a,b)
    cases+=1
 print('PASS_SMP_SC_AUTH_REQUEST_NATIVE',cases)
