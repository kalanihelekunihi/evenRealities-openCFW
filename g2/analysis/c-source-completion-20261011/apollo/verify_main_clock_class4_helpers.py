#!/usr/bin/env python3
"""Direct locked Main/source class 4 count, timeout and trigger helper checks."""
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
ENTRY={'popcount':(0x4c3750,syms['g2_main_clock_popcount_4c3750']),'count':(0x4c37ca,syms['g2_main_clock_request_count_4c37ca']),'wait':(0x4c387e,syms['g2_main_clock_timeout_wait_4c387e']),'finish':(0x4c3ef4,syms['g2_main_clock_timeout_finish_4c3ef4']),'trigger':(0x4d3938,syms['g2_main_clock_class4_trigger_4d3938'])}
RET,TABLE,ACTIVE,SLOT,EXPIRED,TICKS,TRIGGER=0x200ff000,0x20073324,0x20074f57,0x20074264,0x20074f59,0x20008000,0x40004020

def put(cpu,addr,val):cpu.mem_write(addr,int(val).to_bytes(4,'little'))
def get(cpu,addr):return int.from_bytes(cpu.mem_read(addr,4),'little')
def run(source,kind,word,other,active,ticks,mask):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(0x40000000,0x10000)
 for cls in range(7):put(cpu,TABLE+cls*8,word);put(cpu,TABLE+cls*8+4,other)
 cpu.mem_write(ACTIVE,bytes([active]));cpu.mem_write(EXPIRED,b'\x00');put(cpu,SLOT,TICKS);put(cpu,TICKS,ticks);put(cpu,TRIGGER,0xa5a5a5a5)
 args={'popcount':(word,0,0,other),'count':(4,0,0,other),'wait':(ACTIVE,TICKS,0,other),'finish':(TICKS,0,0,other),'trigger':(word,0,0,other)}[kind]
 for reg,val in zip((R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2,R.UC_ARM_REG_R3),args):cpu.reg_write(reg,val)
 cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1);cpu.reg_write(R.UC_ARM_REG_PRIMASK,mask)
 events=[];helpers={syms['g2_main_critical_save_473940'] if source else 0x473940:'critical',syms['audio_delay_us_selected'] if source else 0x4807a0:'delay'}
 def hook(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop();return
  event=helpers.get(pc)
  if event is None:return
  events.append([event,machine.reg_read(R.UC_ARM_REG_R0) if event=='delay' else None])
  if event=='critical':machine.reg_write(R.UC_ARM_REG_R0,mask);machine.reg_write(R.UC_ARM_REG_PRIMASK,1)
  machine.reg_write(R.UC_ARM_REG_PC,machine.reg_read(R.UC_ARM_REG_LR))
 cpu.hook_add(UC_HOOK_CODE,hook)
 cpu.emu_start(ENTRY[kind][1 if source else 0]|1,RET+2,count=20000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 result={'events':events,'r0':cpu.reg_read(R.UC_ARM_REG_R0),'primask':cpu.reg_read(R.UC_ARM_REG_PRIMASK),'active':bytes(cpu.mem_read(ACTIVE,1)).hex(),'expired':bytes(cpu.mem_read(EXPIRED,1)).hex(),'slot':get(cpu,SLOT),'ticks':get(cpu,TICKS),'trigger':get(cpu,TRIGGER)}
 if kind=='finish':result.pop('r0')
 return result
fixtures=[]
for kind in ENTRY:
 for word,other,active,ticks,mask in itertools.product((0,1,0xffffffff,0x12345678,0x80000000),(0,1,0xffffffff),(0,1),(0,1,3),(0,1)):
  if kind in ('popcount','count','trigger') and (active!=0 or ticks!=0 or mask!=0):continue
  if kind=='wait' and mask!=0:continue
  fixtures.append((kind,word,other,active,ticks,mask))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_CLOCK_CLASS4_HELPERS_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Critical save and delay intercepted; synthetic SRAM/MMIO only.','Undefined auxiliary return register of timeout finish is excluded from comparison.','Physical clock operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
