#!/usr/bin/env python3
"""Compiled C/native reset-offset memory comparison for native 0x4b334c."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_reset_offset.c'
STUB='#include <stdint.h>\nuint8_t audio_ble_subsystem_link_state_200719c8[0x80];\n'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSlaveResetAdvDataOffset',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for mode in (0,1):
  for handle in (0,1):
   for values in ((0,0),(3,0),(0,5),(7,9)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
     u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
     data=bytearray([0x66]*0x80);data[0x5d]=mode;data[0x55+handle]=7
     off=0x40+handle*8+mode*4
     data[off:off+2]=values[0].to_bytes(2,'little');data[off+2:off+4]=values[1].to_bytes(2,'little')
     u.mem_write(state,bytes(data));u.reg_write(UC_ARM_REG_R0,handle)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.emu_start((sy['appSlaveResetAdvDataOffset'] if is_c else 0x4b334c)|1,0x600000,count=1000)
     pair.append(bytes(u.mem_read(state,0x80)))
    assert pair[0]==pair[1],(mode,handle,values)
print('PASS_BLE_APP_ADV_RESET_NATIVE 16')
