#!/usr/bin/env python3
"""Pinned FlashDB read_kv complete public-entry stock/source comparison."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess,zlib
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_read_kv_candidates_20261010/read_kv.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-read-kv.elf'
defs={'g2_flashdb_flash_read':0x585a13,'g2_flashdb_get_status':0x5858a9,
      'g2_flashdb_write_status':0x5858d9,'g2_flashdb_crc32':0x585841,
      'g2_flashdb_db_path':0x585c95,'g2_flashdb_print':0x4733ef}
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_read_kv',*[f'-Wl,--defsym={k}={v:#x}' for k,v in defs.items()],str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_read_kv')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;KV=0x20052000;SP=0x200ff000;PATH=0x20054000;DBNAME=0x20055000
def fixture(case):
 length,name_len,value_len,status,crc_bad=case
 payload=bytes((65+i%26 for i in range(max(0,min(length-24,256)))))
 header=bytearray(24);header[:4]=b'\xff'*4
 struct.pack_into('<I',header,4,0x3030564b);struct.pack_into('<I',header,8,length)
 header[16]=name_len;struct.pack_into('<I',header,20,value_len)
 crc=zlib.crc32(header[16:20]);crc=zlib.crc32(header[20:24],crc);crc=zlib.crc32(payload,crc)
 if crc_bad:crc^=0xffffffff
 struct.pack_into('<I',header,12,crc)
 flash=bytes(header)+payload+b'\xff'*256
 return flash
def run(source,case):
 length,name_len,value_len,status,crc_bad=case
 flash=fixture(case)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 d=bytearray(b'\xa5'*2304);struct.pack_into('<I',d,0,DBNAME);struct.pack_into('<II',d,12,4096,4096)
 k=bytearray(b'\xa5'*88);struct.pack_into('<I',k,80,0x1000)
 u.mem_write(DB,bytes(d));u.mem_write(KV,bytes(k));u.mem_write(PATH,b'/db\0')
 u.reg_write(UC_ARM_REG_R0,DB);u.reg_write(UC_ARM_REG_R1,KV)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def ret(emu,value):emu.reg_write(UC_ARM_REG_R0,value);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 def cstring(emu,p):
  out=bytearray()
  for i in range(160):
   c=bytes(emu.mem_read(p+i,1))[0]
   if not c:break
   out.append(c)
  return out.decode('ascii')
 def hook(emu,pc,size,_):
  if pc==0x585a12:
   db,addr,buf,n=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   assert db==DB and addr>=0x1000 and addr+n<=0x1000+len(flash),(case,hex(addr),n)
   calls.append(('read',addr,n,'kv' if KV<=buf<KV+88 else 'stack'))
   emu.mem_write(buf,flash[addr-0x1000:addr-0x1000+n]);ret(emu,0);return
  if pc==0x5858a8:
   table,count=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1))
   assert count==6
   calls.append(('get_status',count));ret(emu,status);return
  if pc==0x5858d8:
   db,addr,table,count=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=emu.reg_read(UC_ARM_REG_SP);extra=struct.unpack('<II',bytes(emu.mem_read(sp,8)))
   assert (db,addr,count,extra)==(DB,0x1000,6,(5,1)),(case,db,addr,count,extra)
   calls.append(('write_status',count,*extra));ret(emu,0);return
  if pc==0x585c94:
   assert emu.reg_read(UC_ARM_REG_R0)==DB
   calls.append(('path',));ret(emu,PATH);return
  if pc==0x4733ee:
   fmtp=emu.reg_read(UC_ARM_REG_R0);fmt=cstring(emu,fmtp)
   args=[emu.reg_read(r) for r in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if fmt=='[%s][%s] ':args=args[:2]
   elif fmt=='Error: The KV @0x%08X length has an error.\n':args=args[:1]
   elif fmt=='Error: Read the KV (%.*s@0x%08X) CRC32 check failed!\n':args=args[:3];args[1]='kv_name' if args[1]==KV+16 else hex(args[1])
   else:args=[]
   calls.append(('print',fmt,*args));ret(emu,0);return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(entry if source else 0x544001,0x10000000,count=200000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 return {'ret':u.reg_read(UC_ARM_REG_R0),'kv':bytes(u.mem_read(KV,88)).hex(),
         'db':bytes(u.mem_read(DB,2304)).hex(),'calls':calls}

cases=[]
for case in itertools.product((0,23,24,25,32,56,88,4097,0xffffffff),
                              (0,1,4,63,64),(0,1,0x12345678),(2,5),(False,True)):
 a,b=run(False,case),run(True,case)
 if a!=b:
  for key in a:
   if a[key]!=b[key]:
    if key in ('kv','db'):
     aa=bytes.fromhex(a[key]);bb=bytes.fromhex(b[key]);i=next(i for i,(x,y) in enumerate(zip(aa,bb)) if x!=y)
     raise AssertionError((case,key,i,aa[i:i+16].hex(),bb[i:i+16].hex()))
    raise AssertionError((case,key,a[key],b[key]))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x544000..0x54418e',
         'stock_body_sha256':hashlib.sha256(B[0x544000-0x437fe0:0x54418e-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete local 398-byte read_kv with coherent synthetic flash/status/write/print/path callbacks; stock CRC32 executes. No persistent flash or logger implementation proof. M4 scalar oracle, M55 archive compile separate.'}
(H/'read-kv-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS read_kv',len(cases))
