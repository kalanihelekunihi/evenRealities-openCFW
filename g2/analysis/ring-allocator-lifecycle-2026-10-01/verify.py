#!/usr/bin/env python3
"""Bounded stock allocator and lifecycle execution. No device/network access."""
from pathlib import Path
import json,struct,hashlib,capstone,unicorn
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R9,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();BASE=0x437fe0
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert len(B)==3523396 and hashlib.sha256(B).hexdigest()==SHA
raw={int(r['entry'],16):r for r in map(json.loads,(ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
entries=[0x43a11e,0x530364,0x530446,0x5304d4,0x4bf99e,0x4bf9b0,0x4bf990,0x4b50ae,0x4c96b6,0x4c9778,0x4c995e,0x4c9c3c,0x4c53a6,0x4c507e,0x4c549c]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)
records=[];lines=[]
for a in entries:
 r=raw[a];z=int(r['body_end_inclusive'],16)+1;data=B[a-BASE:z-BASE];assert hashlib.sha256(data).hexdigest()==r['body_sha256']
 ins=list(md.disasm(data,a));assert sum(i.size for i in ins)==len(data)
 records.append({'entry':hex(a),'end':hex(z),'sha256':r['body_sha256']});lines.append('\n%s..%s sha256=%s'%(hex(a),hex(z),r['body_sha256']))
 lines.extend('%08x %-10s %-8s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str) for i in ins)
(OUT/'disassembly.txt').write_text('\n'.join(lines)+'\n')
def f32(a):return struct.unpack_from('<I',B,a-BASE)[0]
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];STOP=0x10000000
# Independently regenerate SRAM initialized data from stock compressed descriptor.
u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS)
u.mem_map(0x437000,0x35e000);u.mem_write(BASE,B);u.mem_map(0x20000000,0x400000);u.mem_map(STOP,4096)
u.reg_write(UC_ARM_REG_SP,0x203ff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_R9,0);u.reg_write(R[0],0x75d3f4)
u.emu_start(0x43a11f,STOP,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(R[0])==0x75d400
RAM=bytes(u.mem_read(0x20000000,17752));RAMSHA=hashlib.sha256(RAM).hexdigest();assert RAMSHA=='df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743'
assert RAM[0x3b0:0x3c0].hex()=='100008002000040040000a00e0011400'
assert struct.unpack_from('<II',RAM,0x4120)==(0x4c4da5,0x4c4dd1)
assert struct.unpack_from('<II',RAM,0x4068)==(0x4d0af7,0x4d0b1d)
POOL=0x2004fa98;RING=0x20004120
STUB={0x43d0ce:'log',0x43d574:'log',0x43ce9e:'log',0x52b8a4:'cs_enter',0x52b8b6:'cs_exit',0x449238:'thread_flags',0x44969c:'event_wait',0x4495e4:'event_set',0x449bec:'queue_delete',0x449376:'delay_forever',0x4c4de8:'ring_queue_drain'}
class M:
 def __init__(self):
  self.u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS)
  self.u.mem_map(0x437000,0x35e000);self.u.mem_write(BASE,B);self.u.mem_map(0x20000000,0x100000);self.u.mem_write(0x20000000,RAM);self.u.mem_map(STOP,4096)
  self.calls=[];self.wait_ok=True;self.stopped=False
  # Nonzero synthetic task IDs, associated with authentic task descriptor pointers.
  for j,literal in enumerate([0x4c9c94,0x4c9c80,0x4c9c84,0x4c9c88,0x4c9c8c,0x4c9c90,0x4c9c70,0x4c9c74,0x4c9c78,0x4c9cac]):self.w32(f32(literal)+8,0x7000+j)
  self.w32(f32(0x4c9c58)+0x1c,0x8888);self.w32(RING+12,0x9999)
  self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook)
 def w32(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def r32(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def hook(self,u,a,n,_):
  if a not in STUB:
   assert any(e<=a<int(raw[e]['body_end_inclusive'],16)+1 for e in entries),hex(a);return
  name=STUB[a];v=[u.reg_read(r) for r in R];ret=0
  if name=='event_wait':ret=v[1] if self.wait_ok else 0x80000002
  if name not in ('log','cs_enter','cs_exit'):self.calls.append({'call':name,'args':v,'ring_queue':self.r32(RING+12),'result':ret})
  if name=='delay_forever':self.stopped=True;u.emu_stop();return
  u.reg_write(R[0],ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def run(self,a,*args):
  self.stopped=False;self.u.reg_write(UC_ARM_REG_SP,0x200ff000);self.u.reg_write(UC_ARM_REG_LR,STOP|1)
  for r,v in zip(R,args):self.u.reg_write(r,v)
  self.u.emu_start(a|1,STOP,count=100000);assert self.stopped or self.u.reg_read(UC_ARM_REG_PC)==STOP
  return self.u.reg_read(R[0])
 def init_pool(self):
  used=self.run(0x530364,0x2940,POOL,4,0x200003b0);assert used==0x2930
  return used
 def named(self,n):return [c for c in self.calls if c['call']==n]
 def pool_for(self,p):
  for i in range(4):
   z,c,start=struct.unpack('<HBxI',self.u.mem_read(POOL+12*i,8))
   if start<=p<start+z*c:return z
  return None
CASES=[]
def save(name,m,**extra):CASES.append({'case':name,'calls':m.calls,**extra})
m=M();used=m.init_pool();descriptors=bytes(m.u.mem_read(POOL,48));save('pool_init_from_stock_decoded_configuration',m,used=used,descriptors=descriptors.hex())
# Inline payload H=12 stock header, or H=16 proposed extension; no patched encoder runs.
for h in (12,16):
 for n in (0,8,9,12,13,40,41,44,45,456,457,460,461):
  m=M();m.init_pool();p=m.run(0x4bf99e,h+n);need=h+n+8
  expected=next((z for z in (16,32,64,480) if need<=z),None)
  assert (m.pool_for(p-8) if p else None)==expected
  if p:
   m.run(0x4bf9b0,p);assert m.run(0x4bf99e,h+n)==p
  save('inline_h%d_payload%d'%(h,n),m,request_bytes=need,block_class=expected)
# Exhaustion falls forward through larger classes, with no heap fallback.
m=M();m.init_pool();got=[]
for i in range(43):
 p=m.run(0x530446,16);got.append(m.pool_for(p) if p else None)
assert got==[16]*8+[32]*4+[64]*10+[480]*20+[None];save('all_42_blocks_exhausted',m,classes=got)
m=M();m.init_pool();ptrs=[m.run(0x4bf99e,472) for _ in range(21)];assert all(ptrs[:20]) and ptrs[20]==0
m.run(0x4bf9b0,ptrs[7]);assert m.run(0x4bf99e,472)==ptrs[7];save('largest_pool_exhaustion_and_release',m)
for n in (461,462):
 m=M();m.init_pool();p=m.run(0x4b50ae,n+11);assert bool(p)==(n==461);save('att_packet_payload%d'%n,m,block_class=m.pool_for(p-8) if p else None)
# Large inline message and its ATT copy must coexist: one free large block is insufficient.
m=M();m.init_pool()
for _ in range(19):assert m.run(0x530446,480)
inline=m.run(0x4bf99e,472);assert inline and m.run(0x4b50ae,471)==0
m.run(0x4bf9b0,inline);assert m.run(0x4b50ae,471)
save('inline_and_att_copy_need_two_large_blocks',m)
# Oversized WSF request wraps at allocator's u16 boundary; helper must reject first.
m=M();m.init_pool();p=m.run(0x4bf99e,65528);assert m.pool_for(p-8)==16;save('wsf_65528_wraps_to_zero_allocator_request',m)
# Shutdown mode path requests flags and proceeds after success OR timeout.
for mode in (1,2,4,8,16,32):
 for success in (True,False):
  m=M();m.wait_ok=success;m.run(0x4c995e,mode,0,0,0);calls=m.named('thread_flags');wait=m.named('event_wait')
  assert len(wait)==1 and wait[0]['args'][3]==5000
  assert any(c['args'][0]==0x7001 for c in calls) # ring always requested
  assert any(c['args'][0]==0x7005 for c in calls)==(mode!=32)
  assert len(calls)==(7 if mode==32 else 10);assert not m.named('queue_delete')
  save('shutdown_mode%x_%s'%(mode,'ack' if success else 'timeout'),m)
m=M();m.run(0x4c995e,32,0,0,0);m.calls=[];m.run(0x4c995e,32,0,0,0);assert not m.named('event_wait');save('ota_exit_guard_prevents_repeat',m)
# Ring cooperative exit publishes ack before delete, does not await WSF drain.
for flags in (0x800000,0xc00000):
 m=M();m.run(0x4c507e,flags,0,0,0)
 names=[c['call'] for c in m.calls];expected=(['ring_queue_drain'] if flags&0x400000 else [])+['event_set','queue_delete','delay_forever'];assert names==expected
 assert m.named('event_set')[0]['args'][1]==64 and m.named('event_set')[0]['ring_queue']==0x9999 and m.r32(RING+12)==0
 save('ring_exit_flags%x'%flags,m)
m=M();m.w32(RING+12,0);ret=m.run(0x4c549c,0x1000,0x20078000,2,0);assert ret==0xffffffff;save('ring_task_producer_rejects_deleted_queue',m)
report={'input_sha256':SHA,'initializer':{'descriptor':'0x75d3f4','handler':'0x43a11e','output_bytes':17752,'output_sha256':RAMSHA,'pool_config_bytes':RAM[0x3b0:0x3c0].hex()},'functions':records,'case_count':len(CASES),'cases':CASES,'scope':'original allocator and cooperative-exit instructions, decoded authentic data; mutex, logging, RTOS flags/waits/delete/delay and ring queue drain are explicit stubs'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(CASES),'cases;',len(records),'body hashes; fresh stock SRAM initializer')
