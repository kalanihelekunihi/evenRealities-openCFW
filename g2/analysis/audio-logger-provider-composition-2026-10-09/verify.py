from pathlib import Path
import json,hashlib
from unicorn import *
from unicorn.arm_const import *
blob=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();raw=blob[32:];rows=[]
for counter in [0,1,2,255]:
 for clock in [0,3,4]:
  for mask in [0,1]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000);u.mem_map(0xe0000000,0x10000)
   u.mem_write(0x20074f4e,b'\1');u.mem_write(0x20074f7e,bytes([counter]));u.mem_write(0x20074f7d,b'\7');u.mem_write(0x200742f0,(0x12345679).to_bytes(4,'little'));u.mem_write(0xe0000e80,(0x800011).to_bytes(4,'little'));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x100001);u.reg_write(UC_ARM_REG_PRIMASK,mask)
   calls=[];stop=[]
   def hook(uc,pc,size,user):
    if pc in (0x4807fc,0x4807a0,0x4d3f78,0x480f0c):
     calls.append({'address':hex(pc),'r0':uc.reg_read(UC_ARM_REG_R0),'r1':uc.reg_read(UC_ARM_REG_R1),'r2':uc.reg_read(UC_ARM_REG_R2),'r3':uc.reg_read(UC_ARM_REG_R3)})
     uc.reg_write(UC_ARM_REG_R0,clock if pc==0x4d3f78 else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif pc in (0x4c2b44,0x4c2b4e,0x100000):stop.append(hex(pc));uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x4c2b31,0,count=1000)
   firstok=clock in (0,3);secondok=counter<=1 and firstok;success=firstok and secondok
   assert int.from_bytes(u.mem_read(0x200742f0,4),'little')==(0 if success else 0x12345679)
   assert u.mem_read(0x20074f4e,1)[0]==(0 if success else 1)
   assert u.mem_read(0x20074f7e,1)[0]==(max(counter-1,0) if firstok else counter)
   assert u.mem_read(0x20074f7d,1)[0]==(0 if firstok and counter<=1 else 7)
   assert int.from_bytes(u.mem_read(0xe0000e80,4),'little')==0x800000
   assert u.reg_read(UC_ARM_REG_PRIMASK)==mask
   assert stop==[hex(0x4c2b44 if not firstok else 0x4c2b4e if not secondok else 0x100000)]
   rows.append({'counter_before':counter,'clock_stub_return':clock,'primask':mask,'calls':calls,'stop':stop,'success':success})
Path(__file__).with_name('results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'wrapped_sha256':hashlib.sha256(blob).hexdigest(),'comparisons':rows,'limits':'Original children539254,53928c,5392f8,5392d4,5392ae,539304 and473940 composed. Poll4807fc, delay4807a0, shared-clock4d3f78 and pin480f0c explicit stubs; synthetic MMIO register, no physical drain or scheduling proof.'},indent=2)+'\n');print('PASS',len(rows))
