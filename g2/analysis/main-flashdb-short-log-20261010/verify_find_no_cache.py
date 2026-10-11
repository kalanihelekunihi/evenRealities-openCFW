#!/usr/bin/env python3
"""Compare pinned FlashDB no-cache wrapper and iterator callback with source."""
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
SOURCE=ROOT/'g2/components/main/flashdb_find_no_cache_candidates_20261010/find_no_cache.c'
BLOB=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(BLOB).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
CC=subprocess.check_output(['xcrun','--find','clang'],text=True).strip(); ELF=HERE/'flashdb-find-no-cache.elf'
CMD=[CC,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_find_no_cache','-Wl,--defsym=g2_log_candidate_module_length=0x44a43d',
     '-Wl,--defsym=g2_flashdb_kv_iterator=0x5443b1',str(SOURCE),'-o',str(ELF)]
subprocess.run(CMD,check=True,capture_output=True)
with ELF.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000; KEY=0x20051000; KV=0x20052000; FOUND=0x20053000; SP=0x200ff000
def run(source,kind,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(BLOB)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,BLOB)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 key,kvname,nlen,status,crc,initial,provider=case
 u.mem_write(KEY,key+b'\0')
 obj=bytearray(b'\xa5'*88);obj[0]=status;obj[1]=crc;obj[2]=nlen
 obj[16:16+len(kvname)]=kvname
 u.mem_write(KV,bytes(obj));u.mem_write(FOUND,bytes([initial]))
 args=(KV,KEY,FOUND) if kind=='callback' else (DB,KEY,KV)
 for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,_):
  if pc==0x5443b0:
   a=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   sp=emu.reg_read(UC_ARM_REG_SP);cb=struct.unpack('<I',bytes(emu.mem_read(sp,4)))[0]
   assert a[:3]==[DB,KV,KEY],(source,case,a)
   assert cb==(syms['g2_flashdb_find_cb'] if source else 0x54443b),(source,case,hex(cb))
   calls.append([*a[:3], 'found-pointer', 'callback-pointer'])
   emu.mem_write(a[3],bytes([provider]))
   emu.reg_write(UC_ARM_REG_R0,0)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 entry=(syms['g2_flashdb_find_cb'] if kind=='callback' else syms['g2_flashdb_find_no_cache']) if source else (0x54443b if kind=='callback' else 0x54447b)
 u.emu_start(entry,0x10000000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 return (u.reg_read(UC_ARM_REG_R0)&0xff,bytes(u.mem_read(KV,88)),
         bytes(u.mem_read(FOUND,1)),calls)

callback=[]
for key,kvname,nlen,status,crc,initial in itertools.product(
        (b'',b'a',b'name',b'longername'),(b'',b'a',b'name',b'other'),
        (0,1,4,10),(0,1,2,3),(0,1),(0,1)):
 case=(key,kvname,nlen,status,crc,initial,0)
 a,b=run(False,'callback',case),run(True,'callback',case)
 assert a==b,('callback',case,a,b)
 callback.append(case)
wrapper=[]
for initial,provider in itertools.product((0,1),(0,1)):
 case=(b'name',b'name',4,2,1,initial,provider)
 a,b=run(False,'wrapper',case),run(True,'wrapper',case)
 assert a==b,('wrapper',case,a,b)
 wrapper.append(case)
receipt={'status':'PASS','callback_cases':len(callback),'wrapper_cases':len(wrapper),
         'stock_callback':'0x54443a..0x54447a','stock_wrapper':'0x54447a..0x54449a',
         'stock_bodies_sha256':{label:hashlib.sha256(BLOB[a-0x437fe0:b-0x437fe0]).hexdigest()
                                for label,a,b in [('callback',0x54443a,0x54447a),('wrapper',0x54447a,0x54449a)]},
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'compile':CMD,
         'limits':'Callback executes stock strlen and strncmp on coherent RAM; wrapper iterator is shared synthetic callback, with callback pointer ABI verified but no live iterator/flash state. M55 source executes in Unicorn.'}
(HERE/'find-no-cache-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS find_no_cache',len(callback),'callback and',len(wrapper),'wrapper')
