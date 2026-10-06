#!/usr/bin/env python3
"""Task control flow comparison with explicit synthetic provider boundaries."""
import argparse,importlib.util,json,struct,itertools,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.ENTRIES['dfu_task']=0x42de58
HEADER=0x20026ef8;HANDLE=0x20027174;APP=0x438000;LOG=0x08002120
class Machine(v.Machine):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.messages=[];self.got=32;self.valid=1;self.header=struct.pack('<8I',0x4000060,0,0,0,0x21,APP,0,0);self.handoff=False;self.cpu.mem_map(APP,4096);self.w(0x200004d8,0x62);self.w(APP,0x2007fb00)
 def code(self,uc,pc,size,user):
  r0,r1,r2,r3=self.args()
  if pc==0x416920:
   assert r0==0x62 and r2==0 and r3==0
   if self.messages:
    command=self.messages.pop(0);self.cpu.mem_write(r1,struct.pack('<10I',command,*([0]*9)));self.events.append(['queue',command,0]);self.ret()
   else:self.events.append(['queue',None,1]);self.ret(1)
   return
  if pc==0x42d84c:assert r0==1;self.events.append(['mode',r0]);self.ret(0x42dad8);return
  if pc==0x415484:
   assert r0==HEADER and r1==1 and r2==32 and r3==self.open_value;self.cpu.mem_write(r0,self.header[:self.got]);self.events.append(['header_read',self.got]);self.ret(self.got);return
  if pc==0x42d890:assert r0==HANDLE and r1==HEADER;self.events.append(['verify',self.valid]);self.ret(self.valid);return
  if pc==0x42dae8:assert r0==HANDLE and r1==HEADER;self.events.append(['program']);self.ret();return
  if pc==0x42de0e:self.events.append(['error_transaction_synthetic_return']);self.ret();return
  if pc==0x42ddf2:self.events.append(['runtime_enable']);self.ret();return
  if pc==0x42dc90:self.events.append(['handoff',r0]);self.handoff=True;self.finished=True;uc.emu_stop();return
  if pc==LOG:self.events.append(['log',r0,r1]);self.ret();return
  super().code(uc,pc,size,user)
 def invoke(self):
  d=self.run('dfu_task',[]);d.pop('return');d['image_header']=bytes(self.cpu.mem_read(HEADER,32)).hex();d['task_handle']=self.u(HANDLE);d['handoff']=self.handoff;return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();_,seg,sym=v.elf.elf_info(a.elf);cases=[];trace={}
 fixtures=[]
 for command in [[],[2],[0],[APP],[2,1],[1],[1,1]]:
  for stack in [0,0x2007fb00,0xa0000000]:fixtures.append({'commands':command,'stack':stack})
 for opened,got,valid,install,dest,stack in itertools.product([0,0x51],[0,3,31,32],[0,1,0x100],[0,1],[APP,0x90000000],[0,0x2007fb00]):
  fixtures.append({'commands':[1],'open':opened,'got':got,'valid':valid,'install':install,'dest':dest,'stack':stack})
 for fixture in fixtures:
  ms=[Machine(),Machine(True,seg,sym)]
  for m in ms:
   m.messages=list(fixture['commands']);m.open_value=fixture.get('open',0x51);m.got=fixture.get('got',32);m.valid=fixture.get('valid',1);m.w(APP,fixture['stack']);m.header=struct.pack('<8I',96|(fixture.get('install',1)<<26),0x12345678,0,0,0x21,fixture.get('dest',APP),0,0)
  d=[m.invoke() for m in ms];assert d[0]==d[1],(fixture,{k:[x[k] for x in d] for k in d[0] if d[0][k]!=d[1][k]});trace.update(ms[0].trace);cases.append({'fixture':fixture,'result':d[0]})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 d={'status':'PASS','cases':len(cases),'comparisons':cases,'original_trace':trace,'distinct_original_trace_bytes':len(used),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'source_sha256':{p.name:v.sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ['.c','.h','.py','.ld']},'limits':['Actual original/source task instructions execute; queue, file, mode, CRC/install, logger, runtime-enable/error/handoff functions are explicit synthetic cuts.','Error transaction is allowed to return synthetically; actual terminal/reset behavior is not proven by these fixtures.','Logger comparison severity/line only. Handoff stops at provider entry, not architectural execution.','Normal install loop and real file/TLSF integration are tested separately; this harness does not join task execution to those real providers.','Queue exhaustion fixture returns error to exit; actual scheduler/blocking/task lifecycle unproven.','Bit29 stack gate reproduced exactly; no claim it validates safe bootability or physical RAM.','No hardware, full reset/RTOS, IAR identity or source-complete payload proof.']};a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(cases),'original_bytes':len(used)},indent=2))
if __name__=='__main__':main()
