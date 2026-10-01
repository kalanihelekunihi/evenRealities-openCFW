#!/usr/bin/env python3
"""Bounded original-instruction tests; writes only beside this script.
External scheduler, GUI, allocator and lower BLE providers are explicit stubs.
"""
from pathlib import Path
import csv,hashlib,json,struct
import capstone,unicorn
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
BASE=0x437fe0;B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert len(B)==3523396 and hashlib.sha256(B).hexdigest()==SHA
raw={int(r['entry'],16):r for r in map(json.loads,(ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
entries=[0x4c5886,0x4c5892,0x4c5916,0x4c5dbc,0x465748,0x442d86,0x539dea,0x4b50ae,0x4b5640,0x530e30,0x531ac0,0x4e8bcc,0x4e7d20]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)
records=[];text=[]
for a in entries:
 r=raw[a];z=int(r['body_end_inclusive'],16)+1;data=B[a-BASE:z-BASE];assert hashlib.sha256(data).hexdigest()==r['body_sha256']
 ins=list(md.disasm(data,a));assert sum(i.size for i in ins)==len(data)
 calls=[];text.append('\n%08x..%08x sha256=%s'%(a,z,r['body_sha256']))
 for i in ins:
  text.append('%08x %-10s %-8s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str))
  if i.mnemonic in ('bl','b.w') and i.op_str.startswith('#'):calls.append({'site':hex(i.address),'target':i.op_str[1:]})
 records.append({'entry':hex(a),'end':hex(z),'sha256':r['body_sha256'],'raw_decompiler_succeeded':r['decompiled'],'direct_calls':calls})
(OUT/'disassembly.txt').write_text('\n'.join(text)+'\n')
def flash32(a):return struct.unpack_from('<I',B,a-BASE)[0]
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
DATA=0x20077000;CCB=0x20077200;CORE=0x20077300;PAGE=0x20077400;STOP=0x10000000
STUB={0x43d0ce:'log_flags',0x43d574:'log',0x43ce9e:'log',0x43c0e4:'fill',0x439be4:'copy',
 0x464d1c:'sync108',0x45a568:'role',0x4490cc:'tick',0x4c5a58:'dual_hold_track',0x4c5c6e:'usage_track',0x4c5c30:'dual_hold_active',0x46b0ec:'input_allowed',0x464b2e:'system_command',
 0x4646f0:'heap_alloc',0x474d16:'heap_free',0x449abe:'queue_put',0x4495e4:'flags',
 0x45f8e6:'active_page',0x45f8fc:'ui_event',0x442d64:'page_longpress_mode',0x45bbf4:'transition_busy',0x46ae9c:'factory_close',
 0x4bf990:'att_alloc',0x4bf99e:'wsf_alloc',0x4bf9b0:'wsf_free',0x52b8c8:'lock',0x52b8d0:'unlock',0x531820:'ccb',0x531ad6:'att_callback',0x4bf9ba:'wsf_send',0x4b50ba:'l2cap_transfer',0x52a4b8:'timer_start',0x43e2ea:'object_valid',0x44e498:'scroll_position',0x4e7cc0:'animate_scroll',0x4e772c:'index_changed',0x4e7b16:'scroll_boundary'}
class M:
 def __init__(self):
  self.u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS)
  self.u.mem_map(0x437000,0x35e000);self.u.mem_write(BASE,B);self.u.mem_map(0x20000000,0x100000);self.u.mem_map(STOP,4096)
  self.calls=[];self.heap=0x20080000;self.role=1;self.tick=2000;self.allow=1;self.dual=0;self.longmode=1;self.busy=0;self.alloc_no=0;self.fail_n=0;self.ccb=True;self.queue_rc=0
  self.w32(0x200036f8,0xffff);self.w32(0x20074984,0);self.w32(0x200749cc,0x1111)
  # literal-resolved role1 output queue at 0x465FCC, verified instruction at 0x465962
  self.w32(flash32(0x465fcc),0x2222)
  self.w32(flash32(0x465fa8),0x3333) if 0x20000000<=flash32(0x465fa8)<0x20100000 else None
  self.w32(CCB,CORE);self.u.mem_write(CORE,struct.pack('<HBB',23,0,0));self.u.mem_write(0x200610ac+0x60,b'\x09')
  self.w32(0x200744d0,0x20077500);self.w32(PAGE,0x42);self.u.mem_write(PAGE+11,b'\0')
  self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook)
 def w32(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def r32(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def hook(self,u,a,n,_):
  if a not in STUB:
   assert any(e<=a<int(raw[e]['body_end_inclusive'],16)+1 for e in entries),hex(a);return
  name=STUB[a];v=[u.reg_read(r) for r in R];ret=0;c={'call':name,'args':v}
  if name=='fill':u.mem_write(v[0],bytes([v[2]&255])*v[1])
  elif name=='copy':u.mem_write(v[0],bytes(u.mem_read(v[1],v[2])))
  elif name=='sync108':c['record']=bytes(u.mem_read(v[1],v[2])).hex()
  elif name=='object_valid':ret=1
  elif name=='scroll_position':ret=0
  elif name=='role':ret=self.role
  elif name=='tick':ret=self.tick
  elif name=='input_allowed':ret=self.allow
  elif name=='dual_hold_active':ret=self.dual
  elif name=='page_longpress_mode':ret=self.longmode
  elif name=='transition_busy':ret=self.busy
  elif name=='active_page':ret=PAGE
  elif name=='ui_event':c['data']=bytes(u.mem_read(v[2],8)).hex()
  elif name in ('heap_alloc','att_alloc','wsf_alloc'):
   self.alloc_no+=1
   if self.alloc_no!=self.fail_n:ret=self.heap;self.heap+=(v[0]+15)&~15
  elif name=='queue_put':
   ptr=self.r32(v[1]);c['envelope']=bytes(u.mem_read(ptr,12)).hex();c['body']=bytes(u.mem_read(self.r32(ptr+8),12)).hex();ret=self.queue_rc
  elif name=='ccb':ret=CCB if self.ccb else 0
  elif name=='wsf_send':
   c['envelope']=bytes(u.mem_read(v[1],12)).hex();p=self.r32(v[1]+4);c['packet_pointer']=hex(p);c['att_wire']=bytes(u.mem_read(p+8,struct.unpack('<H',u.mem_read(p,2))[0])).hex()
  elif name=='l2cap_transfer':c['att_wire']=bytes(u.mem_read(v[3]+8,v[2])).hex()
  if name not in ('log_flags','log','fill','copy','lock','unlock'):self.calls.append(c)
  u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def run(self,a,*args):
  self.u.reg_write(UC_ARM_REG_SP,0x200ff000);self.u.reg_write(UC_ARM_REG_LR,STOP|1)
  for r,v in zip(R,args):self.u.reg_write(r,v)
  self.u.emu_start(a|1,STOP,count=30000);assert self.u.reg_read(UC_ARM_REG_PC)==STOP
  return self.u.reg_read(UC_ARM_REG_R0)
 def named(self,n):return [c for c in self.calls if c['call']==n]
 def input(self,event,source=4,x=7,y=9):self.u.mem_write(DATA,struct.pack('<HHIBBH',source,0,event,x,y,0))
CASES=[]
def save(name,m,**extra):CASES.append({'case':name,'calls':m.calls,**extra})
for event,want in [(0,'SINGLE_CLICK'),(1,'DOUBLE_CLICK'),(3,'LONG_PRESS'),(4,'UPROLL'),(5,'DOWNROLL'),(14,'RELEASE')]:
 m=M();p=m.run(0x4c5892,event);name=B[p-BASE:p-BASE+40].split(b'\0')[0].decode();assert name==want;save('event_name_%d'%event,m,gesture_name=name,address=hex(p))
for event in (0,1,3,4,5,14):
 m=M();m.run(0x4c5916,4,event,7,9);r=bytes.fromhex(m.named('sync108')[0]['record']);assert r[:2]==b'\4\0' and struct.unpack_from('<I',r,4)[0]==event and r[8:10]==b'\7\11';save('input_pack_%d'%event,m)
for event in (0,1,3,4,5,14):
 m=M();m.input(event);m.run(0x4c5dbc,0,DATA,12,0);c=m.named('queue_put')[0];assert bytes.fromhex(c['body'])==struct.pack('<BBHII',3,7,4,event,0x70009)
 assert m.r32(0x200036f8)==(0xffff if event==14 else 4);save('manager_to_app_packet_%d'%event,m)
for name,setup in [('role2',{'role':2}),('settings_block',{'allow':0}),('dual_hold',{'dual':1})]:
 m=M()
 for k,v in setup.items():setattr(m,k,v)
 m.input(0);m.run(0x4c5dbc,0,DATA,12,0);assert not m.named('queue_put');save(name,m)
for delta,allowed in [(1000,False),(1001,True)]:
 m=M();m.w32(0x200036f8,0);m.w32(0x20074984,m.tick-delta);m.input(0);m.run(0x4c5dbc,0,DATA,12,0);assert bool(m.named('queue_put'))==allowed;save('source_arbitration_%d'%delta,m)
for fail_n in (1,2):
 m=M();m.fail_n=fail_n;assert m.run(0x465748,4,0,0,0)==0xffffffff
 assert len(m.named('heap_free'))==fail_n-1;save('app_packet_alloc_failure_%d'%fail_n,m)
m=M();m.role=2;m.run(0x465748,4,0,0,0);assert bytes.fromhex(m.named('queue_put')[0]['envelope'])[4:6]==b'\0\0';save('forward_role2_local_queue',m)
for event,want in [(0,10),(1,0x48),(3,8),(4,0x44),(5,0x45),(14,0x4a)]:
 m=M();m.u.mem_write(DATA,struct.pack('<HII',4,event,0x70009));m.run(0x442d86,DATA);c=m.named('ui_event')[0];assert c['args'][1]==want
 if event in (4,5,14):assert bytes.fromhex(c['data'])==struct.pack('<ii',9,7)
 save('display_event_%d'%event,m)
m=M();m.longmode=0;m.u.mem_write(DATA,struct.pack('<HII',4,3,0));m.run(0x442d86,DATA);assert m.named('system_command')[0]['args'][0]==3;save('longpress_normal_page_system_command3',m)
# ATT copy success and rejected-connection paths use original AttcWriteCmd,
# attMsgAlloc and attcSendMsg, not a mocked attcSendMsg.
for name,mtu,blocked,connected,fail in [('accepted',23,0,True,0),('no_connection',23,0,False,0),('mtu_too_small',5,0,True,0),('blocked',23,4,True,0),('packet_alloc_failure',23,0,True,1),('envelope_alloc_failure',23,0,True,2)]:
 m=M();m.ccb=connected;m.fail_n=fail;m.u.mem_write(CORE,struct.pack('<HBB',mtu,blocked,0));payload=bytes.fromhex('001a8a011234');m.u.mem_write(DATA,payload)
 m.run(0x539dea,1,0x10,len(payload),DATA)
 if name=='accepted':
  c=m.named('wsf_send')[0];assert c['att_wire']=='521000001a8a011234';p=int(c['packet_pointer'],16)
  m.u.mem_write(DATA,b'\xcc'*6);assert bytes(m.u.mem_read(p+11,6))==payload
  save('att_'+name,m,copy_survives_caller_overwrite=True)
 else:
  assert not m.named('wsf_send');assert len(m.named('wsf_free'))==(0 if fail==1 else 1)
  if name=='mtu_too_small':assert m.named('att_callback')[0]['args'][3]==0x77
  if name=='blocked':assert m.named('att_callback')[0]['args'][3]==0x71
  save('att_'+name,m)
# Successful ATT packet handoff: pending +8 pointer is cleared before lower call.
m=M();packet=0x20079000;m.u.mem_write(packet,struct.pack('<H',9)+bytes(6)+bytes.fromhex('521000001a8a011234'));m.w32(CCB+8,packet);m.u.mem_write(CCB+6,b'\x0a');m.run(0x530e30,CCB)
assert m.r32(CCB+8)==0 and m.named('l2cap_transfer')[0]['att_wire']=='521000001a8a011234';save('att_transfers_copy_to_l2cap',m)
m=M();m.w32(CCB+4,0x20079000);m.run(0x531ac0,CCB);assert m.r32(CCB+4)==0 and m.named('wsf_free')[0]['args'][0]==0x20079000;save('att_free_packet_clears_pointer',m)
# Dashboard action: original callback and original index navigation, GUI primitives stubbed.
for event,start,want in [(0x44,1,2),(0x45,1,0),(0x44,2,2),(0x45,0,0)]:
 m=M();m.w32(flash32(0x4e8454),0x20077600);m.w32(flash32(0x4e7ff4),start);m.w32(flash32(0x4e80dc),3)
 m.run(0x4e8bcc,event,DATA,0,0);assert m.r32(flash32(0x4e7ff4))==want
 assert bool(m.named('animate_scroll'))==(want!=start)
 if want!=start:assert m.named('animate_scroll')[0]['args'][1]==(304 if event==0x44 else 0xfffffed0)
 save('dashboard_%x_index%d'%(event,start),m,index_before=start,index_after=want)
m=M();m.w32(flash32(0x4e939c),1);m.run(0x4e8bcc,0x44,DATA,0,0);assert not m.named('animate_scroll');save('dashboard_roll_blocked_by_state',m)
(OUT/'validation.json').write_text(json.dumps({'input_sha256':SHA,'capstone':capstone.__version__,'unicorn':unicorn.__version__,'scope':'Original code, stubbed provider state and scheduling; no radio/UI hardware; logging disabled','functions':records,'case_count':len(CASES),'cases':CASES},indent=2)+'\n')
print('PASS',len(CASES),'original-code scenarios,',len(records),'body hashes')
