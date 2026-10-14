#!/usr/bin/env python3
"""All 256 serial modes against locked Main 0x4bfed6 MSPI register body."""
import argparse,hashlib,itertools,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==STOCK_SHA
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
with a.elf.open('rb') as f:
 elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
 source=next(s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_main_mspi_configure_aux_4bfed6')
HANDLE,MMIO,RET=0x20006000,0x40060000,0x200ff000

def run(is_source,module,mode,instruction_flag,initial):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(MMIO,0x4000)
 cpu.mem_write(HANDLE,bytes([0xa5])*0x20)
 cpu.mem_write(HANDLE+4,module.to_bytes(4,'little'))
 cpu.mem_write(HANDLE+9,bytes([instruction_flag]))
 cpu.mem_write(HANDLE+10,bytes([mode]))
 cpu.mem_write(MMIO,bytes([initial])*0x4000)
 cpu.reg_write(R.UC_ARM_REG_R0,HANDLE);cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 def stop(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,stop)
 cpu.emu_start((source if is_source else 0x4bfed6)|1,RET+2,count=5000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'r0':cpu.reg_read(R.UC_ARM_REG_R0),'mmio':bytes(cpu.mem_read(MMIO,0x4000)).hex(),'handle':bytes(cpu.mem_read(HANDLE,0x20)).hex()}
fixtures=list(itertools.product((0,1,2,3),range(256),(0,1,255),(0,0xa5)))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 if native!=candidate:
  diffs=[(hex(j),hex(x),hex(y)) for j,(x,y) in enumerate(zip(bytes.fromhex(native['mmio']),bytes.fromhex(candidate['mmio']))) if x!=y]
  raise AssertionError((i,fixture,native['r0'],candidate['r0'],diffs[:20]))
report={'status':'PASS_MAIN_MSPI_AUX_CONFIG_ALL_MODES_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Synthetic MSPI MMIO and SRAM, with all mode bytes and four modules.','Physical MSPI operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
