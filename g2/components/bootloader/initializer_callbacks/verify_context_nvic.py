#!/usr/bin/env python3
"""Compare every low-halfword input against locked NVIC wrapper instructions.

Register backing is RAM; this compares issued writes, not NVIC state effects.
Large nonnegative halfwords target architecturally unrelated addresses, exactly
as the unchecked original does; those cases are not valid device IRQ claims.
"""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
from unicorn import arm_const as a
spec=importlib.util.spec_from_file_location('leaf',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Machine(v.Machine):
 def __init__(self,source,segments,symbols):
  super().__init__(source,segments,symbols);self.cpu.mem_map(0xe000e000,0x2000)
 def memwrite(self,uc,access,address,size,value,user):
  if 0xe000e000<=address<0xe0010000:self.writes.append([address,size,value&0xffffffff])
 def run(self,value):
  self.writes.clear();self.done=False;self.cpu.reg_write(a.UC_ARM_REG_R0,value);self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1)
  pc=self.symbols['opencfw_boot_context_nvic_enable'] if self.source else 0x430471
  self.cpu.emu_start(pc|1,v.STOP+2,count=100);assert self.done
  return self.writes.copy()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest()==v.LOCKED_SHA;_,segments,symbols=v.elf.elf_info(args.elf);ms=[Machine(False,segments,symbols),Machine(True,segments,symbols)];n=0
 for high in (0,0x12340000,0xffff0000):
  for low in range(65536):
   value=high|low;stock,source=[m.run(value) for m in ms];expected=[] if low&0x8000 else [[0xe000e100+4*(low>>5),4,1<<(low&31)]]
   assert stock==source==expected,(hex(value),stock,source,expected);n+=1
 trace={hex(pc):raw for pc,raw in ms[0].trace.items()};report=dict(status='PASS',cases=n,elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,original_entry='0x430470',original_trace=trace,distinct_original_trace_bytes=len({int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}),limits=['All65536 low-halfwords and three high-halfword patterns tested; high-halfword truncation follows original instructions.','Compare issued volatile writes, not actual NVIC W1S behavior, implemented IRQ count, asynchronous delivery or safety of invalid positive IRQ numbers.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
