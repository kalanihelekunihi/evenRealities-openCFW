#!/usr/bin/env python3
"""Exact native-byte check for typed CASE 0x1d04/0x1e4c protocol seeds."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_packet_templates_candidate.c'
obj=H/'transport_packets.oracle.o'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with obj.open('rb') as f:
 e=ELFFile(f);sym={s.name:s for s in e.get_section_by_name('.symtab').iter_symbols()}
 for name,address,size in [('case_boot_transport_action_template',0x1d04,8),('case_policy_ota_probe_template',0x1e4c,12)]:
  s=sym[name];sec=e.get_section(s['st_shndx']);data=sec.data()[s['st_value']:s['st_value']+size]
  assert s['st_size']==size and data==F[address:address+size],(name,data.hex(),F[address:address+size].hex())
print('PASS_CASE_TRANSPORT_PACKET_TEMPLATES',20,'bytes')
