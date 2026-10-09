from pathlib import Path
import struct,json,hashlib
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];word=lambda a:struct.unpack_from('<I',raw,a-0x438000)[0];record=0x75d3f4;src=record+word(record);encoded=word(record+4);dest=word(record+8);end=src+(encoded>>1);assert encoded&1==0 and dest==0x20000000
out=bytearray();p=src;tokens=0
while p!=end:
 assert p<end
 token=raw[p-0x438000];p+=1;literals=token&3;match=token>>4
 if not literals:literals=raw[p-0x438000]+3;p+=1
 if match==15:match=raw[p-0x438000]+15;p+=1
 for i in range(literals-1):out.append(raw[p-0x438000]);p+=1
 if match:
  offset=raw[p-0x438000];p+=1;high=(token>>2)&3
  if high==3:high=raw[p-0x438000];p+=1
  offset+=high<<8;assert 0<offset<=len(out)
  for i in range(match+2):out.append(out[-offset])
 tokens+=1
assert len(out)==0x4558


from unicorn.arm_const import *
from unicorn import *
# Execute original compressed-data decoder, with no provider stubs.
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000)
u.mem_write(dest,b'\xa5'*0x4600);u.reg_write(UC_ARM_REG_R0,record);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
u.emu_start(0x43a11f,0x2007f000,count=1000000)
assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==record+12
assert bytes(u.mem_read(dest,len(out)))==out
assert bytes(u.mem_read(dest+len(out),64))==b'\xa5'*64
rows=[]
for old in [0,0x28,0x7f,0x80,0xa8,0xff]:
 for valid in [0,1]:
  u.mem_write(dest,bytes(out));buf=0x20006000;data=bytearray(36);data[0]=105;data[1]=0;data[2+5]=old;data[34]=valid;u.mem_write(buf,bytes(data))
  u.reg_write(UC_ARM_REG_R0,buf);u.reg_write(UC_ARM_REG_R1,6);u.reg_write(UC_ARM_REG_R2,40);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
  reached=[]
  def hook(uc,pc,size,user):
   if pc==0x43d0ce:
    reached.append('diagnostic-level');uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x53b6f1,0x2007f000,count=10000);u.hook_del(h)
  assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
  got=bytes(u.mem_read(buf,36));expect=bytearray(data)
  if valid:expect[7]=40;expect[35]=1
  assert got==expect
  rows.append(dict(previous_byte=old,valid=valid,new_byte=got[7],dirty=got[35],provider_calls=reached))

commits=[]
for old in [0x80]:
 data=bytearray(36);data[0]=105;data[2:34]=bytes(range(32));data[7]=40;data[34]=1;data[35]=1;u.mem_write(buf,bytes(data));events=[]
 def hook_commit(uc,pc,size,user):
  regs=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
  if pc in [0x43d0ce,0x53b966,0x53b9be,0x4910f4,0x53b032,0x53b08e]:
   if pc==0x53b032:events.append(dict(kind='register-write',register=regs[0],value=regs[1],length=regs[2]))
   if pc==0x53b08e:events.append(dict(kind='block-write',register=regs[0],data=bytes(uc.mem_read(regs[1],regs[2])).hex(),length=regs[2]))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 h=u.hook_add(UC_HOOK_CODE,hook_commit);u.reg_write(UC_ARM_REG_R0,buf);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(0x53ba33,0x2007f000,count=10000);u.hook_del(h)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 checksum=(255-sum(data[2:34]))&255
 assert any(e.get('register')==0x60 and e.get('value')==checksum for e in events)
 assert any(e.get('register')==0x3e and e.get('value')==105 for e in events)
 assert bytes(u.mem_read(buf+35,1))==b'\0'
 commits.append(dict(previous_byte_label=old,checksum=checksum,events=events,limits='Synthetic post-update block; mode, transport and delay calls return success; actual write wrapper and checksum instructions execute. Previous-byte label does not affect post-update block.'))
(D/'commit-instruction-results.json').write_text(json.dumps(dict(status='PASS',cases=commits),indent=2)+'\n')
(D/'original-instruction-results.json').write_text(json.dumps(dict(status='PASS',decoder_compared_bytes=len(out),decoded_sha256=hashlib.sha256(out).hexdigest(),table_bytes=out[0x6ec:0x724].hex(),update_cases=rows,limits=['Original decoder versus independent Python, no callbacks stubbed in decoder.','Original generic update with actual initialized table; diagnostic-level provider returns zero.','Update buffer valid flag synthetic; no device read, bus operation, configure runner, commit or physical gauge behavior executed.']),indent=2)+'\n')
print('PASS original decoder',len(out),'bytes; original update',len(rows),'cases')
