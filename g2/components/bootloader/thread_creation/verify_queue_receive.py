#!/usr/bin/env python3
"""Compare kernel receive/block, timeout arithmetic and queue allocation bytes."""
import argparse,importlib.util,itertools,json
from pathlib import Path
from unicorn import UcError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('timer',HERE/'verify_timer_wait.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);v=t.v
v.ENTRIES.update(kernel_queue_get_blocking=0x41a114,kernel_queue_create_dynamic=0x419d08,timeout_capture=0x418912,timeout_check=0x418922,wait_list_sorted=0x41863e,queue_empty=0x41a5c4,queue_copy_out=0x41a52c)
QUEUE=t.QUEUE;BUF=0x20030300;STORAGE=0x20032000;ALLOC=0x20031000;TIMEOUT=0x20030200
class Machine(t.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.alloc_success=True;self.stop_yield=False
  self.yield_entry=(self.symbols['opencfw_bl_kernel_reschedule']&~1) if self.source else 0x41b3d0
 def code(self,uc,pc,size,user):
  if pc==0x419730:self.events.append(['allocate',self.args()[0]]);self.ret(ALLOC if self.alloc_success else 0);return
  if pc==0x41568c:
   dst,src,n,_=self.args();uc.mem_write(dst,bytes(uc.mem_read(src,n)));self.ret(dst);return
  if pc==self.yield_entry and self.stop_yield:self.events.append(['yield-boundary']);self.finished=True;uc.emu_stop();return
  super().code(uc,pc,size,user)
def snapshot(m):
 return dict(events=m.events,regions={hex(a):bytes(m.cpu.mem_read(a,n)).hex() for a,n in [(QUEUE,80),(ALLOC,80),(BUF,16),(TIMEOUT,12),(0x20030000,112),(0x20024870,1120),(0x20026f34,100),(0x20027130,100)]},basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),nesting=m.u(0x200004c4))
def init(m,now=0):
 t.init(m,now);m.w(0x20027150,1);m.w(QUEUE,STORAGE);m.w(QUEUE+4,STORAGE);m.w(QUEUE+8,STORAGE+24);m.w(QUEUE+12,STORAGE+16);m.w(QUEUE+60,3);m.w(QUEUE+64,8)
 m.cpu.mem_write(STORAGE,bytes(range(24)));m.cpu.mem_write(BUF,b'\xcc'*16);m.cpu.mem_write(ALLOC,b'\xcc'*80)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);trace={};cases=[];fixtures=[]
 for count,timeout,readpos,waiters in itertools.product([0,1,3],[0,13,0xffffffff],[STORAGE,STORAGE+16],[0,1]):fixtures.append(('kernel_queue_get_blocking',[QUEUE,BUF,timeout],dict(count=count,readpos=readpos,waiters=waiters,stop_yield=count==0 and timeout!=0)))
 for now,start,over,oldover,left in itertools.product([0,17,0xffffffff],[0,16,0xfffffff0],[0,1],[0,1],[0,1,32,0xffffffff]):fixtures.append(('timeout_check',[TIMEOUT,TIMEOUT+8],dict(now=now,start=start,over=over,oldover=oldover,left=left)))
 for count,size,typ,success in itertools.product([1,3,50],[0,8,40],[0,257],[False,True]):fixtures.append(('kernel_queue_create_dynamic',[count,size,typ],dict(alloc_success=success)))
 for count,size in [(0,8),(0x80000000,8),(1,0xffffffb0)]:fixtures.append(('kernel_queue_create_dynamic',[count,size,0],dict(fatal=True)))
 for entry,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];results=[];returns=[]
  for m in pair:
   init(m,f.get('now',0));m.alloc_success=f.get('alloc_success',True);m.stop_yield=f.get('stop_yield',False)
   if 'count' in f:m.w(QUEUE+56,f['count']);m.w(QUEUE+12,f['readpos']);m.w(QUEUE+16,f['waiters'])
   if entry=='timeout_check':m.w(TIMEOUT,f['oldover']);m.w(TIMEOUT+4,f['start']);m.w(TIMEOUT+8,f['left']);m.w(0x2002715c,f['over'])
   try:ret=m.run(entry,args)['return'];assert not f.get('fatal');returns.append(None if m.stop_yield else ret)
   except UcError:assert f.get('fatal') and m.invalid['address']==0xffffffff;returns.append('invalid-store')
   results.append(snapshot(m))
  assert results[0]==results[1] and returns[0]==returns[1],(entry,args,f,returns,results)
  trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=f,return_value=returns[0],result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(HERE.joinpath(n).relative_to(ROOT)):v.sha(HERE/n) for n in ['queue_receive.c','queue_receive.h','timer_wait.c','queue_receive_module.ld','verify_queue_receive.py','timer_wait.h','kernel_runtime.c','scheduler_resume.c']},original_trace=trace,comparisons=cases,limits=['Actual receive/critical/suspend/resume, sorted wait and finite/indefinite TCB/list moves execute. Blocking fixtures stop at PendSV-request entry; no task delivery or post-wake receive retry in this direct profile.','Original memcpy41568c uses synthetic copy; compiled source byte loop executes. Event-remove provider clears synthetic waiter count. Allocation uses controlled return rather than real heap here. Queue allocation arithmetic/fatal overflow/80-byte control state tested.','Timeout tick/overflow state is explicit synthetic input; no live clock. No hardware or byte-identical payload claim.'])
 report['source_sha256']['g2/components/bootloader/queue/runtime_mode.c']=v.sha(ROOT/'g2/components/bootloader/queue/runtime_mode.c')
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
