import json,struct
from unicorn import *
from unicorn.arm_const import *
rows=[]
# Exact candidate instructions10006e..10007e: cmp;ITcc;movcc;cbz;ldr;mov;mov;mov.
code=bytes.fromhex("b8f1000f1cbf0398c8f80000039daf4238bf3d4664b11599304622462b46")
for request in [3,8,12]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x100000,4096);u.mem_map(0x20000000,4096);u.mem_write(0x100060,code);u.mem_write(0x20000000+12,struct.pack("<I",8));u.mem_write(0x20000000+84,struct.pack('<I',0xabc400))
 for r,v in [(UC_ARM_REG_R8,0x20000200),(UC_ARM_REG_SP,0x20000000),(UC_ARM_REG_R1,0x20020000),(UC_ARM_REG_R4,0x20030000),(UC_ARM_REG_R5,8),(UC_ARM_REG_R7,request),(UC_ARM_REG_R6,0x20010000)]:u.reg_write(r,v)
 u.emu_start(0x100061,0x10007e,count=30);rows.append({'requested':request,'r1':hex(u.reg_read(UC_ARM_REG_R1)),'expected':'0xabc400','r3':u.reg_read(UC_ARM_REG_R3),'pc':hex(u.reg_read(UC_ARM_REG_PC))})
print(json.dumps(rows,indent=2))
