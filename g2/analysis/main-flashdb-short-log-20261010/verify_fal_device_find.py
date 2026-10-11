#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/fal_device_find_candidates_20261010/device_find.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'fal-device-find.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,g2_fal_flash_device_find','-Wl,--defsym=g2_fal_flash_device_table=0x20054000','-Wl,--defsym=g2_fal_flash_device_count=0x20054080',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_fal_flash_device_find')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
DEV=0x20050000;NAME=0x20053000;TABLE=0x20054000;COUNT=0x20054080
names=(b'norflash',b'norflash0',b'abc',b'ABCDEFGHIJKLMNOPQRSTUVWX')
def run(source,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(0x597e88,struct.pack('<II',TABLE,COUNT)) # data literals only; original instructions remain fixed
 for i,n in enumerate(names):
  u.mem_write(DEV+i*0x100,n.ljust(32,b'\0'))
  u.mem_write(TABLE+i*4,struct.pack('<I',DEV+i*0x100))
 u.mem_write(COUNT,struct.pack('<I',c['count']))
 u.mem_write(NAME,c['name'].ljust(32,b'\0'))
 u.reg_write(UC_ARM_REG_R0,NAME);u.reg_write(UC_ARM_REG_SP,0x200feffc);u.reg_write(UC_ARM_REG_LR,0x10000001)
 try:u.emu_start((entry if source else 0x597e54)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,c,hex(u.reg_read(UC_ARM_REG_PC)))) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==0x200feffc
 return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(NAME,32)),[bytes(u.mem_read(DEV+i*0x100,32)) for i in range(4)]
cases=[]
variants=[*names,b'norflas',b'NORFLASH',b'norflashx',b'',b'ABCDEFGHIJKLMNOQRSTUVWXY',b'ABCDEFGHIJKLMNOPQRSTUVWXy',b'\xfforflash',b'abc\x00suffix',b'ABCDEFGHIJKLMNOPQRSTUVWX']
variants += [b'ABCDEFGHIJKLMNOPQRSTUVWX'[:i]+b'z'+b'ABCDEFGHIJKLMNOPQRSTUVWX'[i+1:] for i in range(24)]
variants += [b'ABCDEFGHIJKLMNOPQRSTUVWX'[:i]+b'\0suffix' for i in range(24)]
for count,name in itertools.product(range(5),variants):
 c=dict(count=count,name=name)
 a,b=run(False,c),run(True,c)
 if a!=b:raise AssertionError((c,a,b))
 cases.append(c)
receipt=dict(status='PASS',cases=len(cases),stock_body_sha256=hashlib.sha256(blob[0x597e54-0x437fe0:0x597e82-0x437fe0]).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,stock_default=dict(table_pointer=0x78f0a4,count_pointer=0x78f0a8,table_first=0x722b30,count=1),limits='Oracle patched only stock literal data pointers to synthetic RAM table/count for count 0..4; stock instructions and strncmp executed. Product table/count, device struct initializer, invalid pointers and hardware remain external.')
(H/'fal-device-find-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS fal device find',len(cases))
