#!/usr/bin/env python3
"""Compare three Apollo display setters with compiled ARM C at their call boundary."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);stubs=d/'stubs.s'
 stubs.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  '.global '+n+'\n.thumb_func\n'+n+':\n bx lr\n' for n in
  ('display_driver_prepare_update_47381e','display_driver_submit_window_474066',
   'display_driver_frame_prepare_46c73c'))+
  '.data\n.global audio_settings_display_profile_cell\naudio_settings_display_profile_cell: .word 8\n'
  '.global audio_settings_display_brightness_cell\naudio_settings_display_brightness_cell: .word 64\n'
  '.global display_driver_uled_context\ndisplay_driver_uled_context: .word 0x20094400\n')
 image=d/'setters.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_position_setters.c'),
  str(here/'display_driver_case3_prelude.c'),str(stubs),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 entries=[('display_driver_set_brightness_46c984',0x46c984,[(0,),(1,),(255,),(0xffffffff,)]),
          ('display_driver_set_profile_46c9aa',0x46c9aa,[(0,),(17,),(0xffffffff,)]),
          ('display_driver_set_offsets_46c9dc',0x46c9dc,
           [(0,0),(48,64),(49,0),(0,65),(0xffffffff,1),(1,0xffffffff),(16,32)])]
 count=0
 for name,native,cases in entries:
  for args in cases:
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    cells=[syms[x] for x in ('audio_settings_display_profile_cell',
           'audio_settings_display_brightness_cell','display_driver_horizontal_offset_cell',
           'display_driver_vertical_offset_cell')] if compiled else [0x20000648,0x2000064c,0x20000650,0x200744c8]
    for a,v in zip(cells,(8,64,24,0)):cpu.mem_write(a,v.to_bytes(4,'little'))
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):cpu.reg_write(reg,value)
    prepare=(syms['display_driver_prepare_update_47381e'] if compiled else 0x47381e)&~1
    submit=(syms['display_driver_submit_window_474066'] if compiled else 0x474066)&~1
    calls=[]
    def hook(u,address,_size,_user):
     if address not in (prepare,submit):return
     if address==prepare:calls.append(('prepare',))
     else:
      sp=u.reg_read(UC_ARM_REG_SP)
      vals=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
      vals += [int.from_bytes(u.mem_read(sp+i,4),'little') for i in (0,4)]
      calls.append(('submit',*vals))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.emu_start((syms[name] if compiled else native)|1,0x600000,count=100)
    observations.append((calls,cpu.reg_read(UC_ARM_REG_R0),
      [int.from_bytes(cpu.mem_read(a,4),'little') for a in cells]))
   assert observations[0]==observations[1],(name,args,observations)
   count+=1
print('PASS_DISPLAY_DRIVER_POSITION_SETTERS_NATIVE',count)
