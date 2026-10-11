#!/usr/bin/env python3
"""Native-byte/C comparison for PDM configuration, including MMIO order."""
from pathlib import Path
import subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4]
S=R/'g2/components/audio/codec_pdm_configure_source_candidate/configure.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'configure.o';q=t/'shim.o';e=t/'configure.elf';shim=t/'shim.c'
 shim.write_text('#include <stdint.h>\nvoid stock_delay_us(uint32_t us) {(void)us;}\n')
 f=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror']
 subprocess.run(f+['-c',str(S),'-o',str(o)],check=True)
 subprocess.run(f+['-c',str(shim),'-o',str(q)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(e),str(o),str(q)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as ef:
  elf=ELFFile(ef);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def run(native,valid,seed,instance):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40201000,0x5000)
  if native:u.mem_write(0x438000,STOCK)
  else:
   for a,b in segs:u.mem_write(a,b)
  h,c=0x20002000,0x20003000;reg=0x40201000+(instance<<12)
  put(u,h,0x01f956e2 if valid else 0);put(u,h+8,instance);put(u,reg,0x11223344);put(u,reg+4,0x87654321);put(u,reg+8,0xf0f0f0f0)
  u.mem_write(c,bytes(((seed+17*i+i*i)&255) for i in range(32)))
  u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_R1,c);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  writes=[];delays=[];done=[False];delay=0x4807a0 if native else sym['stock_delay_us']&~1
  def code(v,pc,_s,_d):
   if pc==0x101180:done[0]=True;v.emu_stop()
   elif pc==delay:delays.append(v.reg_read(A.UC_ARM_REG_R0));v.reg_write(A.UC_ARM_REG_PC,v.reg_read(A.UC_ARM_REG_LR))
  def write(_u,_a,a,size,value,_d):
   if 0x40201000<=a<0x40206000:writes.append((a,size,value&((1<<(8*size))-1)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x5920cc if native else sym['g2_pdm_configure'])|1,0,count=1000)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(h,32)),writes,delays
 n=0
 for valid in (False,True):
  for seed in (0,1,17,0x55,0xa7,0xff):
   for instance in (0,1):
    a,b=run(True,valid,seed,instance),run(False,valid,seed,instance)
    assert a==b,(valid,seed,instance,a,b)
    n+=1
 print('PASS_AUDIO_CODEC_PDM_CONFIGURE',n)
