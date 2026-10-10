from pathlib import Path
import json
import unicorn.arm_const as ac
from unicorn import *
from unicorn.arm_const import *
raw=Path('/repo/g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];rows=[]
for name in ['default','UC_CPU_ARM_CORTEX_M4','UC_CPU_ARM_CORTEX_M33']:
 if name!='default' and not hasattr(ac,name):continue
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 if name!='default':u.ctl_set_cpu_model(getattr(ac,name))
 u.mem_map(0x438000,((len(raw)+4095)//4096)*4096);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_write(0x20020021,b'ABCDEFGHIJKLMNO');u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x20080001)
 for reg,v in [(UC_ARM_REG_R0,0x20030020),(UC_ARM_REG_R1,0x20020021),(UC_ARM_REG_R2,5)]:u.reg_write(reg,v)
 trace=[];stop=[];fault=[]
 def hook(uc,pc,size,user):
  if pc==0x20080000:stop.append('return');uc.emu_stop();return
  trace.append([hex(pc),uc.reg_read(UC_ARM_REG_R2),hex(uc.reg_read(UC_ARM_REG_XPSR))]);trace[:]=trace[-20:]
 def mem(uc,access,a,n,v,user):
  if a>=0x20030025 and a<0x20040000:fault.append([hex(a),n]);uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,mem)
 try:u.emu_start(0x439711,0,count=1000);err=None
 except UcError as e:err=str(e)
 row={'model':name,'return_reached':bool(stop),'write_past_capacity':fault,'engine_error':err,'pc':hex(u.reg_read(UC_ARM_REG_PC)),'r2':u.reg_read(UC_ARM_REG_R2),'trace_tail':trace,'output':bytes(u.mem_read(0x20030020,5)).hex()};rows.append(row);print(name,row['return_reached'],fault,flush=True)
Path('/out/memmove-engine-probe.json').write_text(json.dumps(rows,indent=2)+'\n')
