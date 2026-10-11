#!/usr/bin/env python3
"""Verify source-owned CASE startup composition at the clean ELF placement.

This verifies source relocations and typed CRT state, not stock address layout.
"""
from pathlib import Path
import subprocess,sys,tempfile
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[3]
with tempfile.TemporaryDirectory() as d:
 elf=Path(d)/'case.elf'
 subprocess.run([sys.executable,str(H/'build_case_absolute_experiment.py'),'--output',str(elf)],check=True,capture_output=True)
 with elf.open('rb') as stream:
  e=ELFFile(stream);section=e.get_section_by_name('.isr_vector')
  assert section is not None
  data=section.data();assert len(data)==46*4,len(data)
  vector=[int.from_bytes(data[i:i+4],'little') for i in range(0,len(data),4)]
  symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
  expected={0:0x20002c88,1:symbols['case_reset_entry_0144']|1,
            2:symbols['case_vector_nmi_6d70']|1,
            3:symbols['case_vector_hardfault_6778']|1,
            11:symbols['case_vector_svc_6e18']|1,
            14:symbols['case_vector_pendsv_0102']|1,
            15:symbols['case_vector_systick_8420']|1,
            18:symbols['case_vector_irq_6e08']|1,
            21:symbols['case_vector_irq_3bc8']|1,
            22:symbols['case_vector_irq_3c2c']|1,
            23:symbols['case_vector_irq_3d24']|1,
            28:symbols['case_vector_irq_06c4']|1,
            38:symbols['case_vector_irq_84b0']|1,
            43:symbols['case_vector_irq_8f98']|1}
  assert all(vector[i]==value for i,value in expected.items()),[(i,hex(vector[i]),hex(value)) for i,value in expected.items() if vector[i]!=value]
  assert symbols['case_boot_application_veneer_00c0']&1
  print('PASS_CASE_STARTUP_INTEGRATED_VECTOR',len(vector),'slots',len(expected),'typed_entries')
subprocess.run([sys.executable,str(H/'verify_case_crt_known_defaults.py')],check=True)
