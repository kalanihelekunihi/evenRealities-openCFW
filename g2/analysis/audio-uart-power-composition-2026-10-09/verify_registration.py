from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=D.parents[2];raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
# Static decoder geometry already validated against original instructions by TX batch.
record=0x75d3f4;rel,packed,dst=struct.unpack_from('<III',raw,record-0x438000);stream=raw[record+rel-0x438000:record+rel-0x438000+(packed>>1)];p=0;out=bytearray()
while p<len(stream):
 tok=stream[p];p+=1;lit=tok&3
 if lit==0:lit=stream[p]+3;p+=1
 match=tok>>4
 if match==15:match=stream[p]+15;p+=1
 out.extend(stream[p:p+lit-1]);p+=lit-1
 if match:
  low=stream[p];p+=1;high=(tok>>2)&3
  if high==3:high=stream[p];p+=1
  dist=low+(high<<8)
  for _ in range(match+2):out.append(out[-dist])
assert hashlib.sha256(out).hexdigest()=='df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743';minor=struct.unpack_from('<I',out,0x1e8)[0]
def run(major,minor):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_write(dst,bytes(out));u.mem_map(0x40020000,0x3000);u.mem_map(0x100000,0x1000)
 u.mem_write(0x4002000c,struct.pack('<I',major));u.mem_write(0x200001e8,struct.pack('<I',minor));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x100001);u.reg_write(UC_ARM_REG_PC,0x480435);stop=[];steps=0
 def hook(uc,pc,size,user):
  if pc==0x100000:stop.append('return');uc.emu_stop();return
  first=int.from_bytes(uc.mem_read(0x20073270,4),'little')&~1
  if first and pc==first:stop.append('before-init-callback');uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 for _ in range(3000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1);steps+=1
 assert stop
 table=struct.unpack('<15I',u.mem_read(0x20073270,60))
 return {'major_fixture':hex(major),'revision_fixture':minor,'stop':stop,'instruction_steps':steps,'table':list(map(hex,table)),'group':hex(table[1]),'pre':hex(table[3]),'post':hex(table[4]),'selection_flags':bytes(u.mem_read(0x20074f64,6)).hex()}
rows=[run(ma,mi) for ma,mi in itertools.product([0x21,0x22,0x23,0x24],[0,1,2,3])]
(D/'registration-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'raw_sha256':hashlib.sha256(raw).hexdigest(),'initializer':'0x480434','authenticated_initialized_revision_word':minor,'rows':rows,'limits':'Actual unchanged registrar instructions and authenticated decoded SRAM; silicon revision supplied synthetic. Stops before selected init callback, no boot/runtime registration occurrence or callback initialization effects asserted.'},indent=2)+'\n');print('REGISTRATION',len(rows),'initialized revision word',minor)
for row in rows:print(row['major_fixture'],row['revision_fixture'],row['group'],row['pre'],row['post'])
