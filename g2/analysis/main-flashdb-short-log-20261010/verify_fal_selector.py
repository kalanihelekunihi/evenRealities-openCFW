#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/fal_device_selector_candidates_20261010/device_selector.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'fal-device-selector.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,g2_fal_device_for_partition','-Wl,--defsym=g2_fal_partition_table_base=0x200745dc','-Wl,--defsym=g2_fal_device_cache=0x20074140',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_fal_device_for_partition')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
BASE=0x6d5358;DEV=0x20050000
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(DEV+0x1c,struct.pack('<I',0x7fffffff));return u
def initialize_stock(u):
 # Real stock FAL static-table init at 0x597cae: base=0x6d5358,
 # partition count=2, then cache fill; only flash-device discovery is supplied.
 u.reg_write(UC_ARM_REG_SP,0x200feffc);u.reg_write(UC_ARM_REG_LR,0x10000001)
 lookups=[]
 def hook(emu,pc,size,data):
  if pc==0x597e54:
   lookups.append(emu.reg_read(UC_ARM_REG_R0));emu.reg_write(UC_ARM_REG_R0,DEV)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(0x597cae|1,0x10000000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 state=(struct.unpack('<I',u.mem_read(0x200745dc,4))[0],struct.unpack('<I',u.mem_read(0x200745e0,4))[0],struct.unpack('<II',u.mem_read(0x20074140,8)))
 assert state==(BASE,2,(DEV,DEV)),state
 assert lookups==[BASE+0x1c,BASE+0x5c],lookups
 return dict(base=state[0],count=state[1],cache=list(state[2]),lookups=lookups)
def run(source,part):
 u=machine();state=initialize_stock(u)
 u.reg_write(UC_ARM_REG_R0,part);u.reg_write(UC_ARM_REG_LR,0x10000001);u.reg_write(UC_ARM_REG_SP,0x200feffc)
 u.emu_start((entry if source else 0x597d10)|1,0x10000000,count=1000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==0x200feffc
 return u.reg_read(UC_ARM_REG_R0),state
cases=[]
for off in range(128):
 part=BASE+off;a=run(False,part);b=run(True,part)
 if a!=b:raise AssertionError((hex(part),a,b))
 cases.append(off)
receipt=dict(status='PASS',cases=len(cases),stock_selector_sha256=hashlib.sha256(blob[0x597d10-0x437fe0:0x597d20-0x437fe0]).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,init_state=dict(base=BASE,count=2,cache=[DEV,DEV]),limits='Stock static-table init executed with synthetic flash-device discovery. Selector compared only within the initialized two-row table span; out-of-range/assertion behavior, source ownership of table rows, flash device and hardware remain open.')
(H/'fal-selector-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS fal selector',len(cases))
