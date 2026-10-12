#!/usr/bin/env python3
"""Native/C complete 256-byte HCI disconnect-reason domain."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_disconnect_reason.c'
with tempfile.TemporaryDirectory() as td:
  elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_disconnect_reason',str(S),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  for code in range(256):
    pair=[]
    for is_c in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
      for a,d in seg:u.mem_write(a,d)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,code)
      u.emu_start((sym['audio_ble_disconnect_reason'] if is_c else 0x4b848c)|1,0x600000,count=700)
      pair.append(bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),100)).split(b'\0')[0])
    assert pair[0]==pair[1],(code,pair)
  print('PASS_BLE_DISCONNECT_REASON_NATIVE',256)
