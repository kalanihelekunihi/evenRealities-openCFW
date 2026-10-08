#!/usr/bin/env python3
"""Original/source differential for HAL MSPI requests 26, 27, and 29."""
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location("bootverify",ROOT/"g2/components/bootloader/update_core/verify.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES["control"]=0x4251c0
HANDLE,CONFIG,Q,OPS,QDATA=0x20006000,0x20008000,0x20009000,0x2000a000,0x2000b000
MMIO,MMIO_SIZE=0x40060000,0x4000
CLKGEN,CLKGEN_SIZE=0x40004000,0x1000

class Machine(v.Machine):
 def __init__(self,source=False,segments=(),symbols=None):
  super().__init__(source,segments,symbols);self.cpu.mem_map(0,0x1000);self.cpu.mem_map(MMIO,MMIO_SIZE);self.cpu.mem_map(CLKGEN,CLKGEN_SIZE);self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=MMIO,end=MMIO+MMIO_SIZE-1);self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=CLKGEN,end=CLKGEN+CLKGEN_SIZE-1);self.calls=[];self.fixture={}
  if source:self.symbols["opencfw_boot_control"]=self.symbols["opencfw_hal_mspi_control"]
 def write(self,uc,access,address,size,value,user):self.events.append(["mmio-write",address,size,value])
 def code(self,uc,pc,size,user):
  if pc==0x41d1c0:self.calls.append(["delay",self.args()[0]]);self.ret();return
  if pc==0x422364:
   args=self.args();value=self.fixture.get("release_status",0);self.calls.append(["release",args[0],args[1],value]);self.ret(value);return
  if pc==0x4222f0:
   args=self.args();value=self.fixture.get("request_status",0);self.calls.append(["clock-request",args[0],args[1],value]);self.ret(value);return
  if pc==0x08002220:self.calls.append(["unrecovered",*self.args()]);self.ret(0xdead0001);return
  super().code(uc,pc,size,user)
 def w(self,address,value):self.cpu.mem_write(address,struct.pack("<I",value&0xffffffff))
 def setup(self,request,module=0,config=b"",null=False,null_byte=0,old_mode=1,configured=1,count=0,queue_valid=True,clock_source=4,xip=0,release_status=0,request_status=0):
  self.fixture={"release_status":release_status,"request_status":request_status}
  h=bytearray(0x8d0);struct.pack_into("<II",h,0,0x03bebebe,module);h[8]=1
  struct.pack_into("<I",h,0x18,xip);struct.pack_into("<I",h,0x20,count)
  struct.pack_into("<I",h,0x828,Q);h[0x82c]=old_mode;h[0x82d]=0;h[0x8c8]=0
  struct.pack_into("<I",h,0x82c,old_mode) # preserve byte and initialize adjacent byte
  self.cpu.mem_write(HANDLE,bytes(h));self.cpu.mem_write(CONFIG,config+bytes(max(0,32-len(config))))
  self.cpu.mem_write(0,bytes([null_byte])+bytes(0xfff))
  q=bytearray(0x40);struct.pack_into("<I",q,0,0x01cdcdcd if queue_valid else 0);struct.pack_into("<I",q,4,QDATA);struct.pack_into("<I",q,8,0x20080000);struct.pack_into("<I",q,12,QDATA);struct.pack_into("<I",q,16,QDATA);struct.pack_into("<I",q,20,QDATA);struct.pack_into("<I",q,36,OPS)
  h=bytearray(self.cpu.mem_read(HANDLE,0x8d0));h[0x8c9]=clock_source;self.cpu.mem_write(HANDLE,bytes(h))
  self.cpu.mem_write(Q,bytes(q));ops=[MMIO+0x2a0,MMIO+0x2b0,MMIO+0x2ac,MMIO+0x2b8,0,MMIO+0x104]
  self.cpu.mem_write(OPS,struct.pack("<6I",*ops));self.cpu.mem_write(QDATA,bytes(0x100));self.cpu.mem_write(MMIO,bytes(MMIO_SIZE));self.cpu.mem_write(CLKGEN,bytes(CLKGEN_SIZE))
  return [HANDLE,request,0 if null else CONFIG]
 def observed(self,result):return {"return":result["return"],"events":self.events.copy(),"calls":self.calls.copy(),"handle":bytes(self.cpu.mem_read(HANDLE,0x8d0)).hex(),"queue":bytes(self.cpu.mem_read(Q,0x40)).hex(),"ops":bytes(self.cpu.mem_read(OPS,24)).hex(),"mmio":bytes(self.cpu.mem_read(MMIO,MMIO_SIZE)).hex(),"clkgen":bytes(self.cpu.mem_read(CLKGEN,CLKGEN_SIZE)).hex(),"primask":self.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK)}

