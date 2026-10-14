#!/usr/bin/env python3
"""Locked Main/source clock class 4/5 request release comparison."""
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
NATIVE={0x473940:'critical',0x4d391e:'off4',0x4d3952:'off5',0x4d39e4:'prepare5',0x4c3e9a:'release2',0x4c3d28:'release3'}
SOURCE={syms[name]:event for name,event in [('g2_main_critical_save_473940','critical'),('g2_main_clock_class4_off_4d391e','off4'),('g2_main_clock_class5_off_4d3952','off5'),('g2_main_clock_class5_prepare_off_4d39e4','prepare5'),('g2_main_clock_release_2_4c3e9a','release2'),('g2_main_clock_release_3_4c3d28','release3')]}
TABLE,FLAG,READY,ACTIVE,POINTER,RET=0x20073324,0x20074254,0x20074f5a,0x20074f58,0x20074268,0x200ff000

def run(source,cls,id,other,flag,mask):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000)
 cpu.mem_write(TABLE,bytes(56))
 if id>=0:
  word=cls*8+(id>>5)*4;cpu.mem_write(TABLE+word,(1<<(id&31)).to_bytes(4,'little'))
 if other>=0:
  word=cls*8+(other>>5)*4;old=int.from_bytes(cpu.mem_read(TABLE+word,4),'little');cpu.mem_write(TABLE+word,(old|(1<<(other&31))).to_bytes(4,'little'))
 cpu.mem_write(FLAG,flag.to_bytes(4,'little'))
 cpu.mem_write(READY,b'\x01');cpu.mem_write(ACTIVE,b'\x01');cpu.mem_write(POINTER,(0x20008000).to_bytes(4,'little'))
 cpu.reg_write(R.UC_ARM_REG_R0,id if id>=0 else 16);cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1);cpu.reg_write(R.UC_ARM_REG_PRIMASK,mask)
 events=[];helpers=SOURCE if source else NATIVE
 def hook(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop();return
  event=helpers.get(pc)
  if event is None:return
  events.append([event,machine.reg_read(R.UC_ARM_REG_R0) if event!='prepare5' else None])
  if event=='critical':machine.reg_write(R.UC_ARM_REG_R0,mask);machine.reg_write(R.UC_ARM_REG_PRIMASK,1)
  else:machine.reg_write(R.UC_ARM_REG_R0,0)
  machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 entry=syms[f'g2_main_clock_release_{cls}_{"4c4016" if cls==4 else "4c420c"}'] if source else (0x4c4016 if cls==4 else 0x4c420c)
 cpu.emu_start(entry|1,RET+2,count=4000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'r0':cpu.reg_read(R.UC_ARM_REG_R0),'mask':cpu.reg_read(R.UC_ARM_REG_PRIMASK),'events':events,'bitmap':bytes(cpu.mem_read(TABLE,56)).hex(),'globals':[(x,bytes(cpu.mem_read(x,n)).hex()) for x,n in ((FLAG,4),(READY,1),(ACTIVE,1),(POINTER,4))]}
fixtures=list(itertools.product((4,5),(-1,0,16,31,32,54,56),(-1,0,1,55),(0,1),(0,1)))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_CLOCK_RELEASE_45_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Critical section and peripheral power helpers intercepted.','Synthetic SRAM state and clock request bitmap; physical clock operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
