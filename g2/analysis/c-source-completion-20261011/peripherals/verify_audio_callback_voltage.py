#!/usr/bin/env python3
"""Original-byte/C private audio voltage selector MMIO comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/callback_voltage_source_candidate/voltage.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'voltage.o';e=t/'voltage.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_audio_voltage_routes=0x2005665c','-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def run(native,source,selection,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40020000,0x1000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  for offset in (0x54,0x58,0x5c,0x60):put(u,0x2005665c+offset,(seed*0x19375bd+offset*0x70851)&0xffffffff)
  for address in (0x40020344,0x40020354,0x40020358):put(u,address,(seed*0x13579bdf+address)&0xffffffff)
  u.reg_write(A.UC_ARM_REG_R0,source);u.reg_write(A.UC_ARM_REG_R1,selection);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  writes=[];done=[False]
  def code(c,pc,_s,_d):
   if pc==0x101180:done[0]=True;c.emu_stop()
  def write(_c,_a,a,width,value,_d):
   if 0x40020000<=a<0x40021000:writes.append((a,width,value&((1<<(8*width))-1)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x5a423c if native else sym['callback_voltage'])|1,0,count=300)
  assert done[0]
  return writes,bytes(u.mem_read(0x40020340,0x20))
 n=0
 for source in (0,1,2,3,4,5,6,7,8,255):
  for selection in (0,8,255):
   for seed in (0,1,0x55,0xabcdef):
    a=run(True,source,selection,seed);b=run(False,source,selection,seed)
    assert a==b,(source,selection,seed,a,b)
    n+=1
 print('PASS_AUDIO_CALLBACK_VOLTAGE',n)
