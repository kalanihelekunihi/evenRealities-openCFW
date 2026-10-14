#!/usr/bin/env python3
"""Compare the full Apollo GPU blit descriptor body with decoded firmware."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
                               UC_ARM_REG_SP)
source=Path(__file__).with_name('display_driver_gpu_blit.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);stub=d/'stub.s'
 stub.write_text('.syntax unified\n.thumb\n.text\n.global audio_uart_nema_cl_get_space_514aec\n'
                 '.thumb_func\naudio_uart_nema_cl_get_space_514aec:\n bx lr\n'
                 '.bss\n.global audio_uart_nema_context_cell\n'
                 'audio_uart_nema_context_cell:\n.space 4\n')
 image=d/'gpu-blit.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],
                check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 formats=sorted(set(range(0,0x50))|{0x80,0x92,0xffffffff})
 cases=[]
 for fmt in formats:
  for width,flags,stride in ((1,0,0xffffffff),(3,0x10,0xffffffff),
                             (7,0,0xffffffff),(320,0x10,0xffffffff),
                             (5,0x10,0x12345)):
   cases.append((fmt,width,flags,stride,True))
 for fmt in (0,0xb,0x12,0x29,0x4e,0xffffffff):
  cases.append((fmt,9,0x10,0xffffffff,False))
 for fmt in (0xb,0xc,0x12,0x16,0x29,0x2c,0x39,0x4c,0x4e,0x7f):
  for width in (0,0x7fffffff,0x80000000,0xfffffffd,0xffffffff):
   cases.append((fmt,width,0x10,0xffffffff,True))
 for fmt,width,flags,stride,allocated in cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   context=0x20090000;command=0x20091000;stack=0x200ff000
   cell=syms['audio_uart_nema_context_cell'] if compiled else 0x20074efc
   cpu.mem_write(cell,context.to_bytes(4,'little'))
   cpu.mem_write(context,bytes([0xcc])*0x70)
   cpu.mem_write(command,bytes([0xdd])*24)
   cpu.mem_write(stack,stride.to_bytes(4,'little')+flags.to_bytes(4,'little'))
   cpu.reg_write(UC_ARM_REG_SP,stack);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   cpu.reg_write(UC_ARM_REG_R0,0x20008000)
   cpu.reg_write(UC_ARM_REG_R1,width);cpu.reg_write(UC_ARM_REG_R2,13)
   cpu.reg_write(UC_ARM_REG_R3,fmt)
   alloc=(syms['audio_uart_nema_cl_get_space_514aec'] if compiled else 0x514aec)&~1
   calls=[]
   def hook(u,address,_size,_user):
    if address!=alloc:return
    calls.append(u.reg_read(UC_ARM_REG_R0))
    u.reg_write(UC_ARM_REG_R0,command if allocated else 0)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   start=syms['display_driver_gpu_blit_4b1608'] if compiled else 0x4b1608
   cpu.emu_start(start|1,0x600000,count=250)
   observations.append((calls,bytes(cpu.mem_read(context+0x50,0x18)),
                        bytes(cpu.mem_read(command,24))))
  assert observations[0]==observations[1],(hex(fmt),width,hex(flags),hex(stride),allocated,
                                            observations)
 print('PASS_DISPLAY_DRIVER_GPU_BLIT_NATIVE',len(cases))
