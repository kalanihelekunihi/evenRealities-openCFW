#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Actual suspend/resume/pending-drain transitions linked to queue/daemon/WSF sources."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
BASE=0x438000;G=0x20012340;ITEMS=0x20014000;QUEUE=0x20018000;HIGH=0x20001000;STATE=0x20073230;DEPTH=0x20075045;CB=0x9000000;STOP=0x8000000
w=lambda n:struct.pack('<I',n&0xffffffff)
sha=lambda b:hashlib.sha256(b).hexdigest()
ORIGINAL={'setbits':0x47ed76,'isr':0x47ee4a,'callback':0x47ee1e,'irq':0x4b80be,'disable':0x52dd6a,'dispatch':0x52b9d0,'event':0x52b91e,'send':0x441952,'receive':0x441b0a,'drain':0x47e97a,'remove':0x455370,'count':0x454f10,'suspend':0x454d7c,'resume':0x454dcc,'tick':0x45504c}
NAMES={'setbits':'xEventGroupSetBits','isr':'xEventGroupSetBitsFromISR','callback':'vEventGroupSetBitsCallback','irq':'GPIO0_607F_IRQHandler','disable':'opencfw_radio_gpio_disable','dispatch':'opencfw_wsf_dispatch','event':'opencfw_wsf_set_event','send':'xQueueGenericSendFromISR','receive':'opencfw_queue_receive_nowait','drain':'opencfw_timer_callbacks_drain','remove':'xTaskRemoveFromEventList','count':'uxTaskGetNumberOfTasks','suspend':'vTaskSuspendAll','resume':'xTaskResumeAll','tick':'xTaskIncrementTick'}
BOUNDARIES={0x45547c:'unblock',0x45596e:'disinherit',0x442228:'context',0x52a574:'ticks',0x47ebf8:'wait',0x4558a4:'scheduler_state'}
SOURCE_BOUNDARIES={'vTaskRemoveFromUnorderedEventList':'unblock','xTaskPriorityDisinherit':'disinherit','opencfw_event_group_assert_failure':'assert','opencfw_wsf_context_is_isr':'context','opencfw_wsf_timer_update':'ticks','opencfw_wsf_wait':'wait','opencfw_daemon_scheduler_state':'scheduler_state','opencfw_daemon_positive_boundary':'positive'}
def run(segments,entries,boundaries,radio_callback,c):
 import unicorn as u
 import unicorn.arm_const as arm
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK,UC_ARM_REG_BASEPRI,UC_ARM_REG_XPSR
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS)
 cpu.ctl_set_cpu_model(u.arm_const.UC_CPU_ARM_CORTEX_M4)
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
 DELAYED=0x20026000;OTHER=0x20026040;OVER=0x20026080;PENDING=0x20073d24;READY=0x2006a49c
 graph_lists=[DELAYED,OTHER,OVER,PENDING]+[READY+i*20 for i in range(8)]+[QUEUE+16,QUEUE+36]
 def list_init(a):cpu.mem_write(a,w(0)+w(a+8)+w(0xffffffff)+w(a+8)+w(a+8))
 def append(a,item,value,owner):
  end=a+8;tail=read_setup(a+16)
  cpu.mem_write(item,w(value)+w(end)+w(tail)+w(owner)+w(a));cpu.mem_write(tail+4,w(item));cpu.mem_write(a+16,w(item));cpu.mem_write(a,w(read_setup(a)+1))
 def read_setup(a):return struct.unpack('<I',cpu.mem_read(a,4))[0]
 for a in graph_lists:list_init(a)
 tasks=[TA,TB,TR,CURRENT,EXTRA,TP,TH]
 for index,t in enumerate(tasks):cpu.mem_write(t,b'\xa6'*112);cpu.mem_write(t+4,bytes(40));cpu.mem_write(t+44,w(c['task_priorities'][index]))
 append(READY+c['current_priority']*20,CURRENT+4,0,CURRENT)
 if c['ready_existing']:append(READY+c['priority']*20,TR+4,0,TR)
 if c['high_ready']:append(READY+100,TH+4,0,TH)
 blocked=[TA,TB][:c['waiter_count']]
 locations={'active':DELAYED,'overflow':OVER,'other':OTHER}
 initial_states=[(t,c['wake_times'][i],locations[c['state_locations'][i]]) for i,t in enumerate(blocked)]
 if c['remaining_delayed']:initial_states.append((EXTRA,c['wake_times'][2],locations[c['state_locations'][2]]))
 for t,value,where in sorted(initial_states,key=lambda x:x[1]):append(where,t+4,value,t)
 event_list=QUEUE+(16 if c['event_senders'] else 36)
 for i,t in sorted(enumerate(blocked),key=lambda item:8-read_setup(item[1]+44)):
  if c['event_linked'][i]:append(event_list,t+24,8-read_setup(t+44),t)
 if c['index_removed'] and blocked:
  if c['event_linked'][0]:cpu.mem_write(event_list+4,w(TA+24))
  cpu.mem_write(locations[c['state_locations'][0]]+4,w(TA+4))
 if c['ready_existing'] and c['ready_index_node']:cpu.mem_write(READY+c['priority']*20+4,w(TR+4))
 if c['pending_existing']:append(OTHER,TP+4,70,TP);append(PENDING,TP+24,7,TP)
 if c['pending_existing'] and c['pending_index_node']:cpu.mem_write(PENDING+4,w(TP+24))
 cpu.mem_write(0x20074a20,w(CURRENT));cpu.mem_write(0x20074a24,w(DELAYED));cpu.mem_write(0x20074a30,w(c['task_count']));cpu.mem_write(0x20074a38,w(max(c['current_priority'],c['priority'] if c['ready_existing'] else 0,5 if c['high_ready'] else 0)));cpu.mem_write(0x20074a44,w(c['yield_pending']));cpu.mem_write(0x20074a50,w(c['next_unblock']));cpu.mem_write(0x20074a58,w(c['scheduler_suspended']));cpu.mem_write(0x20074a40,w(c['pended_ticks']));cpu.mem_write(0x20074a28,w(OVER));cpu.mem_write(0x20074a34,w(c['tick_count']));cpu.mem_write(0x20074a48,w(c['overflow_count']))
 PACKET=0x20002000;cpu.mem_write(PACKET,bytes(range(16)))
 cpu.mem_write(DEPTH,bytes([c.get('depth',0)]));cpu.mem_write(HIGH,w(c['initial_higher']));cpu.mem_write(0x20074ab0,w(QUEUE));cpu.mem_write(0x20074ef0,w(G));cpu.mem_write(STATE+7*4,w(CB|1));cpu.mem_write(CB,b'\x70\x47');cpu.mem_write(0x20074fcb,b'\x07');cpu.mem_write(0x20074640,w(0xffffffff));cpu.mem_write(0x20068228+117*4,w(radio_callback|1))
 for i in range(14):cpu.mem_write(0x40010530+i*16,w(0xffffffff if i==3 else 0)+w(1<<21 if i==3 else 0)+w(0))
 history=[];kernel_writes=[];log=[];io=[];trace={};queued=[];stacks=[];resume_active=False;suspended=0;asserted=False;returns=[];group_writes=[]
 def read(a):return struct.unpack('<I',cpu.mem_read(a,4))[0]
 def ret(uc,val=0):uc.reg_write(UC_ARM_REG_R0,val&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def code(uc,pc,size,_):
  nonlocal suspended,asserted,resume_active
  args=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];history.append([hex(pc),*[hex(x) for x in args],hex(uc.reg_read(UC_ARM_REG_XPSR))]);history[:]=history[-24:];prior=uc.reg_read(UC_ARM_REG_PRIMASK)
  if pc in boundaries:
   name=boundaries[pc]
   if name=='tick_boundary':
    index=sum(x[0]=='tick_boundary' for x in log);value=c['tick_returns'][index%len(c['tick_returns'])]
    assert uc.reg_read(UC_ARM_REG_BASEPRI)==0x30 and read(0x20074a58)==0
    log.append(['tick_boundary',index,value,read(0x20074a40),uc.reg_read(UC_ARM_REG_BASEPRI)]);ret(uc,value)
   elif name=='suspend':suspended+=1;log.append(['suspend',suspended,prior]);ret(uc)
   elif name=='resume':
    assert suspended==1;log.append(['resume',read(G),prior]);suspended-=1
    if c['resume_bits']:uc.mem_write(G,w(read(G)|c['resume_bits']))
    ret(uc,c['resume_result'])
   elif name=='unblock':
    ptr,bits=args[:2];assert suspended==1 and ITEMS<=ptr<ITEMS+len(c['waiters'])*32
    old,successor,prev,owner,container=struct.unpack('<IIIII',uc.mem_read(ptr,20));assert container==G+4
    log.append(['unblock',(ptr-ITEMS)//32,bits,read(G),prior])
    uc.mem_write(prev+4,w(successor));uc.mem_write(successor+8,w(prev));uc.mem_write(G+4,w(read(G+4)-1));uc.mem_write(ptr,w(bits)+w(0xdeadc0de));uc.mem_write(ptr+16,w(0));ret(uc)
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
  if pc==c['critical_exit_entry'] and resume_active:
   log.append(['resume_finish',read(0x20074a58),read(0x20074a40),read(0x20074a44)]);resume_active=False
  if pc==entries['tick']:
   log.append(['tick_entry',read(0x20074a34),read(0x20074a58),read(0x20074a40),int(resume_active)])
  if pc in [entries['suspend'],entries['resume']]:
   log.append(['suspend_entry' if pc==entries['suspend'] else 'resume_entry',read(0x20074a58),uc.reg_read(UC_ARM_REG_BASEPRI)])
   if pc==entries['resume']:resume_active=True
  if pc==entries['remove']:
   assert uc.reg_read(UC_ARM_REG_BASEPRI)==0x30
   log.append(['ready_remove_entry',args[0],uc.reg_read(UC_ARM_REG_BASEPRI),read(0x20074a58)])
  if pc==c['yield_entry']:
   assert uc.reg_read(UC_ARM_REG_BASEPRI)==0x30;log.append(['yield_request_entry'])
  if pc==entries['callback']:
   log.append(['callback_entry',args[0],args[1],read(QUEUE+0x38)])
  if pc==CB:
   log.append(['handler',7,args[0],args[1],bytes(uc.mem_read(STATE+0x28+7,1))[0],prior]);ret(uc);return
  matches=[s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data'])];assert len(matches)==1,hex(pc);s=matches[0];raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  prior=uc.reg_read(UC_ARM_REG_PRIMASK)
  if access==u.UC_MEM_WRITE and (QUEUE<=a<QUEUE+80 or DATA<=a<DATA+capacity*max(c['item_size'],1)):
   assert uc.reg_read(UC_ARM_REG_BASEPRI)==0x30,(hex(a),'queue mutation outside expected BASEPRI')
  if access==u.UC_MEM_WRITE and (TA<=a<TH+112 or any(x<=a<x+20 for x in graph_lists) or a in [0x20074a24,0x20074a28,0x20074a34,0x20074a38,0x20074a40,0x20074a44,0x20074a48,0x20074a50]):
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
  saved_registers={getattr(arm,'UC_ARM_REG_R'+str(i)):0xa6000000+i for i in range(4,12)}
  for reg,value in saved_registers.items():cpu.reg_write(reg,value)
  for segment in segments:
   if segment['flags']&1:cpu.ctl_remove_cache(segment['address'],segment['address']+len(segment['data']))
  try:cpu.emu_start(entries[op]|1,STOP,count=20000)
  except u.UcError as error:raise RuntimeError((str(error),hex(cpu.reg_read(UC_ARM_REG_PC)),op,c, [hex(cpu.reg_read(r)) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]], list(trace.items())[-6:],kernel_writes[-40:],bytes(cpu.mem_read(READY+40,20)).hex(),history)) from error
  if asserted:returns.append('positive-command-boundary' if log[-1][0]=='positive-boundary' else 'assert-branch-boundary');break
  assert cpu.reg_read(UC_ARM_REG_PC)==STOP and cpu.reg_read(UC_ARM_REG_SP)==0x2000f000
  assert all(cpu.reg_read(reg)==value for reg,value in saved_registers.items()),'callee-saved register mismatch'
  returns.append(cpu.reg_read(UC_ARM_REG_R0) if op in ['setbits','isr','send','receive','remove','count','resume','tick'] else None)
  if op in ['isr','send']:cpu.mem_write(0x2000efc0,b'\xcc'*64);cpu.mem_write(PACKET,b'\xcc'*16)
 assert bytes(cpu.mem_read(G-4,4))==bytes(cpu.mem_read(G+32,4))==b'\xcc'*4
 return dict(kernel={'lists':{hex(a):bytes(cpu.mem_read(a,20)).hex() for a in graph_lists},'tasks':{hex(t):bytes(cpu.mem_read(t,112)).hex() for t in tasks},'top':read(0x20074a38),'pending_yield':read(0x20074a44),'next_unblock':read(0x20074a50),'suspended':read(0x20074a58),'pended_ticks':read(0x20074a40),'tick_count':read(0x20074a34),'overflow_count':read(0x20074a48),'active':read(0x20074a24),'overflow':read(0x20074a28)},group=bytes(cpu.mem_read(G,32)).hex(),items=[bytes(cpu.mem_read(ITEMS+i*32,20)).hex() for i in range(len(c['waiters']))],state=bytes(cpu.mem_read(STATE+0x28,24)).hex(),depth=bytes(cpu.mem_read(DEPTH,1))[0],primask=cpu.reg_read(UC_ARM_REG_PRIMASK),higher=read(HIGH),asserted=asserted,suspended=suspended,queue_control=bytes(cpu.mem_read(QUEUE,80)).hex(),queue_data=bytes(cpu.mem_read(DATA,capacity*max(size,1))).replace(w(entries['callback']|1),b'CB!!').hex(),task_depth=read(0x2000309c),received_packet=bytes(cpu.mem_read(PACKET,16)).replace(w(entries['callback']|1),b'CB!!').hex(),basepri=cpu.reg_read(UC_ARM_REG_BASEPRI),log=log,io=io,group_writes=group_writes,returns=returns,counter=read(0x20074640),gpio=bytes(cpu.mem_read(0x40010560,12)).hex(),trace=trace)
def graph_expected(c,r):
 """Independent ordered-state model of pending drain and actual tick expiry."""
 TA,TB,TR,CURRENT,EXTRA,TP,TH=[0x20024000+i*256 for i in range(7)]
 DELAYED,OTHER,OVER,PENDING,READY=0x20026000,0x20026040,0x20026080,0x20073d24,0x2006a49c
 k=r['kernel'];lists={int(a,16):struct.unpack('<IIIII',bytes.fromhex(v)) for a,v in k['lists'].items()}
 tasks={int(a,16):bytes.fromhex(v) for a,v in k['tasks'].items()};nodes={}
 for i,(t,raw) in enumerate(tasks.items()):
  assert raw[:4]==b'\xa6'*4 and raw[48:]==b'\xa6'*64
  assert struct.unpack_from('<I',raw,44)[0]==c['task_priorities'][(t-TA)//256]
  for offset in [4,24]:nodes[t+offset]=struct.unpack_from('<IIIII',raw,offset)
 model={a:[] for a in lists};indexes={a:a+8 for a in lists};values={}
 def add(a,item,value):model[a].append(item);values[item]=value
 def priority(t):return c['task_priorities'][(t-TA)//256]
 add(READY+c['current_priority']*20,CURRENT+4,0)
 if c['ready_existing']:add(READY+c['priority']*20,TR+4,0)
 if c['high_ready']:add(READY+100,TH+4,0)
 locations={'active':DELAYED,'overflow':OVER,'other':OTHER};blocked=[TA,TB][:c['waiter_count']]
 initial=[(t,c['wake_times'][i],locations[c['state_locations'][i]]) for i,t in enumerate(blocked)]
 if c['remaining_delayed']:initial.append((EXTRA,c['wake_times'][2],locations[c['state_locations'][2]]))
 for t,value,a in sorted(initial,key=lambda x:x[1]):add(a,t+4,value)
 event=QUEUE+(16 if c['event_senders'] else 36)
 for i,t in sorted(enumerate(blocked),key=lambda item:8-priority(item[1])):
  if c['event_linked'][i]:add(event,t+24,8-priority(t))
 if c['index_removed'] and blocked:
  if c['event_linked'][0]:indexes[event]=TA+24
  indexes[locations[c['state_locations'][0]]]=TA+4
 if c['ready_existing'] and c['ready_index_node']:indexes[READY+c['priority']*20]=TR+4
 if c['pending_existing']:add(OTHER,TP+4,70);add(PENDING,TP+24,7)
 if c['pending_existing'] and c['pending_index_node']:indexes[PENDING]=TP+24
 def remove(a,item):
  pos=model[a].index(item)
  if indexes[a]==item:indexes[a]=model[a][pos-1] if pos else a+8
  model[a].remove(item)
 def insert(a,item):
  pos=model[a].index(indexes[a]) if indexes[a]!=a+8 else len(model[a]);model[a].insert(pos,item)
 def container(item):return next((a for a,seq in model.items() if item in seq),None)
 def transfer_state(t):
  remove(container(t+4),t+4);insert(READY+priority(t)*20,t+4);moved.append(t)
 def reset_next():return values[model[active][0]] if model[active] else 0xffffffff
 suspended=c['scheduler_suspended'];yield_pending=c['yield_pending'];next_unblock=c['next_unblock'];pended=c['pended_ticks'];clock=c['tick_count'];overflows=c['overflow_count'];active=DELAYED;overflow=OVER;moved=[];expected_returns=[];expected_yields=0;resume_outer=False;replay_initial=0;replayed=0
 for entry in r['log']:
  if entry[0]=='suspend_entry':assert entry[1]==suspended;suspended=(suspended+1)&0xffffffff
  elif entry[0]=='ready_remove_entry':
   assert entry[3]==suspended;t=model[event][0]-24;remove(event,t+24)
   if suspended:insert(PENDING,t+24)
   else:transfer_state(t);next_unblock=reset_next()
   if priority(t)>c['current_priority']:yield_pending=1
   expected_returns.append(int(priority(t)>c['current_priority']))
  elif entry[0]=='resume_entry':
   assert entry[1]==suspended
   if not suspended:assert r['asserted'];continue
   suspended-=1;resume_outer=not suspended and bool(c['task_count']);replay_initial=pended;replayed=0
   if resume_outer:
    drained=False
    while model[PENDING]:
     t=model[PENDING][0]-24;remove(PENDING,t+24);transfer_state(t);drained=True
     if priority(t)>=c['current_priority']:yield_pending=1
    if drained:next_unblock=reset_next()
  elif entry[0]=='tick_entry':
   assert entry[1:4]==[clock,suspended,pended]
   required=0
   if suspended:pended=(pended+1)&0xffffffff
   else:
    clock=(clock+1)&0xffffffff
    if clock==0:
     if model[active]:assert r['asserted'];continue
     active,overflow=overflow,active;overflows=(overflows+1)&0xffffffff;next_unblock=reset_next()
    if clock>=next_unblock:
     while model[active]:
      item=model[active][0];t=item-4
      if values[item]>clock:next_unblock=values[item];break
      transfer_state(t)
      event_container=container(t+24)
      if event_container is not None:remove(event_container,t+24)
      if priority(t)>c['current_priority']:required=1
     else:next_unblock=0xffffffff
    if len(model[READY+c['current_priority']*20])>1 or yield_pending:required=1
   if entry[4]:
    assert resume_outer;replayed+=1
    if required:yield_pending=1
   else:expected_returns.append(required)
  elif entry[0]=='yield_request_entry':
   assert resume_outer and yield_pending;expected_yields+=1
  elif entry[0]=='resume_finish':
   if resume_outer:assert replayed==replay_initial;pended=0
   assert entry[1:]==[suspended,pended,yield_pending]
   expected_returns.append(int(resume_outer and bool(yield_pending)))
 seen=set()
 for a,sequence in model.items():
  count,index,value,head,tail=lists[a];end=a+8
  assert (count,index,value,head,tail)==(len(sequence),indexes[a],0xffffffff,sequence[0] if sequence else end,sequence[-1] if sequence else end),(hex(a),sequence,lists[a])
  for i,item in enumerate(sequence):
   assert item not in seen;seen.add(item);val,next_node,prev,owner,where=nodes[item]
   assert (val,next_node,prev,owner,where)==(values[item],sequence[i+1] if i+1<len(sequence) else end,sequence[i-1] if i else end,item-(24 if item%256==24 else 4),a)
 for t in moved:assert nodes[t+24][4]==0 and nodes[t+4][4]==READY+priority(t)*20
 initial_top=max(c['current_priority'],c['priority'] if c['ready_existing'] else 0,5 if c['high_ready'] else 0)
 assert k['top']==max([initial_top]+[priority(t) for t in moved])
 assert (k['pending_yield'],k['next_unblock'],k['suspended'],k['pended_ticks'],k['tick_count'],k['overflow_count'],k['active'],k['overflow'])==(yield_pending,next_unblock,suspended,pended,clock,overflows,active,overflow)
 if all(op[0] in ['suspend','remove','resume','tick'] for op in c['program']) and not r['asserted']:
  assert [v for op,v in zip(c['program'],r['returns']) if op[0] in ['remove','resume','tick']]==expected_returns
 assert r['task_depth']==c['task_depth']
 assert r['basepri']==(0x30 if c['task_depth'] else 0) if any(x[0]=='resume_finish' for x in r['log']) else r['basepri']==c['basepri']
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';stock=[dict(address=BASE,data=blob[32:],memory_size=len(blob)-32,flags=5)];elf,segs,syms=parser.elf_info(a.elf)
 default=dict(tick_count=9,overflow_count=0,wake_times=[10,20,50],state_locations=['active','active','active'],event_linked=[True,True],task_priorities=[3,2,3,1,1,1,5],pended_ticks=0,tick_returns=[0],priority=3,current_priority=1,scheduler_suspended=0,ready_existing=False,high_ready=False,remaining_delayed=0,state_other=False,index_removed=False,ready_index_node=False,pending_existing=False,pending_index_node=False,waiter_count=1,event_senders=False,null_owner=False,yield_pending=0,next_unblock=999,task_depth=0,senders=0,scheduler_state=2,preloaded=[],command=-2,capacity=2,queued_count=0,item_size=16,write_slot=0,tx_lock=-1,receivers=0,receiver_result=0,task_count=4,initial_higher=0,position=0,null_queue=False,null_packet=False,basepri=0x30,waiters=[],initial=0,prior=0,resume_bits=0,resume_result=0,queue_result=1,higher=1,null_higher=False,context=0)
 cases=[]
 def case(**overrides):
  c=dict(default,**overrides);c['task_priorities']=[c['priority'],overrides.get('second_priority',max(0,c['priority']-1)),c['priority'],c['current_priority'],overrides.get('extra_priority',1),1,5];cases.append(c)
 for priority,current in [(0,1),(1,1),(3,1),(7,7)]:
  for count in [1,2]:
   for wakes in [[10,10,50],[10,11,50],[11,12,50]]:
    for links in [[False,False],[True,False],[True,True]]:
     for index in [False,True]:
      case(priority=priority,current_priority=current,second_priority=priority,waiter_count=count,wake_times=wakes,event_linked=links,index_removed=index,ready_existing=index,ready_index_node=index,remaining_delayed=1,next_unblock=wakes[0],program=[['tick',0,0]]*3)
 for suspended in [0,1,3]:
  for pending in [0,0xffffffff]:
   for ready,yielding in [(False,0),(True,0),(False,1)]:
    case(priority=1,current_priority=1,waiter_count=0,next_unblock=0xffffffff,scheduler_suspended=suspended,pended_ticks=pending,ready_existing=ready,yield_pending=yielding,program=[['tick',0,0]])
 for priority,current in [(0,1),(1,1),(3,1)]:
  for wakes in [[0,0,2],[0,1,2],[1,2,3]]:
   for links in [[False,False],[True,True]]:
    for index in [False,True]:
     case(priority=priority,current_priority=current,second_priority=priority,waiter_count=2,tick_count=0xffffffff,overflow_count=0xffffffff,wake_times=wakes,state_locations=['overflow','overflow','overflow'],remaining_delayed=1,event_linked=links,index_removed=index,ready_existing=True,ready_index_node=index,next_unblock=0xffffffff,program=[['tick',0,0]]*3)
 for nesting in [1,2,3]:
  for ticks in [0,1,3]:
   for pending in [False,True]:
    for priority,current in [(0,1),(1,1),(3,1)]:
     case(priority=priority,current_priority=current,second_priority=priority,waiter_count=2,scheduler_suspended=nesting,pended_ticks=ticks,pending_existing=pending,remaining_delayed=1,next_unblock=10,program=[['resume',0,0]]*nesting)
 for priority,current in [(0,1),(1,1),(3,1)]:
  for prior in [0,1]:
   case(priority=priority,current_priority=current,waiter_count=2,basepri=0,scheduler_suspended=1,pended_ticks=2,context=1,prior=prior,next_unblock=10,program=[['disable',0,0],['irq',0,0],['resume',0,0],['drain',0,0],['dispatch',0,0]])
 for priority,second,current in [(3,0,1),(0,3,1),(1,1,1),(7,1,3)]:
  for rollover in [False,True]:
   case(priority=priority,second_priority=second,current_priority=current,waiter_count=2,wake_times=[0,0,50] if rollover else [10,10,50],state_locations=['overflow','overflow','overflow'] if rollover else ['active','active','active'],tick_count=0xffffffff if rollover else 9,overflow_count=0xffffffff if rollover else 0,remaining_delayed=1,next_unblock=0xffffffff if rollover else 10,program=[['tick',0,0]])
 for priority,second in [(0,3),(1,1)]:
  case(priority=priority,second_priority=second,waiter_count=2,wake_times=[0xffffffff,0,2],state_locations=['active','overflow','overflow'],tick_count=0xfffffffe,overflow_count=7,remaining_delayed=1,next_unblock=0xffffffff,program=[['tick',0,0]]*3)
  case(priority=priority,second_priority=second,waiter_count=2,wake_times=[10,10,50],remaining_delayed=1,next_unblock=10,program=[['suspend',0,0],['tick',0,0],['tick',0,0],['resume',0,0]])
 case(tick_count=0xffffffff,next_unblock=10,program=[['tick',0,0]])
 results=[];observed={}
 for c in cases:
  x=run(stock,ORIGINAL,BOUNDARIES,0x4b4a98,dict(c,yield_entry=0x4420bc,critical_exit_entry=0x4420e8));y=run(segs,{k:syms[n]&~1 for k,n in NAMES.items()},{syms[n]&~1:v for n,v in SOURCE_BOUNDARIES.items()},syms['opencfw_radio_gpio_callback'],dict(c,yield_entry=syms['opencfw_resume_yield_request']&~1,critical_exit_entry=syms['opencfw_daemon_critical_exit']&~1));trace=x.pop('trace');y.pop('trace');assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});graph_expected(c,x);observed.update(trace);results.append(dict(inputs=c,result=x,original_trace=trace))
 comp=Path(__file__).resolve().parents[1];report=dict(status='PASS',case_count=len(cases),cases=results,original_trace={hex(k):v for k,v in sorted(observed.items())},unique_original_trace_bytes=sum(len(bytes.fromhex(v)) for v in observed.values()),elf_sha256=sha(elf),firmware_sha256=sha(blob),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},limits='Actual tick increment/defer, rollover list swap, timeout state/event unlink, priority ready insertion, equal-priority time slicing return and yield return execute with native resume/ready/queue/daemon/WSF/radio providers. Accessed task/list graph and globals are synthetic inputs. Actual tick ISR/startup/tick frequency, ready-task selection/context switch, full kernel/object lifecycle and hardware remain unproven. EventGroup unordered unblock, scheduler-state/context/wait/WSF-timer/app callbacks remain fixtures. Invalid rollover stops at assert-provider entry before fault tail.')
 report['execution_policy']='Unicorn 2.1.4 explicit Cortex-M4 model; executable translation caches invalidated on both stock/source before synthetic top-level calls only. No call-boundary restart, instruction/register substitution or physical ISR execution. Tick/resume/list new-target objects use the O0 simulator compiler profile; other linked prior objects retain their existing profile. Optimized diagnostic divergences retained and excluded.'
 report['compiler_profile']='Existing Cortex-M4 Thumb2 soft-float freestanding C11 flags with fwrapv; -O0 final override for tick/resume/list/new simulator-provider objects. Semantic test profile only, not intended firmware optimization or byte-match.'
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(cases),'RTOS-tick comparisons',report['unique_original_trace_bytes'],'unique original bytes')
if __name__=='__main__':main()
