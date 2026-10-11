#!/usr/bin/env python3
"""Pinned FlashDB one-bit status decoder, stock/source public entry."""
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_get_status_candidates_20261010/get_status.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-get-status.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_get_status',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_get_status')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
TABLE=0x20050000;SP=0x200ff000
def run(source,table,count):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(TABLE,table)
 u.reg_write(UC_ARM_REG_R0,TABLE);u.reg_write(UC_ARM_REG_R1,count)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.emu_start(entry if source else 0x5858a9,0x10000000,count=1000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(TABLE,len(table)))==table
 return u.reg_read(UC_ARM_REG_R0)
cases=[]
for count in range(1,33):
 patterns=range(256) if count in (6,8,9,16,32) else (0,1,0x1f,0x3f,0x7f,0x80,0xfe,0xff)
 for p in patterns:
  for location in (0,count//8):
   t=bytearray(b'\xff'*8);t[location]=p;table=bytes(t)
   a,b=run(False,table,count),run(True,table,count)
   assert a==b,(count,p,location,a,b)
   cases.append((count,p,location))
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x5858a8..0x5858d8',
         'stock_body_sha256':hashlib.sha256(B[0x5858a8-0x437fe0:0x5858d8-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete one-bit status decode for positive counts 1..32. M55 compiled source executes in Unicorn; status_num=0 underflows in pinned C and is outside valid API domain.'}
(H/'get-status-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS get_status',len(cases))
