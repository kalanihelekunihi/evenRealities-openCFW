#!/usr/bin/env python3
"""Counterfactual fixed subtype fields for enable failure/retry; no silicon claim."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
from unicorn import arm_const as a
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('children',HERE/'verify_context_children.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Machine(v.Machine):
 def __init__(self,*args):super().__init__(*args);self.pending_subtype=None
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if v.v.v.IRQ<=address<v.v.v.IRQ+0x8000 and (address-v.v.v.IRQ)%0x1000==0x11c:self.pending_subtype=address
 def code(self,uc,pc,size,user):
  if self.pending_subtype is not None:
   p=self.pending_subtype;value=struct.unpack('<I',uc.mem_read(p,4))[0];uc.mem_write(p,struct.pack('<I',(value&~0xee)|0x20));self.pending_subtype=None
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segments,symbols=v.v.v.elf.elf_info(args.elf);cases=[];trace={}
 for interface in (0,1):
  observations=[]
  for source in (False,True):
   m=Machine(source,segments,symbols);m.reset();h=v.v.POOL+4*v.v.STRIDE;m.cpu.mem_write(h,struct.pack('<I',0));m.config(interface,1000000,0,v.BUFFER,32);m.cpu.mem_write(v.v.v.IRQ+0x4000+0x11c,struct.pack('<I',0x20));m.lower_status=4
   statuses=[m.call(e,values) for e,values in [('claim',[4,v.v.OUT]),('configure',[h,v.CFG]),('enable',[h]),('enable',[h]),('claim',[4,v.v.OUT])]]
   result=m.observation(statuses);result['iom_cq_handle']=struct.unpack('<I',m.cpu.mem_read(h+0x828,4))[0];result['cq_prefix']=struct.unpack('<I',m.cpu.mem_read(v.QUEUE+4*44,4))[0];observations.append(result)
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert observations[0]==observations[1];assert observations[0]['status']==[0,0,4,7,7];assert observations[0]['iom_cq_handle']==0;assert observations[0]['cq_prefix']&0x01000000;cases.append(dict(interface=interface,observation=observations[0]))
 report=dict(status='PASS',cases=2,elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.v.LOCKED_SHA,original_trace=trace,comparisons=cases,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['Both instruction streams execute with lower poll status4 injected. After each SUBMODCTRL store, fixed subtype bits0x20 are restored before the next instruction; raw issued stores remain recorded.','This is a conditional MMIO model sensitivity test, not validation of real silicon register reset/type preservation or a hardware reproduction of the failure.','No synthetic success or resource release is injected. CQ claim remains, repeated initialization returns7 and IOM CQ handle slot becomes0 in the recovered source/stock path.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','cases','elf_sha256')}))
if __name__=='__main__':main()
