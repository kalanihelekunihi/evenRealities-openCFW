#!/usr/bin/env python3
"""Original NOR mutex/power wrappers versus source with explicit HAL/constructor cuts."""
import argparse,importlib.util,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('base',HERE/'verify_nor_init.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);v=n.v
v.ENTRIES.update(nor_power=0x41fe28,nor_unpower=0x41fe48,nor_mutex=0x41fe62)
class Machine(v.Machine):
 def code(self,uc,pc,size,user):
  if pc==0x426808:self.events.append(['power',*self.args()[:3]]);self.ret(self.status);return
  if pc==0x416610:self.events.append(['mutex-new',bytes(uc.mem_read(self.args()[0],16)).hex()]);self.ret(self.created);return
  if pc==0x4176ce:
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);self.events.append(['log',self.args()[0],self.u(sp)]);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);trace={};cases=[]
 for entry,flag,status,existing,created in itertools.product(['nor_power','nor_unpower','nor_mutex'],[0,1,2,255],[0,7],[0,0x20026c60],[0,0x20026c60]):
  pair=[Machine(),Machine(True,segs,syms)];results=[]
  for m in pair:
   m.status=status;m.created=created;m.w(0x200270dc,0x20006000);m.w(0x200270e0,existing);m.cpu.mem_write(0x200271c6,bytes([flag]));m.cpu.reg_write(v.a.UC_ARM_REG_R7,0x12345678)
   address=syms['opencfw_provider_'+{'nor_power':'41fe28','nor_unpower':'41fe48','nor_mutex':'41fe62'}[entry]] if m.source else v.ENTRIES[entry]
   m.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);m.cpu.emu_start(address|1,v.STOP+2,count=10000);assert m.finished
   results.append(dict(events=m.events,flag=m.cpu.mem_read(0x200271c6,1)[0],mutex=m.u(0x200270e0)))
  assert results[0]==results[1],(entry,flag,status,existing,created,results)
  trace.update(pair[0].trace);cases.append(dict(entry=entry,flag=flag,status=status,existing=existing,created=created,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'nor_runtime.c',HERE/'runtime_module.ld',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['HAL power and mutex construction return controlled statuses/handles in this direct profile; integrated reset profile executes the actual static mutex constructor.','Power flag is software bookkeeping, updated despite HAL failure; no hardware power transition or concurrency established. Void return registers are incidental and not compared.','Logging severity/line only; no complete firmware or byte equality claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
