#!/usr/bin/env python3
"""Bounded native/source Main MSPI PIO transfer comparison."""
import argparse, hashlib, itertools, json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
parser=argparse.ArgumentParser();parser.add_argument('--elf',type=Path,required=True);parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
blob=STOCK.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
with args.elf.open('rb') as f:
 elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']];syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
SOURCE=syms['g2_norflash_transfer_4c2098'];NATIVE=0x4c2098;RET=0x200ff000;SP=0x200fe000;HANDLE=0x20006000;PIO=0x20007800;MMIO=0x40060000
native_helpers={0x4bfbbc:'read',0x4bfb72:'write',0x480826:'poll'}
source_helpers={syms['g2_main_mspi_fifo_read_4bfbbc']:'read',syms['g2_main_mspi_fifo_write_4bfb72']:'write',syms['g2_main_mspi_status_poll_480826']:'poll'}
def word(cpu,address,value):cpu.mem_write(address,int(value).to_bytes(4,'little'))
def run(source,fixture):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob);cpu.mem_map(0x800000,0x10000)
 for addr,data in segs:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(MMIO,0x4000);cpu.mem_write(MMIO,bytes([0xa5])*0x4000)
 cpu.mem_write(HANDLE,bytes(0x8d0));word(cpu,HANDLE,fixture['magic']);word(cpu,HANDLE+4,1);word(cpu,HANDLE+16,8);cpu.mem_write(HANDLE+10,bytes([fixture['mode']]));cpu.mem_write(HANDLE+13,b'\x05');word(cpu,HANDLE+32,fixture['busy']==1);word(cpu,HANDLE+0x840,fixture['busy']==2);cpu.mem_write(HANDLE+0x82c,bytes([2 if fixture['busy']==3 else 0]))
 word(cpu,PIO,17);cpu.mem_write(PIO+4,bytes([2,1,fixture['direction'],1]));word(cpu,PIO+8,0x12340000|fixture['flags']);cpu.mem_write(PIO+12,bytes.fromhex('01009f000103'));cpu.mem_write(PIO+18,bytes([1 if fixture['busy']==4 else 0,0]));word(cpu,PIO+20,0x20007000)
 cpu.reg_write(R.UC_ARM_REG_SP,SP);cpu.reg_write(R.UC_ARM_REG_LR,RET|1);cpu.reg_write(R.UC_ARM_REG_R0,0 if fixture['null'] else HANDLE);cpu.reg_write(R.UC_ARM_REG_R1,PIO);cpu.reg_write(R.UC_ARM_REG_R2,1000000)
 events=[];helpers=source_helpers if source else native_helpers
 def hook(m,pc,size,user):
  if pc in helpers:
   name=helpers[pc];values=[m.reg_read(r) for r in (R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2,R.UC_ARM_REG_R3)]
   if name=='poll':values.append(int.from_bytes(m.mem_read(m.reg_read(R.UC_ARM_REG_SP),4),'little'))
   events.append([name,*values]);m.reg_write(R.UC_ARM_REG_R0,fixture['poll'] if name=='poll' else fixture['fifo']);m.reg_write(R.UC_ARM_REG_PC,m.reg_read(R.UC_ARM_REG_LR))
  elif pc==RET:m.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start((SOURCE if source else NATIVE)|1,RET+2,count=10000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'result':cpu.reg_read(R.UC_ARM_REG_R0),'events':events,'mmio':bytes(cpu.mem_read(MMIO,0x4000)).hex()}
fixtures=[]
for mode,direction,flags,busy,fifo,poll in itertools.product([0,10,11],[0,1,2],[0,3],[0,1,2,3,4],[0,7],[0,4]):
 fixtures.append(dict(mode=mode,direction=direction,flags=flags,busy=busy,fifo=fifo,poll=poll,magic=0x01bebebe,null=False))
fixtures.extend([dict(mode=0,direction=0,flags=0,busy=0,fifo=0,poll=0,magic=0x01bebebe,null=True),dict(mode=0,direction=0,flags=0,busy=0,fifo=0,poll=0,magic=0,null=False)])
for i,fixture in enumerate(fixtures):
 a=run(False,fixture);b=run(True,fixture);assert a==b,(i,fixture,{k:a[k] for k in ('result','events')},{k:b[k] for k in ('result','events')})
report={'status':'PASS_MAIN_MSPI_TRANSFER_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':hashlib.sha256(blob).hexdigest(),'source_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'g2/components/main/fal_norflash_mspi_transfer_candidates_20261013/transfer.c').read_bytes()).hexdigest(),'limits':['MMIO is synthetic RAM; FIFO movement and timed polling are injected equally.','No physical flash transfer or final image placement is qualified.']}
args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],report['cases'])
