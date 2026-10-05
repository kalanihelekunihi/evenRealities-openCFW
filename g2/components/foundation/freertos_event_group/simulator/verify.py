#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Real event-group APIs + WSF/radio; scheduler and queue copy are fixtures."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
BASE=0x438000;G=0x20012340;ITEMS=0x20014000;QUEUE=0x20018000;HIGH=0x20001000;STATE=0x20073230;DEPTH=0x20075045;CB=0x9000000;STOP=0x8000000
w=lambda n:struct.pack('<I',n&0xffffffff)
sha=lambda b:hashlib.sha256(b).hexdigest()
ORIGINAL={'setbits':0x47ed76,'isr':0x47ee4a,'callback':0x47ee1e,'irq':0x4b80be,'disable':0x52dd6a,'dispatch':0x52b9d0,'event':0x52b91e}
NAMES={'setbits':'xEventGroupSetBits','isr':'xEventGroupSetBitsFromISR','callback':'vEventGroupSetBitsCallback','irq':'GPIO0_607F_IRQHandler','disable':'opencfw_radio_gpio_disable','dispatch':'opencfw_wsf_dispatch','event':'opencfw_wsf_set_event'}
BOUNDARIES={0x454d7c:'suspend',0x454dcc:'resume',0x45547c:'unblock',0x441952:'send',0x5fa0a4:'assert',0x442228:'context',0x52a574:'ticks',0x47ebf8:'wait'}
SOURCE_BOUNDARIES={'vTaskSuspendAll':'suspend','xTaskResumeAll':'resume','vTaskRemoveFromUnorderedEventList':'unblock','opencfw_event_queue_send_isr':'send','opencfw_event_group_assert_failure':'assert','opencfw_wsf_context_is_isr':'context','opencfw_wsf_timer_update':'ticks','opencfw_wsf_wait':'wait'}
def run(segments,entries,boundaries,radio_callback,c):
 import unicorn as u
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS)
 for s in segments:
  if s['memory_size']:
   lo=s['address']&~4095;n=((s['address']+s['memory_size']+4095)&~4095)-lo;cpu.mem_map(lo,n);cpu.mem_write(s['address'],s['data'])
 for lo,n in [(0x20000000,0x80000),(0x40010000,4096),(0xe000e000,4096),(CB,4096),(STOP,4096)]:cpu.mem_map(lo,n)
 count=len(c['waiters']);end=G+12;head=ITEMS if count else end;tail=ITEMS+(count-1)*32 if count else end
 cpu.mem_write(G-4,b'\xcc'*4+w(c['initial'])+w(count)+w(end)+w(0xffffffff)+w(head)+w(tail)+w(0x13579bdf)+bytes([1,0,0,0])+b'\xcc'*4)
 for i,val in enumerate(c['waiters']):
  ptr=ITEMS+i*32;next=ITEMS+(i+1)*32 if i+1<count else end;prev=ITEMS+(i-1)*32 if i else end
  cpu.mem_write(ptr,w(val)+w(next)+w(prev)+w(0x20015000+i*128)+w(G+4))
 cpu.mem_write(HIGH,w(0xabadcafe));cpu.mem_write(0x20074ab0,w(QUEUE));cpu.mem_write(0x20074ef0,w(G));cpu.mem_write(STATE+7*4,w(CB|1));cpu.mem_write(CB,b'\x70\x47');cpu.mem_write(0x20074fcb,b'\x07');cpu.mem_write(0x20074640,w(0xffffffff));cpu.mem_write(0x20068228+117*4,w(radio_callback|1))
 for i in range(14):cpu.mem_write(0x40010530+i*16,w(0xffffffff if i==3 else 0)+w(1<<21 if i==3 else 0)+w(0))
 log=[];io=[];trace={};queued=[];stacks=[];suspended=0;asserted=False;returns=[];group_writes=[]
 def read(a):return struct.unpack('<I',cpu.mem_read(a,4))[0]
 def ret(uc,val=0):uc.reg_write(UC_ARM_REG_R0,val&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def code(uc,pc,size,_):
  nonlocal suspended,asserted
  args=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];prior=uc.reg_read(UC_ARM_REG_PRIMASK)
  if pc in boundaries:
   name=boundaries[pc]
   if name=='suspend':suspended+=1;log.append(['suspend',suspended,prior]);ret(uc)
   elif name=='resume':
    assert suspended==1;log.append(['resume',read(G),prior]);suspended-=1
    if c['resume_bits']:uc.mem_write(G,w(read(G)|c['resume_bits']))
    ret(uc,c['resume_result'])
   elif name=='unblock':
    ptr,bits=args[:2];assert suspended==1 and ITEMS<=ptr<ITEMS+len(c['waiters'])*32
    old,next,prev,owner,container=struct.unpack('<IIIII',uc.mem_read(ptr,20));assert container==G+4
    log.append(['unblock',(ptr-ITEMS)//32,bits,read(G),prior])
    uc.mem_write(prev+4,w(next));uc.mem_write(next+8,w(prev));uc.mem_write(G+4,w(read(G+4)-1));uc.mem_write(ptr,w(bits)+w(0xdeadc0de));uc.mem_write(ptr+16,w(0));ret(uc)
   elif name=='send':
    assert args[0]==QUEUE and args[3]==0
    raw=bytes(uc.mem_read(args[1],16));cmd,callback,group,bits=struct.unpack('<IIII',raw);assert cmd==0xfffffffe and callback==(entries['callback']|1)
    log.append(['send',QUEUE,[cmd,'event_set_callback',group,bits],c['queue_result'],c['higher'],prior]);stacks.append(args[1])
    if args[2]:uc.mem_write(args[2],w(c['higher']))
    if c['queue_result']:queued.append(raw)
    ret(uc,c['queue_result'])
   elif name=='assert':log.append(['assert',prior]);asserted=True;uc.emu_stop()
   elif name=='context':log.append(['context',c['context'],prior]);ret(uc,c['context'])
   elif name=='ticks':log.append(['ticks',prior]);ret(uc)
   elif name=='wait':
    timeout=read(uc.reg_read(UC_ARM_REG_SP));assert args==[G,1,1,0] and timeout==0xffffffff;log.append(['wait',G,1,1,0,timeout,prior]);ret(uc)
   return
  if pc==CB:
   log.append(['handler',7,args[0],args[1],bytes(uc.mem_read(STATE+0x28+7,1))[0],prior]);ret(uc);return
  matches=[s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data'])];assert len(matches)==1,hex(pc);s=matches[0];raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  prior=uc.reg_read(UC_ARM_REG_PRIMASK)
  if access==u.UC_MEM_WRITE and G-4<=a<G+36:
   assert G<=a and a+size<=G+32;group_writes.append([a,size,value,suspended,prior])
  if 0x40010000<=a<0x40011000 or a==0xe000ed04:
   isread=access==u.UC_MEM_READ;v=read(a) if isread else value;assert size==4;io.append(['read' if isread else 'write',a,v,prior])
   if a==0xe000ed04:assert not isread and v==0x10000000
   elif isread:assert prior==1
   elif a==0x40010568:uc.mem_write(a-4,w(read(a-4)&~v))
   else:assert a==0x40010560
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem);cpu.reg_write(UC_ARM_REG_PRIMASK,c['prior'])
 for op,a,b in c['program']:
  if op=='deliver':
   if not queued:continue
   raw=queued.pop(0);cmd,callback,a,b=struct.unpack('<IIII',raw);op='callback';log.append(['daemon_delivery',a,b])
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[a,b,0 if c['null_higher'] else HIGH]):cpu.reg_write(reg,val)
  cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,STOP|1);cpu.emu_start(entries[op]|1,STOP,count=20000)
  if asserted:returns.append('assert-terminal-entry');break
  assert cpu.reg_read(UC_ARM_REG_PC)==STOP;returns.append(cpu.reg_read(UC_ARM_REG_R0) if op in ['setbits','isr'] else None)
  for ptr in stacks:cpu.mem_write(ptr,b'\xcc'*16) # Synthetic queue's copy survives later stack reuse.
  stacks.clear()
 assert bytes(cpu.mem_read(G-4,4))==bytes(cpu.mem_read(G+32,4))==b'\xcc'*4
 return dict(group=bytes(cpu.mem_read(G,32)).hex(),items=[bytes(cpu.mem_read(ITEMS+i*32,20)).hex() for i in range(len(c['waiters']))],state=bytes(cpu.mem_read(STATE+0x28,24)).hex(),depth=bytes(cpu.mem_read(DEPTH,1))[0],primask=cpu.reg_read(UC_ARM_REG_PRIMASK),higher=read(HIGH),asserted=asserted,suspended=suspended,queued=[['event_set_callback',*struct.unpack('<IIII',raw)[2:]] for raw in queued],log=log,io=io,group_writes=group_writes,returns=returns,counter=read(0x20074640),gpio=bytes(cpu.mem_read(0x40010560,12)).hex(),trace=trace)
