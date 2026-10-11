#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/flashdb_db_path_candidates_20261010/db_path.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x585c94-0x437fe0:0x585ca4-0x437fe0]
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
elf=H/'flashdb-db-path.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_db_path',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True)
with elf.open('rb') as f:
 e=ELFFile(f)
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_db_path')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,flag,ptr):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
 u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(0x20050008,struct.pack('<I',ptr))
 u.mem_write(0x20050019,bytes([flag]))
 u.reg_write(UC_ARM_REG_R0,0x20050000)
 u.reg_write(UC_ARM_REG_SP,0x200ff000)
 u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.emu_start((entry if source else 0x585c94)|1,0x10000000,count=50)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20050000,32))
cases=0
for flag in range(256):
 for ptr in (0,0x20051000,0xfffffffc,0xffffffff):
  a,b=run(False,flag,ptr),run(True,flag,ptr)
  if a!=b:raise AssertionError((flag,hex(ptr),a,b))
  cases+=1
receipt={'status':'PASS','cases':cases,'stock_body_sha256':hashlib.sha256(body).hexdigest(),
         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'compile':cmd,
         'limits':'Bounded 16-byte local body with synthetic readable database fields; source ownership of database rows and path string remains external.'}
(H/'db-path-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS db_path',cases)
