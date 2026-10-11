#!/usr/bin/env python3
"""Pinned find_kv cache/fallback wrapper, stock versus C public entry."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/flashdb_find_kv_candidates_20261010/find_kv.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x54449a-0x437fe0:0x5444f4-0x437fe0]
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-find-kv.elf'
defs={'g2_log_candidate_module_length':0x44a43d,
      'g2_flashdb_cache_lookup':0x543e29,'g2_flashdb_read_kv':0x544001,
      'g2_flashdb_find_no_cache':0x54447b,'g2_flashdb_cache_update':0x543d1d}
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-std=c11',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,-e,g2_flashdb_find_kv',*[f'-Wl,--defsym={k}={v:#x}' for k,v in defs.items()],str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f)
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_find_kv')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DB=0x20050000;KEY=0x20051000;KV=0x20052000
def run(source,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(KEY,b'K'*case['key_length']+b'\0')
 u.mem_write(KV,b'\xa5'*88)
 for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(DB,KEY,KV)):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def ret(v):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(emu,pc,size,data):
  if pc==0x543e28:
   args=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   assert args==[DB,KEY,case['key_length'],KV+80]
   calls.append(['cache_lookup',*args])
   emu.mem_write(KV+80,struct.pack('<I',case['address']))
   ret(case['cache']);return
  if pc==0x544000:
   args=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1)]
   calls.append(['read_kv',*args]);assert args==[DB,KV]
   emu.mem_write(KV+12,struct.pack('<I',0x12345678))
   ret(0);return
  if pc==0x54447a:
   args=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
   calls.append(['find_no_cache',*args]);assert args==[DB,KEY,KV]
   emu.mem_write(KV+80,struct.pack('<I',case['address']))
   ret(case['fallback']);return
  if pc==0x543d1c:
   args=[emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   calls.append(['cache_update',*args]);ret(0);return
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x54449a)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,case,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==0x200ff000
 return {'calls':calls,'return':u.reg_read(UC_ARM_REG_R0),'kv':bytes(u.mem_read(KV,88)).hex()}
cases=[]
for cache,fallback,key_length,address in itertools.product((0,1,0x100),(0,1,0x100,0x101),(0,1,63,64),(0,0x12345678,0xffffffff)):
 case=dict(cache=cache,fallback=fallback,key_length=key_length,address=address)
 a,b=run(False,case),run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_body_sha256':hashlib.sha256(body).hexdigest(),
         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'compile':cmd,
         'limits':'Complete local 90-byte wrapper with original stock strlen and synthetic cache lookup, KV read, fallback scan and cache update. No real cache, iterator or flash-backed row proof.'}
(H/'find-kv-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS find_kv',len(cases))
