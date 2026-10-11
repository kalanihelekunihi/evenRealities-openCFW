#!/usr/bin/env python3
"""Stock/source public-entry comparison for FlashDB next-sector address."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_next_sector_candidates_20261010/next_sector.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-next-sector.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_next_sector_addr',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_next_sector_addr')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;SEC=0x20051000;SP=0x200ff000
def run(source,case):
 sector_size,max_size,combined,addr,traversed=case
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 d=bytearray(b'\xa5'*64);s=bytearray(b'\xa5'*24)
 struct.pack_into('<II',d,12,sector_size,max_size)
 struct.pack_into('<I',s,4,addr);struct.pack_into('<I',s,12,combined)
 u.mem_write(DB,bytes(d));u.mem_write(SEC,bytes(s))
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(DB,SEC,traversed)):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.emu_start(entry if source else 0x544375,0x10000000,count=1000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(DB,64))==bytes(d) and bytes(u.mem_read(SEC,24))==bytes(s)
 return u.reg_read(UC_ARM_REG_R0)
cases=[]
for case in itertools.product((0,1,16,4096,0x100000,0xffffffff),
                              (0,1,4096,8192,0x100000,0xffffffff),
                              (0,1,2,3,0xffffffff),(0,1,4096,8192,0xfffffff0),
                              (0,1,4096,8192,0xfffffff0)):
 a,b=run(False,case),run(True,case)
 assert a==b,(case,hex(a),hex(b))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x544374..0x5443b0',
         'stock_body_sha256':hashlib.sha256(B[0x544374-0x437fe0:0x5443b0-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete 60-byte local calculation, including uint32 wrap, with synthetic but coherent DB/sector fields. M55 compiled code executes under Unicorn; no live database initialization or flash behavior.'}
(H/'next-sector-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS next_sector',len(cases))
