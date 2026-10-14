#!/usr/bin/env python3
"""Compare Apollo GPU position's VFP arguments and subsequent clear call."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_gpu_position.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in
  ('display_driver_nema_float_translate_5228b0','display_driver_nema_clear_522ae0'))+
  '.bss\n.global audio_uart_nema_context_cell\naudio_uart_nema_context_cell: .space 4\n')
 image=d/'position.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4',
  '-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-mthumb','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for x,y,width,height in [(0,0,1,1),(1,0xffffffff,64,32),
                           (16777217,0xff000001,0xffffffff,0x80000000),
                           (0x80000000,0x7fffffff,0,0)]:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   cell=syms['audio_uart_nema_context_cell'] if compiled else 0x20074efc
   cpu.mem_write(cell,(0x20088000).to_bytes(4,'little'))
   cpu.mem_write(0x20088054,width.to_bytes(4,'little')+height.to_bytes(4,'little'))
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   cpu.reg_write(UC_ARM_REG_R0,x);cpu.reg_write(UC_ARM_REG_R1,y)
   translate=(syms['display_driver_nema_float_translate_5228b0'] if compiled else 0x5228b0)&~1
   clear=(syms['display_driver_nema_clear_522ae0'] if compiled else 0x522ae0)&~1
   events=[]
   def hook(u,address,_size,_user):
    if address==translate:
     events.append(('translate',u.reg_read(UC_ARM_REG_S0),u.reg_read(UC_ARM_REG_S1)))
    elif address==clear:
     events.append(('clear',*[u.reg_read(r) for r in
       (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]))
    else:return
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   start=syms['display_driver_gpu_position_4b1b48'] if compiled else 0x4b1b48
   cpu.emu_start(start|1,0x600000,count=120)
   observations.append(events)
  assert observations[0]==observations[1],(x,y,width,height,observations)
  count+=1
print('PASS_DISPLAY_DRIVER_GPU_POSITION_NATIVE',count)
