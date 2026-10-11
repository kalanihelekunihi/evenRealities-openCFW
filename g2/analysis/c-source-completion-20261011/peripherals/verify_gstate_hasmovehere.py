#!/usr/bin/env python3
"""Bounded stock/source oracle for the LittleFS gstate move-pair predicate."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4]
S=R/'g2/components/audio/file_sync_candidate/gstate_hasmovehere.c'
D=Path(__file__).resolve().parent
O=D/'gstate-hasmovehere-m4.o';E=D/'gstate-hasmovehere-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);segments=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,tag,pair,statepair):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x10000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segments:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 w(0x20001000,tag);w(0x20001004,statepair[0]);w(0x20001008,statepair[1]);w(0x20002000,pair[0]);w(0x20002004,pair[1])
 for reg,v in ((A.UC_ARM_REG_R0,0x20001000),(A.UC_ARM_REG_R1,0x20002000),(A.UC_ARM_REG_SP,0x2000f000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4caf5c if stock else sy['g2_lfs_gstate_hasmovehere'])|1,0,count=100)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0)
count=0
for tag in (0,0x10000000,0x20000000,0x70000000,0x80000000,0xffffffff):
 for pair in ((1,2),(2,1),(1,3),(3,4),(0xffffffff,2)):
  for statepair in ((1,2),(3,1),(3,4)):
   a=run(True,tag,pair,statepair);b=run(False,tag,pair,statepair)
   assert a==b,(hex(tag),pair,statepair,a,b)
   count+=1
print('PASS_GSTATE_HASMOVEHERE',count)
