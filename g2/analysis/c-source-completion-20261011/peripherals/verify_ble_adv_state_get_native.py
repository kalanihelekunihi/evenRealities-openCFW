#!/usr/bin/env python3
"""Stock/C live-byte getter comparison, native 0x46ef60."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/ble_adv_state_get.c'
with tempfile.TemporaryDirectory() as td:
 epath=Path(td)/'get.elf';shim=Path(td)/'shim.c'
 shim.write_text('#include <stdint.h>\nvolatile uint8_t audio_ble_slave_adv_stop_flag_20074f8d;\n')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_connection_get',str(S),str(shim),'-o',str(epath)],check=True)
 with epath.open('rb') as f:
  e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,value):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_write(sy['audio_ble_slave_adv_stop_flag_20074f8d'] if c else 0x20074f8d,bytes([value]))
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_connection_get'] if c else 0x46ef60)|1,0x600000,count=1000)
  return u.reg_read(UC_ARM_REG_R0)
 for value in range(256):assert run(False,value)==run(True,value)
 print('PASS_BLE_ADV_STATE_GET_NATIVE',256)
