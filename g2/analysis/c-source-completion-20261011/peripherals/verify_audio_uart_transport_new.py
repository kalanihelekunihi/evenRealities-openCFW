#!/usr/bin/env python3
"""Native/C UART ring constructor comparison on valid inputs."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/transport_new.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'transport.o';p=Path(td)/'transport.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--defsym=audio_uart_transport_initialize=0x101011','--defsym=offline_assert=0x101021','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_transport_new')
 def run(native,case):
  capacity,element,selectable,flag=case
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  sp=0x200f0000;args=(capacity,element,selectable,0x20050000)
  for reg,val in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3),args):u.reg_write(reg,val)
  for i,val in enumerate((0x20060000,0x1234,0x5678)):u.mem_write(sp+i*4,val.to_bytes(4,'little'))
  u.mem_write(0x2006001c,bytes([flag]));u.reg_write(A.UC_ARM_REG_SP,sp);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   if pc==(0x57e3a4 if native else 0x101010):
    s=cpu.reg_read(A.UC_ARM_REG_SP)
    calls.append(tuple(cpu.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))+tuple(int.from_bytes(cpu.mem_read(s+i*4,4),'little') for i in range(3)))
    cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x57df7c if native else entry)|1,0,count=1000);assert done[0],case
  return u.reg_read(A.UC_ARM_REG_R0),calls,u.mem_read(0x2006001c,1)[0]
 count=0
 for case in itertools.product((5,6,128,24576),(0,1,2,4),(0,1),(0,1,0xfd)):
  if case[0]<case[1]:continue
  a=run(True,case);b=run(False,case);assert a==b,(case,a,b);count+=1
 print('PASS_AUDIO_UART_TRANSPORT_NEW',count)
