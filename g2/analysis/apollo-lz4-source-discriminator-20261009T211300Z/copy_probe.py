from pathlib import Path
import json
from unicorn import *
from unicorn.arm_const import *
raw=Path('/repo/g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];rows=[]
for n in [1,4,5,8]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,((len(raw)+4095)//4096)*4096);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_write(0x20020021,b'ABCDEFGHIJKLMNO');u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x20080001)
 for reg,v in [(UC_ARM_REG_R0,0x20030020),(UC_ARM_REG_R1,0x20020021),(UC_ARM_REG_R2,n)]:u.reg_write(reg,v)
 trace=[]
 def hook(uc,pc,size,user):
  if pc==0x20080000:uc.emu_stop();return
  trace.append([hex(pc),uc.reg_read(UC_ARM_REG_R2),hex(uc.reg_read(UC_ARM_REG_XPSR))])
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x439be5,0,count=1000);row={'size':n,'pc':hex(u.reg_read(UC_ARM_REG_PC)),'r2':u.reg_read(UC_ARM_REG_R2),'trace_count':len(trace),'trace_tail':trace[-12:],'output':bytes(u.mem_read(0x20030020,n)).hex()};rows.append(row);print(row,flush=True)
Path('/out/copy-provider-probe.json').write_text(json.dumps(rows,indent=2)+'\n')
