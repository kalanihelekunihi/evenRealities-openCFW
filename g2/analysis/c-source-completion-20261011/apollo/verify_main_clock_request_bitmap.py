#!/usr/bin/env python3
"""Locked native/source comparisons for Main seven-class clock bitmaps."""
import argparse,hashlib,itertools,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_MCLASS,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==STOCK_SHA
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
with a.elf.open('rb') as f:
 elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
 syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
ENTRY={'test':(0x4c37a8,syms['g2_main_clock_request_test_4c37a8']),'set':(0x4c37fe,syms['g2_main_clock_request_set_4c37fe']),'any':(0x4c377a,syms['g2_main_clock_request_any_4c377a'])}
TABLE,RET=0x20073324,0x200ff000

def run(source,kind,cls,bit,enabled,pattern):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob)
 cpu.mem_map(0x800000,0x10000)
 for addr,data in segments:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000)
 words=[0]*16
 if pattern==1:words=[0xffffffff]*16
 elif pattern==2:words=[0x80000000 if i%2 else 0x00000001 for i in range(16)]
 elif pattern==3:words=[0 if i%2 else 0x12345678 for i in range(16)]
 cpu.mem_write(TABLE,b''.join(x.to_bytes(4,'little') for x in words))
 for reg,value in zip((R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2),(cls,bit,enabled)):cpu.reg_write(reg,value)
 cpu.reg_write(R.UC_ARM_REG_SP,0x200fe000);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 def stop(machine,pc,_size,_user):
  if pc==RET:machine.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,stop)
 cpu.emu_start(ENTRY[kind][1 if source else 0]|1,RET+2,count=2000)
 assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'r0':cpu.reg_read(R.UC_ARM_REG_R0),'table':bytes(cpu.mem_read(TABLE,64)).hex()}
fixtures=[]
for kind in ('test','set','any'):
 for cls,bit,enabled,pattern in itertools.product((0,1,4,5,6,7,255),(0,1,31,32,54,55,56,57,255),(0,1,256),(0,1,2,3)):
  if kind=='any' and (bit!=0 or enabled!=0):continue
  if kind=='test' and enabled!=0:continue
  if kind=='test' and bit>=64:continue
  if kind=='any' and cls==255:continue
  fixtures.append((kind,cls,bit,enabled,pattern))
for i,fixture in enumerate(fixtures):
 native=run(False,*fixture);candidate=run(True,*fixture)
 assert native==candidate,(i,fixture,native,candidate)
report={'status':'PASS_MAIN_CLOCK_REQUEST_BITMAP_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':STOCK_SHA,'source_elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'limits':['Synthetic SRAM and bounded class/bit values; physical clock behavior and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],len(fixtures))
