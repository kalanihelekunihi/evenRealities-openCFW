#!/usr/bin/env python3
"""All 256 mode values for native/source Main MSPI finish leaf."""
import argparse
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as R
ROOT = Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = BLOB.read_bytes()
assert hashlib.sha256(blob).hexdigest() == STOCK_SHA
p=argparse.ArgumentParser(); p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
with a.elf.open('rb') as f:
 elf=ELFFile(f)
 segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
 source=next(s['st_value'] & ~1 for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_main_mspi_configure_finish_4c07d0')
HANDLE, RET=0x20006000,0x200ff000
def run(is_source,mode,initial):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segs:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000)
 cpu.mem_write(HANDLE,bytes([0xa5])*0x900)
 cpu.mem_write(HANDLE+12,bytes([mode]))
 cpu.mem_write(HANDLE+0x8cc,initial.to_bytes(4,'little'))
 cpu.reg_write(R.UC_ARM_REG_R0,HANDLE);cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 def stop(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,stop)
 cpu.emu_start((source if is_source else 0x4c07d0)|1,RET+2,count=2000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return bytes(cpu.mem_read(HANDLE,0x900))
for mode in range(256):
 for initial in (0,0xa5a5a5a5):
  assert run(False,mode,initial)==run(True,mode,initial),(mode,initial)
report={'status':'PASS_MAIN_MSPI_CONFIGURE_FINISH_ALL_MODES','cases':512,'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Synthetic SRAM; physical MSPI and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],report['cases'])
