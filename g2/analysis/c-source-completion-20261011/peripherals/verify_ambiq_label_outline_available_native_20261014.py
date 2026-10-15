#!/usr/bin/env python3
"""Compare outline font magic and capability byte against Apollo native."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_outline_available.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stub.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n.global audio_uart_lvgl_log\n.thumb_func\naudio_uart_lvgl_log:\n bx lr\n')
 image=d/'outline.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for magic in (0x5f5f4654,0,0xffffffff,0x46545f5f):
  for flag in range(256):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    font=0x20010000;descriptor=0x20011000
    cpu.mem_write(font+0x18,descriptor.to_bytes(4,'little'))
    cpu.mem_write(descriptor,magic.to_bytes(4,'little'))
    cpu.mem_write(descriptor+0x2d,bytes([flag]))
    cpu.reg_write(UC_ARM_REG_R0,font);cpu.reg_write(UC_ARM_REG_SP,0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR,0x600001)
    logs=[];target=(syms['audio_uart_lvgl_log'] if compiled else 0x44d25c)&~1
    def hook(u,address,_size,_user):
     if address==target:logs.append(1);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.emu_start((syms['audio_uart_ambiq_outline_available_529ca4'] if compiled else 0x529ca4)|1,0x600000,count=60)
    observations.append((cpu.reg_read(UC_ARM_REG_R0),logs))
   assert observations[0]==observations[1],(hex(magic),flag,observations)
   count+=1
 print('PASS_AMBIQ_LABEL_OUTLINE_AVAILABLE_NATIVE',count)
