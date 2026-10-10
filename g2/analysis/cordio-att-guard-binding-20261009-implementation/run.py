from unicorn import *
from unicorn.arm_const import *
from pathlib import Path
import json,hashlib,struct
R=Path('/repo'); b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cases=[('none',0,0x13,1,0,0),('mismatch',1,0x13,1,0,0),('write-short',9,0x13,0,1,0),('write-min',9,0x13,1,1,1),('mtu-short',1,3,2,1,0),('mtu-min',1,3,3,1,1),('invalid-method',18,0x25,1,0,0),('null-handler',10,0x15,1,1,0)]
results=[]
for name,event,opcode,length,timer,proc in cases:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,b[32:]);u.mem_map(0x20000000,0x100000)
 c=0x20070000;p=0x20071000;m=0x20072000;stop=0x400000
 u.mem_write(c,struct.pack('<I',m));u.mem_write(c+6,bytes([event,1]));u.mem_write(c+12,struct.pack('<H',0x1234));u.mem_write(c+40,bytes([0,1]));u.mem_write(m+2,bytes([2]));u.mem_write(p+8,bytes([opcode]));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,stop|1)
 for reg,v in [(UC_ARM_REG_R0,c),(UC_ARM_REG_R1,length),(UC_ARM_REG_R2,p)]:u.reg_write(reg,v)
 logs=[];targets={x&~1 for x in struct.unpack('<18I',b[0x700964-0x438000+32:0x700964-0x438000+104]) if x}
 def hook(u,a,size,data):
  if a==stop:u.emu_stop();return
  if a==0x52a4d2:logs.append({'kind':'timer','argument':u.reg_read(UC_ARM_REG_R0)});u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
  if a in targets:
   e=u.reg_read(UC_ARM_REG_R3);raw=bytes(u.mem_read(e,12));logs.append({'kind':'processor','address':hex(a),'length':u.reg_read(UC_ARM_REG_R1),'event':raw[2],'status':raw[3],'value_length':int.from_bytes(raw[8:10],'little'),'handle':int.from_bytes(raw[10:12],'little')});u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x4b5449,0,count=1000)
 counts=[sum(x['kind']==k for x in logs) for k in ['timer','processor']];assert counts==[timer,proc],(name,logs);assert u.reg_read(UC_ARM_REG_PC)==stop
 results.append(dict(name=name,out_request_event=event,opcode=opcode,length=length,expected_counts=[timer,proc],logs=logs,pass_=True))
Path('/tmp/att-fixtures/results.json').write_text(json.dumps(results,indent=2)+'\n');print('8 original-byte cases PASS')
