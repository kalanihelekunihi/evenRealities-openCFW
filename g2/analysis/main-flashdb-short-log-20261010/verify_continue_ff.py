#!/usr/bin/env python3
"""Pinned FlashDB FF-run continuation stock/source public-entry oracle."""
from pathlib import Path
import hashlib,itertools,json,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_continue_ff_candidates_20261010/continue_ff.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-continue-ff.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_continue_ff_addr','-Wl,--defsym=g2_flashdb_flash_read=0x585a13',str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_continue_ff_addr')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;SP=0x200ff000
def pattern(kind):
 if kind==0:return b'\x00'*128
 if kind==1:return b'\xff'*128
 if kind==2:return b'\x00'*16+b'\xff'*112
 if kind==3:return b'\xff'*16+b'\x00'*112
 if kind==4:return b'\x00'*31+b'\xff'*33+b'\x00'*64
 if kind==5:return b'\xff'*31+b'\x00'*33+b'\xff'*64
 if kind==6:return bytes(0xff if i%3==0 else 0 for i in range(128))
 return bytes(0xff if i%29==0 else 0 for i in range(128))
def run(source,case):
 start,length,kind,fail_read=case;end=(start+length)&0xffffffff;flash=pattern(kind)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(DB,b'\xa5'*64)
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(DB,start,end)):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,_):
  if pc==0x585a12:
   from unicorn.arm_const import UC_ARM_REG_R3
   db,addr,buf,n=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   offset=(addr-start)&0xffffffff
   assert db==DB and n<=32 and offset+n<=128,(case,db,addr,n,offset)
   calls.append((addr,n))
   emu.mem_write(buf,flash[offset:offset+n]);emu.reg_write(UC_ARM_REG_R0,2 if len(calls)==fail_read else 0)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(entry if source else 0x5859a1,0x10000000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(DB,64))==b'\xa5'*64
 return {'ret':u.reg_read(UC_ARM_REG_R0),'calls':calls}
cases=[]
for case in itertools.product((0x1000,0x1010,0x1ff0),
                              (0,1,16,31,32,33,63,64,65,96,127,128),range(8),(0,1,2,3)):
 a,b=run(False,case),run(True,case)
 assert a==b,(case,a,b)
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x5859a0..0x585a12',
         'stock_body_sha256':hashlib.sha256(B[0x5859a0-0x437fe0:0x585a12-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete local 114-byte FF-run scanner over bounded valid flash ranges; uint32 address wrap outside accepted FAL range is excluded. Shared synthetic flash-read callback; read errors are ignored by stock. M4 scalar oracle, M55 archive compile separate; no physical flash proof.'}
(H/'continue-ff-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS continue_ff',len(cases))
