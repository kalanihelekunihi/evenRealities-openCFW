#!/usr/bin/env python3
"""Compare native label fill and vector-glyph dispatch lower calls."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
folder=root/'components/main/ambiq_buffer_handlers_candidate_20261014'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_nema_select_522a16',0x522a16),('display_driver_nema_clear_522ae0',0x522ae0),
 ('audio_uart_ambiq_outline_available_529ca4',0x529ca4),('audio_uart_ambiq_label_vector_draw_53d708',0x53d708)]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n,_ in callees))
 image=d/'label_helpers.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(folder/'label_fill_rectangle.c'),str(folder/'label_vector_dispatch.c'),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,kind,seed,available):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
  cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
  for address,data in segments:cpu.mem_write(address,data)
  sp=0x200ff000;cpu.reg_write(UC_ARM_REG_SP,sp);cpu.reg_write(UC_ARM_REG_LR,0x600001)
  if kind=='fill':
   values=[(seed*0x9e3779b9+i*0x1234567)&0xffffffff for i in range(5)]
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),values):cpu.reg_write(reg,v)
   cpu.mem_write(sp,values[4].to_bytes(4,'little'))
   start=syms['audio_uart_ambiq_label_fill_rectangle_4b1ab0'] if compiled else 0x4b1ab0
  else:
   entry=(seed*0x9e3779b9)&0xffffffff;unit=0x20014000;glyph=0x20015000
   cpu.mem_write(glyph+0x10,(0x20016000).to_bytes(4,'little'))
   cpu.mem_write(0x20016000,entry.to_bytes(4,'little'))
   cpu.reg_write(UC_ARM_REG_R0,unit);cpu.reg_write(UC_ARM_REG_R1,glyph)
   start=syms['audio_uart_ambiq_label_vector_dispatch_53d6ea'] if compiled else 0x53d6ea
  targets={((syms[n] if compiled else a)&~1):n for n,a in callees};events=[]
  def hook(u,address,_size,_user):
   n=targets.get(address)
   if n is None:return
   if n=='display_driver_nema_select_522a16':events.append((n,u.reg_read(UC_ARM_REG_R0)))
   elif n=='display_driver_nema_clear_522ae0':events.append((n,*(u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))))
   elif n=='audio_uart_ambiq_outline_available_529ca4':
    events.append((n,u.reg_read(UC_ARM_REG_R0)))
    u.reg_write(UC_ARM_REG_R0,available)
   else:events.append((n,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  cpu.emu_start(start|1,0x600000,count=100)
  return events
 count=0
 for seed in range(128):
  a=run(False,'fill',seed,0);b=run(True,'fill',seed,0);assert a==b,(seed,a,b);count+=1
  for available in (0,1,0x12345678):
   a=run(False,'vector',seed,available);b=run(True,'vector',seed,available)
   assert a==b,(seed,available,a,b);count+=1
 print('PASS_AMBIQ_LABEL_FILL_VECTOR_NATIVE',count)
