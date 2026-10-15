#!/usr/bin/env python3
"""Compare image option dispatch, binder arguments, and flags with native Apollo."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_options.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_ambiq_nema_cf_4b05a4',0x4b05a4,1),
 ('audio_uart_ambiq_texture_bind_4b1298',0x4b1298,7),
 ('audio_uart_ambiq_texture_color_4b146c',0x4b146c,1),
 ('audio_uart_ambiq_image_alpha_513e2e',0x513e2e,1)]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp); asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {name}\n.thumb_func\n{name}:\n bx lr\n' for name,_,_ in callees))
 image=d/'image_options.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f); segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,fmt,color,mode):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
  cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
  for address,data in segments:cpu.mem_write(address,data)
  words=[fmt<<8,0x00230011,0x00450067,0,0x20030000]
  cpu.mem_write(0x20010000,b''.join(v.to_bytes(4,'little') for v in words))
  cpu.reg_write(UC_ARM_REG_R0,0x20010000);cpu.reg_write(UC_ARM_REG_R1,color)
  cpu.reg_write(UC_ARM_REG_R2,mode);cpu.reg_write(UC_ARM_REG_SP,0x200ff000)
  cpu.reg_write(UC_ARM_REG_LR,0x600001)
  calls=[]
  targets={((symbols[name] if compiled else native)&~1):(name,nargs)
           for name,native,nargs in callees}
  def hook(u,address,_size,_user):
   hit=targets.get(address)
   if hit is None:return
   name,nargs=hit;regs=[u.reg_read(r) for r in
    (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if nargs>4:
    sp=u.reg_read(UC_ARM_REG_SP)
    regs += [int.from_bytes(u.mem_read(sp+i*4,4),'little') for i in range(nargs-4)]
   calls.append((name,tuple(regs[:nargs])))
   if nargs==1 and name.endswith('cf_4b05a4'):
    u.reg_write(UC_ARM_REG_R0,(regs[0]*7+3)&0xffffffff)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  start=symbols['audio_uart_ambiq_image_options_4b0d38'] if compiled else 0x4b0d38
  cpu.emu_start(start|1,0x600000,count=400)
  return calls,cpu.reg_read(UC_ARM_REG_R0)
 count=0
 for fmt in range(0,32):
  for color in (0x11223344,0xfc123456,0xfd123456,0xff123456):
   for mode in (0,4,8,0x120):
    native=run(False,fmt,color,mode);compiled=run(True,fmt,color,mode)
    assert native==compiled,(fmt,hex(color),hex(mode),native,compiled)
    count+=1
 print('PASS_AMBIQ_IMAGE_OPTIONS_NATIVE',count)
