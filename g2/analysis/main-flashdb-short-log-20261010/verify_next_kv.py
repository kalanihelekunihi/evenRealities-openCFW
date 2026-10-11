#!/usr/bin/env python3
"""Pinned FlashDB get_next_kv_addr public-entry stock/source comparison."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_next_kv_candidates_20261010/next_kv.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-next-kv.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_next_kv_addr','-Wl,--defsym=g2_flashdb_find_next_kv_addr=0x543ee9',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_next_kv_addr')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;SEC=0x20051000;KV=0x20052000;SP=0x200ff000
def run(source,case):
 status,sec_size,start,crc,kv_len,scan_result=case
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 d=bytearray(b'\xa5'*64);s=bytearray(b'\xa5'*24);k=bytearray(b'\xa5'*88)
 struct.pack_into('<I',d,12,sec_size);s[1]=status;struct.pack_into('<I',s,4,0x1000)
 k[1]=crc;struct.pack_into('<I',k,8,kv_len);struct.pack_into('<I',k,80,start)
 u.mem_write(DB,bytes(d));u.mem_write(SEC,bytes(s));u.mem_write(KV,bytes(k))
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(DB,SEC,KV)):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,_):
  if pc==0x543ee8:
   args=tuple(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   assert args[0]==DB
   calls.append(args)
   emu.reg_write(UC_ARM_REG_R0,scan_result)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(entry if source else 0x543f8d,0x10000000,count=2000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(DB,64))==bytes(d) and bytes(u.mem_read(SEC,24))==bytes(s) and bytes(u.mem_read(KV,88))==bytes(k)
 return {'ret':u.reg_read(UC_ARM_REG_R0),'calls':calls}
cases=[]
for case in itertools.product((0,1,2,3),(0,1,4096,0xffffffff),
                              (0xffffffff,0x1000,0x1010,0x2000,0x2001,0xfffffff0),
                              (0,1),(0,1,16,4096),(0xffffffff,0x1000,0x1010,0x2000,0x2001)):
 a,b=run(False,case),run(True,case)
 assert a==b,(case,a,b)
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x543f8c..0x544000',
         'stock_body_sha256':hashlib.sha256(B[0x543f8c-0x437fe0:0x544000-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete local 116-byte routing with shared synthetic magic-word scanner. Coherent DB/sector/KV fixtures include uint32 edge cases; no physical flash or scanner proof. M4 scalar oracle, M55 archive compile separate.'}
(H/'next-kv-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS next_kv',len(cases))
