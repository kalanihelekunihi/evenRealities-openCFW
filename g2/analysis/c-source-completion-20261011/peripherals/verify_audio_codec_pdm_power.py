#!/usr/bin/env python3
"""Stock/C PDM power control across mode, backup and IRQ transitions."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_pdm_power_source_candidate/power.c';O=D/'codec-pdm-power-m4.o';E=D/'codec-pdm-power-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
names=('audio_power_peripheral_on','audio_power_peripheral_off','g2_gpio_critical_save')
addrs={n:0x101000+i*0x10 for i,n in enumerate(names)}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={n}={a+1:#x}' for n,a in addrs.items()],'-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def run(original,valid,mode,backup,instance,state,irq):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 h=0x20002000;put(u,h,0x01f956e2 if valid else 0xdeadbeef);put(u,h+8,instance);u.mem_write(h+4,bytes([state]))
 u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_R1,mode);u.reg_write(A.UC_ARM_REG_R2,backup);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181);u.reg_write(A.UC_ARM_REG_PRIMASK,irq)
 calls={0x47f5b8:'on',0x47f7ae:'off',0x473940:'critical'} if original else {addrs[n]:k for n,k in zip(names,('on','off','critical'))}
 events=[];writes=[];done=[False]
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop();return
  k=calls.get(pc)
  if k is None:return
  if k=='critical':
   prev=c.reg_read(A.UC_ARM_REG_PRIMASK);events.append((k,prev));c.reg_write(A.UC_ARM_REG_PRIMASK,1);c.reg_write(A.UC_ARM_REG_R0,prev)
  else:
   events.append((k,c.reg_read(A.UC_ARM_REG_R0)));c.reg_write(A.UC_ARM_REG_R0,0)
  c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
 def write(_c,_a,a,size,v,_):
  if h<=a<h+32:writes.append((a,size,v&((1<<(size*8))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x592046 if original else sym['g2_pdm_disable'])|1,0,count=250)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),events,writes,u.mem_read(h+4,1),u.reg_read(A.UC_ARM_REG_PRIMASK)
n=0
for valid in (False,True):
 for mode in (0,1,2,3,0x100):
  for backup in (0,1,0x100):
   for instance in (0,1,3):
    for state in (0,1):
     for irq in (0,1):
      a=run(True,valid,mode,backup,instance,state,irq);b=run(False,valid,mode,backup,instance,state,irq)
      assert a==b,(valid,mode,backup,instance,state,irq,a,b)
      n+=1
print('PASS_AUDIO_CODEC_PDM_POWER',n)
for p in (O,E):p.unlink()
