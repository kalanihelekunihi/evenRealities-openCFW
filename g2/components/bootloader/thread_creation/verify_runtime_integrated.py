#!/usr/bin/env python3
"""Reuse scatter/callback evidence, execute actual attribute wrapper in chain."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('chain',ROOT/'g2/components/bootloader/main_callback/verify_startup_callback_integrated.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.CALLBACK_PROVIDERS.remove(0x4160fe)
c.CALLBACK_PROVIDERS.remove(0x41b2f8)
v=c.v
class Machine(c.StartupCallbackMachine):
 def code(self,uc,pc,size,user):
  if pc==0x41560c:
   dest,n,fill,_=self.args();uc.mem_write(dest,bytes([fill&255])*n);self.ret(dest);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);blob=v.BLOB.read_bytes();trace={};cases=[]
 for mode in [0,7]:
  for handle in [0x20026ac0]:
   pair=[Machine(),Machine(True,segments,symbols)]
   for m in pair:
    m.mode_result=mode;m.created_handle=handle;m.w(c.SLOT,c.SLOT_SENTINEL)
    for addr,n in c.INIT_REGIONS:m.cpu.mem_write(addr,b'\xcc'*n)
    m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob)
   results=[m.run('system_entry',[]) for m in pair]
   for addr,n in [(0x20026ac0,112),(0x20018aa0,16384),(0x20024870,1120),(0x20026f34,100),(0x20027130,64),(0x200004c4,4)]:
    assert bytes(pair[0].cpu.mem_read(addr,n))==bytes(pair[1].cpu.mem_read(addr,n)),hex(addr)
   assert pair[0].cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)==pair[1].cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),(pair[0].cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),pair[1].cpu.reg_read(v.a.UC_ARM_REG_BASEPRI))
   assert results[0]['events']==results[1]['events'],results
   for m in pair:
    assert m.callback_seen and m.u(c.SLOT)==c.PUBLISHED_CALLBACK and m.u(c.HANDLE)==handle
    for addr,n in c.INIT_REGIONS:assert hashlib.sha256(m.ram_after_scatter[addr]).hexdigest()==c.EXPECTED_REGION_SHA256[addr]
   trace.update(pair[0].trace);cases.append(dict(mode=mode,handle=handle,events=results[0]['events'],nesting=pair[0].u(0x200004c4),basepri=pair[0].cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 sources=[]
 for folder in ['thread_creation','main_callback','startup','main_init']:
  sources.extend(p for p in (ROOT/'g2/components/bootloader'/folder).iterdir() if p.is_file())
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in sources},original_trace=trace,comparisons=cases,limits=['Real wrapper, static creation, task initialization, frame construction, ready-list registration/initialization, context guard and critical nesting execute. Setup416058 and scheduler-start4160b0 remain synthetic. PendSV delivery and real scheduling not established.','Compressed streams remain 695 bytes of authenticated fixture inputs. Source record table and actual callback pointer are retained. Original fill41560c intercepted; source byte loops execute. Complete manager TCB/stack/ready lists/globals compared.','M4 compatibility execution, not byte-identical rebuild.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
