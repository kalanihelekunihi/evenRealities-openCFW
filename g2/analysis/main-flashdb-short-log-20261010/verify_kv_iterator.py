#!/usr/bin/env python3
"""Complete local FlashDB kv_iterator routing, stock versus C public entry."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
SRC=R/'g2/components/main/flashdb_kv_iterator_candidates_20261010/kv_iterator.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(B).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-kv-iterator.elf'
defs={'g2_flashdb_read_sector_info':0x54418f,'g2_flashdb_read_kv':0x544001,
      'g2_flashdb_next_kv_addr':0x543f8d,'g2_flashdb_next_sector_addr':0x544375}
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_kv_iterator',*[f'-Wl,--defsym={k}={v:#x}' for k,v in defs.items()],str(SRC),'-o',str(elf)]
subprocess.run(cmd,check=True,capture_output=True)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_kv_iterator')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;KV=0x20052000;ARG1=0x20051000;ARG2=0x20053000;SP=0x200ff000;CALLBACK=0x10010001

def run(source,case):
 statuses,read_error,callback_enabled,stop_after=case
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(B)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,B)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(DB,b'\xa5'*2304);u.mem_write(DB+12,struct.pack('<I',0x1000));u.mem_write(DB+20,struct.pack('<I',0x1000))
 u.mem_write(KV,b'\xa5'*88);u.mem_write(ARG1,b'key\0');u.mem_write(ARG2,b'\0')
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(DB,KV,ARG1,ARG2)):u.reg_write(r,v)
 u.mem_write(SP-4,struct.pack('<I',CALLBACK if callback_enabled else 0))
 u.reg_write(UC_ARM_REG_SP,SP-4);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[];current=[0];row_count=[0];cb_count=[0]
 def ret(value):u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(emu,pc,size,_):
  if pc==0x54418e:
   db,addr,sector,trav=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   assert db==DB and addr in (0x1000,0x2000) and trav==0,(source,case,'readsec',db,addr,sector,trav)
   current[0]=(addr//0x1000)-1;row_count[0]=0
   s=bytearray(24);s[1]=statuses[current[0]];struct.pack_into('<I',s,4,addr)
   emu.mem_write(sector,bytes(s));calls.append(('readsec',addr))
   ret(1 if read_error==current[0] else 0);return
  if pc==0x544000:
   db,kv=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1))
   assert (db,kv)==(DB,KV)
   calls.append(('readkv',struct.unpack('<I',bytes(emu.mem_read(KV+80,4)))[0]))
   emu.mem_write(KV+16,bytes([ord('A')+cb_count[0]]));ret(0);return
  if pc==0x10010000:
   kv,a1,a2=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   assert (kv,a1,a2)==(KV,ARG1,ARG2)
   cb_count[0]+=1;calls.append(('callback',cb_count[0]))
   emu.mem_write(ARG2,bytes([cb_count[0]]))
   ret(1 if stop_after and cb_count[0]>=stop_after else 0);return
  if pc==0x543f8c:
   db,sector,kv=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   assert db==DB and kv==KV
   row_count[0]+=1;calls.append(('nextkv',row_count[0]))
   ret(0x1000*(current[0]+1)+16+row_count[0]*32 if row_count[0]<2 else 0xffffffff);return
  if pc==0x544374:
   db,sector,traversed=(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   assert db==DB and traversed==(current[0]+1)*0x1000,(source,case,'nextsec',traversed,current[0])
   calls.append(('nextsec',traversed))
   ret(0x2000 if current[0]==0 else 0xffffffff);return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(entry if source else 0x5443b1,0x10000000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP-4
 return {'calls':calls,'kv':bytes(u.mem_read(KV,88)).hex(),'found':bytes(u.mem_read(ARG2,1)).hex()}

cases=[]
for case in itertools.product(((0,0),(2,0),(0,3),(2,3),(3,2)),(-1,0,1),(False,True),(0,1,2,3)):
 a,b=run(False,case),run(True,case)
 assert a==b,(case,a,b)
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_address':'0x5443b0..0x54443a',
         'stock_body_sha256':hashlib.sha256(B[0x5443b0-0x437fe0:0x54443a-0x437fe0]).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'compile':cmd,'limits':'Complete local 138-byte iterator routing, with synthetic read-sector/read-KV/next-KV/next-sector and callback boundaries. Coherent two-sector, up-to-two-KV fixture; no stock child or persistent flash proof. M4 scalar execution; M55 archive compile separate.'}
(H/'kv-iterator-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS kv_iterator',len(cases))