def expected(c,r):
 bits=c['initial'];active=list(range(len(c['waiters'])));unblocks=[];returns=[];terminal=False
 for op,group,mask in c['program']:
  if op not in ['setbits','callback']:continue
  if group==0 or mask&0xff000000:terminal=True;returns.append('assert-terminal-entry');break
  bits|=mask;clear=0
  for i in list(active):
   val=c['waiters'][i];wanted=val&0xffffff;matched=(bits&wanted)==wanted if val&0x04000000 else bool(bits&wanted)
   if matched:
    unblocks.append(['unblock',i,bits|0x02000000,bits,c['prior']]);active.remove(i)
    if val&0x01000000:clear|=wanted
  bits&=~clear;bits|=c['resume_bits'];returns.append(bits if op=='setbits' else None)
 if c['program'][0][0] in ['setbits','callback']:
  assert r['asserted']==terminal and struct.unpack('<I',bytes.fromhex(r['group'])[:4])[0]==bits
  assert [x for x in r['log'] if x[0]=='unblock']==unblocks and r['returns']==returns
  assert struct.unpack('<I',bytes.fromhex(r['group'])[4:8])[0]==len(active)
 assert r['suspended']==0
 if c['program'][0][0]=='isr' and len(c['program'])==1:
  assert not r['asserted'] and r['returns']==[c['queue_result']];assert struct.unpack('<I',bytes.fromhex(r['group'])[:4])[0]==c['initial'];assert len(r['queued'])==int(bool(c['queue_result']))
 if c['program'][0][0]=='disable':
  assert r['counter']==0 and bytes.fromhex(r['state'])[7]==0
  assert any(x[:3]==['handler',7,1] and x[4]==0 for x in r['log'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';stock=[dict(address=BASE,data=blob[32:],memory_size=len(blob)-32,flags=5)];elf,segs,syms=parser.elf_info(a.elf)
 default=dict(waiters=[],initial=0,prior=0,resume_bits=0,resume_result=0,queue_result=1,higher=1,null_higher=False,context=0)
 cases=[];scenarios=[[],[1],[0x01000001],[0x04000003],[0x05000003],[2,0x01000001,0x04000003,0x05000003,4],[0x05000000,0x01000003,0x05000001]]
 for waiters in scenarios:
  for initial in [0,1,2,3,0x800000]:
   for mask in [0,1,2,3,0x800000]:cases.append(dict(default,waiters=waiters,initial=initial,program=[['setbits',G,mask]]))
 cases.extend([dict(default,program=[['setbits',0,1]]),dict(default,program=[['setbits',G,0x01000000]]),dict(default,program=[['setbits',G,0xffffffff]]),dict(default,waiters=[0x01000001,1],program=[['setbits',G,1],['setbits',G,1]]),dict(default,resume_bits=8,program=[['setbits',G,1]])])
 for result in [0,1]:
  for higher in [0,1]:
   for null in [False,True]:
    for group,mask in [(G,1),(0,1),(G,0x01000000)]:cases.append(dict(default,queue_result=result,higher=higher,null_higher=null,program=[['isr',group,mask]]))
 for result in [0,1]:
  for waiters in [[],[0x01000001]]:cases.append(dict(default,queue_result=result,waiters=waiters,program=[['isr',G,1],['deliver',0,0]]))
 cases.extend([dict(default,program=[['isr',0,1],['deliver',0,0]]),dict(default,program=[['isr',G,0x01000000],['deliver',0,0]])])
 for context in [0,1]:
  for waiters in [[],[0x01000001]]:
   for result in [0,1]:cases.append(dict(default,context=context,waiters=waiters,queue_result=result,program=[['disable',0,0],['irq',0,0]]+([['deliver',0,0]] if context else [])+[['dispatch',0,0]]))
 results=[];observed={}
 for c in cases:
  x=run(stock,ORIGINAL,BOUNDARIES,0x4b4a98,c);y=run(segs,{k:syms[n]&~1 for k,n in NAMES.items()},{syms[n]&~1:v for n,v in SOURCE_BOUNDARIES.items()},syms['opencfw_radio_gpio_callback'],c);trace=x.pop('trace');y.pop('trace');assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});expected(c,x);observed.update(trace);results.append(dict(inputs=c,result=x,original_trace=trace))
 comp=Path(__file__).resolve().parents[1];report=dict(status='PASS',case_count=len(cases),cases=results,original_trace={hex(k):v for k,v in sorted(observed.items())},unique_original_trace_bytes=sum(len(bytes.fromhex(v)) for v in observed.values()),elf_sha256=sha(elf),firmware_sha256=sha(blob),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},limits='Real pinned EventGroupSetBits/ISRwrapper/timerpend/callback plus WSF/radio/GPIO execute. Scheduler suspend/resume/unblock, queue-send-copy, context/wait/ticks/app handlers remain fixtures. Manual daemon delivery and copy/stackreuse prove fixture contract only, not actual queue/daemon behavior. Invalid asserts checked to terminal diagnostic entry, not full fatal hardware path. No TCB ready insertion, actual scheduling, group destruction/quiescence or physical ISR claim.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(cases),'event-group comparisons',report['unique_original_trace_bytes'],'unique original bytes')
if __name__=='__main__':main()
