#!/usr/bin/env python3
"""Pinned FlashDB one-bit set/write status, valid-domain stock/source oracle."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_write_status_candidates_20261010/write_status.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-write-status.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_write_status','-Wl,--defsym=g2_flashdb_flash_write=0x585a53',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
TABLE=0x20050000;DB=0x20051000;SP=0x200ff000
def run(source,kind,count,index,sync,flash_result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(TABLE,b'\xa5'*16);u.mem_write(DB,b'\xa5'*64)
 if kind=='set':args=(TABLE,count,index)
 else:args=(DB,0x1000,TABLE,count)
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(r,v)
 stack=SP if kind=='set' else SP-8
 if kind=='write':u.mem_write(stack,struct.pack('<II',index,sync))
 u.reg_write(UC_ARM_REG_SP,stack);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,_):
  if pc==0x585a52:
   db,addr,data,n=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=emu.reg_read(UC_ARM_REG_SP);got_sync=struct.unpack('<I',bytes(emu.mem_read(sp,4)))[0]
   assert db==DB and n==1 and got_sync==sync,(kind,count,index,db,addr,data,n,got_sync)
   calls.append((addr,data-TABLE,bytes(emu.mem_read(data,1))[0],n,got_sync))
   emu.reg_write(UC_ARM_REG_R0,flash_result)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 entry=(syms['g2_flashdb_set_status'] if kind=='set' else syms['g2_flashdb_write_status']) if source else (0x585871 if kind=='set' else 0x5858d9)
 u.emu_start(entry,0x10000000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==stack
 return {'ret':u.reg_read(UC_ARM_REG_R0),'table':bytes(u.mem_read(TABLE,16)).hex(),
         'db':bytes(u.mem_read(DB,64)).hex(),'calls':calls}
cases=[]
for count in range(1,33):
 for index in range(count):
  for kind in ('set','write'):
   for sync,flash_result in ((0,0),(1,2),(1,0x102)) if kind=='write' else ((0,0),):
    a,b=run(False,kind,count,index,sync,flash_result),run(True,kind,count,index,sync,flash_result)
    assert a==b,(kind,count,index,sync,flash_result,a,b)
    cases.append((kind,count,index,sync,flash_result))
receipt={'status':'PASS','cases':len(cases),'stock_set':'0x585870..0x5858a8',
         'stock_write':'0x5858d8..0x585948',
         'stock_bodies_sha256':{label:hashlib.sha256(B[a-0x437fe0:b-0x437fe0]).hexdigest()
                                for label,a,b in [('set',0x585870,0x5858a8),('write',0x5858d8,0x585948)]},
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete set-status and valid-input write-status local paths; nonreturning FDB_ASSERT invalid index/null table excluded. Shared synthetic flash-write callback. M4 scalar oracle, M55 archive compile separate.'}
(H/'write-status-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS write_status',len(cases))
