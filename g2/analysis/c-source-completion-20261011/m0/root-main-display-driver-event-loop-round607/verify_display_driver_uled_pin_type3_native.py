#!/usr/bin/env python3
"""Compare composed type-3 pin prepare/control and register writer to native."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('display_driver_uled_pin_prepare_type3_4c3cd4',0x4c3cd4),
         ('display_driver_uled_pin_control_type3_4c3d28',0x4c3d28)]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'type3.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',*[str(here/n) for n in (
                     'display_driver_uled_pin_type3.c',
                     'display_driver_uled_pin_register_write.c',
                     'display_driver_uled_pin_bitmap.c',
                     'display_driver_uled_irq_save.c')],'-o',str(image)],
                check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address in entries:
  for pin in (0,15,31,32,56,0x100,0x138):
   for enabled in (0,1):
    for prior in (0,1):
     for gate in (0,1):
      observed=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
       u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
       u.mem_map(0x40010000,0x10000)
       for base,data in segments:u.mem_write(base,data)
       for i in range(14):set32(u,0x20073324+i*4,0)
       set32(u,0x200001dc,gate)
       set32(u,0x78ee34,0x12345678)
       set32(u,0x78ee38,0x87654321)
       slot=0x20073324+12+((pin&0xff)>>5)*4
       if enabled:set32(u,slot,1<<(pin&31))
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
       u.reg_write(UC_ARM_REG_PRIMASK,prior);u.reg_write(UC_ARM_REG_R0,pin)
       u.emu_start((syms[name] if compiled else address)|1,0x600000,count=5000)
       observed.append((u.reg_read(UC_ARM_REG_R0),
         u.reg_read(UC_ARM_REG_PRIMASK),bytes(u.mem_read(0x20073324,56)),
         bytes(u.mem_read(0x4001003c,4)),bytes(u.mem_read(0x40010400,4))))
      assert observed[0]==observed[1],(name,pin,enabled,prior,gate,observed)
      cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_TYPE3_NATIVE',cases)
