#!/usr/bin/env python3
"""Compare composed type-5 control with native bitmap, power, and type-2/3 paths."""
from pathlib import Path
import json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
root=here.parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
audit=json.loads((root/'build/c-firmware/root-main-uled-vendor-round673/link-audit.json').read_text())
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 objects=[]
 for number,source in enumerate(audit['sources']):
  obj=Path(directory)/f'source-{number}.o'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
   '-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(root/source),'-o',str(obj)],
   check=True,capture_output=True)
  objects.append(obj)
 stub=Path(directory)/'stub.c'
 stub.write_text('''unsigned display_driver_uled_pin_control_type6_4c43ec(unsigned x){return x;}
unsigned display_driver_uled_pin_prepare_type5_4c4086(unsigned x){return x;}
unsigned display_driver_uled_pin_prepare_type6_4c427e(unsigned x){return x;}
unsigned display_driver_uled_rom_delay_00000040(unsigned x){return x;}
''')
 obj=Path(directory)/'stub.o';image=Path(directory)/'type5.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
  '-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(stub),'-o',str(obj)],
  check=True,capture_output=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objects],str(obj),
  '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for pin in (0,31,32,56):
  for enabled in (0,1):
   for other in (0,1):
    for peripheral in (0,1):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      u.mem_map(0x40000000,0x30000)
      for base,data in segments:u.mem_write(base,data)
      for i in range(14):set32(u,0x20073324+i*4,0)
      slot=0x20073324+10*4+((pin&0xff)>>5)*4
      if enabled:set32(u,slot,1<<(pin&31))
      if other:set32(u,0x20073324+10*4,1<<(1 if pin!=1 else 2))
      set32(u,0x20074254,peripheral)
      set32(u,0x200001dc,1)
      set32(u,0x78ee34,0x12345678)
      set32(u,0x78ee38,0x87654321)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_PRIMASK,1);u.reg_write(UC_ARM_REG_R0,pin)
      start=syms['display_driver_uled_pin_control_type5_4c420c'] if compiled else 0x4c420c
      try:u.emu_start(start|1,0x600000,count=20000)
      except Exception as error:raise AssertionError((pin,enabled,other,peripheral,compiled,hex(u.reg_read(UC_ARM_REG_PC)))) from error
      observed.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK),
        bytes(u.mem_read(0x20073324,56)),
        bytes(u.mem_read(0x20074250,0x20)),
        bytes(u.mem_read(0x20074f58,4)),
        bytes(u.mem_read(0x40004044,8)),
        bytes(u.mem_read(0x40020120,0x10))))
     assert observed[0]==observed[1],(pin,enabled,other,peripheral,observed)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_CONTROL_TYPE5_NATIVE',cases)
