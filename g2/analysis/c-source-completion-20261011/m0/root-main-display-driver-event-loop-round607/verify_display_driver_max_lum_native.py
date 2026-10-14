#!/usr/bin/env python3
"""Compare Apollo max-luminance calculation against compiled ARM C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_max_lum.c')
ratio_source=Path(__file__).with_name('display_driver_ratio_cell.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['audio_uart_checksum_copy','audio_uart_device_role_get','audio_log_flags',
        'audio_log_extended','compressed_log_output']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names)+
  '.bss\n.global audio_settings_config_live\naudio_settings_config_live:\n.space 128\n')
 image=d/'maxlum.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16',
  '-mfloat-abi=hard','-mthumb','-O2','-ffp-contract=off','-nostdlib',
  '-Wl,-Ttext=0x100000','-Wl,-e,display_driver_brightness_max_lum_46c23c',str(source),str(ratio_source),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 cases=[(5,1,0),(15,2,10),(4,3,0),(0,1,255),(6,2,3),(255,0,0),
        (10,1,5),(12,2,11),(5,3,10),(7,1,2)]
 for (raw,role,cal),flags in [(case,f) for case in cases for f in (0,1,2,4,7)]:
  count+=1;observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   ratio=syms['display_driver_ratio_cells_20003994']+0x2e if compiled else 0x200039c2
   cpu.mem_write(ratio,bytes([raw]))
   settings=syms['audio_settings_config_live'] if compiled else 0x20072da8
   cpu.mem_write(settings+0x16,bytes([cal,cal]))
   targets={((syms[n] if compiled else native)&~1):label for n,native,label in [
    ('audio_uart_checksum_copy',0x439c04,'copy'),
    ('audio_uart_device_role_get',0x45a568,'role'),
    ('audio_log_flags',0x43d0ce,'flags'),('audio_log_extended',0x43d574,'text'),
    ('compressed_log_output',0x43ce9e,'compact')]}
   calls=[]
   def hook(u,address,_size,_user):
    label=targets.get(address)
    if label is None:return
    if label=='copy':
     dst=u.reg_read(UC_ARM_REG_R0);src=u.reg_read(UC_ARM_REG_R1);n=u.reg_read(UC_ARM_REG_R2)
     assert n==44;u.mem_write(dst,bytes(u.mem_read(src,n)))
    elif label=='role':u.reg_write(UC_ARM_REG_R0,role)
    elif label=='flags':u.reg_write(UC_ARM_REG_R0,flags)
    elif label in ('text','compact'):
     def cs(p):return bytes(u.mem_read(p,200)).split(b'\0')[0].decode('ascii')
     if label=='text':
      assert cs(u.reg_read(UC_ARM_REG_R1))=='service.settings'
      assert cs(u.reg_read(UC_ARM_REG_R3))=='SVC_Settings_GetMaxLum'
     else:
      assert cs(u.reg_read(UC_ARM_REG_R1))==cs(u.reg_read(UC_ARM_REG_R2))
    else:raise AssertionError((raw,role,cal,label))
    calls.append(label)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   cpu.emu_start((syms['display_driver_brightness_max_lum_46c23c'] if compiled else 0x46c23c)|1,0x600000,count=1000)
   observations.append((calls,cpu.reg_read(UC_ARM_REG_R0)))
  assert observations[0]==observations[1],(raw,role,cal,observations)
print('PASS_DISPLAY_DRIVER_MAX_LUM_NATIVE',count)
