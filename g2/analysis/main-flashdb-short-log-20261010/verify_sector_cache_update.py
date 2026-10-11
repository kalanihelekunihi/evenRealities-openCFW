#!/usr/bin/env python3
"""Pinned FlashDB sector-cache update stock/source public-entry oracle."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_sector_cache_update_candidates_20261010/sector_cache_update.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-sector-cache-update.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_update_sector_cache',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_update_sector_cache')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;SEC=0x20051000;SP=0x200ff000;TARGET=0x12345678
def fixture(mode,index,valid):
 d=bytearray(b'\xa5'*2304)
 for i in range(64):struct.pack_into('<I',d,680+24*i+4,0x10000+i)
 if mode in ('hit','duplicate'):struct.pack_into('<I',d,680+24*index+4,TARGET)
 if mode=='duplicate':struct.pack_into('<I',d,680+24*63+4,TARGET)
 if mode in ('empty','two_empty'):struct.pack_into('<I',d,680+24*index+4,0xffffffff)
 if mode=='two_empty':struct.pack_into('<I',d,680+24*63+4,0xffffffff)
 s=bytearray(bytes((i*17+3)&0xff for i in range(24)));s[0]=valid;struct.pack_into('<I',s,4,TARGET)
 return bytes(d),bytes(s)
def run(source,case):
 mode,index,valid=case;before,sector=fixture(*case)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(DB,before);u.mem_write(SEC,sector)
 u.reg_write(UC_ARM_REG_R0,DB);u.reg_write(UC_ARM_REG_R1,SEC)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.emu_start(entry if source else 0x543c49,0x10000000,count=5000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(SEC,24))==sector
 return bytes(u.mem_read(DB,2304))
cases=[]
for case in itertools.product(('hit','duplicate','empty','two_empty','full'),range(64),(0,1)):
 a,b=run(False,case),run(True,case)
 if a!=b:
  i=next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)
  raise AssertionError((case,i,a[i:i+16].hex(),b[i:i+16].hex()))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x543c48..0x543cc0',
         'stock_body_sha256':hashlib.sha256(B[0x543c48-0x437fe0:0x543cc0-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete 120-byte local cache update with synthetic initialized 64-row table. M4 scalar oracle because Unicorn rejects M55 instructions; M55 archive compile separate. No production DB initialization or flash-state proof.'}
(H/'sector-cache-update-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS sector_cache_update',len(cases))
