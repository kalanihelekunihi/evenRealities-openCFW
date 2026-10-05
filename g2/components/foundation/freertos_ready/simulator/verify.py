#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Actual ready/pending-list transitions linked to queue/daemon/WSF sources."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
BASE=0x438000;G=0x20012340;ITEMS=0x20014000;QUEUE=0x20018000;HIGH=0x20001000;STATE=0x20073230;DEPTH=0x20075045;CB=0x9000000;STOP=0x8000000
w=lambda n:struct.pack('<I',n&0xffffffff)
sha=lambda b:hashlib.sha256(b).hexdigest()
ORIGINAL={'setbits':0x47ed76,'isr':0x47ee4a,'callback':0x47ee1e,'irq':0x4b80be,'disable':0x52dd6a,'dispatch':0x52b9d0,'event':0x52b91e,'send':0x441952,'receive':0x441b0a,'drain':0x47e97a,'remove':0x455370,'count':0x454f10}
NAMES={'setbits':'xEventGroupSetBits','isr':'xEventGroupSetBitsFromISR','callback':'vEventGroupSetBitsCallback','irq':'GPIO0_607F_IRQHandler','disable':'opencfw_radio_gpio_disable','dispatch':'opencfw_wsf_dispatch','event':'opencfw_wsf_set_event','send':'xQueueGenericSendFromISR','receive':'opencfw_queue_receive_nowait','drain':'opencfw_timer_callbacks_drain','remove':'xTaskRemoveFromEventList','count':'uxTaskGetNumberOfTasks'}
BOUNDARIES={0x454d7c:'suspend',0x454dcc:'resume',0x45547c:'unblock',0x45596e:'disinherit',0x442228:'context',0x52a574:'ticks',0x47ebf8:'wait',0x4558a4:'scheduler_state'}
SOURCE_BOUNDARIES={'vTaskSuspendAll':'suspend','xTaskResumeAll':'resume','vTaskRemoveFromUnorderedEventList':'unblock','xTaskPriorityDisinherit':'disinherit','opencfw_event_group_assert_failure':'assert','opencfw_wsf_context_is_isr':'context','opencfw_wsf_timer_update':'ticks','opencfw_wsf_wait':'wait','opencfw_daemon_scheduler_state':'scheduler_state','opencfw_daemon_positive_boundary':'positive'}
def run(segments,entries,boundaries,radio_callback,c):
 import unicorn as u
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK,UC_ARM_REG_BASEPRI,UC_ARM_REG_XPSR
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
 DATA=QUEUE+0x100;capacity=c['capacity'];count=c['queued_count'];size=c['item_size'];
 if c['preloaded']:assert c['write_slot']==count%capacity and len(c['preloaded'])==count
 write=DATA+c['write_slot']*size
 cpu.mem_write(QUEUE,w(DATA)+w(write)+w(DATA+capacity*size)+w(DATA+((c['write_slot']-count-1)%capacity)*size)+bytes(40)+w(count)+w(capacity)+w(size)+bytes([255,c['tx_lock']&255,0,0])+w(0)+bytes(4))
 cpu.mem_write(0x2000309c,w(c['task_depth']));cpu.mem_write(DATA,b'\xa5'*(capacity*max(size,1)))
 for slot,bits in enumerate(c['preloaded']):cpu.mem_write(DATA+slot*16,w(c['command'])+w(entries['callback']|1)+w(G)+w(bits))

 TA=0x20024000;TB=0x20024100;TR=0x20024200;CURRENT=0x20024300;EXTRA=0x20024400;TP=0x20024500;TH=0x20024600
 DELAYED=0x20026000;OTHER=0x20026040;PENDING=0x20073d24;READY=0x2006a49c
 graph_lists=[DELAYED,OTHER,PENDING]+[READY+i*20 for i in range(8)]+[QUEUE+16,QUEUE+36]
 def list_init(a):cpu.mem_write(a,w(0)+w(a+8)+w(0xffffffff)+w(a+8)+w(a+8))
 def append(a,item,value,owner):
  end=a+8;tail=read_setup(a+16)
  cpu.mem_write(item,w(value)+w(end)+w(tail)+w(owner)+w(a));cpu.mem_write(tail+4,w(item));cpu.mem_write(a+16,w(item));cpu.mem_write(a,w(read_setup(a)+1))
 def read_setup(a):return struct.unpack('<I',cpu.mem_read(a,4))[0]
 for a in graph_lists:list_init(a)
 tasks=[TA,TB,TR,CURRENT,EXTRA,TP,TH]
 for t in tasks:cpu.mem_write(t,b'\xa6'*112);cpu.mem_write(t+4,bytes(40));cpu.mem_write(t+44,w(c['priority'] if t in [TA,TR] else max(0,c['priority']-1) if t==TB else c['current_priority'] if t==CURRENT else 5 if t==TH else 1))
 append(READY+c['current_priority']*20,CURRENT+4,0,CURRENT)
 if c['ready_existing']:append(READY+c['priority']*20,TR+4,0,TR)
 if c['high_ready']:append(READY+100,TH+4,0,TH)
 if c['remaining_delayed']:append(DELAYED,EXTRA+4,50,EXTRA)
 # Append blocked tasks in increasing wake-time order independently of event priority.
 state_list=OTHER if c['state_other'] else DELAYED
 # Prepend A/B ahead of the optional tick50 task via explicit list rebuilding.
 blocked=[TA]+([TB] if c['waiter_count']>1 else [])
 for a in [DELAYED,OTHER]:list_init(a)
 for t,value in [(TA,10)]+([(TB,20)] if c['waiter_count']>1 else []):append(state_list,t+4,value,t)
 if c['remaining_delayed']:append(DELAYED,EXTRA+4,50,EXTRA)
 event_list=QUEUE+(16 if c['event_senders'] else 36)
 if c['waiter_count']:
  for t in blocked:append(event_list,t+24,8-read_setup(t+44),0 if c['null_owner'] and t==TA else t)
 if c['index_removed'] and c['waiter_count']:cpu.mem_write(event_list+4,w(TA+24));cpu.mem_write(state_list+4,w(TA+4))
 if c['ready_existing'] and c['ready_index_node']:cpu.mem_write(READY+c['priority']*20+4,w(TR+4))
 if c['pending_existing']:append(OTHER,TP+4,70,TP);append(PENDING,TP+24,7,TP)
 if c['pending_existing'] and c['pending_index_node']:cpu.mem_write(PENDING+4,w(TP+24))
 cpu.mem_write(0x20074a20,w(CURRENT));cpu.mem_write(0x20074a24,w(DELAYED));cpu.mem_write(0x20074a30,w(c['task_count']));cpu.mem_write(0x20074a38,w(max(c['current_priority'],c['priority'] if c['ready_existing'] else 0,5 if c['high_ready'] else 0)));cpu.mem_write(0x20074a44,w(c['yield_pending']));cpu.mem_write(0x20074a50,w(c['next_unblock']));cpu.mem_write(0x20074a58,w(c['scheduler_suspended']))
 PACKET=0x20002000;cpu.mem_write(PACKET,bytes(range(16)))
 cpu.mem_write(DEPTH,bytes([c.get('depth',0)]));cpu.mem_write(HIGH,w(c['initial_higher']));cpu.mem_write(0x20074ab0,w(QUEUE));cpu.mem_write(0x20074ef0,w(G));cpu.mem_write(STATE+7*4,w(CB|1));cpu.mem_write(CB,b'\x70\x47');cpu.mem_write(0x20074fcb,b'\x07');cpu.mem_write(0x20074640,w(0xffffffff));cpu.mem_write(0x20068228+117*4,w(radio_callback|1))
 for i in range(14):cpu.mem_write(0x40010530+i*16,w(0xffffffff if i==3 else 0)+w(1<<21 if i==3 else 0)+w(0))
 history=[];kernel_writes=[];log=[];io=[];trace={};queued=[];stacks=[];suspended=0;asserted=False;returns=[];group_writes=[]
 def read(a):return struct.unpack('<I',cpu.mem_read(a,4))[0]
 def ret(uc,val=0):uc.reg_write(UC_ARM_REG_R0,val&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def code(uc,pc,size,_):
  nonlocal suspended,asserted
  args=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];history.append([hex(pc),*[hex(x) for x in args],hex(uc.reg_read(UC_ARM_REG_XPSR))]);history[:]=history[-24:];prior=uc.reg_read(UC_ARM_REG_PRIMASK)
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
   elif name=='receiver':
    assert args[0] in [QUEUE+0x24,QUEUE+0x10] and uc.reg_read(UC_ARM_REG_BASEPRI)==0x30;log.append(['receiver',c['receiver_result'],read(QUEUE+0x38),uc.reg_read(UC_ARM_REG_BASEPRI)]);ret(uc,c['receiver_result'])
   elif name=='tasks':log.append(['tasks',c['task_count']]);ret(uc,c['task_count'])
   elif name=='disinherit':log.append(['disinherit',args[0]]);ret(uc,0)
   elif name=='assert':log.append(['assert',prior]);asserted=True;uc.emu_stop()
   elif name=='positive':log.append(['positive-boundary']);asserted=True;uc.emu_stop()
   elif name=='scheduler_state':log.append(['scheduler_state',c['scheduler_state']]);ret(uc,c['scheduler_state'])
   elif name=='context':log.append(['context',c['context'],prior]);ret(uc,c['context'])
   elif name=='ticks':log.append(['ticks',prior]);ret(uc)
   elif name=='wait':
    timeout=read(uc.reg_read(UC_ARM_REG_SP));assert args==[G,1,1,0] and timeout==0xffffffff;log.append(['wait',G,1,1,0,timeout,prior]);ret(uc)
   return
  if pc==0x5fa0a4 and uc.reg_read(UC_ARM_REG_LR) not in [(0x4419be|1),(0x4420d6|1)]:
   log.append(['assert',prior]);asserted=True;uc.emu_stop();return
  if pc==0x47e9b8:
   log.append(['positive-boundary']);asserted=True;uc.emu_stop();return
  if pc==entries['remove']:
   assert uc.reg_read(UC_ARM_REG_BASEPRI)==0x30
   log.append(['ready_remove_entry',args[0],uc.reg_read(UC_ARM_REG_BASEPRI),read(0x20074a58)])
  if pc==entries['callback']:
   log.append(['callback_entry',args[0],args[1],read(QUEUE+0x38)])
  if pc==CB:
   log.append(['handler',7,args[0],args[1],bytes(uc.mem_read(STATE+0x28+7,1))[0],prior]);ret(uc);return
  matches=[s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data'])];assert len(matches)==1,hex(pc);s=matches[0];raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  prior=uc.reg_read(UC_ARM_REG_PRIMASK)
  if access==u.UC_MEM_WRITE and (QUEUE<=a<QUEUE+80 or DATA<=a<DATA+capacity*max(c['item_size'],1)):
   assert uc.reg_read(UC_ARM_REG_BASEPRI)==0x30,(hex(a),'queue mutation outside expected BASEPRI')
  if access==u.UC_MEM_WRITE and (TA<=a<TH+112 or any(x<=a<x+20 for x in graph_lists) or a in [0x20074a38,0x20074a44,0x20074a50]):
   assert uc.reg_read(UC_ARM_REG_BASEPRI)==0x30
   kernel_writes.append([hex(a),size,hex(value)])
  if access==u.UC_MEM_WRITE and G-4<=a<G+36:
   assert G<=a and a+size<=G+32;group_writes.append([a,size,value,suspended,prior])
  if 0x40010000<=a<0x40011000 or a==0xe000ed04:
   isread=access==u.UC_MEM_READ;v=read(a) if isread else value;assert size==4;io.append(['read' if isread else 'write',a,v,prior])
   if a==0xe000ed04:assert not isread and v==0x10000000
   elif isread:assert prior==1
   elif a==0x40010568:uc.mem_write(a-4,w(read(a-4)&~v))
   else:assert a==0x40010560
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem);cpu.reg_write(UC_ARM_REG_PRIMASK,c['prior']);cpu.reg_write(UC_ARM_REG_BASEPRI,c['basepri'])
 for op,a,b in c['program']:
  if op=='deliver':op='drain'
  if op=='remove':a=event_list
  if op=='receive':a=0 if c['null_queue'] else QUEUE;b=0 if c['null_packet'] else PACKET
  if op=='send':a=0 if c['null_queue'] else QUEUE;b=0 if c['null_packet'] else PACKET
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[a,b,0 if op in ['receive','drain'] else 0 if c['null_higher'] else HIGH,c['position']]):cpu.reg_write(reg,val)
  cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,STOP|1)
  for segment in segments:
   if segment['flags']&1:cpu.ctl_remove_cache(segment['address'],segment['address']+len(segment['data']))
  try:cpu.emu_start(entries[op]|1,STOP,count=20000)
  except u.UcError as error:raise RuntimeError((str(error),hex(cpu.reg_read(UC_ARM_REG_PC)),op,c, [hex(cpu.reg_read(r)) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]], list(trace.items())[-6:],kernel_writes[-40:],bytes(cpu.mem_read(READY+40,20)).hex(),history)) from error
  if asserted:returns.append('positive-command-boundary' if log[-1][0]=='positive-boundary' else 'assert-branch-boundary');break
  assert cpu.reg_read(UC_ARM_REG_PC)==STOP;returns.append(cpu.reg_read(UC_ARM_REG_R0) if op in ['setbits','isr','send','receive','remove','count'] else None)
  if op in ['isr','send']:cpu.mem_write(0x2000efc0,b'\xcc'*64);cpu.mem_write(PACKET,b'\xcc'*16)
 assert bytes(cpu.mem_read(G-4,4))==bytes(cpu.mem_read(G+32,4))==b'\xcc'*4
 return dict(kernel={'lists':{hex(a):bytes(cpu.mem_read(a,20)).hex() for a in graph_lists},'tasks':{hex(t):bytes(cpu.mem_read(t,112)).hex() for t in tasks},'top':read(0x20074a38),'pending_yield':read(0x20074a44),'next_unblock':read(0x20074a50),'suspended':read(0x20074a58)},group=bytes(cpu.mem_read(G,32)).hex(),items=[bytes(cpu.mem_read(ITEMS+i*32,20)).hex() for i in range(len(c['waiters']))],state=bytes(cpu.mem_read(STATE+0x28,24)).hex(),depth=bytes(cpu.mem_read(DEPTH,1))[0],primask=cpu.reg_read(UC_ARM_REG_PRIMASK),higher=read(HIGH),asserted=asserted,suspended=suspended,queue_control=bytes(cpu.mem_read(QUEUE,80)).hex(),queue_data=bytes(cpu.mem_read(DATA,capacity*max(size,1))).replace(w(entries['callback']|1),b'CB!!').hex(),task_depth=read(0x2000309c),received_packet=bytes(cpu.mem_read(PACKET,16)).replace(w(entries['callback']|1),b'CB!!').hex(),basepri=cpu.reg_read(UC_ARM_REG_BASEPRI),log=log,io=io,group_writes=group_writes,returns=returns,counter=read(0x20074640),gpio=bytes(cpu.mem_read(0x40010560,12)).hex(),trace=trace)
