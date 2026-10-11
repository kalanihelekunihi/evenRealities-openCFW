#!/usr/bin/env python3
"""Original-byte/C clock mux current-source oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_clock_mux_prepare_source_candidate/prepare.c';O=D/'codec-mux-prepare-m4.o';E=D/'codec-mux-prepare-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def run(original,group,control,initial):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40020000,0x1000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_write(0x400204e8,control.to_bytes(4,'little'));u.mem_write(0x20003000,bytes([initial]))
 u.reg_write(A.UC_ARM_REG_R0,group);u.reg_write(A.UC_ARM_REG_R1,0x20003000);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 writes=[];done=[False]
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop()
 def write(_c,_a,a,size,v,_):
  if a==0x20003000:writes.append((a,size,v))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x539c9a if original else sym['g2_clock_mux_prepare'])|1,0,count=200)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),writes,u.mem_read(0x20003000,1)
n=0
for group in range(8):
 for control in (0,0xffffffff,0x55,0xaa,0x12345678):
  for initial in (2,0xff):
   a=run(True,group,control,initial);b=run(False,group,control,initial);assert a==b,(group,control,initial,a,b);n+=1
print('PASS_AUDIO_CODEC_CLOCK_MUX_PREPARE',n)
for p in (O,E):p.unlink()
