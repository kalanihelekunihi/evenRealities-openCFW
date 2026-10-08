from pathlib import Path
import json,struct,hashlib,itertools
from unicorn import *
import unicorn.arm_const as a
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
rows=[];vis=set()
for simo,info,stim,mask in itertools.product([0,3],[0,0x1f01600d],[0,1,2,255],[0,1]):
 if simo==3 and info==0x1f01600d:continue
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for addr,size in [(0x410000,0x30000),(0x20000000,0x40000),(0x40020000,0x2000),(0x8000000,0x1000)]:u.mem_map(addr,size)
 u.mem_write(0x410000,b)
 for addr,value in [(0x40021108,simo<<4),(0x20026ba0,info),(0x20002000,0x42340000)]:u.mem_write(addr,struct.pack('<I',value))
 u.mem_write(0x20002004,bytes.fromhex('1122334455667788'));u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_R0,stim);u.reg_write(a.UC_ARM_REG_R1,1);u.reg_write(a.UC_ARM_REG_R2,0x20002000);u.reg_write(a.UC_ARM_REG_PRIMASK,mask)
 def hook(cpu,pc,size,data):
  if pc==0x8000000:cpu.emu_stop();return
  assert 0x42a878<=pc<0x42ab6e,hex(pc)
  vis.update(range(pc,pc+size))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x42a879,0,count=500)
 assert u.reg_read(a.UC_ARM_REG_PC)==0x8000000
 result=u.reg_read(a.UC_ARM_REG_R0);assert result==(1 if simo==3 else 0)
 assert bytes(u.mem_read(0x20002004,8))==bytes.fromhex('1122334455667788');assert u.reg_read(a.UC_ARM_REG_PRIMASK)==mask
 rows.append(dict(simo=simo,info=hex(info),stimulus=stim,mask=mask,result=result,args_unchanged=True))
out=dict(status='PASS',cases=len(rows),distinct_original_bytes=len(vis),results=rows,negative_hypothesis='Pinned public PCM2.2 source handles temperature stimulus when SIMOBUCK is inactive; locked42a878 returns0 without updating temperature bounds or calling classification. Public upstream is family corroboration, not a drop-in exact replacement.',limits=['Original instructions only for inactive SIMOBUCK or invalid INFO guards; no active valid-profile state-update claim.','Public source divergence is static source comparison, not execution of its complete dependency closure.'])
(HERE/'upstream-negative-comparison.json').write_text(json.dumps(out,indent=2));print('PASS',len(rows),len(vis),'original bytes')
