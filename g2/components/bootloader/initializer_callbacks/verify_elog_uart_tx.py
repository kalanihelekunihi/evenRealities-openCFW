#!/usr/bin/env python3
"""Native original/source UART log TX consumption; finite synthetic FIFO."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
s=importlib.util.spec_from_file_location('base',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v);a=v.a
old_uc=v.Uc
def m33_uc(*args,**kwargs):
 cpu=old_uc(*args,**kwargs);cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);return cpu
v.Uc=m33_uc
P=0x20024400;DESC=0x20001000;BUF=0x20002000;RING=0x20003000;OUT=0x20004000;CALLBACK=0x08000100;ROW=0x20000470;UART=0x40039000
ENTRIES={'claim':('opencfw_boot_uart_tx_claim',0x422ee2),'start':('opencfw_boot_uart_tx_start',0x4234d8),'blocking':('opencfw_boot_uart_tx_blocking',0x423444),'pump':('opencfw_boot_uart_tx_pump',0x423524),'transfer':('opencfw_boot_uart_transfer',0x4233e8),'log':('opencfw_boot_uart_log_send',0x41f918)}
class Machine(v.Machine):
 def __init__(self,source,segs,syms,f):
  super().__init__(source,segs,syms);self.cpu.mem_map(UART,0x4000);self.f=f;self.events=[];self.fifo=[];self.delay_count=0;self.writes=[]
 def u(self,p):return int.from_bytes(self.cpu.mem_read(p,4),'little')
 def w(self,p,value):self.cpu.mem_write(p,struct.pack('<I',value&0xffffffff))
 def memwrite(self,uc,access,p,size,val,user):
  if p==UART:
   self.fifo.append(val&255)
   if len(self.fifo)%self.f.get('fifo_capacity',8)==0:uc.mem_write(UART+0x18,struct.pack('<I',0x20))
 def code(self,uc,pc,size,user):
  r0=uc.reg_read(a.UC_ARM_REG_R0);r1=uc.reg_read(a.UC_ARM_REG_R1)
  delays=[0x41d1c0,0x41f9e6] if not self.source else [self.symbols['opencfw_boot_delay_us_math']&~1,self.symbols['opencfw_boot_delay_raw']&~1]
  if pc in delays:
   self.delay_count+=1;self.events.append(['delay',r0]);uc.mem_write(UART+0x18,struct.pack('<I',0x20 if self.f.get('stalled') else 0))
   if self.f.get('completion_after')==self.delay_count:uc.mem_write(ROW+25,b'\1')
   uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc==CALLBACK:self.events.append(['callback',r0,r1]);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc in [0x415ff4,0x41560c]:
   fill=0 if pc==0x415ff4 else uc.reg_read(a.UC_ARM_REG_R2)&255;uc.mem_write(r0,bytes([fill])*r1);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc in [0x42348e,0x4234fa]:self.events.append(['rx-cut',hex(pc),r0]);uc.reg_write(a.UC_ARM_REG_R0,7);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def run(self,kind):
  f=self.f;self.cpu.mem_write(P,bytes([0xa5])*0x11c);self.w(P,f.get('magic',0x01ea9e06));self.w(P+0x28,0);self.cpu.mem_write(P+0x119,bytes([f.get('busy',0)]));self.cpu.mem_write(P+0xdc,bytes([f.get('ring',1)]));self.cpu.mem_write(P+0x34,struct.pack('<6I',0,0,0,f.get('ring_capacity',8),f.get('ring_width',1),RING));self.cpu.mem_write(RING,bytes([0xcc])*64);self.cpu.mem_write(BUF,bytes(range(64)));self.w(OUT,0xeeeeeeee);self.w(UART+0x18,0x20 if f.get('stalled') else 0)
  words=[BUF,f.get('length',16),OUT if f.get('count_pointer',True) else 0,f.get('timeout',3),CALLBACK|1 if f.get('callback',True) else 0,0xdeadbeef,0]+[0]*6+[f.get('mode',0)];self.cpu.mem_write(DESC,struct.pack('<14I',*words));self.w(ROW+4,P);self.cpu.mem_write(ROW+24,bytes([f.get('initialized',1),7]));self.cpu.reg_write(a.UC_ARM_REG_PRIMASK,f.get('primask',0));self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000);self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1)
  args=[1,BUF,f.get('length',16)] if kind=='log' else [f.get('handle',P),DESC]
  for r,n in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2],args+[0]):self.cpu.reg_write(r,n)
  name,stock=ENTRIES[kind];self.cpu.emu_start((self.symbols[name]&~1 if self.source else stock)|1,v.STOP+2,count=600000);assert self.done,(kind,self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
  return dict(status=None if kind=='pump' else self.cpu.reg_read(a.UC_ARM_REG_R0),events=self.events,fifo=self.fifo,context=bytes(self.cpu.mem_read(P,0x11c)).hex(),ring=bytes(self.cpu.mem_read(RING,64)).hex(),row=bytes(self.cpu.mem_read(ROW,28)).hex(),count=self.u(OUT),primask=self.cpu.reg_read(a.UC_ARM_REG_PRIMASK))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);arg=ap.parse_args();_,segs,syms=v.elf.elf_info(arg.elf);assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest()==v.LOCKED_SHA;cases=[];trace={}
 fixtures=[]
 for kind,ring,length,callback,primask in itertools.product(['claim','start','blocking','transfer','log'],[0,1],[0,1,8,16,31],[False,True],[0,1]):fixtures.append((kind,dict(ring=ring,length=length,callback=callback,primask=primask,completion_after=2)))
 for kind in ['claim','start','blocking','transfer','log']:
  for f in [dict(busy=1),dict(magic=0),dict(handle=0),dict(initialized=0)]:
   if kind in ['claim','start','blocking'] and ('magic' in f or 'handle' in f or 'initialized' in f):continue
   fixtures.append((kind,f))
 for mode in [1,2,3,4,255]:fixtures.append(('transfer',dict(mode=mode)))
 for timeout in [1,2,3]:fixtures.append(('blocking',dict(ring=0,stalled=True,timeout=timeout)))
 fixtures.append(('log',dict(length=0,completion_after=0)))
 for callback in [False,True]:fixtures.append(('start',dict(ring_width=2,callback=callback)))
 for kind,f in fixtures:
  obs=[]
  for source in [False,True]:
   m=Machine(source,segs,syms,f)
   try:obs.append(m.run(kind))
   except Exception:print('FAILED',kind,f,source,hex(m.cpu.reg_read(a.UC_ARM_REG_PC)));raise
   if not source:trace.update(m.trace)
  assert obs[0]==obs[1],(kind,f,{k:[o[k] for o in obs] for k in obs[0] if obs[0][k]!=obs[1][k]});cases.append(dict(kind=kind,fixture=f,observation=obs[0]))
 blob=v.BLOB.read_bytes()
 for pc,raw in trace.items():assert bytes.fromhex(raw)==blob[pc-v.BASE:pc-v.BASE+len(bytes.fromhex(raw))]
 ranges={'log':[0x41f918,0x41f9b6],'claim':[0x422ee2,0x422f4c],'dispatch':[0x4233e8,0x423444],'blocking':[0x423444,0x42348e],'start':[0x4234d8,0x4234fa],'pump':[0x423524,0x423608],'fifo':[0x42330e,0x42333e],'drain':[0x423390,0x4233e8],'ring-add':[0x427602,0x427660],'ring-get':[0x427660,0x4276c2]};used={pc+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))};r=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(arg.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),visited_body_bytes={n:len(used&set(range(*r))) for n,r in ranges.items()},original_trace={hex(pc):raw for pc,raw in trace.items()},comparisons=cases,limits=['Native TX dispatcher/start/claim/pump/blocking/ring/FIFO and log wrapper execute. RX modes1/3 injected.','Finite synthetic FIFO flag set after8 writes and cleared by injected delay; no hardware timing/drain or real IRQ/task activity.','Original zero fill modeled; source memset native. Timeout0 default logger path tested under progress; no infinite-stall completion claim.','Synthetic callbacks return; consumption byte count and copied ring/FIFO data compare, not hardware stop or UART shift-register completion.']);arg.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256','visited_body_bytes']}))
if __name__=='__main__':main()
