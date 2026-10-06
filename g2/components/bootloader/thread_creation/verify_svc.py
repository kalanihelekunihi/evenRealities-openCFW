#!/usr/bin/env python3
"""Recover SVC stack selection and dispatch; exception frames are explicit fixtures."""
import argparse,importlib.util,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_MEM_INVALID
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('restore',HERE/'verify_restore.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v
class Machine(r.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.invalid=None;self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.bad)
 def bad(self,uc,access,address,size,value,user):
  self.invalid=dict(access=access,address=address,size=size,value=value);return False

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for use_psp in [False,True]:
  for opcode in [2,0,1,3,255]:
   pair=[Machine(False,segments,symbols),Machine(True,segments,symbols)];results=[]
   for m in pair:
    cb=0x20030000;base=0x20031000;frame=base+0x100
    m.w(0x20027134,cb);m.w(cb,frame);m.cpu.mem_write(frame,struct.pack('<18I',base,0xfffffffd,*range(16)))
    # Opposite stack points to a different SVC immediate: catches wrong LR bit selection.
    for stack,imm in [(0x2003e000,255 if use_psp else opcode),(0x2003d000,opcode if use_psp else 255)]:
     code=v.STOP+0x100+(0x20 if stack==0x2003d000 else 0)
     m.cpu.mem_write(code,bytes([imm,0xdf]));m.w(stack+24,code+2)
    m.w(0xe000ed88,0x123456);m.w(0xe000ef34,0x234567)
    for reg,val in [(v.a.UC_ARM_REG_CONTROL,0),(v.a.UC_ARM_REG_MSP,0x2003e000),(v.a.UC_ARM_REG_PSP,0x2003d000),(v.a.UC_ARM_REG_BASEPRI,48),(v.a.UC_ARM_REG_LR,0xfffffffd if use_psp else 0xfffffff9)]:m.cpu.reg_write(reg,val)
    start=(symbols['opencfw_boot_svc_entry']&~1) if m.source else 0x41b374
    try:
     m.cpu.emu_start(start|1,v.STOP+2,count=200)
     assert opcode==2 and m.finished
    except UcError:
     assert opcode!=2 and m.invalid and m.invalid['address']==0xffffffff and m.invalid['value']==0
    result=dict(fault=m.invalid,psp=m.cpu.reg_read(v.a.UC_ARM_REG_PSP),control=m.cpu.reg_read(v.a.UC_ARM_REG_CONTROL),basepri=m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),cpacr=m.u(0xe000ed88),fpccr=m.u(0xe000ef34))
    results.append(result)
   assert results[0]==results[1],results
   if opcode==2:
    assert results[0]['psp']==base+0x128 and results[0]['control']==2 and results[0]['basepri']==0
    assert results[0]['cpacr']==(0x123456|0xf00000) and results[0]['fpccr']==(0x234567|0xc0000000)
   else:assert results[0]['cpacr']==0x123456 and results[0]['fpccr']==0x234567 and results[0]['basepri']==48
   trace.update(pair[0].trace);cases.append(dict(use_psp=use_psp,svc_immediate=opcode,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Explicit synthetic exception frame and LR EXC_RETURN; no hardware stacking/unstacking, exception priority or automatic SVC entry. Stops before BX EXC_RETURN on success and observes invalid store on rejected immediate, not HardFault delivery.','Both MSP/PSP selection branches execute, only SVC immediate2 enables FPU and restores first task. Source M55 assembly and M33-compatible CPU; no byte identity/source completeness claim.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
