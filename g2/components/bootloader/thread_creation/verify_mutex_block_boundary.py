#!/usr/bin/env python3
"""Native mutex wait setup through the PendSV request boundary."""
import argparse,importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('receive_cases',Path(__file__).with_name('verify_queue_receive.py'));q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
v=q.v;v.ENTRIES['kernel_mutex_take_plain']=0x41a24e
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();_,segs,syms=v.elf.elf_info(a.elf);syms['opencfw_boot_kernel_mutex_take_plain']=syms['opencfw_bl_kernel_mutex_take_plain'];cases=[];trace={}
 for now,ticks in [(0,1),(17,32),(0xfffffff0,32),(0,0xffffffff)]:
  outputs=[]
  for source in [False,True]:
   m=q.Machine(source,segs,syms);q.init(m,now);m.stop_yield=True;m.w(0x20027150,0);m.w(q.QUEUE,0);m.w(q.QUEUE+64,0);m.w(q.QUEUE+56,0);m.w(q.QUEUE+8,0x20030080);m.w(0x20030080+44,8);m.w(0x20030080+96,8);m.w(0x20030080+100,1);m.w(0x20030080+24,48);m.w(0x20030000+36,0x20030000)
   m.run('kernel_mutex_take_plain',[q.QUEUE,ticks]);r=q.snapshot(m);r['owner']=bytes(m.cpu.mem_read(0x20030080,112)).hex();r['icsr']=m.u(0xe000ed04);assert ['yield-boundary'] in m.events;assert m.u(0x20030080+44)==24;assert m.u(q.QUEUE+36)==1;assert m.u(0x20030000+40)==q.QUEUE+36;outputs.append(r)
   if not source:trace.update(m.trace)
  assert outputs[0]==outputs[1],(now,ticks,outputs);cases.append(dict(now=now,ticks=ticks,observed=outputs[0]))
 r=dict(status='PASS',cases=len(cases),elf_sha256=v.sha(a.elf),original_sha256=v.SHA,runner_sha256=v.sha(Path(__file__)),original_trace=trace,comparisons=cases,limits=['Actual timeout capture/check, scheduler suspend/resume, sorted event enqueue, TCB block, queue unlock and priority inheritance execute on coherent synthetic tick/list fixtures. No mutex path is replaced with a returning stub.','Stops at PendSV-request entry before actual exception/task restoration. Does not prove post-wake retry, live ticks, scheduling delivery, cancellation, delete or drain. Inherited timer helpers retain explicit event-wake cuts, not taken in these no-other-waiter fixtures.'])
 a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
