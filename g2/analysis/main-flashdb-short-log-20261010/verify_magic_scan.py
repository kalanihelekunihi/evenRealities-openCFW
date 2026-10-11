#!/usr/bin/env python3
"""Pinned FlashDB magic-word scanner public-entry stock/source comparison."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_magic_scan_candidates_20261010/magic_scan.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-magic-scan.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_find_next_kv_addr',
     '-Wl,--defsym=g2_flashdb_sector_cache_lookup=0x543cc1',
     '-Wl,--defsym=g2_flashdb_flash_read=0x585a13',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_find_next_kv_addr')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;SEC=0x20051000;SP=0x200ff000
MAGIC=b'KV00'
def run(source,case):
 start,span,position,cache_mode,fail_read=case
 end=(start+span)&0xffffffff
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 d=bytearray(b'\xa5'*2304);struct.pack_into('<I',d,12,4096)
 s=bytearray(b'\xa5'*24);struct.pack_into('<I',s,20,start if cache_mode==2 else 0xabcdef00)
 u.mem_write(DB,bytes(d));u.mem_write(SEC,bytes(s))
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(DB,start,end)):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 flash=bytearray(b'\xff'*160)
 if position>=0:flash[position:position+4]=MAGIC
 calls=[];reads=[0]
 def ret(value):emu.reg_write(UC_ARM_REG_R0,value);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 def hook(emu_,pc,size,_):
  nonlocal emu
  emu=emu_
  if pc==0x543cc0:
   db,sec=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1))
   assert db==DB and sec==(start//4096)*4096
   calls.append(('cache',sec))
   ret(SEC if cache_mode else 0);return
  if pc==0x585a12:
   db,addr,buf,n=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   assert db==DB and n==32
   calls.append(('read',addr))
   reads[0]+=1
   offset=(addr-start)&0xffffffff
   assert offset+32<=len(flash),(case,offset)
   emu.mem_write(buf,bytes(flash[offset:offset+32]))
   ret(2 if reads[0]==fail_read else 0);return
 emu=None
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(entry if source else 0x543ee9,0x10000000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(DB,2304))==bytes(d) and bytes(u.mem_read(SEC,24))==bytes(s)
 return {'ret':u.reg_read(UC_ARM_REG_R0),'calls':calls}

cases=[]
for case in itertools.product((0x1000,0x1010,0x1ff0,0xfffffff0),
                              (0,31,32,33,60,90,120),(-1,0,3,4,27,28,31,40,57,84),
                              (0,1,2),(0,1,2,3)):
 a,b=run(False,case),run(True,case)
 assert a==b,(case,a,b)
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x543ee8..0x543f8c',
         'stock_body_sha256':hashlib.sha256(B[0x543ee8-0x437fe0:0x543f8c-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete local 164-byte scanner with coherent synthetic cache and flash-read callbacks. Includes read failure and byte-window positions; no sector-cache implementation or physical flash proof. M4 scalar oracle, M55 archive compile separate.'}
(H/'magic-scan-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS magic_scan',len(cases))
