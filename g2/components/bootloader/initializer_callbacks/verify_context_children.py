#!/usr/bin/env python3
"""Locked IOM child bodies versus compiled shared source; MMIO is modeled RAM."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('claim',HERE/'verify_context_claim.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(configure=('opencfw_boot_context_configure',0x42cc34),enable=('opencfw_boot_context_enable',0x42c538),select=('opencfw_boot_iom_select_interface',0x42c034),clock=('opencfw_boot_iom_clock_config',0x42c26a),frequency=('opencfw_boot_iom_frequency',0x42c222),onebit=('opencfw_boot_iom_onebit',0x42c256),cqinit=('opencfw_boot_iom_cq_initialize',0x42c3e2),cqon=('opencfw_boot_iom_cq_enable',0x42c420),cqoff=('opencfw_boot_iom_cq_disable',0x42c44e),retry=('opencfw_boot_context_retry',0x43048e))
CFG,BUFFER,QUEUE=0x20004000,0x20008000,0x200262f0
class Machine(v.Machine):
 def __init__(self,source,segments,symbols):
  super().__init__(source,segments,symbols)
  for pc,(label,_) in list(self.cuts.items()):
   if label in ('cq-enable','cq-disable'):del self.cuts[pc]
  self.cuts[(symbols['opencfw_boot_delay_scaled']&~1) if source else 0x41f9d8]=('delay-scaled',1)
  self.cuts[(symbols['opencfw_bl_power_register_update']&~1) if source else 0x41d92c]=('power-register',2)
  self.retry_results=None
 def code(self,uc,pc,size,user):
  entry=(self.symbols['opencfw_boot_context_transaction']&~1) if self.source else 0x42c988
  if self.retry_results is not None and pc==entry:
   value=self.retry_results.pop(0);self.events.append(['transaction',*[uc.reg_read(r) for r in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2)],value]);uc.reg_write(a.UC_ARM_REG_R0,value);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if QUEUE<=address<QUEUE+12*44 or BUFFER<=address<BUFFER+4096:self.state_writes.append([address,size,value&((1<<(size*8))-1)])
 def reset(self):
  super().reset();self.cpu.mem_write(QUEUE,b'\0'*(12*44));self.cpu.mem_write(BUFFER,b'\0'*4096);self.lower_status=0;self.clock_status=0;self.retry_results=None
 def call(self,entry,args):
  self.done=False
  for reg,value in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),list(args)+[0]*4):self.cpu.reg_write(reg,value)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.v.STOP|1)
  if len(args)>4:self.cpu.mem_write(v.v.SP,struct.pack('<I',args[4]))
  pc=(self.symbols[v.ENTRIES[entry][0]]&~1) if self.source else v.ENTRIES[entry][1]
  self.cpu.emu_start(pc|1,v.v.STOP+2,count=3000000);assert self.done,(entry,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
  value=self.cpu.reg_read(a.UC_ARM_REG_R0)
  if entry=='clock':value|=self.cpu.reg_read(a.UC_ARM_REG_R1)<<32
  return value
 def observation(self,status):
  result=super().observation(status);result['queue_sha256']=hashlib.sha256(self.cpu.mem_read(QUEUE,12*44)).hexdigest();result['buffer_sha256']=hashlib.sha256(self.cpu.mem_read(BUFFER,4096)).hexdigest();return result
 def handle(self,module,flags=0x01123456):
  h=v.POOL+module*v.STRIDE;self.cpu.mem_write(h,struct.pack('<II',flags,module));return h
 def config(self,interface,hz,mode=0,buffer=0,words=0):self.cpu.mem_write(CFG,struct.pack('<5I',interface,hz,mode,buffer,words))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();blob=v.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.v.LOCKED_SHA;_,segments,symbols=v.v.elf.elf_info(args.elf);machines=[Machine(False,segments,symbols),Machine(True,segments,symbols)];cases=[]
 def compare(kind,parameters,prepare,sequence):
  observations=[]
  for m in machines:
   m.reset();prepare(m);status=[m.call(entry,values) for entry,values in sequence];observations.append(m.observation(status))
  assert observations[0]==observations[1],(kind,parameters,observations)
  cases.append(dict(kind=kind,parameters=parameters,observation=observations[0]));return observations[0]
 hz_values=[0,1,10,100,1000,5858,5859,5860,10000,100000,250000,400000,1000000,2000000,3000000,6000000,12000000,24000000,31999999,32000000,47999999,48000000,48000001,96000000,0xffffffff]
 state=12345
 for _ in range(80):state=(state*1664525+1013904223)&0xffffffff;hz_values.append(state%48000001)
 for hz,phase in itertools.product(hz_values,(0,1,2)):compare('clock',[hz,phase],lambda m:None,[('clock',[hz,phase])])
 for select,div3,enabled,period in itertools.product((1,4,7),(0,1),(0,1),(0,1,2,255)):compare('frequency',[select,div3,enabled,period],lambda m:None,[('frequency',[96000000,select,div3,enabled,period])])
 for value in (0,1,2,3,4,8,9,0x80000000,0xffffffff):compare('onebit',[value],lambda m:None,[('onebit',[value])])
 for module,interface,hz,mode in itertools.product((0,4,7),(0,1,2),(0,100000,400000,1000000,48000000,48000001),(0,3,4)):
  h=v.POOL+module*v.STRIDE
  def prepare(m):m.handle(module);m.config(interface,hz,mode,BUFFER,32)
  compare('configure',[module,interface,hz,mode],prepare,[('configure',[h,CFG])])
 for words,buffer in itertools.product((0,2,8,1008,0xffffffff),(0,BUFFER,0x2007fff0)):
  def prepare(m):m.handle(4);m.config(0,1000000,0,buffer,words)
  compare('configure-buffer',[words,buffer],prepare,[('configure',[v.POOL+4*v.STRIDE,CFG])])
 for handle,config,flags,module in [(0,CFG,0,0),(v.POOL,CFG,0,0),(v.POOL,0,0x01123456,0),(v.POOL,CFG,0x03123456,0),(v.POOL,CFG,0x01123456,8)]:
  def prepare(m):m.cpu.mem_write(v.POOL,struct.pack('<II',flags,module));m.config(0,1000000)
  compare('configure-guard',[handle,config,flags,module],prepare,[('configure',[handle,config])])
 for module,interface,buffer,words,poll,occupied in itertools.product((0,4,7),(0,1,2),(0,BUFFER),(2,16),(0,4),(0,1)):
  h=v.POOL+module*v.STRIDE
  def prepare(m):
   m.handle(module);m.cpu.mem_write(h+8,bytes([interface]));m.cpu.mem_write(h+12,struct.pack('<II',buffer,words));m.cpu.mem_write(v.v.IRQ+module*0x1000+0x11c,struct.pack('<I',0x20));m.lower_status=poll
   if occupied:m.cpu.mem_write(QUEUE+module*44,struct.pack('<I',0x01000000))
  compare('enable',[module,interface,buffer,words,poll,occupied],prepare,[('enable',[h])])
 for handle in (0,v.POOL):
  compare('enable-invalid-handle',[handle],lambda m:None,[('enable',[handle])])
 for module,words,pending in itertools.product((0,4,7),(0,2,4,16),(0,1)):
  h=v.POOL+module*v.STRIDE
  def prepare(m):m.handle(module);m.cpu.mem_write(h+0x24,struct.pack('<I',pending));m.cpu.mem_write(v.v.IRQ+module*0x1000+0x22c,struct.pack('<I',BUFFER))
  compare('cq-lifecycle',[module,words,pending],prepare,[('cqinit',[h,words,BUFFER]),('cqon',[h]),('cqoff',[h])])
 for index,results in itertools.product((2,4,260),([0],[3,0],[3]*999+[0],[3]*1000)):
  def prepare(m):
   h=m.handle(4);m.cpu.mem_write(0x20000374+((index&255)<<4)+4,struct.pack('<II',h,CFG));m.cpu.mem_write(CFG,struct.pack('<II',7,8));m.retry_results=list(results)
  result=compare('retry',[index,len(results),results[-1]],prepare,[('retry',[index])]);assert result['status']==[4 if results[-1] else 0]
 for interface,poll in itertools.product((0,1),(0,4)):
  h=v.POOL+4*v.STRIDE
  def prepare(m):
   m.cpu.mem_write(h,struct.pack('<I',0));m.config(interface,1000000,0,BUFFER,32);m.cpu.mem_write(v.v.IRQ+4*0x1000+0x11c,struct.pack('<I',0x20));m.lower_status=poll
  compare('claim-configure-enable-failure-retry',[interface,poll],prepare,[('claim',[4,v.OUT]),('configure',[h,CFG]),('enable',[h]),('enable',[h]),('claim',[4,v.OUT])])
 trace={hex(pc):raw for pc,raw in machines[0].trace.items()};used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.LOCKED_SHA,original_trace=trace,distinct_original_trace_bytes=len(used),comparisons=cases,source_sha256={str(p.relative_to(v.v.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/n for n in ('context_instance.c','context_clock.c','context_queue.c','context_retry.c','verify_context_children.py')]},limits=['MMIO is mapped RAM. Power/clock/poll/delay callbacks are controlled; retry transaction results are injected only in its isolated limit-count cases.','IOM CQ adapters and reused generic427794/427878/4278c8 bodies execute native stock/source; no asynchronous command consumption or hardware DMA/timing proof.','Clock UDIV-zero models DIV_0_TRP disabled. Only stated argument grids are tested.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','cases','elf_sha256','distinct_original_trace_bytes')}))
if __name__=='__main__':main()