def expected(c,r):
 bits=c['initial'];active=list(range(len(c['waiters'])));unblocks=[];returns=[];terminal=False
 for op,group,mask in c['program']:
  if op not in ['setbits','callback']:continue
  if group==0 or mask&0xff000000:terminal=True;returns.append('assert-branch-boundary');break
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
 # Independent producer model for isolated nonterminal send/ISR cases.
 if len(c['program'])==1 and c['program'][0][0] in ['send','isr'] and not r['asserted']:
  count=c['queued_count'];success=count<c['capacity'] or c['position']==2
  assert r['returns']==[int(success)]
  control=bytes.fromhex(r['queue_control']);data=bytes.fromhex(r['queue_data'])
  expected_count=count+(int(success) if c['position']!=2 or count==0 else 0)
  assert struct.unpack_from('<I',control,0x38)[0]==expected_count
  expected_high=1 if success and c['tx_lock']==-1 and not c['event_senders'] and c['priority']>c['current_priority'] and c['waiter_count'] and not c['null_higher'] else c['initial_higher']
  assert r['higher']==expected_high
  expected_lock=c['tx_lock']
  if success and expected_lock!=-1 and (expected_lock&0xffffffff)<c['task_count']:expected_lock+=1
  assert control[0x45]==(expected_lock&255)
  if not success or c['item_size']==0:assert data==b'\xa5'*(c['capacity']*max(c['item_size'],1))
  elif c['position']==0:
   off=c['write_slot']*c['item_size']
   packet=bytes(range(16)) if c['program'][0][0]=='send' else w(0xfffffffe)+b'CB!!'+w(c['program'][0][1])+w(c['program'][0][2])
   assert data[off:off+c['item_size']]==packet[:c['item_size']]
   assert struct.unpack_from('<I',control,4)[0]==QUEUE+0x100+((c['write_slot']+1)%c['capacity'])*c['item_size']
 expected_basepri=c['basepri']
 if any(x[0] in ['deliver','drain','receive'] for x in c['program']) and not r['asserted']:expected_basepri=0x30 if c['task_depth'] else 0
 assert r['basepri']==expected_basepri or r['asserted']
 assert r['task_depth']==c['task_depth'] or r['asserted']
 if c['program']==[['receive',0,0]] and not r['asserted']:
  assert r['returns']==[int(c['queued_count']!=0)]
  assert struct.unpack_from('<I',bytes.fromhex(r['queue_control']),0x38)[0]==max(0,c['queued_count']-1)
  packet=w(c['command'])+b'CB!!'+w(G)+w(c['preloaded'][0]) if c['preloaded'] else bytes(range(16))
  assert bytes.fromhex(r['received_packet'])==packet
 # Independent FIFO drain: successful send packets remain queue-owned after
 # caller stack clobber; group bits reflect all callbacks in enqueue order.
 if not r['asserted'] and c['program'][-1][0] in ['deliver','drain']:
  assert struct.unpack_from('<I',bytes.fromhex(r['queue_control']),0x38)[0]==0
  wanted=0;callback_bits=list(c['preloaded'])
  for bits in c['preloaded']:wanted|=bits
  available=c['queued_count']
  for op,group,bits in c['program']:
   if op in ['isr','event'] and available<c['capacity']:
    callback_mask=1 if op=='event' else bits
    wanted|=callback_mask;available+=1;callback_bits.append(callback_mask)
  assert struct.unpack_from('<I',bytes.fromhex(r['group']))[0]==(c['initial']|wanted)
  assert [x for x in r['log'] if x[0]=='callback_entry']==[['callback_entry',G,bits,len(callback_bits)-i-1] for i,bits in enumerate(callback_bits)]

 if c['program'][0][0]=='disable':
  assert r['counter']==0 and bytes.fromhex(r['state'])[7]==0
  assert any(x[:3]==['handler',7,1] and x[4]==0 for x in r['log'])
 graph_expected(c,r)

