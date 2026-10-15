#!/usr/bin/env python3
"""Compare pin preparation calls against official Apollo with lower calls bounded."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('''typedef unsigned u32;
const unsigned char *audio_ble_hci_radio_mode_state_50938e(u32 x){return (const unsigned char *)0x20002000u;}
u32 g2_codec_pin_function(u32 a,u32 b){return 0;}
''')
 image=Path(directory)/'pins.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_pin_prepare_pair.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 pin=int.from_bytes(blob[0x78ee40-0x438000:0x78ee44-0x438000],'little')
 assert pin!=0
 for name,native in [('display_driver_uled_type0_pin_prepare_592c78',0x592c78),('display_driver_uled_type1_pin_prepare_5bc690',0x5bc690)]:
  for mode in (0,2,3,4,255):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    u.mem_write(0x20002000,bytes([mode]))
    calls=[]
    def lower(uc,at,size,user):
     if at==(syms['audio_ble_hci_radio_mode_state_50938e']&~1 if compiled else 0x50938e):
      calls.append(('mode',uc.reg_read(UC_ARM_REG_R0)))
      uc.reg_write(UC_ARM_REG_R0,0x20002000)
     else:
      calls.append(('pin',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
      uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for n,at in [('audio_ble_hci_radio_mode_state_50938e',0x50938e),('g2_codec_pin_function',0x480f0c)]:
     target=syms[n]&~1 if compiled else at
     u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((syms[name] if compiled else native)|1,0x600000,count=1000)
    observed.append(calls)
   assert observed[0]==observed[1],(name,mode,pin,observed)
 print('PASS_ULED_OPTION_PIN_PREPARE_PAIR_NATIVE',10,'rom_pin_word',hex(pin))
