#!/usr/bin/env python3
"""Original/source priority setter with ready/delayed, inherited and fatal states."""
import argparse,importlib.util,itertools,json
from pathlib import Path
from unicorn import UcError,UC_HOOK_MEM_INVALID
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(thread_priority_set=0x4161ce,thread_current=0x4161c6)
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.invalid=None;self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.bad)
 def bad(self,uc,access,address,size,value,user):self.invalid=dict(access=access,address=address,size=size,value=value);return False

def initialize(m,target_current,inherited,ready,cursor,high,nesting):
 target=0x20030000;other=0x20030080;effective=48 if inherited else 24
 for addr in [target,other]:m.cpu.mem_write(addr,b'\0'*112)
 m.w(target+0x2c,effective);m.w(target+0x60,24);m.w(target+0x18,0x80001234 if high else 32);m.w(target+0x10,target)
 m.w(other+0x2c,24);m.w(other+0x60,24);m.w(other+0x10,other)
 for addr in [0x20024870+20*p for p in range(56)]+[0x20026f34]:
  end=addr+8
  for off,value in [(0,0),(4,end),(8,0xffffffff),(12,end),(16,end)]:m.w(addr+off,value)
 def insert(cb,addr):
  end=addr+8;last=m.u(addr+16);node=cb+4
  for off,value in [(4,end),(8,last),(16,addr)]:m.w(node+off,value)
  m.w(last+4,node);m.w(end+8,node);m.w(addr,m.u(addr)+1)
 insert(target,0x20024870+20*effective if ready else 0x20026f34)
 if not target_current:insert(other,0x20024870+20*24)
 if cursor:m.w(m.u(target+0x14)+4,target+4)
 m.w(0x20027134,target if target_current else other);m.w(0x20027150,0);m.w(0x2002716c,0);m.w(0x200004c4,nesting);m.w(0x2002714c,max(24,effective) if ready else 24);m.w(0xe000ed04,0)
 return target

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for current,inherited,ready,cursor,high,nesting,priority in itertools.product([False,True],[False,True],[False,True],[False,True],[False,True],[0,0xaaaaaaaa],[8,24,48,55,56]):
  if current and not ready:continue
  pair=[Machine(),Machine(True,segments,symbols)];results=[]
  for m in pair:
   handle=initialize(m,current,inherited,ready,cursor,high,nesting)
   try:
    result=m.run('thread_priority_set',[handle,priority])
    assert priority!=56 and result['return']==0
   except UcError:assert priority==56 and m.invalid and m.invalid['address']==0xffffffff
   results.append(dict(fault=m.invalid,tcbs=bytes(m.cpu.mem_read(0x20030000,224)).hex(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),delayed=bytes(m.cpu.mem_read(0x20026f34,20)).hex(),highest=m.u(0x2002714c),nesting=m.u(0x200004c4),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),icsr=m.u(0xe000ed04)))
  assert results[0]==results[1],(current,inherited,ready,cursor,high,nesting,priority,results)
  trace.update(pair[0].trace);cases.append(dict(current=current,inherited=inherited,ready=ready,cursor_on_item=cursor,event_high_bit=high,nesting=nesting,priority=priority,result=results[0]))
 for handle,priority,ipsr in [(0,8,0),(0x20030000,0,0),(0x20030000,57,0),(0x20030000,8,3)]:
  pair=[Machine(),Machine(True,segments,symbols)];results=[]
  for m in pair:
   initialize(m,True,False,True,False,False,0);m.cpu.reg_write(v.a.UC_ARM_REG_IPSR,ipsr);results.append(m.run('thread_priority_set',[handle,priority])['return'])
  assert results[0]==results[1]==(0xfffffffa if ipsr else 0xfffffffc)
  trace.update(pair[0].trace);cases.append(dict(rejected_handle=handle,priority=priority,ipsr=ipsr,return_value=results[0]))
 for current in [0,0x20030000,0xffffffff]:
  pair=[Machine(),Machine(True,segments,symbols)]
  for m in pair:m.w(0x20027134,current)
  assert [m.run('thread_current',[])['return'] for m in pair]==[current,current]
  trace.update(pair[0].trace);cases.append(dict(current_accessor=current))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Synthetic coherent lists and TCBs: current tasks ready; noncurrent target ready/delayed, inherited effective priority distinct from base, list cursor item/sentinel, protected high event bit, priority up/down/equal and critical sentinel. No actual task switch, event delivery or priority inheritance acquisition/release.','Original/source guard, critical helpers, list unlink and reschedule register store execute without provider cuts. Priority56 wrapper admission reaches invalid store; HardFault delivery not modeled.','Public priority-set result modeled; incidental lower void return not compared. M4 compatible source; no firmware byte identity/hardware boot claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
