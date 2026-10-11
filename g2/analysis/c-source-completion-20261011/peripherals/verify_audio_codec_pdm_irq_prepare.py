#!/usr/bin/env python3
"""Original-byte/C PDM IRQ prepare with controlled clock acquisitions."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_pdm_irq_prepare_source_candidate/prepare.c';O=D/'codec-pdm-irq-prepare-m4.o';E=D/'codec-pdm-irq-prepare-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
names=('g2_pdm_clock_source','audio_power_clock_acquire','audio_power_clock_release','g2_pdm_clock_select','stock_delay_us')
addrs={n:0x101000+0x10*i for i,n in enumerate(names)}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={n}={a+1:#x}' for n,a in addrs.items()],'-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def run(original,valid,instance,source,control,failure):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40201000,0x5000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 h=0x20002000;base=0x40201000+instance*0x1000
 put(u,h,0x01f956e2 if valid else 0xdeadbeef);put(u,h+8,instance);u.mem_write(h+28,int(source).to_bytes(2,'little',signed=True));put(u,base,control)
 u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 originals={'source':0x591d14,'acquire':0x4c44bc,'release':0x4c4530,'select':0x591d7a,'delay':0x4807a0}
 hooks={a:k for k,a in (originals if original else {k:addrs[n] for k,n in zip(originals,names)}).items()}
 calls=[];writes=[];done=[False];acq=[0]
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop();return
  k=hooks.get(pc)
  if k is None:return
  r0=c.reg_read(A.UC_ARM_REG_R0);r1=c.reg_read(A.UC_ARM_REG_R1)
  calls.append((k,r0,r1) if k in ('acquire','release','select') else (k,r0))
  if k=='source':result=5
  elif k=='acquire':acq[0]+=1;result=9 if acq[0]==failure else 0
  else:result=0
  c.reg_write(A.UC_ARM_REG_R0,result);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
 def written(_c,_a,a,size,v,_):
  if 0x40201000<=a<0x40206000:writes.append((a,size,v&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,written)
 u.emu_start((0x592230 if original else sym['g2_pdm_irq_prepare'])|1,0,count=400)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),calls,writes,u.mem_read(base,4)
n=0
for valid in (False,True):
 for instance in (0,1,2,3):
  for source in (-1,0x100,0x217):
   for control in (0,0xffffffff,0x12345678):
    for failure in (0,1,2):
     a=run(True,valid,instance,source,control,failure);b=run(False,valid,instance,source,control,failure)
     assert a==b,(valid,instance,source,control,failure,a,b)
     n+=1
print('PASS_AUDIO_CODEC_PDM_IRQ_PREPARE',n)
for p in (O,E):p.unlink()
