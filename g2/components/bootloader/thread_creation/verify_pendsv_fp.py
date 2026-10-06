#!/usr/bin/env python3
"""Manual non-FP exception state; execute save/select/restore, halt before return."""
import argparse,importlib.util,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('pendsv_v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
original_uc=v.Uc
def m33_uc(*args,**kwargs):
 cpu=original_uc(*args,**kwargs);cpu.ctl_set_cpu_model(v.a.UC_CPU_ARM_CORTEX_M33);return cpu
v.Uc=m33_uc
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.stop_return=0x41b372
  if self.source:
   start=self.symbols['opencfw_boot_pendsv_entry']&~1;dis=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
   self.stop_return=next(i.address for i in dis.disasm(bytes(self.cpu.mem_read(start,160)),start) if i.mnemonic=='bx' and i.op_str=='r3')
 def code(self,uc,pc,size,user):
  if pc==self.stop_return:self.finished=True;uc.emu_stop();return
  if pc==0x41b600:raise AssertionError('unmodeled stack-overflow path')
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for history in [0,63]:
  pair=[Machine(False,segments,symbols),Machine(True,segments,symbols)];results=[]
  for m in pair:
   if not m.source:
    m.cpu.mem_map(0x10000,0x10000)
    for seg in segments:m.cpu.mem_write(seg['address'],seg['data'])
    m.exec_ranges.extend((seg['address'],seg['address']+len(seg['data'])) for seg in segments)
   cb1,cb2=0x20030000,0x20030080;outbase,inbase=0x20031000,0x20032000;outpsp=outbase+0x200;inframe=inbase+0x100
   m.cpu.mem_write(outbase,b'\xa5'*16);m.cpu.mem_write(inbase,b'\xa5'*16);m.cpu.mem_write(outpsp,struct.pack('<8I',*range(8)));m.cpu.mem_write(inframe,struct.pack('<52I',inbase,0xffffffed,*range(0x40,0x48),*range(0x8000,0x8010),*range(26)))
   m.w(0x20027134,cb1);m.w(0x2002716c,0);m.w(0x2002714c,24);m.w(0x20027170,history);m.w(cb1+0x30,outbase);m.w(cb2+0x30,inbase);m.w(cb1+0x58,10);m.w(cb2+0x58,11);m.w(cb2,inframe)
   l=0x20024870+24*20;end=l+8;m.w(l,2);m.w(l+4,cb1+4);m.w(end+4,cb1+4);m.w(end+8,cb2+4)
   for cb,nextnode,previous in [(cb1,cb2+4,end),(cb2,end,cb1+4)]:m.w(cb+8,nextnode);m.w(cb+12,previous);m.w(cb+16,cb)
   m.cpu.reg_write(v.a.UC_ARM_REG_R0,outbase);m.cpu.reg_write(v.a.UC_ARM_REG_R1,outpsp);m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);m.cpu.emu_start(symbols['opencfw_test_set_stack_limits']|1,v.STOP+2,count=10)
   m.finished=False
   regs=[getattr(v.a,'UC_ARM_REG_R'+str(i)) for i in range(4,12)]
   for i,reg in enumerate(regs):m.cpu.reg_write(reg,0x5000+i)
   m.cpu.mem_write(0xe000ed88,struct.pack('<I',0x00f00000))
   for i in range(16,32):m.cpu.reg_write(getattr(v.a,'UC_ARM_REG_S'+str(i)),0x9000+i)
   m.cpu.reg_write(v.a.UC_ARM_REG_LR,0xffffffed);m.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP)
   start=(symbols['opencfw_boot_pendsv_entry']&~1) if m.source else 0x41b31c;m.cpu.emu_start(start|1,v.STOP+2,count=1000);assert m.finished
   result=dict(current=m.u(0x20027134),psp=m.cpu.reg_read(v.a.UC_ARM_REG_PSP),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),exc_return=m.cpu.reg_read(v.a.UC_ARM_REG_R3),fp_registers=[m.cpu.reg_read(getattr(v.a,'UC_ARM_REG_S'+str(i))) for i in range(16,32)],callee_registers=[m.cpu.reg_read(reg) for reg in regs],out_saved_sp=m.u(cb1),out_saved_frame=bytes(m.cpu.mem_read(outpsp-104,104)).hex(),history=bytes(m.cpu.mem_read(0x20026500,512)).hex(),history_index=m.u(0x20027170))
   m.finished=False;m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);m.cpu.emu_start(symbols['opencfw_test_read_psplim']|1,v.STOP+2,count=10);result['psplim']=m.cpu.reg_read(v.a.UC_ARM_REG_R0);results.append(result)
  assert results[0]==results[1],results
  assert results[0]['current']==cb2 and results[0]['callee_registers']==list(range(0x40,0x48));assert results[0]['psp']==inframe+104 and results[0]['psplim']==inbase
  assert results[0]['fp_registers']==list(range(0x8000,0x8010))
  trace.update({pc:b for pc,b in pair[0].trace.items() if int(pc,0)>=0x410000});cases.append(dict(history=history,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['M33-compatible Unicorn manually seeded exception/software frames; actual exception stacking/unstacking/interrupt dispatch not modeled. Stops before BX EXC_RETURN.','FP EXC_RETURNFFFFFFED with manually seeded52-word incoming software+extended hardware frame; actual S16-S31 save/restore executes. Lazy hardware frame creation and unstacking untested. Actual source/original save/select/PSPLIM/PSP/register restore execute.','Synthetic coherent two-task ready list; stack-overflow/empty-ready fatal paths not covered. No hardware or byte identity.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
