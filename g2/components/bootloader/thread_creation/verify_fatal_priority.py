#!/usr/bin/env python3
"""Accepted wrapper priority56 reaches original/static fatal-store path."""
import argparse,importlib.util,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_MEM_INVALID
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('fatal_runtime',HERE/'verify_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v
class Machine(r.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.invalid=None;self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.bad)
 def bad(self,uc,access,address,size,value,user):
  self.invalid=dict(access=access,address=address,size=size,value=value);return False
 def code(self,uc,pc,size,user):
  if pc==0x41b2f8:v.Machine.code(self,uc,pc,size,user);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);pair=[Machine(),Machine(True,segments,symbols)];results=[]
 for m in pair:
  m.w(0x20027150,0);m.w(0x2002716c,0);m.cpu.mem_write(r.t.ATTR,struct.pack('<9I',r.s.NAME,0,r.s.CB,112,r.s.STACK,1024,56,1,0));m.cpu.mem_write(r.s.NAME,b'manager\0');m.cpu.mem_write(r.s.CB,b'\xcc'*112);m.cpu.mem_write(r.s.STACK,b'\xcc'*1024)
  try:m.run('thread_new',[0x42e2f9,0x1234,r.t.ATTR]);raise AssertionError('expected invalid write')
  except UcError:pass
  assert m.invalid and m.invalid['address']==0xffffffff and m.invalid['value']==0
  results.append(dict(fault=m.invalid,tcb=bytes(m.cpu.mem_read(r.s.CB,112)).hex(),stack=bytes(m.cpu.mem_read(r.s.STACK,1024)).hex(),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)))
 assert results[0]==results[1],results
 trace=pair[0].trace;used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=1,distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=results,limits=['Invalid store observed; actual HardFault/exception entry or recovery not modeled. Original fill helper intercepted.','Priority56 accepted by outer wrapper, stack/name initialized, then initializer fatal before priority/frame/registration writes. M4 compatibility profile.'])
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
