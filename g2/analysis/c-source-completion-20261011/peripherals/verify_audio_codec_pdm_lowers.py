#!/usr/bin/env python3
"""Original-byte/C PDM clock, handle acquisition, and DMA-enable oracles."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
sources=[R/'g2/components/audio/codec_pdm_clock_source_candidate/clock.c',R/'g2/components/audio/codec_pdm_acquire_source_candidate/acquire.c',R/'g2/components/audio/codec_pdm_dma_enable_source_candidate/dma.c']
objects=[D/f'codec-pdm-lower-{i}.o' for i in range(3)];E=D/'codec-pdm-lowers-oracle.elf';stub=D/'codec-pdm-pin-stub.c';L=D/'codec-pdm-pin-stub.o'
stub.write_text('#include <stdint.h>\n__attribute__((noinline)) uint32_t g2_codec_pin_function(uint32_t a,uint32_t b){return a+b;}\n')
for s,o in zip(sources+[stub],objects+[L]):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_pdm_clock_pin_50=0x2007421c','--defsym=g2_pdm_clock_pin_51=0x20074220','--defsym=g2_pdm_handle_rows=0x200718c8','-o',str(E),*[str(x) for x in objects],str(L)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def machine(original):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40201000,0x5000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 return u
def invoke(original,kind,a,b=0,c=0):
 u=machine(original);events=[];writes=[];done=[False]
 if kind=='clock':
  put(u,0x2007421c,b);put(u,0x20074220,c);u.reg_write(A.UC_ARM_REG_R0,a)
  child=0x480f0c if original else sym['g2_codec_pin_function']&~1
  entry=0x4c31d8 if original else sym['g2_pdm_clock_enable']
 elif kind=='acquire':
  row=0x200718c8+(a if a<4 else 0)*32;put(u,row,c);put(u,row+8,0xaaaaaaaa);put(u,0x20003000,0xdeadbeef)
  u.reg_write(A.UC_ARM_REG_R0,a);u.reg_write(A.UC_ARM_REG_R1,0x20003000 if b else 0)
  entry=0x591fac if original else sym['g2_pdm_acquire'];child=0
 else:
  h=0x20002000;base=0x40201000+b*0x1000+0x100
  put(u,h,0x01f956e2 if a else 0xdeadbeef);put(u,h+8,b);put(u,base,0x12345678)
  u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_R1,c)
  entry=0x592556 if original else sym['g2_pdm_prepare_dma'];child=0
 def hook(cpu,pc,_s,_):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
  elif pc==child:
   events.append((cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)));cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 def written(_cpu,_a,addr,size,v,_):
  if 0x200718c8<=addr<0x20071948 or 0x40201000<=addr<0x40206000:writes.append((addr,size,v&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,written)
 u.emu_start(entry|1,0,count=300);assert done[0]
 if kind=='clock':return events
 if kind=='acquire':return u.reg_read(A.UC_ARM_REG_R0),writes,bytes(u.mem_read(row,32)),get(u,0x20003000)
 return u.reg_read(A.UC_ARM_REG_R0),writes,get(u,base)
counts={k:0 for k in ('clock','acquire','dma')}
for group in (0,1,2,3,4):
 for x,y in ((0,0),(0x1234,0x5678),(0xffffffff,0xabcdef)):
  p=invoke(True,'clock',group,x,y);q=invoke(False,'clock',group,x,y);assert p==q,(group,x,y,p,q);counts['clock']+=1
for instance in (0,1,2,3,4,5):
 for cell in (0,1):
  for flags in (0,0x01000000,0x02000000,0xff000123):
   p=invoke(True,'acquire',instance,cell,flags);q=invoke(False,'acquire',instance,cell,flags);assert p==q,(instance,cell,flags,p,q);counts['acquire']+=1
for valid in (0,1):
 for instance in (0,1,2,3):
  for mask in (0,1,0x10,0xffffffff):
   p=invoke(True,'dma',valid,instance,mask);q=invoke(False,'dma',valid,instance,mask);assert p==q,(valid,instance,mask,p,q);counts['dma']+=1
print('PASS_AUDIO_CODEC_PDM_LOWERS',counts)
for p in (*objects,L,E,stub):p.unlink()
