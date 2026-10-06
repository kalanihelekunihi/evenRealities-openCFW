#!/usr/bin/env python3
"""Stop at first SVC, compare port state; no exception/task execution claim."""
import argparse,importlib.util,json,struct,hashlib
from pathlib import Path
from unicorn import UC_HOOK_INTR
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('port_runtime',HERE/'verify_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v
v.ENTRIES['scheduler_bootstrap']=0x418148
class Machine(r.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.interrupt=None;self.cpu.hook_add(UC_HOOK_INTR,self.svc)
 def svc(self,uc,number,user):self.interrupt=number;self.finished=True;uc.emu_stop()
 def code(self,uc,pc,size,user):
  if pc==0x41b6fa:self.events.append(['timer-configure']);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);blob=v.BLOB.read_bytes();pair=[Machine(),Machine(True,segments,symbols)];results=[]
 for m in pair:
  if m.source:m.cpu.mem_write(0x410000,blob[:4]) # vector SP remains locked data fixture
  m.w(0xe000ed08,0x410000);m.w(0xe000ed20,0x12345678);m.w(0x200004c4,0xaaaaaaaa);m.w(0x20027134,0);m.w(0x20027144,0);m.w(0x20027150,0);m.w(0x20027160,0);m.w(0x2002714c,0);m.w(0x20027180,0)
  m.run('scheduler_bootstrap',[])
  assert m.interrupt is not None
  results.append(dict(interrupt=m.interrupt,events=m.events,msp=m.cpu.reg_read(v.a.UC_ARM_REG_MSP),primask=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),faultmask=m.cpu.reg_read(v.a.UC_ARM_REG_FAULTMASK),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),priority=m.u(0xe000ed20),nesting=m.u(0x200004c4),state=bytes(m.cpu.mem_read(0x20027130,0x58)).hex(),ready=bytes(m.cpu.mem_read(0x20024870,1120)).hex(),idle_cb=bytes(m.cpu.mem_read(0x20026970,112)).hex(),timer_cb=bytes(m.cpu.mem_read(0x200269e0,112)).hex(),queue=bytes(m.cpu.mem_read(0x20026da0,80)).hex()))
 assert results[0]==results[1],results
 assert results[0]['nesting']==0 and results[0]['msp']==struct.unpack('<I',blob[:4])[0]
 trace=pair[0].trace;used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=1,distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=results,limits=['Execution stops at Unicorn SVC interrupt hook before handler/exception entry or task restoration. Physical timing/MMIO and timer-configure41b6fa synthetic.','Initial vector SP is a4-byte authenticated fixture, not yet source vector. Actual static idle/timer creation, queues/critical state/port priorities/MSP/interrupt enabling/SVC execute.','M4-compatible offline behavior, not M55 hardware or byte identity. Unexpected SVC return continuation untested.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
