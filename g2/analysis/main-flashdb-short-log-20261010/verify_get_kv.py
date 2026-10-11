#!/usr/bin/env python3
"""Bounded pinned FlashDB get_kv stock/source entry comparison."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/flashdb_get_kv_candidates_20261010/get_kv.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x5444f4-0x437fe0:0x54454a-0x437fe0]
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
elf=H/'flashdb-get-kv.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_get_kv',
     '-Wl,--defsym=g2_flashdb_find_kv=0x54449b',
     '-Wl,--defsym=g2_flashdb_flash_read=0x585a13',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f)
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_get_kv')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']

DB=0x20050000;KEY=0x20052000;BUF=0x20053000;LEN=0x20054000;STACK=0x207ff000
def run(source,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
 u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x800000)
 u.mem_write(LEN,struct.pack('<I',0xdeadbeef))
 u.mem_write(BUF,b'\xa5'*32)
 u.mem_write(STACK,struct.pack('<I',LEN if case['value_pointer'] else 0))
 for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                  (DB,KEY,BUF if case['buffer'] else 0,case['request'])):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,STACK);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def ret(v):
  u.reg_write(UC_ARM_REG_R0,v)
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(emu,pc,size,data):
  if pc==0x54449a:
   a,b,c=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
   assert a==DB and b==KEY and 0x207f0000<c<STACK
   calls.append(['find',a,b])
   emu.mem_write(c+12,struct.pack('<I',case['value_len']))
   emu.mem_write(c+84,struct.pack('<I',0x12345678))
   ret(case['found']);return
  if pc==0x585a12:
   calls.append(['read',*[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]])
   ret(case['read_result']);return
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x5444f4)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,case,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==STACK
 return {'calls':calls,'return':u.reg_read(UC_ARM_REG_R0),
         'length':struct.unpack('<I',u.mem_read(LEN,4))[0],
         'buffer':bytes(u.mem_read(BUF,32)).hex()}

cases=[]
for found,request,value_len,buffer,value_pointer,read_result in itertools.product(
        (0,1,0x100),(0,1,20,0xffffffff),(0,1,20,0xfffffffe),(0,1),(0,1),(0,7)):
 case=dict(found=found,request=request,value_len=value_len,buffer=buffer,
           value_pointer=value_pointer,read_result=read_result)
 a,b=run(False,case),run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_body_sha256':hashlib.sha256(body).hexdigest(),
         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'compile':cmd,
         'limits':'M4 scalar code executes in Unicorn because this emulator rejects M55 CSEL; M55 source compilation is separately established by the Main archive build. Pinned local 86-byte body only; synthetic find_kv and flash-read callbacks, no real flash data or database initialization.'}
(H/'get-kv-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS get_kv',len(cases))
