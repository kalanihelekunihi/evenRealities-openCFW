#!/usr/bin/env python3
"""Bounded native/source MSPI clock route comparison against locked Main."""
import argparse, hashlib, itertools, json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==STOCK_SHA
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
with a.elf.open('rb') as f:
 elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
 syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
NATIVE={0x473940:'critical',0x4807a0:'delay'}
SOURCE={syms['g2_main_critical_save_473940']:'critical',syms['audio_delay_us_selected']:'delay'}
RET,REG=0x200ff000,0x40004110

def run(source,module,enable,set_divider,divider,initial,mask):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for address,data in segments:cpu.mem_write(address,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(0x40000000,0x10000)
 cpu.mem_write(REG,initial.to_bytes(4,'little'))
 for reg,val in zip((R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2,R.UC_ARM_REG_R3),(module,enable,set_divider,divider)):cpu.reg_write(reg,val)
 cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1);cpu.reg_write(R.UC_ARM_REG_PRIMASK,mask)
 events=[];helpers=SOURCE if source else NATIVE
 def hook(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop();return
  event=helpers.get(pc)
  if event is None:return
  events.append([event,machine.reg_read(R.UC_ARM_REG_R0) if event=='delay' else None])
  if event=='critical':
   machine.reg_write(R.UC_ARM_REG_R0,mask);machine.reg_write(R.UC_ARM_REG_PRIMASK,1)
  machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 cpu.emu_start((syms['g2_main_mspi_clock_route_4c0758'] if source else 0x4c0758)|1,RET+2,count=2000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'r0':cpu.reg_read(R.UC_ARM_REG_R0),'reg':int.from_bytes(cpu.mem_read(REG,4),'little'),'primask':cpu.reg_read(R.UC_ARM_REG_PRIMASK),'events':events}

fixtures=list(itertools.product((0,1,2,3,6,7),(0,1,0x100),(0,1,0x100),(0,1,7,10,15,255),(0,0xa5a5a5a5,0xffffffff),(0,1)))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_MSPI_CLOCK_ROUTE_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Critical save and delay are intercepted; synthetic clock register and PRIMASK only.','Physical clock operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
