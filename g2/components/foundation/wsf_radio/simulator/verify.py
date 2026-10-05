#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Stock/source WSF execution. RTOS, queue, timer and application handlers are
explicit fixture boundaries. WSF producer/critical/wake/dispatcher run for real."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
BASE=0x438000;STATE=0x20073230;DEPTH=0x20075045;TASK=0x20074ef0;STOP=0x8000000;CB=0x9000000
H,A=0x20068228,0x20068928
sha=lambda b:hashlib.sha256(b).hexdigest()
w=lambda n:struct.pack('<I',n)
ORIGINAL={'set_event':0x52b91e,'ready':0x52b95e,'wake':0x52b8d8,'enter':0x52b8a4,'exit':0x52b8b6,'dispatch':0x52b9d0,'sleep':0x52b99e,'irq':0x4b80be,'disable':0x52dd6a}
NAMES={'set_event':'opencfw_wsf_set_event','ready':'opencfw_wsf_task_ready','wake':'opencfw_wsf_wake','enter':'opencfw_wsf_cs_enter','exit':'opencfw_wsf_cs_exit','dispatch':'opencfw_wsf_dispatch','sleep':'opencfw_wsf_ready_to_sleep','irq':'GPIO0_607F_IRQHandler','disable':'opencfw_radio_gpio_disable'}
BOUNDARIES={0x442228:'context_is_isr',0x47ee4a:'notify_isr',0x47ed76:'notify_task',0x52a574:'timer_update',0x4bf9ec:'msg_deq',0x4bf9b0:'msg_free',0x52a542:'timer_expired',0x47ebf8:'wait'}
def run(segments,entries,boundaries,radio_callback,c):
 import unicorn as u
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS)
 for s in segments:
  if not s['memory_size']:continue
  lo=s['address']&~4095;n=((s['address']+s['memory_size']+4095)&~4095)-lo;cpu.mem_map(lo,n);cpu.mem_write(s['address'],s['data'])
 for lo,n in [(0x20000000,0x80000),(0x40010000,4096),(0xe000e000,4096),(CB,4096),(STOP,4096)]:cpu.mem_map(lo,n)
 cpu.mem_write(STATE,b'\x00'*64)
 for i in range(10):
  cpu.mem_write(STATE+i*4,w(0 if c['null_handlers']>>i&1 else (CB+i*16|1)));cpu.mem_write(CB+i*16,b'\x70\x47')
  cpu.mem_write(STATE+0x28+i,bytes([c['events'].get(str(i),0)]))
 cpu.mem_write(STATE+0x3c,bytes([c['flags']]));cpu.mem_write(DEPTH,bytes([c['depth']]));cpu.mem_write(TASK,w(c['task']))
 cpu.mem_write(0x20074fcb,b'\x07');cpu.mem_write(0x20074640,w(0xffffffff))
 cpu.mem_write(H+117*4,w(radio_callback|1));cpu.mem_write(A+117*4,w(0))
 for i in range(14):cpu.mem_write(0x40010530+i*16,w(0xffffffff if i==3 else 0)+w(1<<21 if i==3 else 0)+w(0))
 for i,hid in enumerate([4,6]):cpu.mem_write(0x20011000+i*32+12,bytes([hid]))
 log=[];mmio=[];state_writes=[];trace={};msg_index=0;timer_index=0;updates=0;posted=set();returns=[]
 def byte(a):return bytes(cpu.mem_read(a,1))[0]
 def ret(uc,value=0):uc.reg_write(UC_ARM_REG_R0,value&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def code(uc,pc,size,_):
  nonlocal msg_index,timer_index,updates
  if pc in boundaries:
   name=boundaries[pc];args=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];prior=uc.reg_read(UC_ARM_REG_PRIMASK)
   if name=='context_is_isr':log.append([name,c['context'],prior]);ret(uc,c['context'])
   elif name=='notify_isr':
    assert args[:2]==[c['task'],1];uc.mem_write(args[2],w(c['higher']));log.append([name,args[0],args[1],c['notify'],c['higher'],prior]);ret(uc,c['notify'])
   elif name=='notify_task':assert args[:2]==[c['task'],1];log.append([name,args[0],args[1],c['notify'],prior]);ret(uc,c['notify'])
   elif name=='timer_update':
    updates+=1;log.append([name,updates,prior])
    if c['late_event'] and updates==2:uc.mem_write(STATE+0x28+3,b'\x80');uc.mem_write(STATE+0x3c,b'\x04')
    ret(uc)
   elif name=='msg_deq':
    assert args[0]==STATE+0x34;log.append([name,msg_index,prior])
    if c['messages'] and msg_index<2:uc.mem_write(args[1],bytes([2 if msg_index==0 else 5]));ptr=0x20010000+msg_index*32;msg_index+=1;ret(uc,ptr)
    else:ret(uc)
   elif name=='msg_free':log.append([name,args[0],prior]);ret(uc)
   elif name=='timer_expired':
    assert args[0]==0;log.append([name,timer_index,prior])
    if c['timers'] and timer_index<2:ptr=0x20011000+timer_index*32;timer_index+=1;ret(uc,ptr)
    else:ret(uc)
   elif name=='wait':
    timeout=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
    assert args==[c['task'],1,1,0] and timeout==0xffffffff
    log.append([name,c['task'],1,1,0,0xffffffff,prior]);ret(uc)
   return
  if CB<=pc<CB+160:
   slot=(pc-CB)//16;assert pc%16==0;event=uc.reg_read(UC_ARM_REG_R0);msg=uc.reg_read(UC_ARM_REG_R1);log.append(['handler',slot,event,msg,uc.reg_read(UC_ARM_REG_PRIMASK),byte(STATE+0x28+slot)])
   if c['repost'] and slot in [0,9] and slot not in posted and msg==0:
    posted.add(slot);uc.reg_write(UC_ARM_REG_R0,9 if slot==0 else 0);uc.reg_write(UC_ARM_REG_R1,2 if slot==0 else 4);uc.reg_write(UC_ARM_REG_PC,entries['set_event']|1)
   else:ret(uc)
   return
  matches=[s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data'])];assert len(matches)==1,hex(pc);s=matches[0];raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  prior=uc.reg_read(UC_ARM_REG_PRIMASK)
  if access==u.UC_MEM_WRITE and (STATE+0x28<=a<STATE+64 or a==DEPTH):state_writes.append([a,size,value,prior])
  if 0x40010000<=a<0x40011000 or a==0xe000ed04:
   read=access==u.UC_MEM_READ;v=struct.unpack('<I',uc.mem_read(a,4))[0] if read else value;mmio.append(['read' if read else 'write',a,size,v,prior]);assert size==4
   if a==0xe000ed04:assert not read and v==0x10000000
   elif read:assert prior==1
   elif a==0x40010568:uc.mem_write(a-4,w(struct.unpack('<I',uc.mem_read(a-4,4))[0]&~v))
   else:assert a==0x40010560
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem);cpu.reg_write(UC_ARM_REG_PRIMASK,c['prior'])
 for op,id,mask in c['program']:
  cpu.reg_write(UC_ARM_REG_R0,id);cpu.reg_write(UC_ARM_REG_R1,mask);cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,STOP|1);cpu.emu_start(entries[op]|1,STOP,count=20000);assert cpu.reg_read(UC_ARM_REG_PC)==STOP;returns.append(cpu.reg_read(UC_ARM_REG_R0) if op=='sleep' else None)
 result=dict(state=bytes(cpu.mem_read(STATE+0x28,24)).hex(),depth=byte(DEPTH),primask=cpu.reg_read(UC_ARM_REG_PRIMASK),log=log,mmio=mmio,state_writes=state_writes,radio_counter=struct.unpack('<I',cpu.mem_read(0x20074640,4))[0],gpio=bytes(cpu.mem_read(0x40010560,12)).hex(),returns=returns,trace=trace)
 return result

