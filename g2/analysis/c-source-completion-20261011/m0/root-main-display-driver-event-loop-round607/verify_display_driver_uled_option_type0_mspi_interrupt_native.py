#!/usr/bin/env python3
"""Compare MSPI interrupt register operations and return codes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_MEM_READ
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'interrupt.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_mspi_interrupt.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for function,native in (('display_driver_uled_interrupt_enable_4c2328',0x4c2328),('display_driver_uled_interrupt_clear_4c23de',0x4c23de)):
  for variant in ('null','invalid','valid'):
   for module in range(4):
    for mask in (0,1,0x1a80,0xffffffff):
     observations=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40060000,0x10000)
      for base,data in segments:u.mem_write(base,data)
      u.mem_write(0x20001000,(0 if variant=='invalid' else 0x01bebebe).to_bytes(4,'little'))
      u.mem_write(0x20001004,module.to_bytes(4,'little'))
      base=0x40060000+module*0x1000
      u.mem_write(base+0x200,(0x11223344).to_bytes(4,'little'))
      u.mem_write(base+0x204,(0x55667788).to_bytes(4,'little'))
      operations=[]
      def memory(uc,access,address,size,value,user):
       if 0x40060000<=address<0x40070000:
        operations.append(('read' if access==UC_MEM_READ else 'write',address,size,value if access!=UC_MEM_READ else None))
      u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_R0,0 if variant=='null' else 0x20001000);u.reg_write(UC_ARM_REG_R1,mask)
      u.emu_start((syms[function] if compiled else native)|1,0x600000,count=300)
      observations.append((u.reg_read(UC_ARM_REG_R0),operations,bytes(u.mem_read(base+0x200,12))))
     assert observations[0]==observations[1],(function,variant,module,mask,observations)
     cases+=1
 print('PASS_ULED_OPTION_TYPE0_MSPI_INTERRUPT_NATIVE',cases)
