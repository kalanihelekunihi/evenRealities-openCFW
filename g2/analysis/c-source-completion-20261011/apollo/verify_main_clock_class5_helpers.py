#!/usr/bin/env python3
"""Direct locked native/source class 5 configuration and timeout checks."""
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
ENTRY={'config':(0x4d3992,syms['g2_main_clock_class5_config_4d3992']),'finish':(0x4c4058,syms['g2_main_clock_class5_finish_4c4058'])}
RET,CONFIG,ACTIVE,SLOT,TICKS=0x200ff000,0x20008000,0x20074f58,0x20074268,0x20008100

def put(cpu,address,value):cpu.mem_write(address,int(value).to_bytes(4,'little'))
def get(cpu,address):return int.from_bytes(cpu.mem_read(address,4),'little')
def run(source,kind,mode,divider,freq,active,ticks,mask,initial):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(0x40000000,0x10000)
 cpu.mem_write(CONFIG,bytes([mode,divider,0,0])+freq.to_bytes(4,'little'))
 cpu.mem_write(ACTIVE,bytes([active]));put(cpu,SLOT,TICKS);put(cpu,TICKS,ticks)
 cpu.mem_write(0x40004040,initial.to_bytes(4,'little')*8)
 cpu.reg_write(R.UC_ARM_REG_R0,(0 if mode==255 else CONFIG) if kind=='config' else TICKS)
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
 cpu.emu_start(ENTRY[kind][1 if source else 0]|1,RET+2,count=5000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 result={'events':events,'r0':cpu.reg_read(R.UC_ARM_REG_R0),'primask':cpu.reg_read(R.UC_ARM_REG_PRIMASK),'active':bytes(cpu.mem_read(ACTIVE,1)).hex(),'slot':get(cpu,SLOT),'ticks':get(cpu,TICKS),'mmio':bytes(cpu.mem_read(0x40004040,32)).hex()}
 if kind=='finish':result.pop('r0')
 return result
fixtures=[]
for kind in ENTRY:
 for mode,divider,freq,active,ticks,mask,initial in itertools.product((0,1,2,255),(0,1,3,255),(0,1,0x12345678,0xffffffff),(0,1),(0,1,3),(0,1),(0,0xa5a5a5a5)):
  if kind=='config' and (active!=0 or ticks!=0 or mask!=0):continue
  if kind=='finish' and (mode!=0 or divider!=0 or freq!=0):continue
  fixtures.append((kind,mode,divider,freq,active,ticks,mask,initial))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_CLOCK_CLASS5_HELPERS_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Critical save and delay intercepted; synthetic SRAM/MMIO only.','Undefined auxiliary return register of timeout finish excluded.','Physical clock behavior and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
