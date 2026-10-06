#!/usr/bin/env python3
"""Execute power guards with static synthetic register state, no hardware timing."""
import argparse
import importlib.util
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
s=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.ENTRIES.update(control_guard_begin=0x41bd92,control_guard_end=0x41bde4)
class Machine(v.Machine):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.cpu.mem_map(0x40021000,4096);self.power_result=0
 def code(self,uc,pc,size,user):
  if pc==0x41cd1a:
   request,on,config,_arg=self.args();self.events.append(['power_control',request,on,self.u(config)]);self.ret(self.power_result);return
  super().code(uc,pc,size,user)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segments,symbols=v.elf.elf_info(a.elf);cases=[];trace={}
 for name in ['control_guard_begin','control_guard_end']:
  for enabled,status,request,power_result in [(0,0,0,0),(2,0x80,0xffffffff,7),(255,0x80,0x20,7),(1,0,0,0),(1,0x80,0xffffffff,0),(1,0x155,0x5a5a,7),(1,0x1d5,0x5a5a,7)]:
   pair=[Machine(),Machine(True,segments,symbols)];outputs=[]
   for m in pair:
    m.cpu.mem_write(0x200271a7,bytes([enabled]));m.w(0x40021018,status);m.w(0x40021014,request);m.power_result=power_result
    d=m.run(name,[]);outputs.append({'return':d['return'],'events':d['events'],'status':m.u(0x40021018),'request':m.u(0x40021014)})
   assert outputs[0]==outputs[1],(name,enabled,status,request,outputs)
   timeout=enabled==1 and ((status&0x80)==0 if name.endswith('begin') else (status&0x80)!=0)
   assert outputs[0]['return']==(4 if timeout else 0)
   assert outputs[0]['request']==(request if enabled!=1 else request|0x20 if name.endswith('begin') else request&~0x20)
   expected_calls=enabled==1 and (name.endswith('begin') or not timeout)
   assert len(outputs[0]['events'])==int(expected_calls)
   trace.update(pair[0].trace);cases.append(dict(function=name,enabled=enabled,status=status,request=request,power_result=power_result,observed=outputs[0]))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 d=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_trace=trace,original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.suffix in ['.c','.h','.S','.ld','.py'] or p.name=='Makefile'},comparisons=cases,
        limits=['Real stock/source guard conditions, register RMW, loops and status results execute; power-control helper at41CD1A is synthetic.',
                'Registers remain static fixture input, testing immediate-ready and poll-exhausted paths; no elapsed-time, hardware transition or interrupt scheduling proof.',
                'Poll bound10000 is iterations, not microseconds or milliseconds. Return from power-control helper is ignored by both guards.',
                'No physical MRAM/power operation or firmware writes.'])
 a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:d[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