def graph_expected(c,r):
 """Independent list sequence model; checks every edge, index and ownership."""
 TA,TB,TR,CURRENT,EXTRA,TP,TH=[0x20024000+i*256 for i in range(7)]
 DELAYED,OTHER,PENDING,READY=0x20026000,0x20026040,0x20073d24,0x2006a49c
 k=r['kernel'];lists={int(a,16):struct.unpack('<IIIII',bytes.fromhex(v)) for a,v in k['lists'].items()}
 nodes={};tasks={int(a,16):bytes.fromhex(v) for a,v in k['tasks'].items()}
 for t,raw in tasks.items():
  assert raw[:4]==b'\xa6'*4 and raw[48:]==b'\xa6'*64
  priority=c['priority'] if t in [TA,TR] else max(0,c['priority']-1) if t==TB else c['current_priority'] if t==CURRENT else 5 if t==TH else 1
  assert struct.unpack_from('<I',raw,44)[0]==priority
  for offset in [4,24]:nodes[t+offset]=struct.unpack_from('<IIIII',raw,offset)
 model={a:[] for a in lists};indexes={a:a+8 for a in lists}
 def add(a,item):model[a].append(item)
 add(READY+c['current_priority']*20,CURRENT+4)
 if c['ready_existing']:add(READY+c['priority']*20,TR+4)
 if c['high_ready']:add(READY+100,TH+4)
 state=OTHER if c['state_other'] else DELAYED
 blocked=[TA]+([TB] if c['waiter_count']>1 else [])
 for t in blocked:add(state,t+4)
 if c['remaining_delayed']:add(DELAYED,EXTRA+4)
 event=QUEUE+(16 if c['event_senders'] else 36)
 if c['waiter_count']:
  for t in blocked:add(event,t+24)
 if c['index_removed'] and c['waiter_count']:indexes[event]=TA+24;indexes[state]=TA+4
 if c['ready_existing'] and c['ready_index_node']:indexes[READY+c['priority']*20]=TR+4
 if c['pending_existing']:add(OTHER,TP+4);add(PENDING,TP+24)
 if c['pending_existing'] and c['pending_index_node']:indexes[PENDING]=TP+24
 def remove(a,item):
  pos=model[a].index(item)
  if indexes[a]==item:indexes[a]=model[a][pos-1] if pos else a+8
  model[a].remove(item)
 def insert(a,item):
  pos=model[a].index(indexes[a]) if indexes[a]!=a+8 else len(model[a]);model[a].insert(pos,item)
 entries=[x for x in r['log'] if x[0]=='ready_remove_entry']
 removed=[] if c['null_owner'] else blocked[:len(entries)]
 assert len(entries)<=len(blocked)
 for t in removed:
  remove(event,t+24)
  if c['scheduler_suspended']:insert(PENDING,t+24)
  else:remove(state,t+4);insert(READY+struct.unpack_from('<I',tasks[t],44)[0]*20,t+4)
 seen=set()
 for a,sequence in model.items():
  count,index,value,head,tail=lists[a];end=a+8
  assert (count,index,value,head,tail)==(len(sequence),indexes[a],0xffffffff,sequence[0] if sequence else end,sequence[-1] if sequence else end),(hex(a),sequence,lists[a])
  for i,item in enumerate(sequence):
   assert item not in seen;seen.add(item)
   val,next,prev,owner,container=nodes[item]
   assert (next,prev,container)==(sequence[i+1] if i+1<len(sequence) else end,sequence[i-1] if i else end,a)
   expected_owner=0 if c['null_owner'] and item==TA+24 else item-(24 if item%256==24 else 4)
   assert owner==expected_owner
 for t in removed:
  assert nodes[t+24][4]==(PENDING if c['scheduler_suspended'] else 0)
 initial_top=max(c['current_priority'],c['priority'] if c['ready_existing'] else 0,5 if c['high_ready'] else 0)
 assert k['top']==max([initial_top]+[struct.unpack_from('<I',tasks[t],44)[0] for t in removed if not c['scheduler_suspended']])
 assert k['pending_yield']==(1 if any(struct.unpack_from('<I',tasks[t],44)[0]>c['current_priority'] for t in removed) else c['yield_pending'])
 remaining=[nodes[item][0] for item in model[DELAYED]]
 assert k['next_unblock']==(min(remaining) if remaining else 0xffffffff) if removed and not c['scheduler_suspended'] else k['next_unblock']==c['next_unblock']
 assert k['suspended']==c['scheduler_suspended']
 if c['program'][0][0]=='remove' and not c['null_owner']:assert r['returns']==[int(struct.unpack_from('<I',tasks[t],44)[0]>c['current_priority']) for t in removed]
 if c['program'][0][0]=='count':assert r['returns']==[c['task_count']]
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';stock=[dict(address=BASE,data=blob[32:],memory_size=len(blob)-32,flags=5)];elf,segs,syms=parser.elf_info(a.elf)
 default=dict(priority=3,current_priority=1,scheduler_suspended=0,ready_existing=False,high_ready=False,remaining_delayed=0,state_other=False,index_removed=False,ready_index_node=False,pending_existing=False,pending_index_node=False,waiter_count=1,event_senders=False,null_owner=False,yield_pending=0,next_unblock=999,task_depth=0,senders=0,scheduler_state=2,preloaded=[],command=-2,capacity=2,queued_count=0,item_size=16,write_slot=0,tx_lock=-1,receivers=0,receiver_result=0,task_count=4,initial_higher=0,position=0,null_queue=False,null_packet=False,basepri=0x30,waiters=[],initial=0,prior=0,resume_bits=0,resume_result=0,queue_result=1,higher=1,null_higher=False,context=0)
 cases=[]
 for suspended in [0,1,3]:
  for priority in [0,1,3]:
   for current in [0,1,3]:
    for other in [False,True]:
     for remaining in [0,1]:
      for index in [False,True]:cases.append(dict(default,scheduler_suspended=suspended,priority=priority,current_priority=current,state_other=other,remaining_delayed=remaining,index_removed=index,ready_existing=True,ready_index_node=index,pending_existing=True,pending_index_node=index,program=[['remove',0,0]]))
 for count in [1,2]:
  for suspended in [0,1]:
   for high in [False,True]:
    for existing_yield in [0,1]:cases.append(dict(default,waiter_count=count,scheduler_suspended=suspended,high_ready=high,yield_pending=existing_yield,program=[['remove',0,0]]*count))
 for priority,current in [(0,1),(1,1),(3,1)]:
  for suspended in [0,1]:
   for null_higher in [False,True]:cases.append(dict(default,priority=priority,current_priority=current,scheduler_suspended=suspended,null_higher=null_higher,program=[['isr',G,1]]))
 for priority,current in [(0,1),(1,1),(3,1)]:
  for context in [0,1]:
   for prior in [0,1]:
    cases.append(dict(default,priority=priority,current_priority=current,context=context,prior=prior,program=[['disable',0,0],['irq',0,0]]+([['drain',0,0]] if context else [])+[['dispatch',0,0]]))
 for suspended in [0,1]:
  for priority,current in [(0,1),(3,1)]:cases.append(dict(default,event_senders=True,senders=1,queued_count=1,write_slot=1,preloaded=[4],priority=priority,current_priority=current,scheduler_suspended=suspended,program=[['receive',0,0]]))
 for lock in [-1,0,4,127]:
  for task_count in [1,4,128]:cases.append(dict(default,tx_lock=lock,task_count=task_count,program=[['isr',G,1]]))
 for id in [7,10,12,15,23,0xffffffff]:
  for mask in [0,1,256,257]:cases.append(dict(default,context=1,program=[['event',id,mask],['drain',0,0]]))
 cases.append(dict(default,null_owner=True,program=[['remove',0,0]]))
 cases.extend([dict(default,program=[['count',0,0]],task_count=n) for n in [0,1,128,0xffffffff]])
 results=[];observed={}
 for c in cases:
  x=run(stock,ORIGINAL,BOUNDARIES,0x4b4a98,c);y=run(segs,{k:syms[n]&~1 for k,n in NAMES.items()},{syms[n]&~1:v for n,v in SOURCE_BOUNDARIES.items()},syms['opencfw_radio_gpio_callback'],c);trace=x.pop('trace');y.pop('trace');assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});expected(c,x);observed.update(trace);results.append(dict(inputs=c,result=x,original_trace=trace))
 comp=Path(__file__).resolve().parents[1];report=dict(status='PASS',case_count=len(cases),cases=results,original_trace={hex(k):v for k,v in sorted(observed.items())},unique_original_trace_bytes=sum(len(bytes.fromhex(v)) for v in observed.values()),elf_sha256=sha(elf),firmware_sha256=sha(blob),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},limits='Actual ordered event-list removal, state ready/pending insertion, next-unblock reset and taskcount getter plus queue/receive/negative-daemon/EventGroup/WSF/radio execute. Coherent task/list/global state is synthetic input. EventGroup unordered unblock, suspend/resume, scheduler state/context/wait/ticks/app handling remain fixtures. Pending-ready drain/task selection/context switch/object lifecycle/hardware unproven; positive timers/blocking receive external. Invalid owner stops before fault tail.')
 report['execution_policy']='Unicorn 2.1.4; translation cache for executable segments is invalidated on both stock and source before each synthetic top-level call. Repeated-call source execution otherwise observed skipping a helper first instruction; no instruction bytes or algorithm substituted. Hardware scheduling and general emulator root cause unproven.'
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(cases),'RTOS-ready comparisons',report['unique_original_trace_bytes'],'unique original bytes')
if __name__=='__main__':main()
