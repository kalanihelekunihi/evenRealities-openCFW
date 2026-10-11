#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/flashdb_flash_write_candidates_20261010/flash_write.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x585a52-0x437fe0:0x585a72-0x437fe0]
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
elf=H/'flashdb-flash-write.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_flash_write',
     '-Wl,--defsym=g2_flashdb_partition_write=0x597d73',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f)
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_flash_write')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;BUF=0x20052000
def run(source,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
 u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(DB+8,struct.pack('<I',case['partition']))
 u.mem_write(DB+25,bytes([case['mode']]))
 u.mem_write(BUF,b'\xa5'*16)
 for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                    (DB,case['address'],BUF,case['size'])):u.reg_write(reg,val)
 u.mem_write(0x200feffc,struct.pack('<I',case['sync']))
 u.reg_write(UC_ARM_REG_SP,0x200feffc);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,data):
  if pc!=0x597d72:return
  calls.append([emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)])
  if case['write']:emu.mem_write(BUF,b'X'*16)
  emu.reg_write(UC_ARM_REG_R0,case['fal_result']&0xffffffff)
  emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x585a52)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,case,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==0x200feffc
 return {'calls':calls,'return':u.reg_read(UC_ARM_REG_R0),'buffer':bytes(u.mem_read(BUF,16)).hex()}
cases=[]
for mode,fal_result in itertools.product(range(256),(0,1,0x7fffffff,0x80000000,0xffffffff)):
 case=dict(mode=mode,fal_result=fal_result,partition=0x20070000,address=0x12345678,size=16,write=True,sync=0)
 a,b=run(False,case),run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases.append(case)
for partition,address,size,write in itertools.product((0,0x20070000,0xffffffff),(0,0x12345678),(0,1,16,0xffffffff),(False,True)):
 case=dict(mode=0,fal_result=0xffffffff,partition=partition,address=address,size=size,write=write,sync=0)
 a,b=run(False,case),run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases.append(case)
for sync in (0,1,0xffffffff):
 case=dict(mode=0,fal_result=0x80000000,partition=0x20070000,address=0x12345678,size=16,write=False,sync=sync)
 a,b=run(False,case),run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_body_sha256':hashlib.sha256(body).hexdigest(),
         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'compile':cmd,
         'limits':'Pinned local 32-byte FAL-mode body with synthetic fal_partition_write, sync ignored, no physical flash, file-mode support or database initialization.'}
(H/'flash-write-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS flash_write',len(cases))
