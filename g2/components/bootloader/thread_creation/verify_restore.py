#!/usr/bin/env python3
"""M33-compatible instruction probe; stop before architectural exception return."""
import argparse,importlib.util,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('restore_v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
original_uc=v.Uc
def m33_uc(*args,**kwargs):
 cpu=original_uc(*args,**kwargs);cpu.ctl_set_cpu_model(v.a.UC_CPU_ARM_CORTEX_M33);return cpu
v.Uc=m33_uc
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs)
  self.stop_return=0x41b2d0
  if self.source:
   start=self.symbols['opencfw_boot_first_task_restore']&~1;dis=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
   self.stop_return=next(i.address for i in dis.disasm(bytes(self.cpu.mem_read(start,80)),start) if i.mnemonic=='bx' and i.op_str=='r2')
 def code(self,uc,pc,size,user):
  if pc==self.stop_return:self.finished=True;uc.emu_stop();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for base in [0x20031000,0x20032000]:
  pair=[Machine(False,segments,symbols),Machine(True,segments,symbols)];results=[]
  for m in pair:
   cb=0x20030000;frame=base+0x100;m.w(0x20027134,cb);m.w(cb,frame);m.cpu.mem_write(frame,struct.pack('<18I',base,0xfffffffd,*range(16)))
   m.cpu.reg_write(v.a.UC_ARM_REG_BASEPRI,48);m.cpu.reg_write(v.a.UC_ARM_REG_CONTROL,0)
   start=(symbols['opencfw_boot_first_task_restore']&~1) if m.source else 0x41b2ac
   m.cpu.emu_start(start|1,v.STOP+2,count=100);assert m.finished
   result=dict(psp=m.cpu.reg_read(v.a.UC_ARM_REG_PSP),control=m.cpu.reg_read(v.a.UC_ARM_REG_CONTROL),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),exception_return=m.cpu.reg_read(v.a.UC_ARM_REG_R2))
   # The Python API lacks PSPLIM. Execute a source-assembled MRS readback probe.
   # Same probe ELF loaded in both machines, outside original address range.
   if not m.source:
    m.cpu.mem_map(0x10000,0x10000)
    for segment in segments:m.cpu.mem_write(segment['address'],segment['data'])
    m.exec_ranges.extend((seg['address'],seg['address']+len(seg['data'])) for seg in segments)
   m.finished=False;m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);m.cpu.emu_start((symbols['opencfw_test_read_psplim']|1),v.STOP+2,count=10);assert m.finished
   result['psplim']=m.cpu.reg_read(v.a.UC_ARM_REG_R0);results.append(result)
  assert results[0]==results[1],results
  assert results[0]==dict(psp=base+0x128,control=2,basepri=0,exception_return=0xfffffffd,psplim=base)
  trace.update({pc:b for pc,b in pair[0].trace.items() if int(pc,0)>=0x410000});cases.append(dict(base=base,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['M33-compatible Unicorn CPU, source compiled M55 assembly. Execution stops before BX EXC_RETURN; no hardware exception unstacking/task entry/FPU extended-frame validation.','Synthetic valid18-word frame; actual PSPLIM/CONTROL/PSP/BASEPRI instructions execute, PSPLIM read back through source-assembled test-only probe.','First restore only, not PendSV/SVC full dispatch; no source completeness or byte identity.'])
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
