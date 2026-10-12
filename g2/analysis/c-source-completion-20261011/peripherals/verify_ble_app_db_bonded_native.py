#!/usr/bin/env python3
"""Actual C/native AppDbCheckBonded record selection."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_db_bonded.c'
STUB='#include <stdint.h>\nuint8_t audio_ble_privacy_rows[2000];\n'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,AppDbCheckBonded',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for active,master in ((False,False),(True,True),(True,False)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   rows=sy['audio_ble_privacy_rows'] if is_c else 0x20067a30
   u.mem_write(rows,bytes([0]*2000))
   u.mem_write(rows+9*200+0x2f,bytes([int(active)]));u.mem_write(rows+9*200+0xc3,bytes([int(master)]))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['AppDbCheckBonded'] if is_c else 0x47a600)|1,0x600000,count=1000)
   pair.append(u.reg_read(UC_ARM_REG_R0)&255)
  assert pair[0]==pair[1],(active,master,pair)
print('PASS_BLE_APP_DB_BONDED_NATIVE 3')
