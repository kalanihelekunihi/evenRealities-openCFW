#!/usr/bin/env python3
"""Bounded control requests; exact register-write ordering against stock."""
import argparse,importlib.util,json,itertools,random
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
s=importlib.util.spec_from_file_location('v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);v.ENTRIES.update(control=0x4251c0,mixed=0x42488e)
HANDLE=0x20006000;CFG=0x20008000
class Machine(v.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.cpu.mem_map(0x40060000,0x4000);self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0x40060000,end=0x40063fff)
  if self.source:self.symbols['opencfw_boot_control']=self.symbols['opencfw_hal_mspi_control'];self.symbols['opencfw_boot_mixed']=self.symbols['opencfw_hal_mspi_pio_mixed']
 def write(self,uc,access,address,size,value,user):self.events.append(['mmio-write',hex(address),size,value])
 def code(self,uc,pc,size,user):
  if pc==0x41d1c0:self.events.append(['delay-argument',self.args()[0]]);self.ret();return
  if pc==0x08002220:raise AssertionError('request outside recovered subset')
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={};rng=random.Random(20261006)
 def check(name,request,data,module=0,handle=HANDLE,magic=0x03bebebe,configured=1,null=False):
  pair=[Machine(),Machine(True,segs,dict(syms))]
  for m in pair:m.w(HANDLE,magic);m.w(HANDLE+4,module);m.cpu.mem_write(HANDLE+8,bytes([configured,0,0,data[0]]));m.cpu.mem_write(CFG,data);m.cpu.mem_write(0x40060000,b'\xa5\x5a\xa5\xd5'*4096)
  args=[handle,request,0 if null else CFG] if name=='control' else [HANDLE];got=[m.run(name,args) for m in pair];out=[{'events':r['events'],'handle':bytes(m.cpu.mem_read(HANDLE,16)).hex(),'mmio':bytes(m.cpu.mem_read(0x40060000,0x4000)).hex(),'config':bytes(m.cpu.mem_read(CFG,16)).hex(),**({'return':r['return']} if name=='control' else {})} for m,r in zip(pair,got)];assert out[0]==out[1],(name,request,data.hex(),module,{k:[r[k] for r in out] for k in out[0] if out[0][k]!=out[1][k]});trace.update(pair[0].trace);cases.append(dict(function=name,request=request,data=data.hex(),module=module,handle=handle,magic=hex(magic),configured=configured,null=null,result={'return':out[0].get('return'),'events':out[0]['events'],'handle':out[0]['handle']}))
 for module in [0,1,2,3]:
  for data in [bytes(6),bytes([255]*6),bytes(range(6))]+[rng.randbytes(6) for _ in range(20)]:check('control',16,data,module)
  for mode in list(range(29))+[127,255]:check('control',24,bytes([mode])+bytes(5),module);check('mixed',0,bytes([mode])+bytes(5),module)
 for module,request in itertools.product(range(4),range(25)):
  for data in [bytes(16),bytes([255]*16),bytes(range(16))]+[rng.randbytes(16) for _ in range(8)]:check('control',request,data,module)
  if request!=18:check('control',request,bytes(16),module,null=True)
  if request==18:
   for base in [0,0x5fffffff,0x60000000,0x6fffffff,0x70000000,0x80000000,0x83ffffff,0x84000000,0x87ffffff,0x88000000,0x8fffffff,0x90000000,0xffffffff]:
    data=bytearray(rng.randbytes(16));data[8:12]=base.to_bytes(4,'little');check('control',request,bytes(data),module)
 for request,magic,configured,null,handle in itertools.product([16,24,41,255,272,280],[0x01bebebe,0],[0,1],[False,True],[0,HANDLE]):check('control',request,bytes(6),magic=magic,configured=configured,null=null,handle=handle)
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))};r=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'control_read.c',HERE/'control_read_module.ld',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['Validation plus requests0..24 and mixed-mode helper reconstructed here; higher accepted requests route to explicit remaining-provider cut that raises if reached. Not full HAL control closure.','Synthetic MMIO register-write addresses/width/order/value and final registers/handle/status compared. No physical device configuration or timing.','Valid module0..3 fixtures only, no module index guard claimed; void helper return is incidental.']);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
