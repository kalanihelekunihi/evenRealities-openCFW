#!/usr/bin/env python3
"""Compare Nema alpha command call with Apollo native 0x522960."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_alpha_command.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stub.s';asm.write_text('.syntax unified\n.thumb\n.text\n.global audio_uart_nema_child_514846\n.thumb_func\naudio_uart_nema_child_514846:\n bx lr\n')
 image=d/'nema_alpha_command.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for color in [0,1,0x12345678,0xff000000,0xffffffff]+[(i*0x9e3779b9)&0xffffffff for i in range(64)]:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   cpu.reg_write(UC_ARM_REG_R0,color);cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   target=(symbols['audio_uart_nema_child_514846'] if compiled else 0x514846)&~1
   calls=[]
   def hook(u,address,_size,_user):
    if address==target:
     calls.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   cpu.emu_start((symbols['audio_uart_nema_alpha_command_522960'] if compiled else 0x522960)|1,0x600000,count=40)
   observations.append(calls)
  assert observations==[[(0x1d8,color)],[(0x1d8,color)]],(hex(color),observations)
 print('PASS_NEMA_ALPHA_COMMAND_NATIVE',69)
