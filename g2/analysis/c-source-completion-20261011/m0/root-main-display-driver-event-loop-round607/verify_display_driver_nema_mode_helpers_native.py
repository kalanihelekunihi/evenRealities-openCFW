#!/usr/bin/env python3
"""Compare three NEMA mode lower calls with the authenticated image."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_SP)
source=Path(__file__).with_name('display_driver_nema_mode_helpers.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);stub=d/'stub.s'
 stub.write_text('.syntax unified\n.thumb\n.text\n.global audio_uart_nema_child_514846\n'
                 '.thumb_func\naudio_uart_nema_child_514846:\n bx lr\n'
                 '.bss\n.global audio_uart_nema_context_cell\n'
                 'audio_uart_nema_context_cell:\n.space 4\n')
 image=d/'helpers.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],
                check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 for name,address in (('display_driver_nema_mode_control_5226d6',0x5226d6),
                      ('display_driver_nema_mode_commit_52294c',0x52294c)):
  for value in (0,1,2,0x80000000,0xffffffff):cases.append((name,address,value,None))
 for value in (0,1,2,0xffffffff):
  for words in ((0,0,0),(0x12345678,0xf0000000,0x00040000)):
   cases.append(('display_driver_gpu_mode_mask_4b1588',0x4b1588,value,words))
 for name,address,value,words in cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for base,data in segments:cpu.mem_write(base,data)
   cell=syms['audio_uart_nema_context_cell'] if compiled else 0x20074efc
   context=0x20090000;cpu.mem_write(cell,context.to_bytes(4,'little'))
   cpu.mem_write(context,bytes([0xcc])*0x30)
   if words is not None:
    for offset,word in zip((0xc,0x10,0x1c),words):
     cpu.mem_write(context+offset,word.to_bytes(4,'little'))
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   cpu.reg_write(UC_ARM_REG_R0,value)
   child=(syms['audio_uart_nema_child_514846'] if compiled else 0x514846)&~1
   calls=[]
   def hook(u,pc,_size,_user):
    if pc!=child:return
    calls.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   cpu.emu_start((syms[name] if compiled else address)|1,0x600000,count=80)
   observations.append((calls,bytes(cpu.mem_read(context,0x30)) if words is not None else b''))
  assert observations[0]==observations[1],(name,hex(value),words,observations)
 print('PASS_DISPLAY_DRIVER_NEMA_MODE_HELPERS_NATIVE',len(cases))
