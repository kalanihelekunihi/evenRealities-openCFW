#!/usr/bin/env python3
"""Compare native and C IRQ_Context return and scheduler call boundary."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_IPSR,UC_ARM_REG_PRIMASK,UC_ARM_REG_BASEPRI
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('unsigned display_driver_uled_scheduler_state_4558a4(void){return 0;}\n')
 image=Path(directory)/'irq.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_irq_context.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for ipsr in (0,1,15):
  for state in (0,1,2):
   for primask in (0,1):
    for basepri in (0,0x80):
     observations=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      for base,data in segments:u.mem_write(base,data)
      calls=[]
      def scheduler(uc,at,size,user):
       calls.append('scheduler');uc.reg_write(UC_ARM_REG_R0,state);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      target=syms['display_driver_uled_scheduler_state_4558a4']&~1 if compiled else 0x4558a4
      u.hook_add(UC_HOOK_CODE,scheduler,begin=target,end=target)
      u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.emu_start((syms['display_driver_uled_irq_context_44900e'] if compiled else 0x44900e)|1,0x600000,count=100)
      observations.append((calls,u.reg_read(UC_ARM_REG_R0)))
     assert observations[0]==observations[1],(ipsr,state,primask,basepri,observations)
     cases+=1
 print('PASS_ULED_IRQ_CONTEXT_NATIVE',cases)