def expected(c,r):
 if c['depth']==0 and not all(x[0] in ['wake','sleep'] for x in c['program']):assert r['primask']==0
 if c['depth']>0:assert r['primask']==c['prior']
 if all(x[0] in ['wake','sleep'] for x in c['program']):assert r['primask']==c['prior']
 if c['program']==[['wake',0,0]]:
  log=[];mmio=[]
  if c['task']:
   log=[['context_is_isr',c['context'],c['prior']]]
   if c['context']==1:log.append(['notify_isr',c['task'],1,c['notify'],c['higher'],c['prior']])
   else:log.append(['notify_task',c['task'],1,c['notify'],c['prior']])
   if c['notify'] and (c['context']!=1 or c['higher']):mmio=[['write',0xe000ed04,4,0x10000000,c['prior']]]
  assert r['log']==log and r['mmio']==mmio
 # Exact independent event-only coalescing model, including invalid-slot aliasing.
 if all(x[0]=='set_event' for x in c['program']):
  slots=bytearray(24)
  for i,v in c['events'].items():slots[int(i)]=v
  slots[20]=c['flags']
  for _,id,mask in c['program']:slots[id&15]|=mask&255;slots[20]|=4
  assert bytes.fromhex(r['state'])==slots
 if c['program'][-1][0]=='dispatch' and not c['late_event']:
  handlers=[x for x in r['log'] if x[0]=='handler']
  if c['repost']:assert [(x[1],x[2]) for x in handlers]==[(0,1),(9,2),(0,4)]
  if c['messages'] and c['timers']:assert [x[1] for x in handlers]==[2,5,4,6,0,7,9]
  if c['program'][0][0]=='disable':assert [(x[1],x[2]) for x in handlers]==[(7,1)] and r['radio_counter']==0
  for x in handlers:
   if x[3]==0:assert x[5]==0 # Slot cleared before handler invocation.

