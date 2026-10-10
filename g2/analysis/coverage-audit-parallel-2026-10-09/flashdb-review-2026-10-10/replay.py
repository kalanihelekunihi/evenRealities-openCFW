from pathlib import Path
import json,struct,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path('/repo/g2/analysis/flashdb-blob-build-interface-20261010-implementation');raw=Path('/repo/g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
with (D/'blobmake.elf').open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='fdb_blob_make')
base=int.from_bytes(raw[0x5412c8-0x437fe0:0x5412cc-0x437fe0],'little');SP=0x200ff000;K=0x20080000;BUF=0x20081000;STOP=0x100000;cases=[(0,0,0,0),(1,1,1,1),(2,0xffff,16,16),(0x101,0x10001,0,7),(0,5,3,0),(0xff,0xffffffff,9,3)];results=[]
for index,size,returned,saved in cases:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(STOP,0x1000);u.mem_write(K,b'key\0');u.mem_write(BUF,b'\xcc'*64);u.mem_write(SP-128,b'\xa7'*128);trace=[];blob_before=None;calls=0
 for reg,v in [(UC_ARM_REG_R0,index),(UC_ARM_REG_R1,K),(UC_ARM_REG_R2,BUF),(UC_ARM_REG_R3,size),(UC_ARM_REG_SP,SP),(UC_ARM_REG_LR,STOP|1)]:u.reg_write(reg,v)
 def hook(u,a,n,d):
  global blob_before,calls
  if a==STOP:u.emu_stop();return
  if 0x54116e<=a<0x5411f2:return
  if a==0x4490cc:trace.append('tick');u.reg_write(UC_ARM_REG_R0,0)
  elif a==0x54454a:
   p=u.reg_read(UC_ARM_REG_R2);assert [u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]==[base+(index&255)*0x8ac,K];blob_before=bytes(u.mem_read(p,20));assert struct.unpack('<II',blob_before[:8])==(BUF,size&65535);assert blob_before[8:]==b'\xa7'*12
   v=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);v.mem_map(STOP,0x10000);v.mem_map(0x20000000,0x100000)
   for address,data in sections:v.mem_write(address,data)
   v.mem_write(p,b'\xa7'*20)
   for reg,val in [(UC_ARM_REG_R0,p),(UC_ARM_REG_R1,BUF),(UC_ARM_REG_R2,size&65535),(UC_ARM_REG_SP,0x20070000),(UC_ARM_REG_LR,0x108001)]:v.reg_write(reg,val)
   v.emu_start(entry|1,0x108000,count=100);assert bytes(v.mem_read(p,20))==blob_before and v.reg_read(UC_ARM_REG_R0)==p
   trace.append(dict(kind='get-blob-boundary',database=hex(base+(index&255)*0x8ac),key=hex(K),blob=hex(p),blob_fields=blob_before.hex(),public_blob_make_equal=True));u.mem_write(p+16,struct.pack('<I',saved));u.reg_write(UC_ARM_REG_R0,returned);calls+=1
  elif a==0x43d0ce:trace.append('flags-zero');u.reg_write(UC_ARM_REG_R0,0)
  else:raise RuntimeError(('unknown dependency',hex(a)))
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def write(u,acc,a,n,val,d):assert SP-128<=a and a+n<=SP
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x54116f,0,count=2000);assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==returned and calls==1;assert bytes(u.mem_read(BUF,64))==b'\xcc'*64 and bytes(u.mem_read(K,4))==b'key\0';assert trace.count('tick')==2 and trace.count('flags-zero')==(3 if saved==0 else 0)
 results.append(dict(database_input=index,length_input=size,provider_return=returned,saved_len=saved,trace=trace,return_unchanged=True,output_key_unchanged=True,pass_=True))
Path('/tmp/flashdb-audit-results.json').write_text(json.dumps(dict(count=6,all_pass=True,database_base=hex(base),cases=results,scope='stock adapter vs genuine public ARM blob_make; get-blob/tick/flags mocked, no flash I/O'),indent=2)+'\n');print('Six stock adapter/public blob constructor comparisons PASS')
