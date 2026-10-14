#!/usr/bin/env python3
"""Compare the Apollo case-3 prelude's frame-call arguments with compiled C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_case3_prelude.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);stubs=d/'stubs.s'
 stubs.write_text('.syntax unified\n.thumb\n.text\n.global display_driver_frame_prepare_46c73c\n'
  '.thumb_func\ndisplay_driver_frame_prepare_46c73c:\n bx lr\n.data\n'
  '.global audio_settings_display_profile_cell\naudio_settings_display_profile_cell: .word 8\n'
  '.global audio_settings_display_brightness_cell\naudio_settings_display_brightness_cell: .word 64\n'
  '.global display_driver_uled_context\ndisplay_driver_uled_context: .word 0x20094400\n')
 image=d/'prelude.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_case3_prelude',
  str(source),str(stubs),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[(8,0x18,64,0),(0,0,0,0),(1,0,1,0),(64,0,192,0),
        (65,0,193,0),(0xffffffff,1,0xffffffff,1),(60,5,190,5),
        (0x80000000,0,0x80000000,0),(63,1,191,1)]
 count=0
 for profile,dx,brightness,dy in cases:
  observed=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   cpu.mem_write(0x200007b8,(0x20094400).to_bytes(4,'little'))
   for address,data in segments:cpu.mem_write(address,data)
   addresses=[syms['audio_settings_display_profile_cell'],syms['display_driver_horizontal_offset_cell'],
              syms['audio_settings_display_brightness_cell'],syms['display_driver_vertical_offset_cell']] if compiled else [0x20000648,0x20000650,0x2000064c,0x200744c8]
   for a,v in zip(addresses,(profile,dx,brightness,dy)):
    cpu.mem_write(a,v.to_bytes(4,'little'))
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   target=(syms['display_driver_frame_prepare_46c73c'] if compiled else 0x46c73c)&~1
   calls=[]
   def hook(u,address,_size,_user):
    if address!=target:return
    sp=u.reg_read(UC_ARM_REG_SP)
    args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    args += [int.from_bytes(u.mem_read(sp+i,4),'little') for i in (0,4,8,12)]
    calls.append(args)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   start=syms['display_driver_case3_prelude'] if compiled else 0x46ca14
   cpu.emu_start(start|1,0x600000,count=100)
   observed.append((calls,cpu.reg_read(UC_ARM_REG_R0)))
  assert observed[0]==observed[1],((profile,dx,brightness,dy),observed)
  assert len(observed[0][0])==1
  count+=1
print('PASS_DISPLAY_DRIVER_CASE3_PRELUDE_NATIVE',count)
