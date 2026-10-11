#!/usr/bin/env python3
"""Bounded stock/source public-entry oracle for FlashDB fdb_kv_get_blob."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/flashdb_get_blob_candidates_20261010/get_blob.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x54454a-0x437fe0:0x5445b2-0x437fe0]
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
elf=H/'flashdb-get-blob.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_candidate_get_blob',
     '-Wl,--defsym=g2_flashdb_get_kv=0x5444f5',
     '-Wl,--defsym=g2_flashdb_db_path=0x585c95',
     '-Wl,--defsym=g2_flashdb_print=0x4733ef',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f)
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_candidate_get_blob')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']

DB=0x20050000;BLOB=0x20051000
def run(source,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
 u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x800000)
 u.mem_write(DB,struct.pack('<I',0x20053000))
 u.mem_write(DB+24,bytes([case['init']]))
 u.mem_write(DB+28,struct.pack('<II',0x10002001 if case['lock'] else 0,0x10002011 if case['unlock'] else 0))
 u.mem_write(BLOB,struct.pack('<5I',0x20054000,case['size'],0xdead,0xbeef,0xabcdef01))
 u.mem_write(0x20053000,b'old-name\0')
 u.mem_write(0x20053100,b'new-name\0')
 u.mem_write(0x20053200,b'last-name\0')
 u.mem_write(0x20052000,b'KV\0')
 u.reg_write(UC_ARM_REG_SP,0x207ff000);u.reg_write(UC_ARM_REG_LR,0x10000001)
 for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(DB,0x20055000,BLOB)):u.reg_write(reg,val)
 calls=[]
 def ret(value):
  u.reg_write(UC_ARM_REG_R0,value)
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def cstr(a):return bytes(u.mem_read(a,128)).split(b'\0')[0].decode()
 def hook(emu,pc,size,data):
  if pc==0x4733ee:
   fmt=cstr(emu.reg_read(UC_ARM_REG_R0))
   args=[]
   if fmt=='[%s][%s] ':args=[cstr(emu.reg_read(UC_ARM_REG_R1)),cstr(emu.reg_read(UC_ARM_REG_R2))]
   elif fmt=="Error: KV (%s) isn't initialize OK.\n":args=[cstr(emu.reg_read(UC_ARM_REG_R1))]
   calls.append(['print',fmt,args]);
   if fmt=='[%s][%s] ' and case['mutate_name_after_pair']:emu.mem_write(DB,struct.pack('<I',0x20053200))
   ret(0);return
  if pc==0x585c94:
   calls.append(['db_name',emu.reg_read(UC_ARM_REG_R0)])
   if case['mutate_name_at_dbname']:emu.mem_write(DB,struct.pack('<I',0x20053100))
   ret(0x20052000);return
  if pc==0x10002000:
   calls.append(['lock',emu.reg_read(UC_ARM_REG_R0)])
   if case['mutate_unlock']:emu.mem_write(DB+32,struct.pack('<I',0))
   ret(0);return
  if pc==0x10002010:calls.append(['unlock',emu.reg_read(UC_ARM_REG_R0)]);ret(0);return
  if pc==0x5444f4:
   fifth=struct.unpack('<I',emu.mem_read(emu.reg_read(UC_ARM_REG_SP),4))[0]
   calls.append(['get_kv',emu.reg_read(UC_ARM_REG_R0),emu.reg_read(UC_ARM_REG_R1),emu.reg_read(UC_ARM_REG_R2),emu.reg_read(UC_ARM_REG_R3),fifth])
   emu.mem_write(fifth,struct.pack('<I',0x11223344))
   if case['mutate_unlock']:emu.mem_write(DB+32,struct.pack('<I',0))
   ret(case['read_result']);return
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x54454a)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,case,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return {'calls':calls,'return':u.reg_read(UC_ARM_REG_R0),
         'saved_len':struct.unpack('<I',u.mem_read(BLOB+16,4))[0],
         'name':struct.unpack('<I',u.mem_read(DB,4))[0]}

cases=[]
for init,lock,unlock,mutate_name_at_dbname,mutate_name_after_pair,mutate_unlock,read_result,size in itertools.product(
        (0,1,255),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1,0xffffffff),(0,1,0xffff)):
 case=dict(init=init,lock=lock,unlock=unlock,mutate_name_at_dbname=mutate_name_at_dbname,
           mutate_name_after_pair=mutate_name_after_pair,mutate_unlock=mutate_unlock,
           read_result=read_result,size=size)
 a,b=run(False,case),run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_body_sha256':hashlib.sha256(body).hexdigest(),
         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'compile':cmd,
         'limits':'Pinned local body with synthetic get_kv, db-name, print, lock/unlock callbacks and initialized RAM; no complete lookup/FAL/logger or DB object lifecycle.'}
(H/'get-blob-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS get_blob',len(cases))
