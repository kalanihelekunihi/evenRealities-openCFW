#!/usr/bin/env python3
"""Original/source comparisons for control request 30 and callback."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location("extension",ROOT/"g2/analysis/bootloader-completion-2026-10-06/inventory-worker/control-request-extension/verify_control_request_extension.py")
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);v=x.v
v.ENTRIES.update(control=0x4251c0,completion=0x424978)
HANDLE,CONFIG,Q,OPS,QDATA=0x20006000,0x20008000,0x20009000,0x2000a000,0x2000b000
MMIO=0x40060000

class Machine(x.Machine):
 def __init__(self,source=False,segments=(),symbols=None):
  super().__init__(source,segments,symbols);self.clock_status=0
  if source:
   self.symbols["opencfw_boot_completion"]=self.symbols["opencfw_bl_control_request_completion"]
 def code(self,uc,pc,size,user):
  if pc in self.clock_request_pcs:
   args=self.args();self.calls.append(["clock",*args[:2],self.clock_status]);self.ret(self.clock_status);return
  super().code(uc,pc,size,user)
 def setup(self,request=30,module=0,cfg=b"\x00"+bytes(11),*,null=False,mode=1,completion_byte=0,handle_count=0,queue_valid=True,write=0,producer=0,read=0x800,sequence=4,queue_visible=True,clock_status=0):
  argv=super().setup(request,module,cfg,null_config=null,slot=0,ring=4,index=sequence)
  self.clock_status=clock_status
  h=bytearray(self.cpu.mem_read(HANDLE,0x8d0));h[0x82c]=mode;h[0x82d]=completion_byte;h[0x8c8]=0
  struct.pack_into("<I",h,0x20,handle_count);struct.pack_into("<I",h,0x828,Q)
  self.cpu.mem_write(HANDLE,bytes(h))
  base=QDATA;ops=[MMIO+0x2a0,MMIO+0x2b0,MMIO+0x2ac,MMIO+0x2b8,0,MMIO+0x104,0,0,0,0]
  q=[0x01cdcdcd if queue_valid else 0,base,0x20080000 if queue_visible else base+0x1000,base+read,base+write,base+producer,0x1000,sequence,sequence,OPS,0]
  self.cpu.mem_write(Q,struct.pack("<11I",*q));self.cpu.mem_write(OPS,struct.pack("<10I",*ops));self.cpu.mem_write(QDATA,bytes(0x1000));self.cpu.mem_write(MMIO,bytes(0x4000))
  self.put32(MMIO+0x2ac,sequence&0xff);self.put32(MMIO+0x2b0,base+read);self.put32(MMIO+0x2b8,0);self.put32(MMIO+0x104,0)
  return argv
 def observe(self,result):
  h=bytearray(self.cpu.mem_read(HANDLE,0x8d0));callback_values={0x424979}
  if self.source:callback_values.add((self.symbols["opencfw_bl_control_request_completion"]&~1)|1)
  callbacks=[]
  for off in range(0x28,0x428,4):
   value=struct.unpack_from("<I",h,off)[0]
   if value in callback_values:callbacks.append([off,value]);h[off:off+4]=bytes(4)
  return {"return":result["return"],"handle":bytes(h),"queue":bytes(self.cpu.mem_read(Q,44)),"qdata":bytes(self.cpu.mem_read(QDATA,0x100)),"ops":bytes(self.cpu.mem_read(OPS,40)),"mmio":bytes(self.cpu.mem_read(MMIO,0x4000)),"calls":self.calls.copy(),"callback":callbacks}

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--elf",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);cases=[];failures=[];trace={}
 def check(req=30,**kw):
  pair=[Machine(),Machine(True,segments,dict(symbols))];args=[m.setup(req,**kw) for m in pair]
  results=[m.run("control",argv) for m,argv in zip(pair,args)]
  obs=[m.observe(r) for m,r in zip(pair,results)]
  for m in pair:trace.update(m.trace)
  diff=[k for k in obs[0] if k!="callback" and obs[0][k]!=obs[1][k]]
  cases.append({"request":req,"fixture":{k:(v.hex() if isinstance(v,bytes) else v) for k,v in kw.items()},"return":obs[0]["return"],"stock_callback":obs[0]["callback"],"source_callback":obs[1]["callback"]})
  if diff:
   details={}
   for key in diff:
    if isinstance(obs[0][key],bytes):
     left,right=obs[0][key],obs[1][key]
     details[key]=[{"offset":i,"stock":left[i],"source":right[i]} for i in range(min(len(left),len(right))) if left[i]!=right[i]][:32]
   failures.append({"request":req,"fixture":{k:(v.hex() if isinstance(v,bytes) else v) for k,v in kw.items()},"fields":diff,"returns":[o["return"] for o in obs],"byte_differences":details})
 for module in range(4):
  check(30,module=module,null=True)
  check(30,module=module,cfg=b"\0"+bytes(11))
  check(30,module=module,cfg=b"\1"+bytes(11))
  check(30,module=module,cfg=b"\0\0\0\0\xe0"+bytes(7))
  check(30,module=module,cfg=b"\0"+bytes(7)+struct.pack("<I",0x00e0e0e0))
  check(30,module=module,cfg=b"\0"+bytes(11),mode=0)
  check(30,module=module,cfg=b"\1"+bytes(11),completion_byte=1)
  check(30,module=module,cfg=b"\1"+bytes(11),clock_status=7)
 # The asynchronous callback itself is compared at its stock and source entry.
 pair=[Machine(),Machine(True,segments,dict(symbols))];
 for m in pair:
  h=bytearray(m.cpu.mem_read(HANDLE,0x8d0));struct.pack_into("<I",h,0x830,4);struct.pack_into("<I",h,0x20,9);struct.pack_into("<I",h,4,2);m.cpu.mem_write(HANDLE,bytes(h));m.cpu.mem_write(MMIO,bytes(0x4000))
 result=[m.run("completion",[HANDLE]) for m in pair];states=[bytes(m.cpu.mem_read(HANDLE,0x8d0)) for m in pair];events=[m.events for m in pair]
 if states[0]!=states[1] or events[0]!=events[1]:failures.append({"function":"completion","fields":["state/events"]})
 for m in pair:trace.update(m.trace)
 blob=v.BLOB.read_bytes();used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 files=[HERE/"verify_control_request_transactions.py",HERE/"Makefile",HERE/"module.ld",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_transactions.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_transactions.h",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_helpers.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_helpers.h",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_state.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_clock.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_request_extension.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_read.c",ROOT/"g2/components/bootloader/nor_mspi_init/control_remaining.c",ROOT/"g2/components/bootloader/nor_mspi_queue/queue_descriptors.c",ROOT/"g2/components/bootloader/nor_mspi_queue/nor_mspi_queue.c",ROOT/"g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c",ROOT/"g2/components/bootloader/platform_control/critical_save.S",ROOT/"g2/components/bootloader/nor_mspi_init/status_poll.c",ROOT/"g2/components/bootloader/nor_mspi_power/device_configure.c"]
 out={"status":"PASS" if not failures else "FAIL","cases":len(cases)+1,"failures":failures,"original_sha256":v.SHA,"source_elf_sha256":digest(a.elf),"source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in files},"distinct_original_instruction_bytes":len(used),"original_trace":trace,"coverage_requests":[30],"comparisons":cases,"limits":["Request30 uses the pinned 0x4251c0 original dispatcher against synthetic RAM/MSPI MMIO; no hardware is accessed.","Clock request is an intercepted synthetic status provider. The queue descriptors/allocator/post/release and CQ enable bodies execute compiled source.","Callback pointers are rebased to the compiled source callback; the callback body has a separate original/source differential.","This is a request30-only isolated source provider and does not alter shared control routing; asynchronous DMA/peripheral progress remains synthetic."]}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({k:out[k] for k in ("status","cases","distinct_original_instruction_bytes","coverage_requests")},indent=2))
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
