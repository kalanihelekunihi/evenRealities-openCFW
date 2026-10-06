#!/usr/bin/env python3
"""Differential event-loop object initialization with exact raw static attributes."""
import argparse,importlib.util,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.ENTRIES['event_runtime_init']=0x42e53c
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.fail=False
 def cstr(self,address):
  data=bytearray()
  for i in range(512):
   byte=self.cpu.mem_read(address+i,1)[0]
   if not byte:return data.decode('ascii')
   data.append(byte)
  raise AssertionError('unterminated string')
 def attrs(self,address,count):
  words=list(struct.unpack('<'+str(count)+'I',self.cpu.mem_read(address,count*4)));return [words,self.cstr(words[0])]
 def code(self,uc,pc,size,user):
  r0,r1,r2,r3=self.args()
  if pc==0x416816:self.events.append(['queue-new',r0,r1,*self.attrs(r2,6)]);self.ret(0 if self.fail else 0x71);return
  if pc==0x4163b2:self.events.append(['timer-new',r0,r1,r2,*self.attrs(r3,4)]);self.ret(0 if self.fail else 0x72);return
  if pc==0x416610:self.events.append(['mutex-new',*self.attrs(r0,4)]);self.ret(0 if self.fail else 0x73);return
  if pc==0x416200:self.events.append(['thread-terminate',r0]);self.ret(0xfffffffa);return
  if pc==0x4160fe:self.events.append(['thread-new',r0,r1,*self.attrs(r2,9)]);self.ret(0 if self.fail else 0x74);return
  if pc==0x4176ce:
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);self.events.append(['log',r0,self.cstr(r1),self.cstr(r2),self.cstr(r3),self.u(sp),self.cstr(self.u(sp+4))]);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 slots=[0x200270ec,0x200270f8,0x200270f4,0x200270f0]
 for presence in range(16):
  for fail in [False,True]:
   pair=[Machine(),Machine(True,segments,symbols)];results=[]
   for m in pair:
    m.fail=fail
    for i,addr in enumerate(slots):m.w(addr,0x81+i if presence&(1<<i) else 0)
    m.run('event_runtime_init',[]);results.append(dict(events=m.events,globals=bytes(m.cpu.mem_read(0x200270ec,16)).hex()))
   assert results[0]==results[1],(presence,fail,results)
   assert pair[0].u(slots[3])==pair[1].u(slots[3])==(0 if fail else 0x74)
   for i in range(3):assert pair[0].u(slots[i])==pair[1].u(slots[i])==(0x81+i if presence&(1<<i) else (0 if fail else 0x71+i))
   if presence&8:assert ['thread-terminate',0x84] in results[0]['events']
   trace.update(pair[0].trace);cases.append(dict(presence=presence,all_new_fail=fail,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Actual42e53c conditional allocation/logging/global writes/terminate-and-replace flow executes. Queue/timer/mutex/thread creation, thread termination and logging are synthetic providers; selected termination error ignored as stock does.','Source static attribute arrays and three source-built name strings match raw data; callback addresses42e6f5/42e645 remain unimplemented asynchronous code dependencies, not called by this slice. Existing resource handles are synthetic.','All16 prior-presence combinations and all-new-success/all-new-failure outcomes; mixed per-object failures are not separately enumerated. Failures log and continue; no proof of valid usable resources, timer callback delivery, actual thread cleanup or runtime scheduling.','M4 compatibility candidate; no physical hardware, byte identity or source-complete image claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
