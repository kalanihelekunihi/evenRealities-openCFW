#!/usr/bin/env python3
"""Compare Apollo NEMA VFP translation packets and threshold behavior."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_nema_float_translate.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
F=lambda x:int.from_bytes(struct.pack('<f',x),'little')
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in
  ('audio_uart_nema_cl_get_space_514aec','audio_uart_nema_child_514846')))
 image=d/'float.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4',
  '-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-mthumb','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 pairs=[(F(0),F(0)),(F(1.25),F(-3.5)),(F(2048),F(2048)),
        (F(2049),F(0)),(F(0),F(2049)),(F(-2049),F(-4096)),
        (0x80000000,F(0)),(0x7f800000,0xff800000),
        (0x7fc00000,F(2049)),(F(2049),0x7fc00000)]
 count=0
 for x,y in pairs:
  for allocation in (False,True):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cpu.mem_write(0x20090000,bytes([0xcc])*16)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.reg_write(UC_ARM_REG_S0,x);cpu.reg_write(UC_ARM_REG_S1,y)
    alloc=(syms['audio_uart_nema_cl_get_space_514aec'] if compiled else 0x514aec)&~1
    child=(syms['audio_uart_nema_child_514846'] if compiled else 0x514846)&~1
    events=[]
    def hook(u,address,_size,_user):
     if address==alloc:
      events.append(('alloc',u.reg_read(UC_ARM_REG_R0)))
      u.reg_write(UC_ARM_REG_R0,0x20090000 if allocation else 0)
     elif address==child:
      events.append(('child',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
     else:return
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    start=syms['display_driver_nema_float_translate_5228b0'] if compiled else 0x5228b0
    cpu.emu_start(start|1,0x600000,count=150)
    observations.append((events,bytes(cpu.mem_read(0x20090000,16)).hex()))
   assert observations[0]==observations[1],(hex(x),hex(y),allocation,observations)
   count+=1
print('PASS_DISPLAY_DRIVER_NEMA_FLOAT_TRANSLATE_NATIVE',count)
