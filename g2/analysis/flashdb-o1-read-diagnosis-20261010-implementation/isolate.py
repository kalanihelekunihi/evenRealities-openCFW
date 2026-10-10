from pathlib import Path
import json,struct
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).parent
with (D/'candidate-O1.elf').open('rb') as f:
 e=ELFFile(f);text=e.get_section_by_name('.text');code=text.data();base=text['sh_addr']
rows=[]
for requested in [3,8,12]:
 for mode in ['none','code','memory-write','both']:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x100000,0x1000);u.mem_write(base,code);u.mem_map(0x20000000,0x100000);sp=0x200fef90;u.mem_write(sp+12,struct.pack('<I',8));u.mem_write(sp+84,struct.pack('<I',0xabc400));u.mem_write(0x20040000,b'\xcc'*4)
  for r,v in [(UC_ARM_REG_SP,sp),(UC_ARM_REG_R8,0x20040000),(UC_ARM_REG_R1,0x20020000),(UC_ARM_REG_R4,0x20030000),(UC_ARM_REG_R6,0x20010000),(UC_ARM_REG_R7,requested)]:u.reg_write(r,v)
  trace=[]
  if mode in ['code','both']:u.hook_add(UC_HOOK_CODE,lambda u,a,n,d:trace.append(hex(a)))
  if mode in ['memory-write','both']:u.hook_add(UC_HOOK_MEM_WRITE,lambda u,acc,a,n,v,d:None)
  u.emu_start(0x100061,0x10007e,count=100);rows.append({'requested':requested,'mode':mode,'r1':hex(u.reg_read(UC_ARM_REG_R1)),'r3':u.reg_read(UC_ARM_REG_R3),'saved_value':int.from_bytes(u.mem_read(0x20040000,4),'little'),'trace':trace,'xpsr':hex(u.reg_read(UC_ARM_REG_XPSR))})
(D/'isolate-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
