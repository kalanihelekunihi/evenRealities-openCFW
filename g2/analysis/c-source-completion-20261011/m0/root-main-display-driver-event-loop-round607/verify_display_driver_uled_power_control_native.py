#!/usr/bin/env python3
"""Native/C MMIO oracle for Apollo uLED power controls 0x4d391e/0x4d3938."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('display_driver_uled_power_set_4d391e',0x4d391e),
         ('display_driver_uled_power_apply_4d3938',0x4d3938)]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'power.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_power_control.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address in entries:
  for argument in (0,1,0x100,0x101,0xffffffff):
   for initial in (0,0x12345678,0xaaaaaaaa,0xffffffff):
    observed=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     u.mem_map(0x40000000,0x10000)
     for base,data in segments:u.mem_write(base,data)
     set32(u,0x40004020,initial);set32(u,0x40004044,initial)
     accesses=[]
     def on_mmio(_u,kind,where,size,value,_user):
      if where in (0x40004020,0x40004044):
       accesses.append((kind,where,size,value if kind==UC_HOOK_MEM_WRITE else None))
     u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,on_mmio)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,argument)
     u.emu_start((syms[name] if compiled else address)|1,0x600000,count=1000)
     observed.append((u.reg_read(UC_ARM_REG_R0),
       bytes(u.mem_read(0x40004020,4)),bytes(u.mem_read(0x40004044,4)),accesses))
    assert observed[0]==observed[1],(name,argument,initial,observed)
    cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_POWER_CONTROL_NATIVE',cases)
