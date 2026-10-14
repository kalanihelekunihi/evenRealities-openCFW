#!/usr/bin/env python3
"""Bounded locked Main/source class 4 clock acquire control-flow oracle."""
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
NATIVE={0x473940:'critical',0x4c3ef4:'finish',0x4d3938:'trigger'}
SOURCE={syms['g2_main_critical_save_473940']:'critical',syms['g2_main_clock_timeout_finish_4c3ef4']:'finish',syms['g2_main_clock_class4_trigger_4d3938']:'trigger'}
TABLE,ACTIVE,SLOT,EXPIRED,FLAG,PERIPH,TRIGGER,CONTROL,RET=0x20073324,0x20074f57,0x20074264,0x20074f59,0x20004536,0x20074250,0x40004020,0x40004044,0x200ff000

def put(cpu,address,value):cpu.mem_write(address,int(value).to_bytes(4,'little'))
def get(cpu,address):return int.from_bytes(cpu.mem_read(address,4),'little')
def run(source,id,requested,other,active,flag,periph,fail,mask):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(0x40000000,0x10000)
 cpu.mem_write(TABLE,bytes(56))
 if requested:
  address=TABLE+4*8+(id//32)*4;put(cpu,address,get(cpu,address)|(1<<(id%32)))
 if other>=0:
  address=TABLE+4*8+(other//32)*4;put(cpu,address,get(cpu,address)|(1<<(other%32)))
 cpu.mem_write(ACTIVE,bytes([active]));cpu.mem_write(EXPIRED,b'\x00');cpu.mem_write(FLAG,bytes([flag]));put(cpu,PERIPH,periph)
 put(cpu,0x20008000,3);put(cpu,SLOT,0x20008000)
 put(cpu,TRIGGER,0xa5a5a5a5);put(cpu,CONTROL,0xa5a5a5a5)
 cpu.reg_write(R.UC_ARM_REG_R0,id);cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1);cpu.reg_write(R.UC_ARM_REG_PRIMASK,mask)
 events=[];helpers=SOURCE if source else NATIVE
 def hook(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop();return
  event=helpers.get(pc)
  if event is None:return
  if event=='critical':
   events.append(['critical']);machine.reg_write(R.UC_ARM_REG_R0,mask);machine.reg_write(R.UC_ARM_REG_PRIMASK,1)
  elif event=='finish':
   ptr=machine.reg_read(R.UC_ARM_REG_R0);events.append(['finish',get(machine,ptr)]);machine.reg_write(R.UC_ARM_REG_R0,0)
  else:
   events.append(['trigger',machine.reg_read(R.UC_ARM_REG_R0)]);machine.reg_write(R.UC_ARM_REG_R0,7 if fail else 0)
  machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 cpu.emu_start((syms['g2_main_clock_acquire_4_4c3f2a'] if source else 0x4c3f2a)|1,RET+2,count=6000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 slot=get(cpu,SLOT)
 return {'r0':cpu.reg_read(R.UC_ARM_REG_R0),'primask':cpu.reg_read(R.UC_ARM_REG_PRIMASK),'events':events,'bitmap':bytes(cpu.mem_read(TABLE+32,8)).hex(),'active':bytes(cpu.mem_read(ACTIVE,1)).hex(),'expired':bytes(cpu.mem_read(EXPIRED,1)).hex(),'slot_kind':'stack' if 0x200fd000<=slot<=0x200fe000 else hex(slot),'trigger':get(cpu,TRIGGER),'control':get(cpu,CONTROL)}
fixtures=list(itertools.product((0,1,16,31,32,54,56),(False,True),(-1,1,55),(0,1),(0,1),(0,1),(False,True),(0,1)))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_CLOCK_CLASS4_ACQUIRE_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Critical save, timeout finish and trigger are intercepted; finish/timeout helpers require separate comparisons.','Synthetic SRAM/MMIO only; physical clock operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