def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';stock=[dict(address=BASE,data=blob[32:],memory_size=len(blob)-32,flags=5)];elf,segs,syms=parser.elf_info(a.elf)
 # zero-length RW ELF sections not mapped by run; stock/source data RAM initialized explicitly.
 defaults=dict(depth=0,prior=0,task=0x20012340,context=0,notify=1,higher=1,events={},flags=0,null_handlers=0,messages=False,timers=False,repost=False,late_event=False)
 cases=[]
 for id in [0,7,9,10,11,12,13,14,15,16,23,255,0xffffffff]:
  for mask in [0,1,255,256,257,0xffff,0xffffffff]:cases.append(dict(defaults,program=[['set_event',id,mask]]))
 for depth in [0,1,254,255]:
  for prior in [0,1]:cases.append(dict(defaults,depth=depth,prior=prior,program=[['set_event',7,1],['set_event',7,2],['set_event',7,1]]))
 for task in [0,0x20012340]:
  for context in [0,1,2]:
   for notify in [0,1,0xffffffff]:
    for higher in [0,1,0xffffffff]:cases.append(dict(defaults,task=task,context=context,notify=notify,higher=higher,program=[['wake',0,0]]))
 for depth in [0,1]:
  for prior in [0,1]:
   cases.extend([dict(defaults,depth=depth,prior=prior,events={'0':1,'7':3,'9':128},flags=7,messages=True,timers=True,program=[['dispatch',0,0]]),dict(defaults,depth=depth,prior=prior,events={'0':1},flags=4,repost=True,program=[['dispatch',0,0]]),dict(defaults,depth=depth,prior=prior,events={'3':2},null_handlers=1<<3,flags=4,program=[['dispatch',0,0]]),dict(defaults,depth=depth,prior=prior,late_event=True,program=[['dispatch',0,0]]),dict(defaults,depth=depth,prior=prior,context=1,program=[['disable',0,0],['irq',0,0],['dispatch',0,0]])])
 for mask in [0,1,2,4,255,256,0xffff]:cases.append(dict(defaults,program=[['ready',255,mask]]))
 results=[];observed={}
 for c in cases:
  x=run(stock,ORIGINAL,BOUNDARIES,0x4b4a98,dict(c,stock=True));y=run(segs,{k:syms[v]&~1 for k,v in NAMES.items()},{syms['opencfw_wsf_'+v]&~1:v for v in BOUNDARIES.values()},syms['opencfw_radio_gpio_callback'],dict(c,stock=False));trace=x.pop('trace');y.pop('trace');assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});observed.update(trace)
  if not c['late_event']:expected(c,x)
  else:assert x['primask']==c['prior'] and x['log']==[['timer_update',1,c['prior']],['timer_update',2,c['prior']]]
  results.append(dict(inputs=c,result=x,original_trace=trace))
 comp=Path(__file__).resolve().parents[1];report=dict(status='PASS',case_count=len(cases),cases=results,original_trace={hex(k):v for k,v in sorted(observed.items())},unique_original_trace_bytes=sum(len(bytes.fromhex(v)) for v in observed.values()),elf_sha256=sha(elf),firmware_sha256=sha(blob),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},limits='Actual WSF critical/event/wake/dispatcher and linked radio/GPIO execute. Synthetic context classification, RTOS notifications/wait, timers/queue providers and app handlers intercepted. Message/timer buffer fixtures prove dispatcher call/release order, not real allocator/queue ownership or OS scheduling. MMIO W1C synthetic. Invalid handler/depth cases preserve stock behavior and do not claim safe use.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(cases),'WSF comparisons',report['unique_original_trace_bytes'],'unique original bytes')
if __name__=='__main__':main()
