#!/usr/bin/env python3
"""Original/source thread-attribute routing; kernel providers synthetic."""
import argparse,importlib.util,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('thread_v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES['thread_new']=0x4160fe
ATTR=0x20030000
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.guard=0;self.handle=0x20026ac0;self.dynamic_status=1
 def code(self,uc,pc,size,user):
  if pc==0x41602a:
   self.events.append(['guard',self.guard]);self.ret(self.guard);return
  if pc in [0x417c7c,0x417d16]:
   args=self.args();sp=uc.reg_read(v.a.UC_ARM_REG_SP);priority=self.u(sp)
   if pc==0x417c7c:
    self.events.append(['static',*args,priority,self.u(sp+4),self.u(sp+8)]);self.ret(self.handle)
   else:
    self.events.append(['dynamic',*args,priority]);self.w(self.u(sp+4),self.handle);self.ret(self.dynamic_status)
   return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(args.elf);trace={};cases=[]
 attrs=[None,[0]*9,[0x434134,0,0x20026ac0,112,0x20018aa0,0x4000,48,1,0], [0x4341a4,0,0x20026b30,112,0x20020e00,0x2000,46,1,0]]
 for index,values in [(2,[0,1]),(3,[0,111,112,113]),(4,[0,0x20018aa0]),(5,[0,1,3,4,0x3ffff,0x40000,0xffffffff]),(6,[0,1,56,57,0xffffffff]),(1,[1,2,0x100])]:
  for value in values:
   a=[0]*9;a[index]=value;attrs.append(a)
 for guard in [0,1]:
  for entry in [0,0x42e2f9]:
   for attr in attrs:
    for status in [0,1,2]:
     pair=[Machine(),Machine(True,segments,symbols)];results=[]
     for m in pair:
      m.guard=guard;m.dynamic_status=status
      if attr is not None:m.cpu.mem_write(ATTR,struct.pack('<9I',*attr))
      r=m.run('thread_new',[entry,0x1234,ATTR if attr is not None else 0]);results.append((r['return'],r['events']))
     assert results[0]==results[1],(guard,entry,attr,status,results)
     trace.update(pair[0].trace);cases.append(dict(guard=guard,entry=entry,attr=attr,status=status,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(args.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Context guard 41602a and kernel creators 417c7c/417d16 are synthetic. No allocation, scheduling, IRQ, or hardware behavior established.','M4 compatibility execution; M55 compilation separately. No source completeness or byte identity claim.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
