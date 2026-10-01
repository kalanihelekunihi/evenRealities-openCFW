#!/usr/bin/env python3
"""Stock PCM routing/LC3 geometry/stream layout; codec DSP and transport stubbed."""
from pathlib import Path
import json,struct,hashlib,capstone,unicorn
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R9,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();BASE=0x437fe0
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';assert hashlib.sha256(B).hexdigest()==SHA
raw={int(r['entry'],16):r for r in map(json.loads,(ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
entries=[0x43a11e,0x57a900,0x57a940,0x57ab78,0x57acd0,0x57adf8,0x5915dc,0x590e64,0x590dc8,0x590d3c,0x590d74,0x590e6c,0x590f68,0x590f78,0x475d78,0x53c6f2]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS);records=[];lines=[]
for a in entries:
 r=raw[a];z=int(r['body_end_inclusive'],16)+1;data=B[a-BASE:z-BASE];assert hashlib.sha256(data).hexdigest()==r['body_sha256']
 ins=list(md.disasm(data,a));assert sum(i.size for i in ins)==len(data)
 records.append({'entry':hex(a),'end':hex(z),'sha256':r['body_sha256']});lines.append('\n%s..%s sha256=%s'%(hex(a),hex(z),r['body_sha256']));lines.extend('%08x %-10s %-8s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str) for i in ins)
(OUT/'disassembly.txt').write_text('\n'.join(lines)+'\n')
def f32(a):return struct.unpack_from('<I',B,a-BASE)[0]
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];STOP=0x10000000;CALLBACK=STOP+0x1000
# Fresh stock SSRAM initializer: supplies actual LC3 config, no ignored outputs used.
u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS);u.mem_map(0x437000,0x35e000);u.mem_write(BASE,B);u.mem_map(0x20000000,0x400000);u.mem_map(STOP,8192)
u.reg_write(UC_ARM_REG_SP,0x203ff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_R9,0);u.reg_write(R[0],0x75d404);u.emu_start(0x43a11f,STOP,count=10000000);assert u.reg_read(UC_ARM_REG_PC)==STOP
RAM=bytes(u.mem_read(0x20080000,769646));assert hashlib.sha256(RAM).hexdigest()=='a5be949c41cf1e9a7d4a6b4aa6e3a6cb2f9c9bcb3a04a866d15e49e3976a7d0c'
CONFIG=f32(0x57b3e4);SLOTS=f32(0x57b3b4);SEQ=f32(0x57b3e8);PCM=0x20078000;OUTPUT=0x2007a000;LEN=0x2007b000
assert struct.unpack_from('<7I',RAM,CONFIG-0x20080000)==(0,10000,16000,1,0,32000,0)
# Get I2S accessor's direct address from authenticated DMA function call metadata.
dma_callees=[int(a,16) for a in raw[0x53c6f2]['callees']];known={0x4490cc,0x57adf8,0x43d0ce,0x43d574,0x43ce9e};dma_get=next(a for a in dma_callees if a not in known)
STUB={0x43d0ce:'log',0x43d574:'log',0x43ce9e:'log',0x43dacc:'hexdump',0x43c0e4:'fill',0x439be4:'copy',0x4490cc:'tick',0x591bfc:'algorithm',0x591374:'lc3_setup',0x59138a:'lc3_encode',0x4487ac:'ota_active',0x47564e:'transport_enqueue',dma_get:'i2s_buffer',CALLBACK:'pcm_callback'}
class M:
 def __init__(self):
  self.u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS);self.u.mem_map(0x437000,0x35e000);self.u.mem_write(BASE,B);self.u.mem_map(0x20000000,0x400000);self.u.mem_write(0x20080000,RAM);self.u.mem_map(STOP,8192)
  self.calls=[];self.fail_frame=-1;self.frame=0;self.ota=0;self.tick=1000;self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook)
 def w32(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def r32(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def hook(self,u,a,n,_):
  if a not in STUB:
   assert any(e<=a<int(raw[e]['body_end_inclusive'],16)+1 for e in entries),hex(a);return
  name=STUB[a];v=[u.reg_read(r) for r in R];c={'call':name,'args':v};ret=0
  if name=='fill':u.mem_write(v[0],bytes([v[2]&255])*v[1])
  elif name=='copy':u.mem_write(v[0],bytes(u.mem_read(v[1],v[2])))
  elif name=='tick':ret=self.tick
  elif name=='algorithm':u.mem_write(v[2],struct.pack('<H',0x1234));u.mem_write(v[3],struct.pack('<h',-123))
  elif name=='lc3_setup':ret=0x2007c000
  elif name=='lc3_encode':
   size,out=struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8));c['size']=size;c['output']=hex(out);c['frame_index']=self.frame
   if self.frame==self.fail_frame:ret=0xffffffff
   else:u.mem_write(out,bytes([0xa0+self.frame])*size)
   self.frame+=1
  elif name=='ota_active':ret=self.ota
  elif name=='transport_enqueue':
   p,size=struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8));c['payload']=bytes(u.mem_read(p,size)).hex();c['length']=size;c['pointer']=hex(p)
  elif name=='i2s_buffer':self.w32(v[0],PCM);self.w32(v[1],3200)
  if name not in ('log','fill','copy','tick'):self.calls.append(c)
  u.reg_write(R[0],ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def run(self,a,*args):
  sp=0x203ff000;self.u.reg_write(UC_ARM_REG_SP,sp);self.u.reg_write(UC_ARM_REG_LR,STOP|1)
  for r,v in zip(R,args):self.u.reg_write(r,v)
  for i,v in enumerate(args[4:]):self.w32(sp+4*i,v)
  self.u.emu_start(a|1,STOP,count=100000);assert self.u.reg_read(UC_ARM_REG_PC)==STOP
  return self.u.reg_read(R[0])
 def named(self,n):return [c for c in self.calls if c['call']==n]
CASES=[]
def save(name,m,**extra):CASES.append({'case':name,'calls':m.calls,**extra})
for fmt,expected in [(0,2),(1,4),(2,3),(3,4),(4,0)]:
 m=M();assert m.run(0x57a900,fmt)==expected;save('sample_bytes_%d'%fmt,m,result=expected)
m=M();assert m.run(0x590e64,10000,16000)==160 and m.run(0x590f78,10000,32000)==40;save('default_geometry_160_samples_40_bytes',m)
for channels,channel,n in [(1,0,1600),(2,1,3200)]:
 m=M();m.w32(CONFIG+12,channels);m.w32(CONFIG+16,channel);assert m.run(0x57a940,PCM,n,OUTPUT,LEN,CONFIG)==0
 enc=m.named('lc3_encode');assert len(enc)==5 and m.r32(LEN)==200 and [c['args'][2] for c in enc]==[PCM+2*channel+320*channels*i for i in range(5)]
 assert all(c['args'][3]==channels and c['size']==40 for c in enc);save('encode_%d_channels'%channels,m)
for name,n,fail in [('unaligned',1599,-1),('zero',0,-1),('first_error',1600,0),('second_error',1600,1)]:
 m=M();m.fail_frame=fail;m.w32(LEN,99);ret=m.run(0x57a940,PCM,n,OUTPUT,LEN,CONFIG)
 assert ret==(0 if n==0 else 0xffffffff);assert m.r32(LEN)==(99 if n==1599 else 40 if fail==1 else 0);save('encode_'+name,m,output_length=m.r32(LEN))
for source in (0,1):
 m=M();assert m.run(0x57ab78,7,source,CALLBACK|1)==0;m.run(0x57adf8,source,PCM,3200,0);assert len(m.named('pcm_callback'))==1 and not m.named('transport_enqueue')
 assert m.run(0x57acd0,8,source)==0xffffffff and m.r32(SLOTS+source*12+8)==CALLBACK|1
 assert m.run(0x57acd0,7,source)==0 and m.r32(SLOTS+source*12+8)==0;save('registered_source%d_callback_and_owner_check'%source,m)
m=M();m.run(0x57ab78,7,0,CALLBACK|1);m.run(0x57ab78,8,0,CALLBACK|1);assert m.r32(SLOTS)==8;save('registration_replaces_previous_owner',m)
for name,source,ptr,length in [('source1_no_callback',1,PCM,3200),('source2',2,PCM,3200),('null_pcm',0,0,3200),('zero_length',0,PCM,0)]:
 m=M();m.run(0x57adf8,source,ptr,length,0);assert not m.named('algorithm') and not m.named('transport_enqueue');save(name,m)
for name,fail,seq,ota in [('normal',-1,1,0),('sequence_wrap',-1,255,0),('encoder_first_error',0,1,0),('encoder_second_error',1,1,0),('ota_suppressed',-1,1,1)]:
 m=M();m.fail_frame=fail;m.ota=ota;m.u.mem_write(SEQ,bytes([seq]));m.run(0x57adf8,0,PCM,3200,0)
 assert bytes(m.u.mem_read(SEQ,1))==bytes([(seq+1)&255]);sent=m.named('transport_enqueue');assert bool(sent)==(ota==0)
 if sent:
  c=sent[0];p=bytes.fromhex(c['payload']);assert c['args']==[1,1,0,0] and len(p)==205 and p[204]==seq
  encoded=200 if fail<0 else 40*fail;assert p[encoded:encoded+4]==bytes.fromhex('341285ff')
  assert p[encoded+4:204]==bytes(200-encoded)
 save('fallback_'+name,m)
for age,expect in [(40,True),(41,False)]:
 m=M();m.w32(0x2007d008,m.tick-age);m.run(0x53c6f2,0x2007d000);assert bool(m.named('transport_enqueue'))==expect;save('dma_age%d_ticks'%age,m)
report={'input_sha256':SHA,'initializer':{'descriptor':'0x75d404','output_sha256':hashlib.sha256(RAM).hexdigest(),'output_bytes':len(RAM)},'config':{'address':hex(CONFIG),'words':list(struct.unpack_from('<7I',RAM,CONFIG-0x20080000))},'functions':records,'case_count':len(CASES),'cases':CASES,'scope':'original routing/frame geometry/packet assembly; actual DSP, LC3 bitstream encoder, I2S acquisition and transport enqueue are stubs'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(CASES),'cases;',len(records),'body hashes')