def sh(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--elf",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);cases=[];failures=[];trace={}
 def run(req,**kw):
  pair=[Machine(),Machine(True,segments,dict(symbols))];argv=[m.setup(req,**kw) for m in pair]
  try:results=[m.run("control",x) for m,x in zip(pair,argv)]
  except Exception:
   from unicorn import arm_const
   print("emulation failure",req,kw,[(m.source,hex(m.cpu.reg_read(arm_const.UC_ARM_REG_PC)),hex(m.cpu.reg_read(arm_const.UC_ARM_REG_SP))) for m in pair]);raise
  obs=[m.observed(r) for m,r in zip(pair,results)]
  diff=[k for k in obs[0] if obs[0][k]!=obs[1][k]]
  for m in pair:trace.update(m.trace)
  fixture={k:(v.hex() if isinstance(v,bytes) else v) for k,v in kw.items()}
  cases.append({"request":req,"fixture":fixture,"return":obs[0]["return"],"mmio_writes":[e for e in obs[0]["events"] if e[0]=="mmio-write"]})
  if diff:failures.append({"request":req,"fixture":fixture,"fields":diff,"returns":[x["return"] for x in obs]})
 for module in range(4):
  run(27,module=module,null=True,old_mode=2)
  run(29,module=module,config=b"\0",old_mode=1)
  run(29,module=module,config=b"\1",old_mode=0,count=0)
  run(29,module=module,config=b"\1",old_mode=0,count=1)
  run(29,module=module,config=b"\0",old_mode=2)
  run(29,module=module,config=b"\1",old_mode=2)
  run(29,module=module,config=b"\0",old_mode=1,configured=0)
  for frequency in range(0,25):
   run(26,module=module,config=bytes([frequency]),clock_source=4,xip=0)
  run(26,module=module,config=b"\x01",clock_source=5,xip=1)
  run(26,module=module,config=b"\x12",clock_source=5,xip=1)
  run(26,module=module,config=b"\x17",clock_source=5,xip=1)
  run(26,module=module,config=b"\x18",clock_source=5,xip=1)
  run(26,module=module,config=b"\xff",clock_source=5,xip=1)
  run(26,module=module,config=b"\x19",clock_source=5,xip=0)
  for null_byte in [0,1,23]:
   run(26,module=module,null=True,null_byte=null_byte,clock_source=5,xip=1)
  run(26,module=module,config=b"\x03",clock_source=4,xip=0,release_status=9)
  run(26,module=module,config=b"\x03",clock_source=4,xip=0,request_status=7)
 blob=v.BLOB.read_bytes();used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 files=[HERE/"verify_control_request_state.py",HERE/"Makefile",HERE/"module.ld",ROOT/"g2/components/bootloader/nor_mspi_init/control_read.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_remaining.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_state.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_state.h",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_clock.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_clock.h",ROOT/"g2/components/bootloader/nor_mspi_queue/queue_descriptors.c",ROOT/"g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c",ROOT/"g2/components/bootloader/nor_mspi_power/mspi_clockgen_control.c",ROOT/"g2/components/bootloader/nor_mspi_power/device_configure.c",ROOT/"g2/components/bootloader/platform_control/critical_save.S"]
 out={"status":"PASS" if not failures else "FAIL","cases":len(cases),"failures":failures,"original_sha256":v.SHA,"source_elf_sha256":sh(a.elf),"source_sha256":{str(p.relative_to(ROOT)):sh(p) for p in files},"distinct_original_instruction_bytes":len(used),"original_trace":trace,"coverage_requests":[26,27,29],"comparisons":cases,"limits":["Original 0x4251c0 executes against synthetic RAM and MMIO; no hardware accesses.","Request26 clock release/request and XIP-delay calls are explicit intercepted providers; clockgen source is compiled, and MMIO is synthetic.","Request27/request29 mode2 pause runs with status-ready synthetic MMIO; physical delay and peripheral liveness are not asserted.","Request29 queue reset uses reconstructed 0x427baa with synthetic queue operation pointers.","Request26 has no null guard. For null config, this fixture maps address zero and compares frequencies 0, 1, and 23; the target's actual address-zero contents determine behavior.","This isolated receipt validates its source alias for requests26/27/29; it does not assert the shared control_remaining.c routing has been integrated."]}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({k:out[k] for k in ("status","cases","distinct_original_instruction_bytes","coverage_requests")},indent=2))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
