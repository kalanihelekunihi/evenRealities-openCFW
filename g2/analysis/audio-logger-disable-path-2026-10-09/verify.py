from pathlib import Path
import json,hashlib
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
blob=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();raw=blob[32:]
rows=[]
for flag,a,b in [(0,0,0),(2,0,0),(1,1,0),(1,0,1),(1,0,0)]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000)
 u.mem_write(0x20074f4e,bytes([flag]));u.mem_write(0x200742f0,(0x12345679).to_bytes(4,'little'));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x100001)
 calls=[];stop=[]
 def hook(uc,pc,size,user):
  if pc in (0x539254,0x539304,0x480f0c):
   calls.append({'address':hex(pc),'r0':uc.reg_read(UC_ARM_REG_R0),'r1':uc.reg_read(UC_ARM_REG_R1)})
   uc.reg_write(UC_ARM_REG_R0,a if pc==0x539254 else b if pc==0x539304 else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  elif pc in (0x4c2b44,0x4c2b4e,0x100000):stop.append(hex(pc));uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x4c2b31,0,count=100)
 pointer=int.from_bytes(u.mem_read(0x200742f0,4),'little');newflag=u.mem_read(0x20074f4e,1)[0]
 successful=flag==1 and a==0 and b==0
 assert pointer==(0 if successful else 0x12345679) and newflag==(0 if successful else flag)
 expected=0x4c2b44 if flag==1 and a else 0x4c2b4e if flag==1 and b else 0x100000
 assert stop==[hex(expected)]
 rows.append({'flag':flag,'first_stub_return':a,'second_stub_return':b,'calls':calls,'callback_after':hex(pointer),'flag_after':newflag,'stop':stop})
out={'status':'PASS','cases':len(rows),'wrapped_sha256':hashlib.sha256(blob).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'limits':'Actual original instructions; calls 539254/539304/480f0c stubbed. No child lifecycle, live driver, scheduler or hardware inference.'}
Path(__file__).with_name('results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows))
