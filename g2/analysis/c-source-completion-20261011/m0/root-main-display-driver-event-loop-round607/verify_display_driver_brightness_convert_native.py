#!/usr/bin/env python3
"""Compare Apollo brightness conversion arithmetic, logs, and outputs with compiled C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_brightness_convert.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['display_driver_brightness_max_lum_46c23c','audio_log_flags','audio_log_extended','compressed_log_output']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names))
 image=d/'brightness.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_case4_read',str(source),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for level in (0,1,2,3,30,31,32,100,101,0xffffffff):
  for max_lum in (0,333,1000):
   for flags in (0,1,2,4,7):
    count+=1;observations=[]
    clamped=min(100,max(2,level));low=clamped<31
    for compiled in (False,True):
     cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
     cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
     for address,data in segments:cpu.mem_write(address,data)
     targets={((syms[n] if compiled else native)&~1):label for n,native,label in [
      ('display_driver_brightness_max_lum_46c23c',0x46c23c,'maxlum'),
      ('audio_log_flags',0x43d0ce,'flags'),('audio_log_extended',0x43d574,'text'),
      ('compressed_log_output',0x43ce9e,'compact')]}
     calls=[]
     def cs(u,p):return bytes(u.mem_read(p,160)).split(b'\0')[0].decode('ascii')
     def hook(u,address,_size,_user):
      label=targets.get(address)
      if label is None:return
      r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
      if label=='maxlum':u.reg_write(UC_ARM_REG_R0,max_lum)
      elif label=='flags':u.reg_write(UC_ARM_REG_R0,flags)
      elif label=='text':
       sp=u.reg_read(UC_ARM_REG_SP)
       assert r0==3 and cs(u,r1)=='service.settings'
       assert cs(u,u.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\platform\service\settings\service_settings.c'
       assert cs(u,u.reg_read(UC_ARM_REG_R3))=='SVC_Settings_BrightnessLevelToLumAndCurrent'
       assert int.from_bytes(u.mem_read(sp,4),'little')==(0x223 if low else 0x22d)
       expected=('Convert brightness level %d to lum %d, max_lum=%d' if low else
                 'Convert brightness level %d to current %d, lum=%d')
       assert cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))==expected
       assert int.from_bytes(u.mem_read(sp+8,4),'little')==clamped
      elif label=='compact':
       assert r0==0x0cc00000 and u.reg_read(UC_ARM_REG_R3)==clamped
       expected=('[service.settings]Convert brightness level %d to lum %d, max_lum=%d' if low else
                 '[service.settings]Convert brightness level %d to current %d, lum=%d')
       assert cs(u,r1)==expected and cs(u,u.reg_read(UC_ARM_REG_R2))==expected
      calls.append(label)
      u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
     cpu.hook_add(UC_HOOK_CODE,hook)
     cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
     cpu.reg_write(UC_ARM_REG_R0,level);cpu.reg_write(UC_ARM_REG_R1,0x20003000);cpu.reg_write(UC_ARM_REG_R2,0x20003004)
     cpu.mem_write(0x20003000,b'\xaa'*8)
     cpu.emu_start((syms['display_driver_case4_read'] if compiled else 0x46c410)|1,0x600000,count=400)
     outputs=tuple(int.from_bytes(cpu.mem_read(0x20003000+i*4,4),'little') for i in range(2))
     observations.append((calls,cpu.reg_read(UC_ARM_REG_R0),outputs))
    assert observations[0]==observations[1],(level,max_lum,flags,observations)
print('PASS_DISPLAY_DRIVER_BRIGHTNESS_CONVERT_NATIVE',count)
