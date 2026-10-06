#!/usr/bin/env python3
"""FIFO/poll instruction comparisons; RAM ports, controlled poll/delay callbacks."""
import argparse,importlib.util,itertools,json
from pathlib import Path
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('base',HERE/'verify_leaves.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);v=n.v
ENTRIES={'opencfw_hal_mspi_fifo_read':0x423e8a,'opencfw_hal_mspi_fifo_write':0x423e40,'opencfw_hal_status_poll':0x41d246};BUF=0x20007000;PORT=0x40060000
class Machine(v.Machine):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cpu.mem_map(PORT,0x4000);self.port_events=[];self.poll_calls=0;self.delay_calls=0;self.is_poll=False;self.cpu.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,self.memory,begin=PORT,end=PORT+0x3fff)
 def memory(self,uc,access,address,size,value,user):self.port_events.append([access,address,size,value if access==17 else bytes(uc.mem_read(address,size)).hex()])
 def code(self,uc,pc,size,user):
  if pc==0x41d246 and not self.is_poll:
   self.events.append(['poll',*self.args(),self.u(uc.reg_read(v.a.UC_ARM_REG_SP))]);status=self.poll_statuses[min(self.poll_calls,len(self.poll_statuses)-1)];self.poll_calls+=1;self.ret(status);return
  if pc==0x41d1c0:
   self.delay_calls+=1;self.events.append(['delay-argument',self.args()[0]])
   if self.change_after and self.delay_calls==self.change_after:self.w(PORT+0x90,self.changed)
   self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fifo-elf',type=Path,required=True);ap.add_argument('--poll-elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 info={False:v.elf.elf_info(a.fifo_elf)[1:],True:v.elf.elf_info(a.poll_elf)[1:]};fixtures=[];trace={};cases=[]
 for entry,module,length,statuses in itertools.product(list(ENTRIES)[:2],[0,1,3,4,255],[0,1,2,3,4,5,7,8,9,11],[[0],[4],[4,0],[0,4]]):fixtures.append((entry,[module,BUF,length,3],dict(statuses=statuses)))
 for count,value,equal,change_after in itertools.product([0,1,3],[0,2],[0,1,256,257],[0,1,2,4]):fixtures.append(('opencfw_hal_status_poll',[count,PORT+0x90,3,2,equal],dict(value=value,change_after=change_after,changed=2 if value==0 else 0)))
 for entry,args,f in fixtures:
  is_poll=entry=='opencfw_hal_status_poll';segs,syms=info[is_poll];pair=[Machine(),Machine(True,segs,syms)];results=[]
  for m in pair:
   m.is_poll=is_poll;m.poll_statuses=f.get('statuses',[0]);m.change_after=f.get('change_after',0);m.changed=f.get('changed',0);m.cpu.mem_write(BUF,bytes(range(32)));m.w(PORT+0x90,f.get('value',0))
   for module in range(4):m.w(PORT+(module<<12)+0x14,0x78563412)
   m.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
   for reg,x in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3],args+[0]*4):m.cpu.reg_write(reg,x)
   if len(args)>4:m.w(v.SP,args[4])
   m.cpu.emu_start((syms[entry] if m.source else ENTRIES[entry])|1,v.STOP+2,count=10000);assert m.finished
   results.append(dict(status=m.cpu.reg_read(v.a.UC_ARM_REG_R0),events=m.events,ports=m.port_events,buffer=bytes(m.cpu.mem_read(BUF,32)).hex(),delay_calls=m.delay_calls))
  assert results[0]==results[1],(entry,args,f,results);trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=f,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,fifo_elf_sha256=v.sha(a.fifo_elf),poll_elf_sha256=v.sha(a.poll_elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'fifo_transfer.c',HERE/'status_poll.c',HERE/'fifo_module.ld',HERE/'poll_module.ld',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['FIFO registers are RAM ports; exact read/write addresses, words and output tail bytes compared, no physical FIFO popping or overflow behavior. FIFO profile observes controlled status polls including first-failure/last-status behavior.','Actual poll loop compares masks/equality and models delay-call counts; delay(1) callback can update synthetic status after selected calls. No elapsed microseconds or real clock/timing established.','TX rounded-up word reads require accessible padded caller memory; no added buffer guard. Length0..11, modules0/1/3 and rejected4/255 tested, huge lengths/pointers not accepted-safe. PublicR0 status only, incidental stockR1 not interface output.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
