#!/usr/bin/env python3
"""Exact eight-entry CASE divisor/rate table data check."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_rate_tables_candidate.c'
obj=H/'sensor_rate_tables.oracle.o'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with obj.open('rb') as f:
 e=ELFFile(f);syms={s.name:s for s in e.get_section_by_name('.symtab').iter_symbols()}
 for name,address in [('case_boot_sensor_divisor_table',0xd398),('case_boot_sensor_rate_table',0xd3a0)]:
  s=syms[name];data=e.get_section(s['st_shndx']).data()[s['st_value']:s['st_value']+8]
  assert s['st_size']==8 and data==F[address:address+8],(name,data.hex(),F[address:address+8].hex())
print('PASS_CASE_SENSOR_RATE_TABLES',16,'bytes')
