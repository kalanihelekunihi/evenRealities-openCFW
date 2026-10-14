#!/usr/bin/env python3
"""Locked Main/source clock class dispatch comparison."""
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
 syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
ADDRESSES={'acquire':[0x4c3bfc,0x4c3c60,0x4c3d9e,0x4c3cd4,0x4c3f2a,0x4c4086,0x4c427e],
           'release':[0x4c3c2e,0x4c3ca2,0x4c3e9a,0x4c3d28,0x4c4016,0x4c420c,0x4c43ec]}
NATIVE={addr:(family,i) for family,addresses in ADDRESSES.items() for i,addr in enumerate(addresses)}
SOURCE={syms[f'g2_main_clock_{family}_{i}_{addr:06x}']:(family,i) for family,addresses in ADDRESSES.items() for i,addr in enumerate(addresses)}
RET=0x200ff000

def run(source,family,cls,peripheral,lower_status):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for address,data in segments:cpu.mem_write(address,data)
 cpu.mem_map(0x20000000,0x100000)
 cpu.reg_write(R.UC_ARM_REG_R0,cls);cpu.reg_write(R.UC_ARM_REG_R1,peripheral)
 cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 events=[];helpers=SOURCE if source else NATIVE
 def hook(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop();return
  event=helpers.get(pc)
  if event is None:return
  events.append([event[0],event[1],machine.reg_read(R.UC_ARM_REG_R0)])
  machine.reg_write(R.UC_ARM_REG_R0,lower_status)
  machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 start=(syms[f'g2_main_mspi_clock_{family}_4c44bc' if family=='acquire' else 'g2_main_mspi_clock_release_4c4530'] if source else (0x4c44bc if family=='acquire' else 0x4c4530))
 cpu.emu_start(start|1,RET+2,count=2000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return cpu.reg_read(R.UC_ARM_REG_R0),events
fixtures=list(itertools.product(('acquire','release'),(0,1,2,3,4,5,6,7,255,256,260),(0,1,16,55,56,57,58,255,256,272),(0,3,9)))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_MSPI_CLOCK_DISPATCH_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Selected per-class clock providers are intercepted.','Physical clock control and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
