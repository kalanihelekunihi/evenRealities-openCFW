#!/usr/bin/env python3
"""Locked native/source Main class 4/5 power leaf comparison."""
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
ENTRY={'class4':(0x4d391e,syms['g2_main_clock_class4_off_4d391e']),'class5':(0x4d3952,syms['g2_main_clock_class5_off_4d3952']),'prepare5':(0x4d39e4,syms['g2_main_clock_class5_prepare_off_4d39e4'])}
RET,CONTROL,STATUS,PREP=0x200ff000,0x40004044,0x40004030,0x40004048

def run(source,kind,enable,control,prep,status,helper_return):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(0x40000000,0x10000)
 for addr,val in ((CONTROL,control),(PREP,prep),(STATUS,status)):cpu.mem_write(addr,val.to_bytes(4,'little'))
 cpu.reg_write(R.UC_ARM_REG_R0,enable);cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 calls=[];helper=syms['g2_main_mspi_status_poll_480826'] if source else 0x480826
 def hook(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop();return
  if pc!=helper:return
  regs=[machine.reg_read(r) for r in (R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2,R.UC_ARM_REG_R3)]
  stack=machine.reg_read(R.UC_ARM_REG_SP)
  calls.append(regs+[int.from_bytes(machine.mem_read(stack,4),'little')])
  machine.reg_write(R.UC_ARM_REG_R0,helper_return);machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 cpu.emu_start(ENTRY[kind][1 if source else 0]|1,RET+2,count=2000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'r0':cpu.reg_read(R.UC_ARM_REG_R0),'calls':calls,'control':int.from_bytes(cpu.mem_read(CONTROL,4),'little'),'prep':int.from_bytes(cpu.mem_read(PREP,4),'little')}
fixtures=list(itertools.product(('class4','class5','prepare5'),(0,1,2,256),(0,1,0x20,0xffffffff),(0,1,0xffffffff),(0,0x1000000),(0,4,9)))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_CLOCK_POWER_LEAF_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['MSPI status polling is intercepted; synthetic MMIO only.','Physical power control and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
