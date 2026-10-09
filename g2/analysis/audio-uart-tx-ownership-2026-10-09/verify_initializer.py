from pathlib import Path
import struct,json,hashlib
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=D.parents[2];raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];base=0x438000;record=0x75d3f4;rel,packed,dst=struct.unpack_from('<III',raw,record-base);src=record+rel;stream=raw[src-base:src-base+(packed>>1)]
p=0;out=bytearray()
while p<len(stream):
 tok=stream[p];p+=1;lit=tok&3
 if lit==0:lit=stream[p]+3;p+=1
 match=tok>>4
 if match==15:match=stream[p]+15;p+=1
 for _ in range(lit-1):out.append(stream[p]);p+=1
 if match:
  low=stream[p];p+=1;high=(tok>>2)&3
  if high==3:high=stream[p];p+=1
  distance=low+(high<<8);assert 0<distance<=len(out)
  for _ in range(match+2):out.append(out[-distance])
assert p==len(stream);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(base,0x360000);u.mem_write(base,raw);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x100001);u.reg_write(UC_ARM_REG_R0,record);u.reg_write(UC_ARM_REG_PC,0x43a11f)
steps=0
while u.reg_read(UC_ARM_REG_PC)!=0x100000:
 u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1);steps+=1
 assert steps<1000000
actual=bytes(u.mem_read(dst,len(out)));assert actual==bytes(out);assert u.reg_read(UC_ARM_REG_R0)==record+12
channels=[]
for ch in range(4):
 a=0xd2c+ch*28;words=struct.unpack_from('<6I',out,a);channels.append({'channel':ch,'module':words[0],'handle':hex(words[1]),'pins':hex(words[2]),'config':hex(words[3]),'queues':hex(words[4]),'callback':hex(words[5]),'active':out[a+24],'completion':out[a+25]})
def readwords(a,n):
 data=raw[a-base:a-base+n*4] if base<=a<base+len(raw) else bytes(u.mem_read(a,n*4))
 return list(struct.unpack('<'+str(n)+'I',data))
qptr=int(channels[1]['queues'],16);qwords=readwords(qptr,4);config=int(channels[1]['config'],16);cfg=readwords(config,6)
result={'status':'PASS','cases':1,'raw_sha256':hashlib.sha256(raw).hexdigest(),'record':hex(record),'source':hex(src),'packed':hex(packed),'input_bytes':len(stream),'destination':hex(dst),'output_bytes':len(out),'decoded_sha256':hashlib.sha256(out).hexdigest(),'original_instruction_steps':steps,'channels':channels,'channel1_queue_words':list(map(hex,qwords)),'channel1_config_words':list(map(hex,cfg)),'limits':'Static decoder matches original instruction-stepped decoder over entire initialized SRAM record. Not full reset/runtime; no peripheral initialization or hardware execution.'}
(D/'initializer-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
