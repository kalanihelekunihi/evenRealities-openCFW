#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Stock/source timer unlink, nested WSF port and timer→GPIO shutdown slice."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[4];BASE=0x438000;GPIO=0x40010000;QUEUE=0x200741b0;DEPTH=0x20075045;NODE=0x20073000;RADIO_TIMER=0x20073e64;STOP=0x8000000
spec=importlib.util.spec_from_file_location('control',ROOT/'g2/components/foundation/ambiq_gpio_config/simulator/verify_control.py');control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control);gpio=control.gpio;w=gpio.w;sha=gpio.sha
NODES=[NODE+i*32 for i in range(5)]+[RADIO_TIMER]
FUN={'stop':(0x52a4d2,'WsfTimerStop'),'remove':(0x52a3fc,'opencfw_wsf_timer_remove_raw'),'queue':(0x538cc8,'WsfQueueRemove'),'phase':(0x4b49d0,'opencfw_radio_timer_gpio_shutdown_phase')}
BODIES=[(0x52a4d2,20),(0x52a3fc,40),(0x538cc8,46),(0x52b8a4,18),(0x52b8b6,18),(0x52b8c8,8),(0x52b8d0,8)]
def initialize(c):
 nodes={a:bytearray(w(NODES[4])+w(0x11000000+i)+w(0x22000000+i)+bytes([0x60+i,c['started'],0x5a,0xa5])) for i,a in enumerate(NODES)}
 chain=[NODES[i] for i in c['chain']]
 for i,a in enumerate(chain):nodes[a][:4]=w(chain[i+1] if i+1<len(chain) else 0)
 return nodes,[chain[0] if chain else 0,chain[-1] if chain else 0],control.init(c)

