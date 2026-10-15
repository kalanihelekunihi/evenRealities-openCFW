#!/usr/bin/env python3
"""Compare Ambiq label dispatch threshold and renderer callback argument."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/draw_label.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stub.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n.global audio_uart_lv_draw_label_48a0be\n.thumb_func\naudio_uart_lv_draw_label_48a0be:\n bx lr\n.global audio_uart_ambiq_label_pixel_53fcc4\n.thumb_func\naudio_uart_ambiq_label_pixel_53fcc4:\n bx lr\n')
 image=d/'label.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for threshold in range(256):
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   desc=0x20011000;cpu.mem_write(desc+0x50,bytes([threshold]))
   cpu.reg_write(UC_ARM_REG_R0,0x20010000);cpu.reg_write(UC_ARM_REG_R1,desc)
   cpu.reg_write(UC_ARM_REG_R2,0x20012000);cpu.reg_write(UC_ARM_REG_SP,0x200ff000)
   cpu.reg_write(UC_ARM_REG_LR,0x600001)
   target=(syms['audio_uart_lv_draw_label_48a0be'] if compiled else 0x48a0be)&~1
   callback=(syms['audio_uart_ambiq_label_pixel_53fcc4'] if compiled else 0x53fcc5)
   calls=[]
   def hook(u,address,_size,_user):
    if address!=target:return
    calls.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),
     u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3)==callback))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   cpu.emu_start((syms['audio_uart_ambiq_draw_label_53faa6'] if compiled else 0x53faa6)|1,0x600000,count=50)
   observations.append(calls)
  assert observations[0]==observations[1],(threshold,observations)
  assert len(observations[0])==(1 if threshold>=3 else 0),threshold
 print('PASS_AMBIQ_DRAW_LABEL_DISPATCH_NATIVE',256)
