#!/usr/bin/env python3
"""Reuse scatter/callback evidence, execute actual attribute wrapper in chain."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('chain',ROOT/'g2/components/bootloader/main_callback/verify_startup_callback_integrated.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.CALLBACK_PROVIDERS.remove(0x4160fe)
v=c.v
class Machine(c.StartupCallbackMachine):
 def code(self,uc,pc,size,user):
  if pc==0x41602a:
   self.events.append(['guard',0]);self.ret(0);return
  if pc==0x417c7c:
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);r=self.args();extra=[self.u(sp+i) for i in [0,4,8]]
   assert r==[c.THREAD_ENTRY,c.MANAGER_NAME,4096,0],r
   assert extra==[48,0x20018aa0,0x20026ac0],extra
   self.events.append(['static-thread',*r,*extra]);self.ret(self.created_handle);return
  if pc==0x417d16:raise AssertionError('manager must use static creator')
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);blob=v.BLOB.read_bytes();trace={};cases=[]
 for mode in [0,7]:
  for handle in [1,0x51]:
   pair=[Machine(),Machine(True,segments,symbols)]
   for m in pair:
    m.mode_result=mode;m.created_handle=handle;m.w(c.SLOT,c.SLOT_SENTINEL)
    for addr,n in c.INIT_REGIONS:m.cpu.mem_write(addr,b'\xcc'*n)
    m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob)
   results=[m.run('system_entry',[]) for m in pair]
   assert results[0]['events']==results[1]['events'],results
   for m in pair:
    assert m.callback_seen and m.u(c.SLOT)==c.PUBLISHED_CALLBACK and m.u(c.HANDLE)==handle
    for addr,n in c.INIT_REGIONS:assert hashlib.sha256(m.ram_after_scatter[addr]).hexdigest()==c.EXPECTED_REGION_SHA256[addr]
   trace.update(pair[0].trace);cases.append(dict(mode=mode,handle=handle,events=results[0]['events']))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 sources=[]
 for folder in ['thread_creation','main_callback','startup','main_init']:
  sources.extend(p for p in (ROOT/'g2/components/bootloader'/folder).iterdir() if p.is_file())
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in sources},original_trace=trace,comparisons=cases,limits=['Real thread-attribute wrapper is executed; context guard and static kernel creator are synthetic. Scheduler and hardware not established.','Compressed streams remain 695 bytes of authenticated fixture inputs. Source record table and actual callback pointer are retained.','M4 compatibility execution, not byte-identical rebuild.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
