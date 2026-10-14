#!/usr/bin/env python3
"""Bounded native/source Main NOR entry and exit wrapper comparison."""
import argparse,hashlib,itertools,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4];BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);args=p.parse_args()
with args.elf.open('rb') as f:
 elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']];syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
NATIVE={'enter':0x470f68,'exit':0x470e90};SOURCE={'enter':syms['g2_norflash_enter_470f68'],'exit':syms['g2_norflash_exit_470e90']};RET=0x200ff000;SP=0x200fe000;HANDLE=0x20074544
NATIVE_HELPERS={0x470d7c:'set',0x46f6ba:'mode',0x4c0f78:'transfer',0x439c04:'copy',0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'simple'}
SOURCE_HELPERS={syms['g2_norflash_set_serial_470d7c']:'set',syms['g2_norflash_mode_select_46f6ba']:'mode',syms['g2_norflash_config_transfer_4c0f78']:'transfer',syms['audio_uart_checksum_copy']:'copy',syms['g2_flashdb_candidate_flags']:'flags',syms['g2_flashdb_candidate_log']:'extended',syms['audio_log_simple']:'simple'}
def cstring(cpu,address):
 data=bytearray()
 for i in range(256):
  b=cpu.mem_read(address+i,1)[0]
  if b==0:return data.decode()
  data.append(b)
 raise AssertionError('unterminated')
def run(kind,source,flags,set_status,transfer_status,handle):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob);cpu.mem_map(0x800000,0x10000)
 for addr,data in segs:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_write(0x200007f0,bytes(range(64)));cpu.mem_write(HANDLE,handle.to_bytes(4,'little'));cpu.mem_write(syms['g2_norflash_controller_handle_20074544'],handle.to_bytes(4,'little'));cpu.reg_write(R.UC_ARM_REG_SP,SP);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 events=[];helpers=SOURCE_HELPERS if source else NATIVE_HELPERS
 def hook(m,pc,size,user):
  if pc in helpers:
   name=helpers[pc];r0=m.reg_read(R.UC_ARM_REG_R0);r1=m.reg_read(R.UC_ARM_REG_R1);r2=m.reg_read(R.UC_ARM_REG_R2);r3=m.reg_read(R.UC_ARM_REG_R3);stack=m.reg_read(R.UC_ARM_REG_SP);result=0
   if name=='set':events.append(['set',bytes(m.mem_read(r0,24)).hex()]);result=set_status
   elif name=='mode':events.append(['mode',r0])
   elif name=='transfer':events.append(['transfer',r0,r1,m.mem_read(r2,1)[0]]);result=transfer_status
   elif name=='copy':events.append(['copy',r2,bytes(m.mem_read(r1,r2)).hex()]);m.mem_write(r0,bytes(m.mem_read(r1,r2)))
   elif name=='flags':events.append(['flags']);result=flags
   elif name=='extended':events.append(['extended',r0,cstring(m,r1),cstring(m,r2),cstring(m,r3),int.from_bytes(m.mem_read(stack,4),'little'),cstring(m,int.from_bytes(m.mem_read(stack+4,4),'little'))])
   elif name=='simple':events.append(['simple',r0,cstring(m,r1),cstring(m,r2)])
   m.reg_write(R.UC_ARM_REG_R0,result);m.reg_write(R.UC_ARM_REG_PC,m.reg_read(R.UC_ARM_REG_LR))
  elif pc==RET:m.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start((SOURCE if source else NATIVE)[kind]|1,RET+2,count=3000);assert cpu.reg_read(R.UC_ARM_REG_PC)==RET,(kind,source)
 return {'events':events,'shared_config':bytes(cpu.mem_read(0x200007f0,64)).hex()}
cases=0
for kind,flags,set_status,transfer_status,handle in itertools.product(('enter','exit'),(0,1,2,3,4,7),(0,3),(0,5),(0,0x20070000)):
 native=run(kind,False,flags,set_status,transfer_status,handle);source=run(kind,True,flags,set_status,transfer_status,handle);assert native==source,(kind,flags,set_status,transfer_status,handle,native,source);cases+=1
report={'status':'PASS_MAIN_NOR_ENTRY_EXIT_BOUNDED_NATIVE_SOURCE','cases':cases,'stock_sha256':hashlib.sha256(blob).hexdigest(),'source_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'limits':['Mode validator, 24-bit configuration transfer, mode selection, copy and logging are injected equally; exact outer control and arguments are compared.','The configuration transfer consumes one payload byte in the stock command-24 branch; hardware and full-image SRAM ownership remain open.']}
args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],report['cases'])
