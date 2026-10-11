#!/usr/bin/env python3
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent; R=H.parents[2]
src=R/'g2/components/main/flashdb_partition_read_candidates_20261010/partition_read.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
elf=H/'flashdb-partition-read.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,g2_flashdb_partition_read','-Wl,--defsym=g2_fal_device_for_partition=0x597d11',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f); entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_partition_read')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
PART=0x20050000;DEV=0x20051000;BUF=0x20052000;CALLBACK=0x10020000
regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
def run(source,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(PART+0x34,struct.pack('<II',c['offset'],c['length']))
 u.mem_write(DEV+0x28,struct.pack('<I',CALLBACK|1))
 u.mem_write(BUF,b'\xa5'*16)
 for reg,val in zip(regs,(PART,c['address'],BUF,c['size'])):u.reg_write(reg,val)
 u.reg_write(UC_ARM_REG_SP,0x200feffc);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,data):
  if pc==0x597d10:
   calls.append(['device',emu.reg_read(UC_ARM_REG_R0)])
   emu.reg_write(UC_ARM_REG_R0,DEV if c['device'] else 0)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
  elif pc==CALLBACK:
   calls.append(['read',*[emu.reg_read(reg) for reg in regs[:3]]])
   if c['mutate']:emu.mem_write(BUF,b'R'*16)
   emu.reg_write(UC_ARM_REG_R0,c['result']&0xffffffff)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x597d34)|1,0x10000000,count=1000)
 except Exception as exc:raise RuntimeError((source,c,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==0x200feffc
 return dict(calls=calls,result=u.reg_read(UC_ARM_REG_R0),buffer=bytes(u.mem_read(BUF,16)).hex())
cases=[]
for length,address,size,offset,device in itertools.product(
 (0,1,16,0xffffffff),(0,1,15,16,0xfffffffe),(0,1,2,16,0xffffffff),
 (0,0x12345678,0xffffffff),(False,True)):
 c=dict(length=length,address=address,size=size,offset=offset,device=device,result=0x80000000,mutate=False)
 a,b=run(False,c),run(True,c)
 if a!=b:raise AssertionError((c,a,b))
 cases.append(c)
for result,mutate in itertools.product((0,1,0x7fffffff,0x80000000,0xffffffff),(False,True)):
 c=dict(length=16,address=3,size=8,offset=0x12345678,device=True,result=result,mutate=mutate)
 a,b=run(False,c),run(True,c)
 if a!=b:raise AssertionError((c,a,b))
 cases.append(c)
receipt=dict(status='PASS',cases=len(cases),stock_body_sha256=hashlib.sha256(blob[0x597d34-0x437fe0:0x597d72-0x437fe0]).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='M55 compile and Unicorn scalar execution with shared synthetic FAL device lookup and read callback; no real FAL table, flash device, logging, invalid pointers or hardware proof.')
(H/'partition-read-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS partition_read',len(cases))
