#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/fal_partition_state_candidates_20261010/partition_state.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'fal-partition-state.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-Oz','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,--section-start=.bss=0x20080000','-Wl,-e,g2_fal_partition_init','-Wl,--defsym=g2_fal_partition_rows=0x6d5358','-Wl,--defsym=g2_fal_flash_device_find=0x597e55',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
BASE=0x6d5358; DEV0=0x20050000; DEV1=0x20050100
def u32(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def run(source,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 put(u,DEV0+0x1c,c['lengths'][0]);put(u,DEV1+0x1c,c['lengths'][1])
 if source:
  aok=syms['g2_fal_partition_init_ok'];abas=syms['g2_fal_partition_table_base'];alen=syms['g2_fal_partition_table_length'];acache=syms['g2_fal_device_cache']
 else:aok=0x20074fc7;abas=0x200745dc;alen=0x200745e0;acache=0x20074140
 if c['prior']:
  u.mem_write(aok,b'\x01');put(u,abas,BASE);put(u,alen,2);put(u,acache,DEV0);put(u,acache+4,DEV1)
 u.reg_write(UC_ARM_REG_SP,0x200feffc);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,data):
  if pc==0x597e54:
   call=len(calls);calls.append(emu.reg_read(UC_ARM_REG_R0))
   emu.reg_write(UC_ARM_REG_R0,c['devices'][call] if call<len(c['devices']) else 0)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((syms['g2_fal_partition_init'] if source else 0x597cae)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,c,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==0x200feffc
 return dict(ret=u.reg_read(UC_ARM_REG_R0),base=u32(u,abas),length=u32(u,alen),cache=[u32(u,acache),u32(u,acache+4)],init_ok=u.mem_read(aok,1)[0],calls=calls)
cases=[]
for devices in ((0,0),(DEV0,0),(0,DEV1),(DEV0,DEV1),(DEV0,DEV0)):
 for lengths in ((0x7fffffff,0x7fffffff),(0x80000000,0x7fffffff),(0x7fffffff,0x10000),(0x7fffffff,0x1ff80),(0x7fffffff,0x1ff81)):
  for prior in (False,True):
   c=dict(devices=devices,lengths=lengths,prior=prior);a,b=run(False,c),run(True,c)
   if a!=b:raise AssertionError((c,a,b))
   cases.append(c)
receipt=dict(status='PASS',cases=len(cases),stock_init_sha256=hashlib.sha256(blob[0x597cae-0x437fe0:0x597cde-0x437fe0]).hexdigest(),stock_cache_fill_sha256=hashlib.sha256(blob[0x597c6c-0x437fe0:0x597cae-0x437fe0]).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Scalar Cortex-M4 oracle because Unicorn rejects an M55 instruction; independent Main archive compiles M55. Static two-row FAL table and synthetic flash-device discovery. Main C source imports rows and finder; no source-owned row initializer, finder, physical flash, absolute RAM placement or invalid pointer behavior.')
(H/'fal-state-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS fal state',len(cases))