def expected(c):
 nodes,q,regs=initialize(c);depth=c['depth'];mask=c['prior'];writes=[];mmio=[];snapshots=[]
 def enter():
  nonlocal depth,mask
  if depth==0:mask=1
  depth=(depth+1)&255;writes.append([DEPTH,1,depth,mask])
 def exit():
  nonlocal depth,mask
  depth=(depth-1)&255;writes.append([DEPTH,1,depth,mask])
  if depth==0:mask=0
 def link(a,value):
  if a in [QUEUE,QUEUE+4]:q[(a-QUEUE)//4]=value
  else:struct.pack_into('<I',nodes[a],0,value)
  writes.append([a,4,value,mask])
 def queue_remove(target,prev):
  enter()
  if target==q[0]:link(QUEUE,struct.unpack_from('<I',nodes[target])[0])
  elif prev:link(prev,struct.unpack_from('<I',nodes[target])[0])
  if target==q[1]:link(QUEUE+4,prev)
  exit()
 def remove(target):
  prev=0;curr=q[0]
  while curr and curr!=target:prev=curr;curr=struct.unpack_from('<I',nodes[curr])[0]
  if curr:
   queue_remove(target,prev);nodes[target][13]=0;writes.append([target+13,1,0,mask])
 def stop(target):enter();remove(target);exit()
 target=0 if c['target']<0 else NODES[c['target']]
 if c['op']=='queue':queue_remove(target,0 if c['prev']<0 else NODES[c['prev']])
 elif c['op']=='remove':remove(target)
 else:stop(RADIO_TIMER if c['op']=='phase' else target)
 if c['op']=='phase':
  cc=dict(c,op='phase',prior=mask);e=control.expected(cc);regs=bytearray.fromhex(e['registers']);mmio=e['mmio'];snapshots.append(dict(queue=q[:],nodes={hex(a):raw.hex() for a,raw in nodes.items()},depth=depth,primask=mask))
 return dict(status=None,queue=q,nodes={hex(a):raw.hex() for a,raw in nodes.items()},depth=depth,primask=mask,ram_writes=writes,mmio=mmio,registers=bytes(regs).hex(),timer_at_gpio_entry=snapshots)

def run(segments,entry,c,stock,phase_entry):
 import unicorn as u
 import unicorn.arm_const as arm
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);cpu.ctl_set_cpu_model(arm.UC_CPU_ARM_CORTEX_M4);pages=set()
 for s in segments:
  for a in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
   if a not in pages:cpu.mem_map(a,4096);pages.add(a)
  cpu.mem_write(s['address'],s['data'])
 for lo,n in [(0x20000000,0x10000),(NODE-4096,0x4000),(GPIO,4096),(STOP,4096)]:
  for a in range(lo,lo+n,4096):
   if a not in pages:cpu.mem_map(a,4096);pages.add(a)
 nodes,q,regs=initialize(c)
 for a,raw in nodes.items():cpu.mem_write(a-8,b'\xcc'*8+bytes(raw)+b'\xcc'*8)
 cpu.mem_write(QUEUE-8,b'\xcc'*8+w(q[0])+w(q[1])+b'\xcc'*8);cpu.mem_write(DEPTH-4,b'\xdd'*4+bytes([c['depth']])+b'\xdd'*4);cpu.mem_write(GPIO,bytes(regs));trace={};writes=[];mmio=[];snapshots=[]
 def read_state(uc):return dict(queue=list(struct.unpack('<II',uc.mem_read(QUEUE,8))),nodes={hex(a):bytes(uc.mem_read(a,16)).hex() for a in NODES},depth=uc.mem_read(DEPTH,1)[0],primask=uc.reg_read(arm.UC_ARM_REG_PRIMASK))
 def code(uc,pc,size,_):
  if c['op']=='phase' and pc==phase_entry:snapshots.append(read_state(uc))
  s=next(s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data']));raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  if GPIO<=a<GPIO+0x610:
   assert size==4 and a%4==0;read=access==u.UC_MEM_READ;v=struct.unpack('<I',uc.mem_read(a,4))[0] if read else value;mask=uc.reg_read(arm.UC_ARM_REG_PRIMASK);mmio.append(['read' if read else 'write',a,v,mask])
   if a>=GPIO+0x530 or a<GPIO+224*4 or a==GPIO+0x400:assert mask==1
   if not read:
    if a<GPIO+224*4:assert struct.unpack('<I',uc.mem_read(GPIO+0x400,4))[0]==0x73
    raw=bytearray(uc.mem_read(GPIO,0x610));effect=gpio.device_effect(raw,a,value,c)
    if effect:offset,v=effect;uc.mem_write(GPIO+offset,w(v))
  elif access==u.UC_MEM_WRITE:
   assert (a==DEPTH and size==1) or (a in [QUEUE,QUEUE+4] and size==4) or any((a==n and size==4) or (a==n+13 and size==1) for n in NODES),(hex(a),size)
   # Unicorn reports the full source register for STRB; only size bytes
   # are committed. Normalize bus value, with complete post-memory checked too.
   writes.append([a,size,value&((1<<(8*size))-1),uc.reg_read(arm.UC_ARM_REG_PRIMASK)])
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem,begin=GPIO,end=GPIO+0x60f)
 for a,n in [(NODE-8,5*32+16),(RADIO_TIMER-8,32),(QUEUE-8,24),(DEPTH-4,9)]:cpu.hook_add(u.UC_HOOK_MEM_WRITE,mem,begin=a,end=a+n-1)
 target=0 if c['target']<0 else NODES[c['target']];r0=QUEUE if c['op']=='queue' else target
 for reg,value in [(arm.UC_ARM_REG_R0,r0),(arm.UC_ARM_REG_R1,target),(arm.UC_ARM_REG_R2,0 if c['prev']<0 else NODES[c['prev']]),(arm.UC_ARM_REG_SP,0x2000f000),(arm.UC_ARM_REG_LR,STOP|1),(arm.UC_ARM_REG_PRIMASK,c['prior'])]:cpu.reg_write(reg,value)
 saved={getattr(arm,'UC_ARM_REG_R'+str(i)):0xa6000000+i for i in range(4,12)}
 for reg,value in saved.items():cpu.reg_write(reg,value)
 end=0x4b49e6 if stock and c['op']=='phase' else STOP;cpu.emu_start(entry|1,end,count=3000);assert cpu.reg_read(arm.UC_ARM_REG_PC)==end and cpu.reg_read(arm.UC_ARM_REG_SP)==0x2000f000;assert all(cpu.reg_read(reg)==value for reg,value in saved.items())
 for a in NODES:assert bytes(cpu.mem_read(a-8,8))==bytes(cpu.mem_read(a+16,8))==b'\xcc'*8
 assert bytes(cpu.mem_read(QUEUE-8,8))==bytes(cpu.mem_read(QUEUE+8,8))==b'\xcc'*8
 assert bytes(cpu.mem_read(DEPTH-4,4))==bytes(cpu.mem_read(DEPTH+1,4))==b'\xdd'*4
 return dict(status=None,**read_state(cpu),ram_writes=writes,mmio=mmio,registers=bytes(cpu.mem_read(GPIO,0x610)).hex(),timer_at_gpio_entry=snapshots,trace=trace)

