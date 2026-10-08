#!/usr/bin/env python3
"""Execute stock setter instructions against reconstructed C; sink is explicit."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
s=importlib.util.spec_from_file_location('base',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v);a=v.a
ENTRIES={'opencfw_bl_service_mode':0x4173ca,'opencfw_bl_service_enable':0x417438,'opencfw_bl_invalid_pin_configure':0x4174a6,'opencfw_bl_service_configure':0x417510}
CALLBACK=0x08000100
class Machine(v.Machine):
 def __init__(self,source,segs,syms):
  super().__init__(source,segs,syms);self.cpu.mem_map(0xe000e000,0x1000);self.events=[];self.reset=False
 def string(self,p):
  out=bytearray()
  while p and len(out)<512:
   c=self.cpu.mem_read(p,1)[0]
   if not c:break
   out.append(c);p+=1
  return out.decode()
 def code(self,uc,pc,size,user):
  args=[uc.reg_read(r) for r in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3]]
  if pc==CALLBACK:
   self.events.append(['assert-callback',self.string(args[0]),self.string(args[1]),args[2]]);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc==0x4176ce:
   sp=uc.reg_read(a.UC_ARM_REG_SP);self.events.append(['logger',args[0],*[self.string(p) for p in args[1:]],self.u(sp),self.string(self.u(sp+4)),self.string(self.u(sp+8)),self.string(self.u(sp+12)),self.u(sp+16)]);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def u(self,p):return int.from_bytes(self.cpu.mem_read(p,4),'little')
 def memwrite(self,uc,access,p,size,val,user):
  if p==0xe000ed0c:self.events.append(['reset-request',val&0xffffffff]);self.reset=True;self.done=True;uc.emu_stop()
 def run(self,name,value,callback,aircr):
  self.cpu.mem_write(0x20026700,bytes([0xa5])*1280);self.cpu.mem_write(0x200270e4,struct.pack('<I',CALLBACK|1 if callback else 0));self.cpu.mem_write(0xe000ed0c,struct.pack('<I',aircr));self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000);self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1);self.cpu.reg_write(a.UC_ARM_REG_R0,value);self.cpu.reg_write(a.UC_ARM_REG_R1,0x12345678)
  self.cpu.emu_start((self.symbols[name]&~1 if self.source else ENTRIES[name])|1,v.STOP+2,count=10000);assert self.done,(name,self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
  return dict(events=self.events,reset=self.reset,region=bytes(self.cpu.mem_read(0x20026700,1280)).hex())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);x=ap.parse_args();_,segs,syms=v.elf.elf_info(x.elf);assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest()==v.LOCKED_SHA;cases=[];trace={}
 for name in ENTRIES:
  for value in [0,1,2,5,6,127,255,256,257,261,262,0xffffffff]:
   for callback in [False,True]:
    for aircr in [0,0xffffffff]:
     obs=[]
     for source in [False,True]:
      m=Machine(source,segs,syms);obs.append(m.run(name,value,callback,aircr))
      if not source:trace.update(m.trace)
     assert obs[0]==obs[1],(name,value,callback,aircr,obs);cases.append(dict(name=name,value=value,callback=callback,aircr=aircr,observation=obs[0]))
 blob=v.BLOB.read_bytes()
 for pc,raw in trace.items():assert bytes.fromhex(raw)==blob[pc-v.BASE:pc-v.BASE+len(bytes.fromhex(raw))]
 ranges={n:[p,dict(zip(ENTRIES,[0x417438,0x4174a6,0x417510,0x417570]))[n]] for n,p in ENTRIES.items()};used={p+i for p,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 out=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(x.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),body_ranges=ranges,visited_body_bytes={n:len(used&set(range(*r))) for n,r in ranges.items()},original_trace={hex(p):r for p,r in trace.items()},comparisons=cases,limits=['Logger4176ce is an injected sink; arguments and strings compare, formatter/output are not recovered by this suite.','Callback is injected and returns; post-callback invalid writes execute and retained1280-byte SRAM compares, including level255 out-of-structure format writes.','Native reset request compares AIRCR write and stops at that write. No hardware reset or repeated reset-spin behavior is certified.','Source executes only ELF segments, no original executable fallback. Source strings are reconstructed data, not imported upstream source.']);x.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','cases','elf_sha256','visited_body_bytes']}))
if __name__=='__main__':main()
