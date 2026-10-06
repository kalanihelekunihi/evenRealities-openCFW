#!/usr/bin/env python3
"""Manager setup/priority choreography and bit-test handshake; scheduling synthetic."""
import argparse,importlib.util,json
from pathlib import Path
from unicorn import UcError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('priority',ROOT/'g2/components/bootloader/thread_creation/verify_priority.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);v=p.v
v.ENTRIES.update(manager_event_init=0x42e254,manager_setup=0x42e278,manager_callback_dispatch=0x42e284,manager_signal_wait=0x42e2a2,manager_signal_dfu=0x42e2ea)
class Machine(p.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.event_handle=0x65;self.wait_result=2
 def cstr(self,address):
  data=bytearray()
  for i in range(512):
   byte=self.cpu.mem_read(address+i,1)[0]
   if not byte:return data.decode('ascii')
   data.append(byte)
  raise AssertionError('unterminated string')
 def code(self,uc,pc,size,user):
  r0,r1,r2,r3=self.args()
  if pc==0x4164da:self.events.append(['event-new',r0]);self.ret(self.event_handle);return
  if pc==0x42e53c:self.events.append(['event-runtime-setup']);self.ret();return
  if pc==0x42ddae:
   cb=self.u(0x20027134);self.events.append(['dfu-thread-init-boundary',self.u(cb+0x2c),self.u(cb+0x60)]);self.ret();return
  if pc==0x41623a:self.events.append(['thread-flags-set',r0,r1]);self.ret(0xdeadbeef);return
  if pc==0x416590:self.events.append(['event-wait',r0,r1,r2,r3,self.wait_result]);self.ret(self.wait_result);return
  if pc==0x4176ce:
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);self.events.append(['log',r0,self.cstr(r1),self.cstr(r2),self.cstr(r3),self.u(sp),self.cstr(self.u(sp+4)),self.u(sp+8),self.u(sp+12)]);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 fixtures=[('manager_event_init',[],dict(event_handle=h)) for h in [0,0x65]]+[(name,[],{}) for name in ['manager_setup','manager_callback_dispatch']]+[('manager_signal_wait',[0x51,bit],dict(wait_result=ret)) for bit in [0,1,31,32,255,256] for ret in [0,2,0xffffffff,0x80000000]]+[('manager_signal_dfu',[],dict(wait_result=ret)) for ret in [0,2,0xffffffff,0x80000000]]
 for entry,args,fixture in fixtures:
  pair=[Machine(),Machine(True,segments,symbols)];results=[]
  for m in pair:
   cb=p.initialize(m,True,False,True,False,False,0);m.w(cb+0x2c,48);m.w(cb+0x60,48);m.w(cb+0x18,8)
   # Rebuild container to match48, not merely change the priority words.
   old=0x20024870+24*20;new=0x20024870+48*20;node=cb+4;end=new+8
   m.w(old,0);m.w(old+12,old+8);m.w(old+16,old+8)
   m.w(new,1);m.w(new+12,node);m.w(new+16,node);m.w(node+4,end);m.w(node+8,end);m.w(node+16,new)
   m.w(0x2002714c,48);m.w(0x20027150,1);m.w(0x200004cc,0x42ddaf);m.w(0x20000510,0x65);m.w(0x200004d4,0x63)
   for key,value in fixture.items():setattr(m,key,value)
   try:m.run(entry,args);assert not(entry=='manager_event_init' and m.event_handle==0)
   except UcError:assert entry=='manager_event_init' and m.event_handle==0 and m.invalid and m.invalid['address']==0xffffffff
   results.append(dict(events=m.events,fault=m.invalid,tcb=bytes(m.cpu.mem_read(cb,112)).hex(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),event_handle=m.u(0x20000510),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),icsr=m.u(0xe000ed04)))
  assert results[0]==results[1],(entry,args,fixture,results)
  if entry in ['manager_setup','manager_callback_dispatch']:
   assert ['dfu-thread-init-boundary',8,8] in results[0]['events']
   assert pair[0].u(cb+0x2c)==pair[1].u(cb+0x2c)==48 and results[0]['icsr']==0x10000000
  trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=fixture,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in list(HERE.iterdir())+[ROOT/'g2/components/bootloader/thread_creation'/name for name in ['thread_priority.c','kernel_runtime.c','verify_priority.py']] + [ROOT/'g2/components/bootloader/queue/runtime_mode.c'] if p.is_file()},original_trace=trace,comparisons=cases,limits=['Actual manager setup/callback dispatch/signal-and-wait, current getter/priority wrapper/kernel setter/critical/ready-list/PendSV-store paths execute. Event creation, event runtime init42e53c, DFU thread init42ddae, flags set/wait and logging are provider cuts.','Callback slot200004cc fixture42ddaf matches decoded authenticated625-byte initializer, not invented live value. Context event/managerhandle inputs remain synthetic. Fatal event allocation observes invalid store, not hardware exception.','PRIMASK/BASEPRI and PendSV register stores do not deliver actual scheduling in this model. Priority8 callback then48 ordering proven, not that another task initializes its queue in between. Raw timeout20000 is in ticks; result is a bit-test, so high-bit returns containing requestedbit also satisfy it.','ARM shift low-byte/shift>=32 semantics tested including bit256 aliases0. Original logging records low-byte task number. No hardware/source completeness/byte identity claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
