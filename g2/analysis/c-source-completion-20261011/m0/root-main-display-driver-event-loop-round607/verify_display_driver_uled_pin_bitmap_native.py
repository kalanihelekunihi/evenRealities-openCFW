#!/usr/bin/env python3
"""Native/C bitmap oracle for five Apollo pin providers."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('display_driver_uled_popcount_4c3750',0x4c3750),
         ('display_driver_uled_pin_group_query_4c377a',0x4c377a),
         ('display_driver_uled_pin_query_4c37a8',0x4c37a8),
         ('display_driver_uled_pin_group_check_4c37ca',0x4c37ca),
         ('display_driver_uled_pin_apply_4c37fe',0x4c37fe)]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'pin-bitmap.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_pin_bitmap.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address in entries:
  if address==0x4c3750:
   args=[(v,0,0) for v in (0,1,2,3,0x55555555,0xaaaaaaaa,
         0x80000000,0x7fffffff,0xffffffff,0x12345678,0xf0f0f0f0)]
  else:
   args=[(kind,pin,enabled) for kind in (0,4,6,7)
         for pin in (0,31,32,56,57,0x100,0x138)
         for enabled in (0,1,0x100)]
  for a,b,c in args:
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    for i in range(16):set32(u,0x20073324+i*4,(0xa5a50101*i+0x12345678)&0xffffffff)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,b);u.reg_write(UC_ARM_REG_R2,c)
    u.emu_start((syms[name] if compiled else address)|1,0x600000,count=2000)
    observed.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20073324,64))))
   assert observed[0]==observed[1],(name,a,b,c,observed)
   cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_BITMAP_NATIVE',cases)
