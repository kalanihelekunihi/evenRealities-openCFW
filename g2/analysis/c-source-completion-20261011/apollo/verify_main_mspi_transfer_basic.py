#!/usr/bin/env python3
"""Locked native/source selectors 0..13 of the Main MSPI dispatcher."""
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
 source=next(s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_main_mspi_transfer_basic_candidate')
HANDLE,CONFIG,MMIO,RET=0x20006000,0x20008000,0x40060000,0x200ff000

def run(is_source,module,valid,enabled,selector,present,value,pattern):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(MMIO,0x4000)
 cpu.mem_write(HANDLE,bytes([0xa5])*0x20)
 cpu.mem_write(HANDLE,(0x01bebebe if valid else 0).to_bytes(4,'little'))
 cpu.mem_write(HANDLE+4,module.to_bytes(4,'little'))
 cpu.mem_write(HANDLE+8,bytes([enabled]))
 cpu.mem_write(CONFIG,value.to_bytes(4,'little'))
 cpu.mem_write(MMIO,bytes([pattern])*0x4000)
 for reg,val in zip((R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2),(HANDLE,selector,CONFIG if present else 0)):cpu.reg_write(reg,val)
 cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 def stop(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,stop)
 cpu.emu_start((source if is_source else 0x4c0f78)|1,RET+2,count=6000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'r0':cpu.reg_read(R.UC_ARM_REG_R0),'mmio':bytes(cpu.mem_read(MMIO,0x4000)).hex(),'handle':bytes(cpu.mem_read(HANDLE,0x20)).hex()}
values=(0,1,2,3,4,7,8,15,0xe0e0e0,0xffffffff,0x12345678)
fixtures=[(module,True,1,selector,present,value,pattern) for module,selector,present,value,pattern in itertools.product((0,1,2,3),range(14),(False,True),values,(0,0xa5))]
fixtures += [(module,valid,enabled,selector,present,value,pattern) for module,valid,enabled,selector,present,value,pattern in itertools.product((0,1,3),(False,True),(0,1),range(14),(False,True),(0,7,0xffffffff),(0,0xa5))]
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 if native!=candidate:
  n=bytes.fromhex(native['mmio']);c=bytes.fromhex(candidate['mmio']);diff=[(hex(j),hex(a),hex(b)) for j,(a,b) in enumerate(zip(n,c)) if a!=b]
  raise AssertionError((i,fixture,native['r0'],candidate['r0'],diff[:20]))
report={'status':'PASS_MAIN_MSPI_TRANSFER_BASIC_SELECTORS_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Only selectors 0..13 represented; complete 0x4c0f78 remains unresolved.','Synthetic MMIO/SRAM only; physical MSPI operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
