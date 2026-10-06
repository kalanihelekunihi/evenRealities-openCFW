#!/usr/bin/env python3
import argparse,importlib.util,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
s=importlib.util.spec_from_file_location('v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);v.ENTRIES['release_all']=0x4223d8
class Machine(v.Machine):
 def __init__(self,*a,status=0,**kw):
  super().__init__(*a,**kw);self.status=status
  if self.source:self.symbols['opencfw_boot_release_all']=self.symbols['opencfw_bl_clock_release_all']
 def code(self,uc,pc,size,user):
  if pc==0x422364:self.events.append(['release',*self.args()[:2]]);self.ret(self.status);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={}
 for user,mask,status in itertools.product([0,16,31,32,56,57,255,256,272,0xffffffff],range(128),[0,7]):
  pair=[Machine(status=status),Machine(True,segs,dict(syms),status=status)]
  for m in pair:
   for id in range(7):m.w(0x20026e74+id*8,(1<<(user&31)) if mask>>id&1 else 0);m.w(0x20026e78+id*8,(1<<(user&31)) if mask>>id&1 else 0)
  result=[m.run('release_all',[user]) for m in pair];got=[{k:r[k] for k in ['return','events']} for r in result];assert got[0]==got[1],(user,mask,status,got);trace.update(pair[0].trace);cases.append(dict(user=user,mask=mask,release_status=status,result=got[0]))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))};r=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'clock_release_all.c',HERE/'release_all_module.ld',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['Register-bit membership scan executes; individual clock_release calls intercepted and controlled status ignored asstock. No clock hardware/critical ordering beyond this function proved.']);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
