#!/usr/bin/env python3
"""Actual guard/register instructions; lower scheduler startup synthetic."""
import argparse,importlib.util,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('lifecycle_v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(kernel_initialize=0x416058,kernel_state=0x416088,kernel_start=0x4160b0)
class Machine(v.Machine):
 def code(self,uc,pc,size,user):
  if pc==0x418148:self.events.append(['kernel-start',self.u(0x200270d4)]);self.ret(0xdeadbeef);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for name,mode,state,primask,basepri,ipsr in itertools.product(v.ENTRIES.keys() & {'kernel_initialize','kernel_state','kernel_start'},[1,2,0],[0,1,2],[0,1],[0,48],[0,3]):
  pair=[Machine(),Machine(True,segments,symbols)];results=[]
  for m in pair:
   m.w(0x20027150,0 if mode==1 else 1);m.w(0x2002716c,0 if mode==2 else 1);m.w(0x200270d4,state)
   for reg,value in [(v.a.UC_ARM_REG_PRIMASK,primask),(v.a.UC_ARM_REG_BASEPRI,basepri),(v.a.UC_ARM_REG_IPSR,ipsr)]:m.cpu.reg_write(reg,value)
   r=m.run(name,[]);results.append(dict(ret=r['return'],events=r['events'],state=m.u(0x200270d4),primask=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)))
  assert results[0]==results[1],(name,mode,state,primask,basepri,ipsr,results)
  trace.update(pair[0].trace);cases.append(dict(function=name,mode=mode,state=state,primask=primask,basepri=basepri,ipsr=ipsr,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Lower scheduler startup418148 synthetic; deliberately returns deadbeef to establish ignored return. IPSR/PRIMASK/BASEPRI are synthetic register initial states; no actual interrupt delivery.','Actual context guard41602a/runtime query418b56 execute. M4-compatible offline execution; no hardware or byte equality claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
