#!/usr/bin/env python3
"""Actual C/stock SMP SC cat, passkey-bit, and security-level effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sc_small_children.c'
STUB='''#include <stdint.h>
void Calc128Cpy(uint8_t*d,uint8_t*s){for(int i=0;i<16;i++)d[i]=s[i];}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SmpScCat128',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[('cat',0,0,0),*[( 'bit',p,0,0) for p in (0,7,8,63,127,128,255)],
        ('level',0,0,0),('level',4,16,16),('level',4,16,7),('level',4,8,16)]
 for kind,a,b,c in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for addr,data in seg:u.mem_write(addr,data)
   ccb,sc,scratch,dst,src=0x20080000,0x20080100,0x20080200,0x20080400,0x20080500
   u.mem_write(ccb+0x48,sc.to_bytes(4,'little'))
   u.mem_write(sc+0x14,scratch.to_bytes(4,'little'))
   u.mem_write(sc+3,bytes([a]));u.mem_write(scratch,bytes([0x55]*0x200))
   u.mem_write(ccb+0x40,bytes([a]));u.mem_write(ccb+0x24,bytes([b]));u.mem_write(ccb+0x2b,bytes([c]))
   u.mem_write(dst,bytes([0xa5]*20));u.mem_write(src,bytes(range(16)))
   if kind=='cat':
    start=sy['SmpScCat128'] if compiled else 0x56cfdc
    u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,src)
    if not compiled:
     def hook(uc,pc,n,user):
      d,s=uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)
      uc.mem_write(d,bytes(uc.mem_read(s,16)))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=0x542a44,end=0x542a44)
   else:
    start=(sy['smpGetPkBit'] if kind=='bit' else sy['smpGetScSecLevel']) if compiled else (0x56d150 if kind=='bit' else 0x537c00)
    u.reg_write(UC_ARM_REG_R0,ccb)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start(start|1,0x600000,count=3000)
   pair.append((u.reg_read(UC_ARM_REG_R0)&0xff,bytes(u.mem_read(dst,20)) if kind=='cat' else b''))
  assert pair[0]==pair[1],(kind,a,b,c,pair)
print('PASS_BLE_SMP_SC_SMALL_NATIVE 12')
