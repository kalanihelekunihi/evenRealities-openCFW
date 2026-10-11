#!/usr/bin/env python3
"""Observe reset request ordering in Unicorn; no physical device operations."""
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_LR
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4]; HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-system-reset-20261011';OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/eeprom_offline/system_reset.c';obj=OUT/'reset.o';elf=OUT/'reset.elf'
subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--entry=touch_reset_boundary',str(obj),'-o',str(elf)],check=True)
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=e.get_section_by_name('.symtab').get_symbol_by_name('touch_reset_boundary')[0]['st_value']
def run(original,initial):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0x100000,0x10000),(0x20000000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x3300,fw.read_bytes()[32:])
 if not original:
  for a,b in segments:u.mem_write(a,b)
 u.mem_write(0xe000ed0c,struct.pack('<I',initial));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001)
 events=[];nops=0
 def code(uc,pc,size,_):
  nonlocal nops
  b=bytes(uc.mem_read(pc,size))
  if b==bytes.fromhex('bff34f8f'):events.append(['dsb'])
  if b in (bytes.fromhex('c046'),bytes.fromhex('00bf')):
   nops+=1
   if nops==2:uc.emu_stop()
 def write(uc,access,address,size,value,_):events.append(['write',hex(address),size,hex(value)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x7e14 if original else entry)|1,0x20000000,count=64)
 assert nops==2
 assert events==[['dsb'],['write','0xe000ed0c',4,'0x5fa0004'],['dsb']],events
 assert u.reg_read(UC_ARM_REG_SP)==0x20008000
 return events
for initial in [0,0xffffffff,0x05fa0700,0x12345678]:assert run(True,initial)==run(False,initial)
r={'status':'PASS_NATIVE_COMPILED_C_RESET_SEQUENCE','cases':4,'firmware_sha256':sha(fw),'source_sha256':sha(src),'elf_sha256':sha(elf),'events':run(False,0),'limits':['Synthetic emulator register writes only; no physical reset or device operation.','Observed sequence through two terminal loop visits; this does not validate reset hardware or final image placement.']}
(HERE/'system-reset-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
