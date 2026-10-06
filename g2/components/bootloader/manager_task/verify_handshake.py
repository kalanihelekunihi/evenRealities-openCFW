#!/usr/bin/env python3
"""Compare system-start handshake wrappers with controlled flag provider returns."""
import argparse,importlib.util,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('boot',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(manager_start_wait=0x42e3e0,manager_start_done=0x42e412,manager_start_signal=0x42e444,dfu_control_one=0x42dd9a,dfu_control_two=0x42dda4)
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.waits=[0x800000];self.wait_index=0
 def cstr(self,address):
  out=bytearray()
  for i in range(512):
   val=self.cpu.mem_read(address+i,1)[0]
   if not val:return out.decode()
   out.append(val)
  raise AssertionError('unterminated string')
 def code(self,uc,pc,size,user):
  r0,r1,r2,r3=self.args()
  if pc==0x4162c4:
   val=self.waits[self.wait_index];self.wait_index+=1;self.events.append(['wait',r0,r1,r2,val]);self.ret(val);return
  if pc==0x41652e:self.events.append(['event-set',r0,r1]);self.ret(17);return
  if pc==0x4176ce:
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);self.events.append(['log',r0,self.cstr(r1),self.cstr(r2),self.cstr(r3),self.u(sp),self.cstr(self.u(sp+4)),self.u(sp+8)]);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);trace={};cases=[]
 for entry,task in itertools.product(['manager_start_wait','manager_start_done','manager_start_signal','dfu_control_one','dfu_control_two'],[0,1,31,32,255,256]):
  waits=[0,0x800000] if 'wait' in entry or entry=='dfu_control_one' else [0x800000]
  for wake in ([0x800000,0xfffffffe] if len(waits)>1 else [0x800000]):
   pair=[Machine(),Machine(True,segs,syms)];events=[]
   for m in pair:
    m.w(0x20000510,0x20033000);m.waits=waits[:-1]+[wake];m.run(entry,[task]);events.append(m.events)
   assert events[0]==events[1],(entry,task,wake,events)
   trace.update(pair[0].trace);cases.append(dict(entry=entry,task=task,wake=wake,events=events[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(HERE.joinpath(n).relative_to(ROOT)):v.sha(HERE/n) for n in ['manager_handshake.c','handshake_module.ld','verify_handshake.py']},original_trace=trace,comparisons=cases,limits=['Thread-wait and event-set returns are explicit synthetic providers. Exact bit23 test, timeoutFFFFFFFF/options1, repeat on zero, high-bit error containingbit23 accepted, low-byte logger argument and ARM low-byte shifts compared.','Void incidental register return is not compared. No real flags/scheduling or hardware startup is established by this standalone wrapper profile.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
