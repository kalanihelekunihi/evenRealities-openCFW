#!/usr/bin/env python3
"""Semaphore wrapper/counting/failure-free differential with controlled factories."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
spec=importlib.util.spec_from_file_location('leaf',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ATTR,CB,DYNAMIC=0x20004000,0x20005000,0x20006000
CALLS={'opencfw_bl_context_guard':(0x41602a,'guard'),'opencfw_bl_kernel_queue_create_dynamic':(0x419d08,'dynamic'),'opencfw_bl_kernel_queue_create_static':(0x419c9c,'static'),'opencfw_bl_kernel_queue_put_blocking':(0x419ec0,'put'),'opencfw_bl_rtos_free':(0x419830,'free')}
class Machine(v.Machine):
 def __init__(self,source,segments,symbols):
  super().__init__(source,segments,symbols);self.cuts={(symbols[n]&~1 if source else pc):label for n,(pc,label) in CALLS.items()}
 def code(self,uc,pc,size,user):
  if pc in self.cuts:
   label=self.cuts[pc];args=[uc.reg_read(r) for r in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3]]
   if label=='guard':args=[];result=self.guard
   elif label in ['dynamic','static']:
    if label=='static':args.append(struct.unpack('<I',uc.mem_read(uc.reg_read(a.UC_ARM_REG_SP),4))[0]);result=args[3] if self.factory else 0
    else:args=args[:3];result=DYNAMIC if self.factory else 0
    if result:uc.mem_write(result+0x46,bytes([1 if label=='static' else 0]))
   elif label=='put':result=self.put
   else:args=args[:1];result=0
   self.events.append([label,*args,result]);uc.reg_write(a.UC_ARM_REG_R0,result);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def run(self,maximum,initial,attr,storage,size,guard,factory,put):
  self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000);self.events=[];self.guard=guard;self.factory=factory;self.put=put;self.done=False;self.cpu.mem_write(CB,b'\xcc'*80);self.cpu.mem_write(DYNAMIC,b'\xcc'*80);self.cpu.mem_write(ATTR,struct.pack('<4I',0x433b50,0xdeadbeef,storage,size))
  for reg,val in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2],[maximum,initial,ATTR if attr else 0]):self.cpu.reg_write(reg,val)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1);pc=self.symbols['opencfw_boot_semaphore_create'] if self.source else 0x416763;
  try:self.cpu.emu_start(pc|1,v.STOP+2,count=500)
  except Exception as error:raise AssertionError((self.source,maximum,initial,attr,storage,size,guard,factory,put,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)),self.events)) from error
  assert self.done
  return dict(result=self.cpu.reg_read(a.UC_ARM_REG_R0),events=self.events,static_bytes=bytes(self.cpu.mem_read(CB,80)).hex(),dynamic_bytes=bytes(self.cpu.mem_read(DYNAMIC,80)).hex())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest()==v.LOCKED_SHA;_,segs,syms=v.elf.elf_info(args.elf);machines=[Machine(False,segs,syms),Machine(True,segs,syms)];cases=[]
 for maximum,initial,attribute,guard,factory,put in itertools.product([0,1,2,0xffffffff],[0,1,2,0xffffffff],[(False,0,0),(True,0,0),(True,0,80),(True,CB,0),(True,CB,79),(True,CB,80),(True,CB,81)],[0,1],[False,True],[0,1,2]):
  attr,storage,size=attribute;params=[maximum,initial,attr,storage,size,guard,factory,put];observations=[m.run(*params) for m in machines];assert observations[0]==observations[1],(params,observations);cases.append(dict(parameters=params,observation=observations[0]))
 trace={hex(pc):raw for pc,raw in machines[0].trace.items()};report=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,original_trace=trace,distinct_original_trace_bytes=len({int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}),comparisons=cases,limits=['Guard, dynamic/static factories, put and free callbacks controlled. Actual wrapper/counting constructors/destroy body execute.','Initial-token put failure verifies free invocation only for factory flag0; no real heap free, waiter cancellation or live scheduling proof. Native allocation is exercised separately by shared seven-case integration.','Wrapper rejects invalid maxima/initial counts; unreachable direct-constructor/null-delete fatal paths are not covered here.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
