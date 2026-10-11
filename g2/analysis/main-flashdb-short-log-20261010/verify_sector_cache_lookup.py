#!/usr/bin/env python3
"""Pinned FlashDB sector cache lookup, stock/source public-entry comparison."""
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_sector_cache_lookup_candidates_20261010/sector_cache_lookup.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-sector-cache-lookup.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_sector_cache_lookup',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_sector_cache_lookup')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;SP=0x200ff000;TARGET=0x12345678
def run(source,mode,index):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 d=bytearray(b'\xa5'*2304)
 for i in range(64):struct.pack_into('<I',d,680+24*i+4,0x10000+i)
 if mode in ('hit','duplicate'):struct.pack_into('<I',d,680+24*index+4,TARGET)
 if mode=='duplicate':struct.pack_into('<I',d,680+24*63+4,TARGET)
 u.mem_write(DB,bytes(d));u.reg_write(UC_ARM_REG_R0,DB);u.reg_write(UC_ARM_REG_R1,TARGET)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.emu_start(entry if source else 0x543cc1,0x10000000,count=2000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(DB,2304))==bytes(d)
 return u.reg_read(UC_ARM_REG_R0)
cases=[]
for mode in ('miss','hit','duplicate'):
 for index in range(64):
  a,b=run(False,mode,index),run(True,mode,index)
  assert a==b,(mode,index,hex(a),hex(b))
  assert a==(DB+680+24*index if mode in ('hit','duplicate') else 0)
  cases.append((mode,index))
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x543cc0..0x543cec',
         'stock_body_sha256':hashlib.sha256(B[0x543cc0-0x437fe0:0x543cec-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete 44-byte linear lookup with coherent synthetic 64-row table. M55 compiled code executes in Unicorn; no database initialization or persistent state claim.'}
(H/'sector-cache-lookup-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS sector_cache_lookup',len(cases))
