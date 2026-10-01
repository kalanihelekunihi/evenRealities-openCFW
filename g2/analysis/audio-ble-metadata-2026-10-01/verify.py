#!/usr/bin/env python3
"""Stock stream queue/ESS/ATT framing and metadata arithmetic. Providers explicit."""
from pathlib import Path
import json,struct,hashlib,math,capstone,unicorn
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_C1_C0_2,UC_ARM_REG_FPEXC
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();BASE=0x437fe0;SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';assert hashlib.sha256(B).hexdigest()==SHA
raw={int(r['entry'],16):r for r in map(json.loads,(ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
entries=[0x47564e,0x47538c,0x475524,0x47530a,0x4be2f6,0x4be24e,0x4be228,0x533ed8,0x533c6c,0x59173a,0x591ba4,0x5915ea,0x591c26]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS);records=[];lines=[]
for a in entries:
 r=raw[a];z=int(r['body_end_inclusive'],16)+1;data=B[a-BASE:z-BASE];assert hashlib.sha256(data).hexdigest()==r['body_sha256']
 ins=list(md.disasm(data,a));assert sum(i.size for i in ins)==len(data)
 records.append({'entry':hex(a),'end':hex(z),'sha256':r['body_sha256']});lines.append('\n%s..%s sha256=%s'%(hex(a),hex(z),r['body_sha256']));lines.extend('%08x %-10s %-8s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str) for i in ins)
(OUT/'disassembly.txt').write_text('\n'.join(lines)+'\n')
def f32(a):return struct.unpack_from('<I',B,a-BASE)[0]
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];STOP=0x10000000;DATA=0x20078000;CCB=0x2007b000;MTU=0x2007b100
TX=f32(0x475d70);ESS=f32(0x4be38c);E0=f32(0x591cb0);E1=f32(0x591cc0);WINDOW=f32(0x591d04)
BODY=bytes([0x55])*200+bytes.fromhex('1200d3ff07')
STUB={0x43d0ce:'log',0x43d574:'log',0x43ce9e:'log',0x439be4:'copy',0x43c0e4:'fill',0x474cd2:'heap_alloc',0x474d16:'heap_free',0x4780f8:'fast_mode',0x478160:'request_fast',0x449bc8:'queue_count',0x449bbc:'queue_capacity',0x449abe:'queue_put',0x449b3c:'queue_get',0x449238:'thread_flags',0x449a6e:'unused',0x4d0c2c:'take_tx_token',0x46efd8:'connection_state',0x4487ac:'ota',0x4d0c36:'tx_complete',0x4bf99e:'wsf_alloc',0x4bf9ba:'wsf_send',0x4bf9b0:'wsf_free',0x52b8c8:'lock',0x52b8d0:'unlock',0x534f14:'atts_ccb',0x52c928:'change_aware',0x533934:'att_callback',0x4b50ae:'att_alloc',0x47cc60:'u64_divmod',0x5918cc:'correlation',0x449a46:'queue_new'}
# Resolve CMSIS queue-new target without guessing its symbol address.
for target in raw[0x47530a]['callees']:
 if target not in ('005fa0a4',):STUB[int(target,16)]='queue_new'
class M:
 def __init__(self,fp=False):
  self.u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|(0 if fp else unicorn.UC_MODE_MCLASS));self.u.mem_map(0x437000,0x35e000);self.u.mem_write(BASE,B);self.u.mem_map(0x20000000,0x400000);self.u.mem_map(STOP,4096)
  self.u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);self.u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  self.w32(TX+12,0x1111);self.w32(TX+8,0x2222);self.u.mem_write(ESS,bytes([1,9,1,1]));self.u.mem_write(DATA,BODY);self.w32(CCB+16,MTU);self.u.mem_write(MTU,struct.pack('<HBB',208,0,0));self.u.mem_write(0x200610ac+0x60,b'\x03')
  self.calls=[];self.queue=[];self.wsf=[];self.heap=0x20080000;self.count=0;self.cap=150;self.putrc=0;self.fast=1;self.token=1;self.ota=0;self.fail_heap=False;self.fail_alloc=False;self.poison=False;self.rad=0.;self.connection=True;self.aware=True
  self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook)
 def w32(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def r32(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def hook(self,u,a,n,_):
  if a not in STUB:
   assert any(e<=a<int(raw[e]['body_end_inclusive'],16)+1 for e in entries),hex(a);return
  name=STUB[a];v=[u.reg_read(r) for r in R];c={'call':name,'args':v};ret=0
  if name=='fill':u.mem_write(v[0],bytes([v[2]&255])*v[1])
  elif name=='copy':u.mem_write(v[0],bytes(u.mem_read(v[1],v[2])))
  elif name=='queue_new':ret=0x1111
  elif name in ('heap_alloc','wsf_alloc','att_alloc'):
   if not (self.fail_heap if name=='heap_alloc' else self.fail_alloc):ret=self.heap;self.heap+=(v[0]+31)&~31
   c['result']=ret
  elif name=='heap_free' and self.poison:u.mem_write(v[0],b'\xdd'*216)
  elif name=='fast_mode':ret=self.fast
  elif name=='queue_count':ret=self.count
  elif name=='queue_capacity':ret=self.cap
  elif name=='queue_put':
   ret=self.putrc;p=self.r32(v[1]);c['record']=bytes(u.mem_read(p,213)).hex()
   if not ret:self.queue.append(p)
  elif name=='queue_get':
   if self.queue:self.w32(v[1],self.queue.pop(0))
   else:ret=0xfffffffd
  elif name=='take_tx_token':ret=self.token
  elif name=='ota':ret=self.ota
  elif name=='wsf_send':
   p=v[1];self.wsf.append(p);c['message']=bytes(u.mem_read(p,12)).hex()
   if bytes(u.mem_read(p+2,1))==b'\x21':
    packet=self.r32(p+4);length=struct.unpack('<H',u.mem_read(packet,2))[0];c['att_wire']=bytes(u.mem_read(packet+8,length)).hex()
  elif name=='atts_ccb':ret=CCB if self.connection else 0
  elif name=='change_aware':ret=int(self.aware)
  elif name=='u64_divmod':
   num=v[0]|(v[1]<<32);den=v[2]|(v[3]<<32);q,r=divmod(num,den);ret=q&0xffffffff;u.reg_write(R[1],q>>32);u.reg_write(R[2],r&0xffffffff);u.reg_write(R[3],r>>32);c['numerator']=num;c['denominator']=den;c['quotient']=q
  elif name=='correlation':
   ptr=self.r32(u.reg_read(UC_ARM_REG_SP));u.mem_write(ptr,struct.pack('<d',self.rad));c['radians']=self.rad
  if name not in ('log','copy','lock','unlock'):self.calls.append(c)
  u.reg_write(R[0],ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def run(self,a,*args):
  sp=0x203ff000;self.u.reg_write(UC_ARM_REG_SP,sp);self.u.reg_write(UC_ARM_REG_LR,STOP|1)
  for r,v in zip(R,args):self.u.reg_write(r,v)
  for i,v in enumerate(args[4:]):self.w32(sp+4*i,v)
  self.u.emu_start(a|1,STOP,count=100000);assert self.u.reg_read(UC_ARM_REG_PC)==STOP
  return self.u.reg_read(R[0])
 def named(self,n):return [c for c in self.calls if c['call']==n]
 def enqueue(self):return self.run(0x47564e,1,1,0,0,DATA,205)
 def consume(self):self.run(0x47538c)
 def dispatch_ess(self):
  p=self.wsf.pop(0);self.run(0x4be24e,p)
CASES=[]
def save(name,m,**extra):CASES.append({'case':name,'calls':m.calls,**extra})
m=M();m.run(0x47530a);assert m.named('queue_new')[0]['args'][:2]==[150,4];save('queue_configuration_150_pointers',m)
m=M();assert m.enqueue()==0;rec=m.queue[0];assert m.r32(rec)==2 and m.r32(rec+4)==205 and bytes(m.u.mem_read(rec+8,205))==BODY
m.u.mem_write(DATA,b'\xcc'*205);m.consume();assert m.named('heap_free');m.dispatch_ess();wire=bytes.fromhex(m.named('wsf_send')[-1]['att_wire']);assert wire==bytes.fromhex('1b6408')+BODY
save('copied_queue_to_raw_ESS_ATT_notification',m)
for count,expected in [(74,True),(75,False),(149,False)]:
 m=M();m.count=count;assert m.enqueue()==0;assert bool(m.queue)==expected and bool(m.named('heap_free'))!=expected;save('queue_watermark_%d'%count,m)
for name in ['no_queue','allocation_failure','queue_put_failure','not_fast_mode']:
 m=M()
 if name=='no_queue':m.w32(TX+12,0)
 if name=='allocation_failure':m.fail_heap=True
 if name=='queue_put_failure':m.putrc=0xfffffffd
 if name=='not_fast_mode':m.fast=0
 ret=m.enqueue();assert ret==(0 if name=='not_fast_mode' else 0xffffffff)
 if name=='not_fast_mode':assert m.named('request_fast') and m.queue
 save(name,m)
m=M();m.enqueue();m.token=0;m.consume();assert not m.wsf and m.named('heap_free');save('token_timeout_drops_and_frees',m)
m=M();m.enqueue();assert m.run(0x475524)==1 and not m.queue and m.named('heap_free');save('queue_clear_discards_record',m)
for name in ['disconnected','ccc_disabled','ota','wsf_alloc_failure']:
 m=M();m.enqueue()
 if name=='disconnected':m.u.mem_write(ESS,b'\0')
 if name=='ccc_disabled':m.u.mem_write(ESS+2,b'\0')
 if name=='ota':m.ota=1
 if name=='wsf_alloc_failure':m.fail_alloc=True
 m.consume();assert not m.wsf and m.named('tx_complete') and m.named('heap_free');save('ess_drop_'+name,m)
for mtu,accepted in [(207,False),(208,True),(247,True)]:
 m=M();m.u.mem_write(MTU,struct.pack('<HBB',mtu,0,0));m.enqueue();m.consume();m.dispatch_ess();assert bool([c for c in m.named('wsf_send') if 'att_wire' in c])==accepted
 if not accepted:assert m.named('att_callback')[0]['args'][2]==0x77
 save('att_mtu_%d'%mtu,m)
m=M();m.poison=True;m.enqueue();m.consume();m.dispatch_ess();assert bytes.fromhex(m.named('wsf_send')[-1]['att_wire'])[3:]==b'\xdd'*205;save('synthetic_delayed_ESS_reads_released_queue_buffer',m)
# Metadata0: integer ratio of current channel mean-square to ten-window baseline.
for name,left,right,baseline in [('unity',100,100,100),('ratio18',100,300,10),('zero_channel',0,300,10),('truncate_u16',65536,65536,0)]:
 m=M();m.u.mem_write(E0,struct.pack('<Q',left));m.u.mem_write(E1,struct.pack('<Q',right));m.u.mem_write(WINDOW,struct.pack('<10Q',*([baseline]*10)));ret=m.run(0x59173a,DATA,3200)
 expected=(((left+right)//2+1)//(baseline+1))&65535 if left and right else 0
 assert ret==expected;save('SSR_'+name,m,result=ret)
# Real deinterleave/mono and mean-square preprocessing, arithmetic division stub only.
m=M();m.u.mem_write(DATA,struct.pack('<hh',10,30)*800);assert m.run(0x5915ea,DATA,3200,0,0)==0
assert struct.unpack('<Q',m.u.mem_read(E0,8))[0]==100 and struct.unpack('<Q',m.u.mem_read(E1,8))[0]==900
front=f32(0x591c9c);assert bytes(m.u.mem_read(front,1600))==struct.pack('<h',20)*800
m.u.mem_write(WINDOW,struct.pack('<10Q',*([100]*10)));assert m.run(0x59173a,DATA,3200)==4
save('stereo_10_30_to_mono20_and_SSR4',m)
m=M();m.u.mem_write(DATA,struct.pack('<hh',3,-3));assert m.run(0x591c26,DATA,4)==0
assert struct.unpack('<Q',m.u.mem_read(WINDOW,8))[0]==9 and m.r32(f32(0x591d00))==1
save('baseline_window_mean_square9_and_advance',m)
# Metadata1: execute original double multiply/divide/conversion, correlation stub supplies radians.
for rad,degrees in [(0.,0),(math.pi/2,90),(-math.pi/2,-90),(0.5,28),(-0.5,-28)]:
 m=M(fp=True);m.rad=rad;ret=m.run(0x591ba4);signed=ret if ret<0x80000000 else ret-0x100000000;assert signed==degrees;save('angle_%s_radians'%rad,m,degrees=signed)
report={'input_sha256':SHA,'functions':records,'case_count':len(CASES),'cases':CASES,'scope':'original queue, drain, ESS and ATT packet construction; RTOS, allocator backing, ATT connection state, uint64 division and angle correlation provider stubbed'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(CASES),'cases;',len(records),'body hashes')
