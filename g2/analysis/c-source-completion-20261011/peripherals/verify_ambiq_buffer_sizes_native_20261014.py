#!/usr/bin/env python3
"""Compare Ambiq buffer byte-rounding and format sizing with Apollo S200."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/size.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('unsigned audio_uart_lv_color_bpp_440f44(unsigned x){return 0;}\n')
 image=Path(directory)/'size.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,which,pixels,fmt,bits):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  calls=[]
  def bpp(uc,at,size,user):
   calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,bits);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  at=syms['audio_uart_lv_color_bpp_440f44']&~1 if compiled else 0x440f44
  u.hook_add(UC_HOOK_CODE,bpp,begin=at,end=at)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.reg_write(UC_ARM_REG_R0,pixels);u.reg_write(UC_ARM_REG_R1,fmt)
  entry=(syms['audio_uart_ambiq_buffer_round_bytes_53cfe4'] if which==0 else syms['audio_uart_ambiq_buffer_format_bytes_53cff0']) if compiled else (0x53cfe4 if which==0 else 0x53cff0)
  u.emu_start(entry|1,0x600000,count=100)
  return calls,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for pixels in (0,1,2,7,8,9,63,65535,0xfffffffe,0xffffffff):
  for fmt in (0,1,2,255,256,513):
   for bits in (1,2,4,8,16,24,32):
    for which in (0,1):
     native=run(False,which,pixels,fmt,bits);compiled=run(True,which,pixels,fmt,bits)
     assert native==compiled,(which,pixels,fmt,bits,native,compiled)
     cases+=1
 print('PASS_AMBIQ_BUFFER_SIZES_NATIVE',cases)
