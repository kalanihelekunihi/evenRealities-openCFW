#!/usr/bin/env python3
"""Bounded native/source Main MSPI enable/disable comparison."""
import argparse,hashlib,itertools,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4];BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);args=p.parse_args()
with args.elf.open('rb') as f:
 elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']];syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
NATIVE={'enable':0x4c0e1e,'disable':0x4c0ea8};SOURCE={'enable':syms['g2_norflash_enable_mspi_4c0e1e'],'disable':syms['g2_norflash_disable_mspi_4c0ea8']};NH={0x4bfc5a:'init',0x4bfd62:'cq_disable',0x4bfc86:'term',0x4807a0:'delay'};SH={syms['g2_main_mspi_cq_init_4bfc5a']:'init',syms['g2_main_mspi_cq_disable_4bfd62']:'cq_disable',syms['g2_main_mspi_cq_term_4bfc86']:'term',syms['audio_delay_us_selected']:'delay'};HANDLE=0x20006000;MMIO=0x40060000;RET=0x200ff000;SP=0x200fe000
def word(cpu,address,value):cpu.mem_write(address,int(value).to_bytes(4,'little'))
def run(kind,source,fx):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob);cpu.mem_map(0x800000,0x10000)
 for addr,data in segs:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(MMIO,0x4000);cpu.mem_write(HANDLE,bytes([0xcc])*0x8d0);cpu.mem_write(MMIO,bytes([0xa5])*0x4000)
 word(cpu,HANDLE,fx['magic']);word(cpu,HANDLE+4,1);word(cpu,HANDLE+20,256);word(cpu,HANDLE+24,fx['cq']);word(cpu,HANDLE+28,0xaabbccdd);word(cpu,HANDLE+32,1 if fx['busy']==1 else 0);word(cpu,HANDLE+0x840,1 if fx['busy']==2 else 0);word(cpu,HANDLE+0x8cc,17);cpu.mem_write(HANDLE+8,bytes([fx['configured']]));word(cpu,MMIO+0x1000+0x90,fx['delayed']);cpu.reg_write(R.UC_ARM_REG_SP,SP);cpu.reg_write(R.UC_ARM_REG_LR,RET|1);cpu.reg_write(R.UC_ARM_REG_R0,0 if fx['null'] else HANDLE)
 events=[];helpers=SH if source else NH
 def hook(m,pc,size,user):
  if pc in helpers:
   name=helpers[pc];values=[m.reg_read(r) for r in (R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2)];events.append([name,*values[:(3 if name=='init' else 1)]]);m.reg_write(R.UC_ARM_REG_R0,fx['cq_status'] if name=='cq_disable' else 0);m.reg_write(R.UC_ARM_REG_PC,m.reg_read(R.UC_ARM_REG_LR))
  elif pc==RET:m.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start((SOURCE if source else NATIVE)[kind]|1,RET+2,count=5000);assert cpu.reg_read(R.UC_ARM_REG_PC)==RET,(kind,source,fx)
 return {'result':cpu.reg_read(R.UC_ARM_REG_R0),'events':events,'handle':bytes(cpu.mem_read(HANDLE,0x8d0)).hex(),'mmio':bytes(cpu.mem_read(MMIO,0x4000)).hex()}
fixtures=[]
for kind,magic,configured,cq,busy,cq_status,delayed in itertools.product(('enable','disable'),(0,0x01bebebe,0x03bebebe),(0,1),(0,8),(0,1,2),(0,7),(0,1)):
 fixtures.append((kind,dict(magic=magic,configured=configured,cq=cq,busy=busy,cq_status=cq_status,delayed=delayed,null=False)))
for kind in ('enable','disable'):fixtures.append((kind,dict(magic=0,configured=0,cq=0,busy=0,cq_status=0,delayed=0,null=True)))
for i,(kind,fx) in enumerate(fixtures):
 native=run(kind,False,fx);source=run(kind,True,fx);assert native==source,(i,kind,fx,{k:native[k] for k in ('result','events')},{k:source[k] for k in ('result','events')})
report={'status':'PASS_MAIN_MSPI_ENABLE_DISABLE_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':hashlib.sha256(blob).hexdigest(),'source_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'limits':['Synthetic MMIO and injected CQ init/disable/term and delay calls bound the comparison.','No physical MSPI operation, timing or complete Main image is verified.']}
args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],report['cases'])
