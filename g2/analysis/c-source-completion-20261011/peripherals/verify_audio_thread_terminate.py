#!/usr/bin/env python3
"""Native/C CMSIS thread termination wrapper with controlled kernel cuts."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/thread_terminate_source_candidate/terminate.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'terminate.o';p=Path(td)/'terminate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'audio_irq_context':0x101011,'audio_task_state':0x101021,'audio_task_delete':0x101031}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_thread_terminate_peer')
 def run(native,irq,handle,state):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.reg_write(A.UC_ARM_REG_R0,handle);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  old={0x44900e:'irq',0x454b88:'state',0x454aae:'delete'};new={0x101010:'irq',0x101020:'state',0x101030:'delete'}
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind is None:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);calls.append((kind,r0))
   cpu.reg_write(A.UC_ARM_REG_R0,{'irq':irq,'state':state,'delete':0}[kind]);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x4491fe if native else entry)|1,0,count=1000);assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls
 count=0
 for irq,handle,state in itertools.product((0,1,2),(0,0x20040000),(0,1,3,4,5,0x104)):
  a=run(True,irq,handle,state);b=run(False,irq,handle,state)
  assert a==b,(irq,handle,state,a,b)
  count+=1
 print('PASS_AUDIO_THREAD_TERMINATE',count)