def cases():
 d=dict(op='stop',chain=[],target=0,prev=-1,started=1,depth=0,prior=0,enabled=0xa5a55a5a,wt=0xa5a55a5a,en=0x5a5aa5a5,model='raw',output_active_mask=0xffffffff)
 for op in ['stop','remove']:
  for chain in [[],[0],[0,1],[0,1,2],[0,1,2,3]]:
   for target in [-1,0,1,2,3,4]:
    for started in [0,1,255]:
     for depth in [0,1,2,253,254,255]:
      for prior in [0,1]:yield dict(d,op=op,chain=chain,target=target,started=started,depth=depth,prior=prior)
 for chain in [[0],[0,1],[0,1,2],[0,1,2,3]]:
  for target in chain:
   prev=chain[chain.index(target)-1] if chain.index(target)>0 else -1
   for depth in [0,1,2,254,255]:
    for prior in [0,1]:yield dict(d,op='queue',chain=chain,target=target,prev=prev,depth=depth,prior=prior)
 # Safe-memory malformed predecessor diagnostic: no membership/invariant guarantee.
 for depth in [0,1]:
  for prior in [0,1]:yield dict(d,op='queue',chain=[0,1,2],target=1,prev=-1,depth=depth,prior=prior,diagnostic='missing predecessor; caller contract violation')
 for chain in [[],[5],[5,0,1],[0,5,1],[0,1,5],[0,1,2]]:
  for started in [0,1,255]:
   for depth in [0,1,2,254,255]:
    for prior in [0,1]:
     for model in ['raw','side_effects']:yield dict(d,op='phase',chain=chain,target=5,started=started,depth=depth,prior=prior,model=model)

def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';elf,segs,syms=gpio.parser.elf_info(a.elf)
 stock=[dict(address=pc,data=blob[32+pc-BASE:32+pc-BASE+4096],memory_size=4096,flags=5) for pc in [0x52a000,0x538000,0x52b000,0x4b4000,0x52d000,0x52e000,0x480000,0x481000,0x473000,0x768000,0x78e000]];results=[];observed={}
 for c in cases():
  pc,name=FUN[c['op']];x=run(stock,pc,c,True,0x52dd6a);y=run(segs,syms[name]&~1,c,False,syms['opencfw_radio_gpio_shutdown_phase']&~1);t=x.pop('trace');y.pop('trace');assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});z=expected(c);assert x==z,(c,{k:(x[k],z[k]) for k in x if x[k]!=z[k]});observed.update(t);results.append(dict(inputs=c,result=x,original_trace=t))
 executed={pc+i for pc,raw in observed.items() for i in range(len(bytes.fromhex(raw)))}
 for pc,n in BODIES:assert set(range(pc,pc+n))<=executed,hex(pc)
 assert set(range(0x4b49d0,0x4b49e6))<=executed
 comp=Path(__file__).resolve().parent;paths=[p for d in [comp,ROOT/'g2/components/foundation/ambiq_gpio_config'] for p in d.rglob('*') if p.suffix in ['.c','.h','.ld','.py']]+[ROOT/'g2/components/foundation/wsf_radio/wsf_radio.c',ROOT/'g2/components/foundation/wsf_radio/wsf_radio.h'];report=dict(status='PASS',cases=len(results),results=results,original_trace={hex(pc):raw for pc,raw in sorted(observed.items())},unique_original_trace_bytes=len(executed),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(paths)},firmware_sha256=sha(blob),elf_sha256=sha(elf),limits='Actual nested WSF port, queue unlink, timer stop and timer→GPIO shutdown slice; no executable call stubs. Caller-owned timer remains allocated, stale next retained, absent flag unchanged. Serialized acyclic mapped queues only; overflow depths/malformed predecessor are diagnostics. WSF byte-depth port may unmask unrelated incoming PRIMASK. No expiry handoff/queued-message drain, pending IRQ/NVIC cleanup, transport release, asynchronous lifetime or complete shutdown-safety proof. Synthetic GPIO register side effects; optimized tick blocker unchanged.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),'original/source/model cases;',len(executed),'unique original bytes')
if __name__=='__main__':main()
