#!/usr/bin/env python3
"""Execute original/cache-enable source; compare writes, barriers and ABI."""
import argparse, importlib.util, itertools, json
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
spec=importlib.util.spec_from_file_location('cache',Path(__file__).with_name('verify_cache_runtime.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class Machine(p.Machine):
 def __init__(self,source,segments,syms,kind):
  super().__init__(source,segments,dict(syms,opencfw_boot_cache_maintain=syms['opencfw_boot_'+kind+'cache_enable']))
  self.entry=syms['opencfw_boot_'+kind+'cache_enable'] if source else {'i':0x41e1e9,'d':0x41e267}[kind]
  self.cpu.mem_map(0xe001e000,4096)
  self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0xe001e000,end=0xe001efff)
 def invoke(self,guard,ccr,descriptor,configuration,operand):
  for address,value in [(0xe001e300,guard),(0xe000ed14,ccr),(0xe000ed80,descriptor)]:self.cpu.mem_write(address,value.to_bytes(4,'little'))
  self.cpu.mem_write(0x20000078,bytes(configuration))
  self.cpu.reg_write(a.UC_ARM_REG_R0,operand)
  self.cpu.reg_write(a.UC_ARM_REG_SP,0x2003f000);self.cpu.reg_write(a.UC_ARM_REG_LR,0x08000001)
  registers=[a.UC_ARM_REG_R4,a.UC_ARM_REG_R5,a.UC_ARM_REG_R6,a.UC_ARM_REG_R7,a.UC_ARM_REG_R8,a.UC_ARM_REG_R9,a.UC_ARM_REG_R10,a.UC_ARM_REG_R11]
  for index,register in enumerate(registers):self.cpu.reg_write(register,0x12340000+index)
  self.cpu.emu_start(self.entry,0,count=200000)
  assert self.cpu.reg_read(a.UC_ARM_REG_PC)==0x08000000
  assert self.cpu.reg_read(a.UC_ARM_REG_SP)==0x2003f000
  assert [self.cpu.reg_read(r) for r in registers]==[0x12340000+i for i in range(8)]
  return self.cpu.reg_read(a.UC_ARM_REG_R0),self.events
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 assert p.sha(p.BLOB)==p.SHA
 _,segments,syms=p.elf.elf_info(args.elf);cases=[];trace={}
 for kind,guard,ccr,descriptor,configuration,operand in itertools.product(['i','d'],[0,0x100,0x200,0x400],[0,0x10000,0x20000,0x30000],[0,(2<<13)|(1<<3),(0x200<<13)|(3<<3)],[(0,0,0),(7,7,7),(255,128,9)],[0,1,256,257,0xffffffff]):
  pair=[Machine(source,segments,syms,kind) for source in [False,True]]
  results=[m.invoke(guard,ccr,descriptor,configuration,operand) for m in pair]
  assert results[0]==results[1],(kind,guard,ccr,descriptor,configuration,operand,results)
  trace.update(pair[0].trace);cases.append(dict(kind=kind,guard=guard,ccr=ccr,descriptor=descriptor,configuration=configuration,operand=operand,result=results[0]))
 used={int(pc,16)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_instruction_bytes=len(used),original_sha256=p.SHA,elf_sha256=p.sha(args.elf),source_sha256={str(x.relative_to(p.ROOT)):p.sha(x) for x in [Path(__file__),Path(__file__).with_name('cache_enable.c'),Path(__file__).with_name('cache_enable.ld')]},comparisons=cases,original_trace=trace,limits=['Original instructions vs compiled source under synthetic SCB/control registers; barrier/write order and callee-save/SP tested. No silicon cache coherence, hardware geometry or timing proof.','Guard e001e300 bits8/9 inhibits work; clean operand uses low byte. Descriptor geometry is synthetic bounded input.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_instruction_bytes']}))
if __name__=='__main__':main()
