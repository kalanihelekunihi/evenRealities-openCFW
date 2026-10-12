#!/usr/bin/env python3
"""Stock/C alternate radio pin-mode call order and values."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_alt_mode.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t g2_codec_pin_function(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
int32_t g2_gpio_hal_write(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_alt_mode_52dd24',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 pair=[]
 for is_c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  pin=(sym['g2_codec_pin_function']&~1) if is_c else 0x480f0c
  gpio=(sym['g2_gpio_hal_write']&~1) if is_c else 0x480fd6
  calls=[]
  def hook(uc,a,size,_):
   if a in (pin,gpio):calls.append(('pin' if a==pin else 'gpio',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,7);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_ble_radio_alt_mode_52dd24'] if is_c else 0x52dd24)|1,0x600000,count=300)
  pair.append(calls)
 assert pair[0]==pair[1],pair
 print('PASS_RADIO_ALT_MODE_NATIVE',len(pair[0]))
