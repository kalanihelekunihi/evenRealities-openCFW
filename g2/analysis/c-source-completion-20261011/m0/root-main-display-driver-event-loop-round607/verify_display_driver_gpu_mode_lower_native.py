#!/usr/bin/env python3
"""Compare Apollo Ambiq cached-mode decisions and state writes with ARM C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_gpu_mode_lower.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stub.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in
  ('audio_uart_ambiq_default_unit_4c791a','display_driver_nema_mode_513924')))
 image=d/'mode_lower.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0x20001000,7,0,1,255,0,7,0,1,255),
        (0x20001000,8,0,1,255,0,7,0,1,255),
        (0x20001000,7,0xffffffff,0x80,0x7f,0,7,255,0x80,0x7f),
        (0x20001000,7,0,1,255,1,7,0,1,255),
        (0x20001000,7,0,1,255,256,7,0,1,255),
        (0,7,0,1,255,0,7,0,1,255),
        (0,7,0,1,255,1,7,0,1,255),
        (0,0xffffffff,0x100,0x101,0x102,0,0,0,0,0)]
 count=0
 for unit,mode,a,b,c,force,old_mode,old_a,old_b,old_c in cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   state=unit or 0x20002000
   cpu.mem_write(state+0x50,old_mode.to_bytes(4,'little')+bytes((old_a,old_b,old_c)))
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(unit,mode,a,b)):
    cpu.reg_write(reg,value)
   cpu.mem_write(0x200ff000,c.to_bytes(4,'little')+force.to_bytes(4,'little'))
   default=(syms['audio_uart_ambiq_default_unit_4c791a'] if compiled else 0x4c791a)&~1
   nema=(syms['display_driver_nema_mode_513924'] if compiled else 0x513924)&~1
   events=[]
   def hook(u,address,_size,_user):
    if address==default:
     events.append(('default',));u.reg_write(UC_ARM_REG_R0,0x20002000)
    elif address==nema:
     events.append(('nema',*[u.reg_read(r) for r in
       (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]))
    else:return
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   start=syms['display_driver_gpu_mode_lower_4b06c0'] if compiled else 0x4b06c0
   cpu.emu_start(start|1,0x600000,count=100)
   observations.append((events,bytes(cpu.mem_read(state+0x50,7)).hex()))
  assert observations[0]==observations[1],(unit,mode,a,b,c,force,observations)
  count+=1
print('PASS_DISPLAY_DRIVER_GPU_MODE_LOWER_NATIVE',count)
