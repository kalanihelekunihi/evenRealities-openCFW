#!/usr/bin/env python3
"""Original-byte/C I2S source reconfiguration oracle with mux child cut."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_i2s_reconfigure_source_candidate/reconfigure.c';O=D/'codec-i2s-reconfigure-m4.o';L=D/'codec-i2s-mux-stub-m4.o';E=D/'codec-i2s-reconfigure-oracle.elf';stub=D/'codec-i2s-mux-stub.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline)) void g2_codec_source_mux(uint32_t a,uint32_t b){(void)a;(void)b;}\n')
for s,o in ((S,O),(stub,L)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O),str(L)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def run(original,instance,source,control,clock):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40020000,0x1000);u.mem_map(0x40208000,0x3000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 base=0x40208000+instance*0x1000;put(u,base+0x100,control);put(u,base+0x54,0xa5a5a5a5);put(u,0x400204e8,clock)
 u.reg_write(A.UC_ARM_REG_R0,instance);u.reg_write(A.UC_ARM_REG_R1,source);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 child=0x58fd7e if original else sym['g2_codec_source_mux']&~1;calls=[];writes=[];done=[False]
 def hook(cpu,pc,_s,_):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
  elif pc==child:
   calls.append((cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)));cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 def written(_cpu,_a,a,size,v,_):
  if 0x40208000<=a<0x4020b000:writes.append((a,size,v&((1<<(size*8))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,written)
 u.emu_start((0x58fdbc if original else sym['audio_power_reconfigure'])|1,0,count=1000)
 assert done[0]
 return calls,writes,bytes(u.mem_read(base+0x54,4)),bytes(u.mem_read(base+0x100,4))
n=0
for instance in (0,1):
 for source in (0x217,0x210,0x202,0x201,0x10000,0x10003,0x10202):
  for control in (0,1,0x170,0x1000,0x12345):
   for clock in (0,0x20,0x40,0x80,0x100):
    a=run(True,instance,source,control,clock);b=run(False,instance,source,control,clock)
    assert a==b,(instance,source,control,clock,a,b)
    n+=1
print('PASS_AUDIO_CODEC_I2S_RECONFIGURE',n)
for p in (O,L,E,stub):p.unlink()
