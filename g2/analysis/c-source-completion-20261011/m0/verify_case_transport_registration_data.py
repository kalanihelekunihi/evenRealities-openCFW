#!/usr/bin/env python3
"""Compare typed CASE 0xd26c descriptors to stock fields and task labels."""
from pathlib import Path
import struct,subprocess
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_registration_data_candidate.c'
obj=H/'transport_registration_data.oracle.o';elf=H/'transport_registration_data.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s for s in e.get_section_by_name('.symtab').iter_symbols()};p=sym['case_boot_transport_registration_storage'];assert p['st_size']==0x114
 seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
 def read(a,n):
  for v,b in seg:
   if v<=a and a+n<=v+len(b):return b[a-v:a-v+n]
  raise AssertionError(hex(a))
 got=read(p['st_value'],0x114);stock=F[0xd26c:0xd380]
 positions=[i*16 for i in range(6)]+[0x60+i*36 for i in range(4)]+[0xf0]
 for pos in range(0,0x114,4):
  n=struct.unpack_from('<I',stock,pos)[0];c=struct.unpack_from('<I',got,pos)[0]
  if pos in positions:
   assert n>=0x08000000
   native=F[n-0x08000000:].split(b'\0')[0]
   candidate=read(c,len(native)+1).split(b'\0')[0]
   assert native==candidate,(hex(pos),native,candidate)
  else:assert n==c,(hex(pos),hex(n),hex(c))
print('PASS_CASE_TRANSPORT_REGISTRATION_DATA',0x114,'bytes',len(positions),'typed labels')
