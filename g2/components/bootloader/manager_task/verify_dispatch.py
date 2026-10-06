#!/usr/bin/env python3
"""Deferred callback queue and64-slot countdown processor, synthetic RTOS boundary."""
import argparse,importlib.util,itertools,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(event_thread=0x42e644,event_enqueue=0x42e686,event_timer_callback=0x42e6f4)
CB=0x08009001;TABLE=0x20025ff0
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.put_status=0;self.lock_status=0;self.unlock_status=0;self.timer_status=0;self.get_index=0
 def cstr(self,address):
  data=bytearray()
  for i in range(512):
   byte=self.cpu.mem_read(address+i,1)[0]
   if not byte:return data.decode('ascii')
   data.append(byte)
  raise AssertionError('unterminated string')
 def code(self,uc,pc,size,user):
  r0,r1,r2,r3=self.args()
  if pc==0x4168a2:self.events.append(['queue-put',r0,bytes(uc.mem_read(r1,8)).hex(),r2,r3,self.put_status]);self.ret(self.put_status);return
  if pc==0x416920:
   assert [r0,r2,r3]==[0x62,0,0xffffffff];self.events.append(['queue-get',r0,r2,r3])
   if self.get_index==3:self.finished=True;uc.emu_stop();return
   status=[0,0xfffffffc,0][self.get_index]
   if status==0:uc.mem_write(r1,struct.pack('<II',[0x51,0,0xffffffff][self.get_index],CB+(4 if self.get_index==2 else 0)))
   self.get_index+=1;self.ret(status);return
  if pc in [CB&~1,(CB+4)&~1]:self.events.append(['callback',hex(pc),r0]);self.ret(0xdeadbeef);return
  if pc==0x4166aa:self.events.append(['mutex-acquire',r0,r1,self.lock_status]);self.ret(self.lock_status);return
  if pc==0x416710:self.events.append(['mutex-release',r0,self.unlock_status]);self.ret(self.unlock_status);return
  if pc==0x41649a:self.events.append(['timer-start',r0,r1,self.timer_status]);self.ret(self.timer_status);return
  if pc==0x4160e8:self.events.append(['tick',0x12345678]);self.ret(0x12345678);return
  if pc==0x4176ce:
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);line=self.u(sp);e=['log',r0,self.cstr(r1),self.cstr(r2),self.cstr(r3),line,self.cstr(self.u(sp+4))]
   if line in [0x8c,0xa0]:e.append(self.u(sp+8))
   if line==0xe1:e.extend([self.u(sp+8),self.u(sp+12)])
   self.events.append(e);self.ret();return
  super().code(uc,pc,size,user)
def seed(m):
 m.w(0x200270ec,0x62);m.w(0x200270f0,0x63);m.w(0x200270f4,0x65);m.w(0x200270f8,0x66);m.w(0x20027100,32);m.w(0x200270fc,0xcafef00d);m.w(0x200004c4,0);m.cpu.mem_write(TABLE,b'\0'*768)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 def check(entry,args,fixture):
  pair=[Machine(),Machine(True,segments,symbols)];results=[]
  for m in pair:
   seed(m)
   for key,value in fixture.items():
    if key=='thread':m.w(0x200270f0,value)
    elif key=='queue':m.w(0x200270ec,value)
    elif key=='table':
     for index,remaining in enumerate(value):
      m.w(TABLE+4*index,CB+4*index);m.w(TABLE+256+4*index,0xabcdef00+index);m.w(TABLE+512+4*index,remaining)
    else:setattr(m,key,value)
   m.run(entry,args)
   results.append(dict(events=m.events,table=bytes(m.cpu.mem_read(TABLE,768)).hex(),period=m.u(0x20027100),timestamp=m.u(0x200270fc),nesting=m.u(0x200004c4),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)))
  assert results[0]==results[1],(entry,args,fixture,results)
  if entry=='event_thread':assert [e for e in results[0]['events'] if e[0]=='callback']==[['callback',hex(CB&~1),0x51],['callback',hex((CB+4)&~1),0xffffffff]]
  if entry=='event_timer_callback' and fixture.get('table')==[]:assert ['timer-start',0x66,0xffffffff,fixture.get('timer_status',0)] in results[0]['events']
  trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=fixture,result=results[0]))
 check('event_thread',[0],{})
 for thread,queue,status,timeout,callback,arg in itertools.product([0,0x63],[0,0x62],[0,7,0xffffffff],[0,1,20000],[0,CB],[0,0xffffffff]):check('event_enqueue',[callback,arg,timeout],dict(thread=thread,queue=queue,put_status=status))
 profiles=[[]]+[[n] for n in [0,1,31,32,33,0x7fffffff,0xffffffff]]+[[16,40],list(range(1,65))]
 for arg,table,mode in itertools.product([0,0xff000000,0xff000001,0xff000020,0xfe000020],profiles,range(6)):
  f=dict(table=table)
  if mode==1:f['put_status']=7
  elif mode==2:f['lock_status']=0xfffffffd
  elif mode==3:f['unlock_status']=0xfffffffd
  elif mode==4:f['timer_status']=0xfffffffa
  elif mode==5:f['thread']=0
  check('event_timer_callback',[arg],f)
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in list(HERE.iterdir())+[ROOT/'g2/components/bootloader/thread_creation/kernel_runtime.c',ROOT/'g2/components/bootloader/queue/runtime_mode.c'] if p.is_file()},original_trace=trace,comparisons=cases,limits=['Actual original/source42e644/42e686/42e6f4 queue-envelope/consumer/countdown/critical logic executes. Queue get/put, callback invocation, mutex acquire/release, timer start, tick accessor and logger are synthetic. Consumer bounded on fourth get; no hardware scheduler or asynchronous task/callback delivery.','64-slot table is fixture SRAM with64 callback words,+100 argument words,+200 countdown words. Source/original full768bytes and period/timestamp/critical states compared. Raw countdown subtraction uses nominalstored period orFF-prefix override, not measured wall time.','Expired callbacks are cleared before enqueue; selected queue failures/absent thread drop work without retry. Failed mutex acquisition logs then continues table mutation/release; no actual race/lifetime hazard on hardware is asserted.','Empty table leads to timer-startffffffff because exact stock guard excludes7fffffff/zero. Caller-saved residual registers/void return not compared. M4 compatibility; no byte identity/source-complete image claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
