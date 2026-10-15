#!/usr/bin/env python3
"""Compare bounded immediate paths of Apollo power helpers with native code."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'stub.c';stub.write_text('unsigned display_driver_uled_delay_4807a0(unsigned x){(void)x;return 0;}\n')
 image=Path(directory)/'power.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_power_enable_clear.c'),
  str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for function,native in (('display_driver_uled_poll_480826',0x480826),
                         ('display_driver_uled_power_enable_4d3952',0x4d3952),
                         ('display_driver_uled_power_clear_4d39e4',0x4d39e4)):
  for enable in (0,1):
   for ready in (0,1):
    for initial in (0,0xffffffff):
     if function=='display_driver_uled_power_enable_4d3952' and enable and not ready and not (initial&0x20):
      continue
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      u.mem_map(0x40000000,0x10000)
      for base,data in segments:u.mem_write(base,data)
      set32(u,0x40004044,initial)
      set32(u,0x40004048,initial)
      set32(u,0x40004030,0x01000000 if ready else 0)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      if function=='display_driver_uled_poll_480826':
       # Count zero avoids delay; both equal and unequal branches are exercised.
       u.reg_write(UC_ARM_REG_R0,0)
       u.reg_write(UC_ARM_REG_R1,0x40004030)
       u.reg_write(UC_ARM_REG_R2,0x01000000)
       u.reg_write(UC_ARM_REG_R3,0x01000000)
       set32(u,0x200ff000,enable)
      else:u.reg_write(UC_ARM_REG_R0,enable)
      u.emu_start((syms[function] if compiled else native)|1,0x600000,count=2000)
      observed.append((u.reg_read(UC_ARM_REG_R0),
        bytes(u.mem_read(0x40004030,4)),bytes(u.mem_read(0x40004044,4)),
        bytes(u.mem_read(0x40004048,4))))
     assert observed[0]==observed[1],(function,enable,ready,initial,observed)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_POWER_HELPERS_NATIVE',cases)
