#!/usr/bin/env python3
"""Original/source transaction differential for HAL request 34."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location("ext",ROOT/"g2/analysis/bootloader-completion-2026-10-06/inventory-worker/control-request-extension/verify_control_request_extension.py")
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);v=x.v
v.ENTRIES.update(control=0x4251c0,completion_noop=0x424976)
HANDLE,CONFIG,Q,OPS,QDATA,TUPLES,OUTPUT=0x20006000,0x20008000,0x20009000,0x2000a000,0x2000b000,0x2000c000,0x2000d000
MMIO=0x40060000

class Machine(x.Machine):
 def __init__(self,source=False,segments=(),symbols=None):
  super().__init__(source,segments,symbols);self.clock_status=0
  if source:self.symbols["opencfw_boot_completion_noop"]=self.symbols["opencfw_bl_control_request34_noop"]
 def code(self,uc,pc,size,user):
  if pc in self.clock_request_pcs:
   a=self.args();self.calls.append(["clock",*a[:2],self.clock_status]);self.ret(self.clock_status);return
  super().code(uc,pc,size,user)
 def setup(self,*,module=0,config=None,null=False,mode_state=0,mode_byte=0,pending=0,rate=0,threshold=0,queue_valid=True,read=0x800,sequence=4,visible=True,clock_status=0):
  if config is None:config={"flags":0,"value":0,"count":0,"callback":0,"context":0x55aa,"output":OUTPUT,"tuples":[0x40060020,0xabcdef01]}
  raw=bytearray(28);struct.pack_into("<7I",raw,0,config["flags"],config["value"],TUPLES,config["count"],config["callback"],config["context"],config["output"])
  argv=super().setup(34,module,bytes(raw),null_config=null,slot=0,ring=4,index=sequence)
  self.clock_status=clock_status
  h=bytearray(self.cpu.mem_read(HANDLE,0x8d0));h[0x82c]=mode_byte;h[0x8c8]=0
  struct.pack_into("<I",h,0x20,pending);struct.pack_into("<I",h,0x828,0 if null else Q)
  struct.pack_into("<I",h,0x838,mode_state);struct.pack_into("<I",h,0x858,threshold);struct.pack_into("<I",h,0x85c,rate)
  self.cpu.mem_write(HANDLE,bytes(h));self.cpu.mem_write(CONFIG,bytes(raw));self.cpu.mem_write(TUPLES,struct.pack("<2I",*config["tuples"]))
  base=QDATA;ops=[MMIO+0x2a0,MMIO+0x2b0,MMIO+0x2ac,MMIO+0x2b8,0,MMIO+0x104,0,0,0,0]
  q=[0x01cdcdcd if queue_valid else 0,base,0x20080000 if visible else base+0x1000,base+read,base,base,0x1000,sequence,sequence,OPS,0]
  self.cpu.mem_write(Q,struct.pack("<11I",*q));self.cpu.mem_write(OPS,struct.pack("<10I",*ops));self.cpu.mem_write(QDATA,bytes(0x1000));self.cpu.mem_write(MMIO,bytes(0x4000));self.put32(MMIO+0x2ac,sequence&0xff);self.put32(MMIO+0x2b0,base+read)
  self.put32(OUTPUT,0)
  return argv
 def observe(self,result):
  h=bytearray(self.cpu.mem_read(HANDLE,0x8d0));callback_values={0x424977}
  if self.source:callback_values.add((self.symbols["opencfw_bl_control_request34_noop"]&~1)|1)
  callback=[]
  for off in range(0x28,0x428,4):
   val=struct.unpack_from("<I",h,off)[0]
   if val in callback_values:callback.append([off,val]);h[off:off+4]=bytes(4)
  return {"return":result["return"],"handle":bytes(h),"queue":bytes(self.cpu.mem_read(Q,44)),"qdata":bytes(self.cpu.mem_read(QDATA,0x100)),"ops":bytes(self.cpu.mem_read(OPS,40)),"mmio":bytes(self.cpu.mem_read(MMIO,0x4000)),"output":self.get32(OUTPUT),"calls":self.calls.copy(),"callback":callback}
 def get32(self,address):return struct.unpack("<I",self.cpu.mem_read(address,4))[0]

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--elf",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);cases=[];failures=[];trace={}
 def check(**kw):
  pair=[Machine(),Machine(True,segments,dict(symbols))];args=[m.setup(**kw) for m in pair]
  results=[m.run("control",argv) for m,argv in zip(pair,args)];obs=[m.observe(r) for m,r in zip(pair,results)]
  for m in pair:trace.update(m.trace)
  diff=[k for k in obs[0] if k!="callback" and obs[0][k]!=obs[1][k]]
  cases.append({"fixture":{k:v.hex() if isinstance(v,bytes) else v for k,v in kw.items()},"return":obs[0]["return"],"stock_callback":obs[0]["callback"],"source_callback":obs[1]["callback"]})
  if diff:failures.append({"fixture":{k:v.hex() if isinstance(v,bytes) else v for k,v in kw.items()},"fields":diff,"returns":[o["return"] for o in obs]})
 for module in range(4):
  check(module=module)
  check(module=module,config={"flags":1,"value":0x1234,"count":1,"callback":0,"context":0xdeadbeef,"output":OUTPUT,"tuples":[0x40060020,0xabcdef01]})
  check(module=module,config={"flags":0,"value":0x5678,"count":2,"callback":0x12345679,"context":0x55aa,"output":0,"tuples":[0x40060020,0xabcdef01]})
 check(null=True)
 check(mode_state=1)
 check(mode_state=2,mode_byte=1)
 check(pending=0x100)
 check(queue_valid=False)
 check(clock_status=7)
 # The default callback literal is stock 0x424977 (a return-only leaf).
 pair=[Machine(),Machine(True,segments,dict(symbols))]
 results=[m.run("completion_noop",[0x20006000]) for m in pair]
 if results[0]["return"]!=results[1]["return"]:failures.append({"function":"completion-noop","returns":[r["return"] for r in results]})
 for m in pair:trace.update(m.trace)
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 files=[HERE/"verify_control_request34.py",HERE/"Makefile",HERE/"module.ld",ROOT/"g2/analysis/bootloader-completion-2026-10-06/inventory-worker/control-request-extension/verify_control_request_extension.py",ROOT/"g2/components/bootloader/nor_mspi_init/control_request34.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request34.h",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_helpers.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_helpers.h",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_state.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_clock.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_extension.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_read.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_remaining.c",ROOT/"g2/components/bootloader/nor_mspi_queue/queue_descriptors.c",ROOT/"g2/components/bootloader/nor_mspi_queue/nor_mspi_queue.c",ROOT/"g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c",ROOT/"g2/components/bootloader/platform_control/critical_save.S",ROOT/"g2/components/bootloader/nor_mspi_init/status_poll.c",ROOT/"g2/components/bootloader/nor_mspi_power/device_configure.c"]
 out={"status":"PASS" if not failures else "FAIL","cases":len(cases)+1,"failures":failures,"original_sha256":v.SHA,"source_elf_sha256":digest(a.elf),"source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in files},"distinct_original_instruction_bytes":len(used),"original_trace":trace,"coverage_requests":[34],"comparisons":cases,"limits":["Request34 runs from pinned original dispatcher 0x4251c0 against synthetic RAM/MSPI MMIO.","Clock request is intercepted; queue descriptor allocation/post/rollback and CQ enable execute source.","The stock default callback pointer 0x424977 is rebound to compiled return-only source callback; callback pointer values are normalized for request-state comparison.","No physical queue execution or peripheral progress is claimed; no shared control routing is changed."]}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({k:out[k] for k in ("status","cases","distinct_original_instruction_bytes","coverage_requests")},indent=2))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
