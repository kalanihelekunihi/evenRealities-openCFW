#!/usr/bin/env python3
"""Differential leaves for stock 0x423e14 and 0x427c12."""
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location("bootverify",ROOT/"g2/components/bootloader/update_core/verify.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(mode_flags=0x423e14,queue_post=0x427c12,queue_release=0x4279be)
HANDLE,Q,OPS,BUFFER=0x20006000,0x20008000,0x20009000,0x20010000
REGS,REGS_SIZE=0x40000000,0x10000

class Machine(v.Machine):
 def __init__(self,source=False,segments=(),symbols=None):
  super().__init__(source,segments,symbols);self.cpu.mem_map(REGS,REGS_SIZE)
  if source:
   self.symbols["opencfw_boot_mode_flags"]=self.symbols["opencfw_bl_control_stage_two_flags"]
   self.symbols["opencfw_boot_queue_post"]=self.symbols["opencfw_provider_427c12"]
   self.symbols["opencfw_boot_queue_release"]=self.symbols["opencfw_provider_4279be"]
 def w(self,p,x):self.cpu.mem_write(p,struct.pack("<I",x&0xffffffff))
 def setup_flags(self,mode,flags):
  h=bytearray(0x8d0);struct.pack_into("<I",h,0x838,mode);self.cpu.mem_write(HANDLE,bytes(h));return [HANDLE,flags]
 def setup_post(self,*,valid=True,write=0,producer=8,queue_base=0x20010000,tag=0x1234,doorbell=0x40000040,index=0x40000080,kind=1,sequence=0):
  q=[0x01cdcdcd if valid else 0,queue_base,0x20020000,0,BUFFER+write,BUFFER+producer,0,0,sequence,OPS,0]
  self.cpu.mem_write(Q,struct.pack("<11I",*q));self.cpu.mem_write(OPS,struct.pack("<10I",0,tag,index,doorbell,0,0,0,0,0,0));self.cpu.mem_write(BUFFER,bytes(0x200));self.w(index,0xabcd);self.w(doorbell,0x5555)
  return [Q,kind]
 def setup_release(self,*,valid=True,write=0,producer=8,sequence=1):
  q=[0x01cdcdcd if valid else 0,BUFFER,0x20020000,0,BUFFER+write,BUFFER+producer,0,0,sequence,OPS,0]
  self.cpu.mem_write(Q,struct.pack("<11I",*q));return [Q]
 def state(self,mode=False):
  if mode:return bytes(self.cpu.mem_read(HANDLE,0x8d0))
  return {"queue":bytes(self.cpu.mem_read(Q,44)),"buffer":bytes(self.cpu.mem_read(BUFFER,0x200)),"ops":bytes(self.cpu.mem_read(OPS,40)),"registers":bytes(self.cpu.mem_read(REGS,0x100))}

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--elf",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);cases=[];failures=[];trace={}
 def run(name,args_fn,state_kind,fixture):
  pair=[Machine(),Machine(True,segments,dict(symbols))];args=[args_fn(m) for m in pair]
  results=[m.run(name,x) for m,x in zip(pair,args)];states=[m.state(state_kind) for m in pair]
  trace.update(pair[0].trace);diff=results[0]["return"]!=results[1]["return"] or states[0]!=states[1]
  cases.append({"function":name,"fixture":fixture,"return":results[0]["return"]})
  if diff:
   delta={}
   if states[0]!=states[1]:
    keys=states[0].keys() if isinstance(states[0],dict) else []
    delta={k:[states[0][k].hex(),states[1][k].hex()] for k in keys if states[0][k]!=states[1][k]}
   failures.append({"function":name,"fixture":fixture,"returns":[x["return"] for x in results],"state_diff":delta})
 for mode in [0,1,2,3,0xffffffff]:
  for flags in [0,0x40,0x400000,0x400040,0xffffffff]:
   run("mode_flags",lambda m:m.setup_flags(mode,flags),True,{"mode":mode,"flags":flags})
 for opts in [
  {"valid":True,"write":0,"producer":8,"queue_base":0x20010000,"kind":0,"sequence":0},
  {"valid":True,"write":0,"producer":8,"queue_base":0x20080000,"kind":1,"sequence":0x12345678},
  {"valid":True,"write":0,"producer":0,"kind":0x101,"sequence":0xff},
  {"valid":False,"write":0,"producer":8},
  {"valid":True,"write":0,"producer":0},
 ]:
  for null in ([False,True] if opts.get("valid",True) else [False]):
   def setup(m,o=dict(opts),n=null):
    if n:return [0,1]
    return m.setup_post(**o)
   run("queue_post",setup,False,{**opts,"queue_null":null})
 for opts in [{"valid":True,"write":0,"producer":8,"sequence":1},{"valid":True,"write":0,"producer":0,"sequence":0},{"valid":False,"write":0,"producer":8,"sequence":1}]:
  run("queue_release",lambda m,o=dict(opts):m.setup_release(**o),False,opts)
 blob=v.BLOB.read_bytes();used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 files=[HERE/"verify_control_request_helpers.py",HERE/"Makefile",HERE/"module.ld",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_helpers.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_helpers.h"]
 out={"status":"PASS" if not failures else "FAIL","cases":len(cases),"failures":failures,"original_sha256":v.SHA,"source_elf_sha256":digest(a.elf),"source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in files},"distinct_original_instruction_bytes":len(used),"original_trace":trace,"coverage":{"mode_flags":"0x423e14","queue_post":"0x427c12","queue_release":"0x4279be"},"comparisons":cases,"limits":["All queue, descriptor, and MMIO memory is synthetic; this validates finite helper state transitions, not peripheral progress."]}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({k:out[k] for k in ("status","cases","distinct_original_instruction_bytes","coverage")},indent=2))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
