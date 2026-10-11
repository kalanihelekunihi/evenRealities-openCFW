#!/usr/bin/env python3
"""Pinned FlashDB read_sector_info stock/source complete local routing oracle."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_read_sector_candidates_20261010/read_sector.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-read-sector.elf'
defs={'g2_flashdb_sector_cache_lookup':0x543cc1,'g2_flashdb_flash_read':0x585a13,
      'g2_flashdb_get_status':0x5858a9,'g2_flashdb_read_kv':0x544001,
      'g2_flashdb_next_kv_addr':0x543f8d,'g2_flashdb_continue_ff_addr':0x5859a1,
      'g2_flashdb_update_sector_cache':0x543c49}
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_read_sector_info',*[f'-Wl,--defsym={k}={v:#x}' for k,v in defs.items()],str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_read_sector_info')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;SECTOR=0x20051000;CACHE=0x20052000;SP=0x200ff000;ADDR=0x1000
STATUS_BYTES=(0xff,0x7f,0x3f,0x1f)
def run(source,case):
 cache_mode,traversal,header_mode,store,kv_mode,rows,ff_mode=case
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 d=bytearray(b'\xa5'*2304);struct.pack_into('<I',d,12,4096)
 initial=bytes(b'\xa5'*24);cache=bytearray(b'\x63'*24);struct.pack_into('<II',cache,4,ADDR,0x30424446)
 struct.pack_into('<I',cache,20,0xffffffff if cache_mode==2 else 0x1100)
 header=bytearray(16);header[0]=STATUS_BYTES[store];header[1]=STATUS_BYTES[2]
 struct.pack_into('<I',header,4,0x30424446 if header_mode!=1 else 0x12345678)
 struct.pack_into('<I',header,8,0xffffffff if header_mode!=2 else 1)
 u.mem_write(DB,bytes(d));u.mem_write(SECTOR,initial);u.mem_write(CACHE,bytes(cache))
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(DB,ADDR,SECTOR,traversal)):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[];cache_calls=[0];readkv_calls=[0]
 def ret(emu,value):emu.reg_write(UC_ARM_REG_R0,value);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 def hook(emu,pc,size,_):
  if pc==0x543cc0:
   db,addr=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1))
   assert (db,addr)==(DB,ADDR)
   cache_calls[0]+=1;calls.append(('cache',cache_calls[0]))
   ret(emu,CACHE if cache_mode in (1,2) else 0);return
  if pc==0x585a12:
   db,addr,buf,n=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   assert (db,addr,n)==(DB,ADDR,16),(case,db,addr,n)
   emu.mem_write(buf,bytes(header));calls.append(('read_header',));ret(emu,0);return
  if pc==0x544000:
   db,kv=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1))
   assert db==DB
   readkv_calls[0]+=1
   start=struct.unpack('<I',bytes(emu.mem_read(kv+80,4)))[0]
   calls.append(('readkv',start))
   status,crc=(2,1) if kv_mode==0 else (2,0) if kv_mode==1 else (1,0) if kv_mode==2 else (5,0)
   emu.mem_write(kv,bytes([status,crc]))
   emu.mem_write(kv+8,struct.pack('<I',32))
   ret(emu,0);return
  if pc==0x543f8c:
   db,sec,kv=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   assert db==DB and sec==SECTOR
   calls.append(('nextkv',readkv_calls[0]))
   ret(emu,ADDR+16+32*readkv_calls[0] if readkv_calls[0]<rows else 0xffffffff);return
  if pc==0x5859a0:
   db,start,end=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   assert db==DB and end==ADDR+4096
   calls.append(('continueff',start,end))
   ret(emu,start if ff_mode==0 else start+16);return
  if pc==0x543c48:
   db,sec=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1))
   assert (db,sec)==(DB,SECTOR)
   calls.append(('update_cache',));ret(emu,0);return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(entry if source else 0x54418f,0x10000000,count=30000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 return {'ret':u.reg_read(UC_ARM_REG_R0),'sector':bytes(u.mem_read(SECTOR,24)).hex(),
         'cache':bytes(u.mem_read(CACHE,24)).hex(),'db':bytes(u.mem_read(DB,2304)).hex(),'calls':calls}

cases=[]
for case in itertools.product((0,1,2),(0,1),(0,1,2),(0,1,2,3),(0,1,2,3),(1,2),(0,1)):
 a,b=run(False,case),run(True,case)
 if a!=b:
  for key in a:
   if a[key]!=b[key]:
    if key in ('sector','cache','db'):
     aa=bytes.fromhex(a[key]);bb=bytes.fromhex(b[key]);i=next(i for i,(x,y) in enumerate(zip(aa,bb)) if x!=y)
     raise AssertionError((case,key,i,aa[i:i+16].hex(),bb[i:i+16].hex()))
    raise AssertionError((case,key,a[key],b[key]))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x54418e..0x544374',
         'stock_body_sha256':hashlib.sha256(B[0x54418e-0x437fe0:0x544374-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete valid-input 486-byte local body with coherent synthetic cache/header/KV/FF/update children. FDB_ASSERT unaligned/null fatal paths excluded. M4 scalar oracle, M55 archive compile separate; no persistent flash/cache-state proof.'}
(H/'read-sector-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS read_sector',len(cases))
