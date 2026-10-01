#!/usr/bin/env python3
"""Exercise original G2 ring protocol/ownership instructions with offline stubs.
Only writes disassembly.txt and validation.json in this directory.
"""
from pathlib import Path
import csv, hashlib, json, struct
import capstone, unicorn
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
P=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
B=P.read_bytes(); BASE=0x437fe0
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert len(B)==3523396 and hashlib.sha256(B).hexdigest()==SHA
rows={int(r['address'],16):r for r in csv.DictReader((ROOT/'g2/symbols/apollo_main.tsv').open(),delimiter='\t')}
# The symbol seed has no hash for 0x472244 and overstates its end. Use the
# authenticated raw-export body range/hash (ends at 0x4722cc), not its literal tail.
for line in (ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines():
 r=json.loads(line)
 if r['entry']=='00472244':
  rows[0x472244]['end']=hex(int(r['body_end_inclusive'],16)+1)
  rows[0x472244]['stock_sha256']=r['body_sha256']
# Primary bodies plus narrowly inspected providers; previous batch functions are
# executed for the ownership chain without claiming newly recovered coverage.
ENTRIES=[0x472244,0x4722d8,0x472362,0x472378,0x4723d6,0x472426,0x472546,
 0x47263c,0x47269e,0x4727aa,0x4728a0,0x4728b2,0x472988,0x4c4de8,0x4c507e,
 0x4c548c,0x4c549c,0x4d0b36,0x4d0b64,0x4d0c36,0x4bf9ba,0x47697e]
PREVIOUS=[0x4c4b7e,0x4c4910,0x4c48ac]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)
records=[]; lines=[]
for a in ENTRIES:
 r=rows[a];z=int(r['end'],16);data=B[a-BASE:z-BASE]
 digest=hashlib.sha256(data).hexdigest();assert digest==r['stock_sha256'],hex(a)
 ins=list(md.disasm(data,a));assert sum(i.size for i in ins)==len(data),hex(a)
 calls=[];lines.append('\n%s %08x..%08x sha256=%s'%(r['name'] or 'unnamed',a,z,digest))
 for i in ins:
  tail=''
  if i.mnemonic in ('bl','b.w') and i.op_str.startswith('#'):
   t=int(i.op_str[1:],0);name=rows.get(t,{}).get('name','');tail=' ; '+name
   calls.append({'site':hex(i.address),'target':hex(t),'name':name})
  lines.append('%08x %-10s %-8s %s%s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str,tail))
 records.append({'entry':hex(a),'end':hex(z),'stock_name':r['name'],'sha256':digest,'calls':calls})
(OUT/'disassembly.txt').write_text('\n'.join(lines)+'\n')
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
DATA=0x20077000; STOP=0x10000000; STACK=0x200ff000; CTX=0x20074074; HANDLES=0x20077500
STUBS={0x43d0ce:'log_flags',0x43d574:'log',0x43ce9e:'log',0x43dacc:'dump',
 0x43c0e4:'fill',0x439be4:'copy',0x4c4b7e:'send',0x4c5916:'input_event',
 0x4c659a:'battery',0x4490cc:'ticks',0x48eb32:'telemetry',0x476ace:'remove_delayed',
 0x47697e:'delayed',0x4a2914:'owner',0x4bc418:'phone_ring_info',0x4a271e:'link_ready',
 0x4a2190:'ring_mac',0x4a2c9c:'unpair',0x474cd2:'heap_alloc',0x474d16:'heap_free',
 0x449abe:'queue_put',0x449b3c:'queue_get',0x449238:'thread_flags',
 0x44994e:'sem_acquire',0x449a0e:'sem_count',0x4499b8:'sem_release',0x449376:'delay',
 0x4bf99e:'wsf_alloc',0x52b97c:'wsf_queue',0x4bf9de:'wsf_enq',0x52b95e:'wsf_ready',
 0x4b73c4:'role',0x539dea:'write_cmd',0x4497b6:'mutex_take',0x44981c:'mutex_release',
 0x4494d8:'timer_stop',0x4767a8:'timer_callback'}
class M:
 def __init__(self,integrated=False):
  self.u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS)
  self.u.mem_map(0x437000,0x35e000);self.u.mem_write(BASE,B)
  self.u.mem_map(0x20000000,0x100000);self.u.mem_map(STOP,4096)
  self.calls=[];self.heap=0x20080000;self.queue=[];self.wsf=[];self.integrated=integrated
  self.fail_alloc=False;self.queue_rc=0;self.sem_rc=0;self.sem_count=0;self.owner=1;self.tick=1000
  self.stub=dict(STUBS)
  if integrated:del self.stub[0x4c4b7e]
  self.write32(0x2000412c,0x1234);self.write32(0x20004128,0x4321)
  self.write32(0x2000407c,0x5678)
  self.u.mem_write(CTX,struct.pack('<BBHIH',1,9,0,HANDLES,7));self.u.mem_write(HANDLES,struct.pack('<HHH',0x10,0x12,0x13))
  self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook)
 def write32(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def read32(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def allocate(self,n):a=self.heap;self.heap+=(n+15)&~15;return a
 def hook(self,u,a,size,_):
  if a not in self.stub:
   assert any(e<=a<int(rows[e]['end'],16) for e in ENTRIES+PREVIOUS),hex(a)
   return
  name=self.stub[a];v=[u.reg_read(r) for r in REGS];ret=0;c={'call':name,'args':v}
  if name=='fill':u.mem_write(v[0],bytes([v[2]&255])*v[1])
  elif name=='copy':u.mem_write(v[0],bytes(u.mem_read(v[1],v[2])))
  elif name in ('send','write_cmd'):
   ptr,n=(v[0],v[1]) if name=='send' else (v[3],v[2]);c['packet']=bytes(u.mem_read(ptr,n)).hex()
  elif name=='battery':c['record']=bytes(u.mem_read(v[0],8)).hex()
  elif name=='telemetry':c['duration_ticks']=self.read32(v[2])
  elif name=='ticks':ret=self.tick
  elif name=='owner':ret=self.owner
  elif name=='ring_mac':u.mem_write(v[0],b'\x01\x02\x03\x04\x05\x06')
  elif name=='unpair':c['mac']=bytes(u.mem_read(v[0],6)).hex()
  elif name in ('heap_alloc','wsf_alloc'):ret=0 if self.fail_alloc else self.allocate(v[0])
  elif name=='queue_put':
   p=self.read32(v[1]);c['record']=bytes(u.mem_read(p,8+self.read32(p+4))).hex();ret=self.queue_rc
   if not ret:self.queue.append(p)
  elif name=='queue_get':
   if self.queue:self.write32(v[1],self.queue.pop(0))
   else:ret=0xfffffffe
  elif name=='sem_acquire':ret=self.sem_rc
  elif name=='sem_count':ret=self.sem_count
  elif name=='wsf_queue':ret=0x20078000
  elif name=='wsf_enq':
   self.wsf.append(v[2]);c['message']=bytes(u.mem_read(v[2],12)).hex()
   c['packet_at_enqueue']=bytes(u.mem_read(self.read32(v[2]+4),struct.unpack('<H',u.mem_read(v[2]+8,2))[0])).hex()
  if name not in ('log_flags','log','dump','fill','copy'):self.calls.append(c)
  u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def run(self,a,*args):
  # Each invocation is a completed synthetic call; same stack deliberately used.
  self.u.reg_write(UC_ARM_REG_SP,STACK);self.u.reg_write(UC_ARM_REG_LR,STOP|1)
  for r,v in zip(REGS,args):self.u.reg_write(r,v)
  self.u.emu_start(a|1,STOP,count=60000)
  assert self.u.reg_read(UC_ARM_REG_PC)==STOP and self.u.reg_read(UC_ARM_REG_SP)==STACK
  return self.u.reg_read(UC_ARM_REG_R0)
 def named(self,n):return [c for c in self.calls if c['call']==n]
 def packet(self,cmd,payload=b'',status=0):
  b=bytes([0,0x1a,cmd,status])+payload;self.u.mem_write(DATA,b+bytes(32));return len(b)
CASES=[]
def save(n,m,**extra):CASES.append({'case':n,'calls':m.calls,**extra})
for a,args,want in [(0x472244,[],'001a9401'),(0x4722d8,[0x1234],'001a8a013412'),
 (0x472378,[0],'001a8501ffaaaaaa'),(0x472378,[1],'001a850100aaaaaa'),
 (0x4723d6,[0,0],'001a890100000000'),(0x4723d6,[1,0],'001a890180000000'),
 (0x4723d6,[0,1],'001a890140000000'),(0x4723d6,[1,1],'001a8901c0000000'),
 (0x472546,[],'00358800')]:
 m=M();m.run(a,*args);assert m.named('send')[0]['packet']==want;save('encode_%x_%s'%(a,args),m)
# RX heap ownership: original wrapper, copier, queue consumer and parser execute.
m=M();n=m.packet(0x8b,bytes([73,1]));m.run(0x4c548c,DATA,n)
p=m.queue[0];m.u.mem_write(DATA,bytes([0xcc])*n);m.run(0x4c4de8)
assert m.named('battery')[0]['record'][:12]=='040002004901' and m.named('heap_free')[0]['args'][0]==p
save('rx_owns_copy_and_frees_after_parse',m)
for name,config,args in [('queue_failure',{'queue_rc':0xfffffffd},[2,DATA,4]),('alloc_failure',{'fail_alloc':True},[2,DATA,4]),('null_data',{},[2,0,4])]:
 m=M()
 for k,v in config.items():setattr(m,k,v)
 assert m.run(0x4c549c,*args)==0xffffffff
 if name=='queue_failure':assert m.named('heap_free')
 save(name,m)
m=M();m.run(0x472362,0x1234);m.run(0x4c4de8)
assert m.named('send')[0]['packet']=='001a8a011234';save('public_interval_path_big_endian',m)
m=M();m.run(0x472426,1);m.run(0x4c4de8);assert m.named('send')[0]['packet']=='001a850100aaaaaa';save('public_touch_enable',m)
for typ,want in [(0,3),(1,0),(2,1),(4,5),(5,4),(8,14),(3,None)]:
 m=M();n=m.packet(0x61,bytes([typ,9,10])+struct.pack('<I',1000));m.run(0x472988,DATA,n)
 ev=m.named('input_event');assert bool(ev)==(want is not None)
 if ev:assert ev[0]['args']==[4,want,9 if typ in (4,5) else 0,10 if typ in (4,5) else 0]
 save('touch_type_%d'%typ,m)
for name,prev,tick,typ,want in [('suppress_delta99',1000,1099,1,False),('allow_delta100',1000,1100,1,True),('type8_bypasses',1000,1001,8,True),('wrap_delta',0xfffffff0,0x20,1,False)]:
 m=M();m.write32(0x20074900,prev);n=m.packet(0x61,bytes([typ,0,0])+struct.pack('<I',tick));m.run(0x472988,DATA,n)
 assert bool(m.named('input_event'))==want;save(name,m)
m=M();n=m.packet(0x61,bytes([1,0,0])+struct.pack('<I',1000),status=1);m.run(0x472988,DATA,n);assert not m.named('input_event') and m.read32(0x20074900)==1000;save('nonzero_status_still_updates_tick',m)
m=M();m.packet(0x61,bytes([1,0,0])+struct.pack('<I',0x11223344));m.run(0x47269e,DATA,8);assert m.read32(0x20074900)==0x11223344;save('length8_reads_through_offset10_in_padded_buffer',m)
m=M();m.packet(0x8b,bytes([73]));assert m.run(0x4727aa,DATA,5)==0xffffffff and not m.named('battery');save('battery_short_rejected',m)
for owner in (0,1):
 m=M();m.owner=owner;n=m.packet(0x85,b'\1',status=1);m.run(0x472988,DATA,n)
 assert bool(m.named('link_ready'))==bool(owner) and bool(m.named('phone_ring_info'))==(not bool(owner));save('hid_ack_owner%d'%owner,m)
for value in (0,0x20,0x40):
 m=M();n=m.packet(0x94,bytes([value]));m.run(0x472988,DATA,n)
 assert [c['args'][2] for c in m.named('delayed')]==([100,500] if value else []);save('heartbeat_reply_%x'%value,m)
m=M();n=m.packet(0x96);m.run(0x472988,DATA,n);assert m.named('unpair')[0]['mac']=='010203040506';save('invalid_glasses_mac_cleans_current_ring',m)
m=M();m.run(0x4728a0);n=m.packet(0x8c,b'\1');m.run(0x472988,DATA,n);m.tick=1256;n=m.packet(0x8c,b'\0');m.run(0x472988,DATA,n);assert m.named('telemetry')[0]['duration_ticks']==256;save('wear_duration_in_kernel_ticks',m)
# Original readiness function proceeds after 21 failed acquire calls (0 then
# twenty timeout=10) and twenty osDelay(10); it is not a completion barrier.
m=M();m.sem_rc=0xfffffffe;m.run(0x4d0b64)
assert [c['args'][1] for c in m.named('sem_acquire')]==[0]+[10]*20 and len(m.named('delay'))==20;save('tx_wait_timeout_returns',m)
for count in (0,1):
 m=M();m.sem_count=count;m.run(0x4d0c36);assert bool(m.named('sem_release'))==(count==0);save('tx_notify_count%d'%count,m)
# Full original command -> send -> wait -> WsfMsgSend. Delay WSF processing
# intentionally; no radio timing or real RTOS schedule is claimed.
m=M(integrated=True);m.sem_rc=0xfffffffe
m.run(0x4722d8,0x1234);first=m.wsf[0];ptr=m.read32(first+4);original=bytes(m.u.mem_read(ptr,6)).hex()
m.run(0x4722d8,0x5678);assert m.read32(m.wsf[1]+4)==ptr
current=bytes(m.u.mem_read(ptr,6)).hex();assert current=='001a8a017856'
m.run(0x4c4910,0,first);assert m.named('write_cmd')[0]['packet']==current
save('delayed_consumer_reads_reused_stack_payload',m,first_enqueued_packet=m.named('wsf_enq')[0]['packet_at_enqueue'],after_first_return=original,after_second_return=current,payload_pointer=hex(ptr),schedule='Both encoders return before first WSF message is dispatched; semaphore acquisition fails.')
# Pin time unit using original scheduler arithmetic, with providers stubbed.
m=M();del m.stub[0x47697e]
m.write32(0x200745f0,1);m.write32(0x200745f4,1);m.write32(0x200745f8,1);m.write32(0x200745fc,100)
m.run(0x47697e,0x472589,0,500);deadline=m.read32(0x2006dad4+0x200)
assert deadline==1400;save('delayed_argument_added_to_kernel_ticks',m,deadline=deadline,tick_now=1000,epoch_base=100,delay_argument=500)
# Event 4 schedules setup callbacks, with no CCC success check in this body.
m=M();m.run(0x4c507e,4);assert [c['args'][:3] for c in m.named('delayed')]==[[0x4c5033,0,200],[0x4c4ee5,0,500],[0x4a285d,0,3000]];save('event4_setup_schedule',m)
report={'firmware_sha256':SHA,'input_path':str(P.relative_to(ROOT)),'runtime_base':hex(BASE),'capstone':capstone.__version__,'unicorn':unicorn.__version__,
 'scope':'Original bytes, external call stubs, synthetic scheduler. No radio/hardware. Logging disabled. No whole-program safety claim.',
 'functions':records,'case_count':len(CASES),'cases':CASES}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS',len(CASES),'original-code cases;',len(records),'function hashes')
