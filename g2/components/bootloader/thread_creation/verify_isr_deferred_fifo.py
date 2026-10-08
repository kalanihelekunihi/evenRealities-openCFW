#!/usr/bin/env python3
"""Native callback-record FIFO and full rejection; synthetic consumer invocation."""
import argparse,importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('isr_fixture',Path(__file__).with_name('verify_isr_delivery.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class Machine(v.Machine):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.delivered=[]
 def code(self,uc,pc,size,user):
  target=(self.symbols['opencfw_boot_event_flags_deferred']&~1) if self.source else 0x419bae
  if pc==target:self.delivered.append(self.args()[:2])
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();_,segs,syms=v.v.elf.elf_info(a.elf);outputs=[];trace={}
 for source in [False,True]:
  m=Machine(source,segs,syms);m.seed_queue(size=16);m.cpu.mem_write(v.BUF,bytes(64));other=v.EVENT+64;m.w(other,0x20);m.list_init(other+4)
  # Exercise pend callback itself as an exported compiled body, not only
  # compiler-inlined calls from the flags ISR wrapper.
  posts=[(v.EVENT,1),(other,2),(v.EVENT,4),(other,8)];returns=[]
  for target,flags in posts:returns.append(m.call('opencfw_boot_pend_callback_isr',[m.callback(),target,flags,v.FLAG]))
  assert returns==[1,1,1,0] and m.u(v.EVENT)==0x10 and m.u(other)==0x20 and not m.delivered
  m.call('opencfw_bl_timer_process_commands',[]);assert m.delivered==[[v.EVENT,1],[other,2],[v.EVENT,4]];assert m.u(v.EVENT)==0x15 and m.u(other)==0x22 and m.u(v.Q+56)==0
  out=m.snapshot(returns);out['delivered']=m.delivered;out['second_event']=bytes(m.cpu.mem_read(other,32)).hex();outputs.append(out)
  if not source:trace.update(m.trace)
 assert outputs[0]==outputs[1]
 r=dict(status='PASS',cases=1,elf_sha256=v.v.sha(a.elf),original_sha256=v.v.SHA,runner_sha256=v.v.sha(Path(__file__)),original_trace=trace,comparison=outputs[0],limits=['Actual pend callback compiled body, ISR put, queue copy/get, timer dispatcher and flags callback execute;3 callback records deliver FIFO and fourth full-queue rejection produces no callback. Consumer is explicitly invoked, not scheduled by an IRQ/timer.','Event pointers remain borrowed; no deletion, reentrant producer, callback exception recovery or whole-system drain proof. Source callback word normalized only in recognized16-byte records.'])
 a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
