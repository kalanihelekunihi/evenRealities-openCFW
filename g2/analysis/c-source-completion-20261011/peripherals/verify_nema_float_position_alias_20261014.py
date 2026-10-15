#!/usr/bin/env python3
"""Check the alternate 0x5228b0 symbol forwards both VFP arguments unchanged."""
from pathlib import Path
import struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_position_alias.c'
F=lambda x:int.from_bytes(struct.pack('<f',x),'little')
with tempfile.TemporaryDirectory() as d:
 d=Path(d)
 asm=d/'stub.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n.global display_driver_nema_float_translate_5228b0\n.thumb_func\ndisplay_driver_nema_float_translate_5228b0:\n bx lr\n')
 image=d/'alias.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f); segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']; syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 pairs=[(F(x),F(y)) for x in (-4096.,-2049.,-1.,-0.,0.,1.,2048.,2049.,4096.) for y in (-4096.,-1.,0.,1.,4096.)]
 pairs += [(0x7f800000,0xff800000),(0x7fc00000,F(3.5)),(F(-1.25),0x7fc00000)]
 for x,y in pairs:
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  cpu.mem_map(0x100000,0x200000); cpu.mem_map(0x20000000,0x100000)
  for address,data in segments:cpu.mem_write(address,data)
  cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x200001)
  cpu.reg_write(UC_ARM_REG_S0,x);cpu.reg_write(UC_ARM_REG_S1,y)
  calls=[]; target=syms['display_driver_nema_float_translate_5228b0']&~1
  def hook(u,address,_size,_user):
   if address==target:
    calls.append((u.reg_read(UC_ARM_REG_S0),u.reg_read(UC_ARM_REG_S1)))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  cpu.emu_start(syms['audio_uart_nema_float_position_5228b0']|1,0x200000,count=40)
  assert calls==[(x,y)],(hex(x),hex(y),calls)
print('PASS_NEMA_FLOAT_POSITION_ALIAS',len(pairs))
