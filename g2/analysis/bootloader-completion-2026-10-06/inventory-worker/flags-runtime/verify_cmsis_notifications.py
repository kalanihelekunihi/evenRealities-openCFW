#!/usr/bin/env python3
"""Compare stock CMSIS notification wrappers with readable source in Unicorn."""
import argparse, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location('bootverify',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
TRANSFER=0x41623a;WAIT=0x4162c4;THREAD=0x20008000;OUT=0x20008100
v.ENTRIES.update({'cmsis_transfer':TRANSFER,'cmsis_wait':WAIT})
class M(v.Machine):
 def __init__(self,source=False,segs=(),syms=None):
  super().__init__(source,segs,syms);self.events=[];self.fixture={};self.tick_i=0;self.wait_i=0
  if source:
   self.symbols['opencfw_boot_cmsis_transfer']=self.symbols['opencfw_provider_41623a']
   self.symbols['opencfw_boot_cmsis_wait']=self.symbols['opencfw_provider_4162c4']
 def code(self,uc,pc,size,user):
  if pc==0x41602a:
   val=self.fixture.get('context',0);self.events.append(['context',val]);self.ret(val);return
  if pc==0x41835a:
   seq=self.fixture.get('ticks',[100]);val=seq[min(self.tick_i,len(seq)-1)];self.tick_i+=1;self.events.append(['tick',val]);self.ret(val);return
  if pc==0x418dac:
   r0,r1,r2,r3=self.args();sp=uc.reg_read(v.a.UC_ARM_REG_SP);ticks=self.u(sp)
   seq=self.fixture.get('waits',[1]);val=seq[min(self.wait_i,len(seq)-1)];self.wait_i+=1
   output=self.fixture.get('outputs',[0]);out=output[min(self.wait_i-1,len(output)-1)]
   if r3:self.w(r3,out)
   self.events.append(['notify_wait',r0,r1,r2,r3,ticks,val,out]);self.ret(val);return
  if pc==0x418e70:
   r0,r1,r2,r3=self.args();sp=uc.reg_read(v.a.UC_ARM_REG_SP);previous=self.u(sp)
   if r3==0 and previous:self.w(previous,self.fixture.get('previous',0x1234))
   self.events.append(['notify',r0,r1,r2,r3,previous]);self.ret(1);return
  if pc==0x418fe8:
   args=self.args();sp=uc.reg_read(v.a.UC_ARM_REG_SP);self.events.append(['isr_notify',*args,self.u(sp),self.u(sp+4)])
   previous=self.u(sp+4) or self.u(sp)
   if previous:self.w(previous,self.fixture.get('previous',0x1234))
   self.ret(1);return
  super().code(uc,pc,size,user)
 def run_case(self,name,args,fixture):
  self.events=[];self.fixture=fixture;self.tick_i=0;self.wait_i=0
  self.w(THREAD+0x68,0);self.w(0xe000ed04,0)
  result=self.run(name,args)
  events=[]
  for event in self.events:
   event=list(event)
   if event[0]=='notify':event[-1]=int(bool(event[-1]))
   if event[0]=='notify_wait':event[4]=int(bool(event[4]))
   if event[0]=='isr_notify':event[-2:]=[int(bool(x)) for x in event[-2:]]
   events.append(event)
  return {'r0':result['return'],'r1':self.cpu.reg_read(v.a.UC_ARM_REG_R1) if name=='cmsis_wait' else None,'events':events,
          'aircr':self.u(0xe000ed04)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 _,segs,syms=v.elf.elf_info(a.elf);rows=[
  ('cmsis_transfer',[THREAD,0x800000],[{}]),('cmsis_transfer',[0,1],[{}]),
  ('cmsis_transfer',[THREAD,0x800000],[{'context':1,'previous':0x800000}]),
  ('cmsis_wait',[0xffffff,0,60000,0],[{'waits':[1],'outputs':[0x10],'ticks':[100]}]),
  ('cmsis_wait',[3,1,0,0],[{'waits':[1],'outputs':[1]}]),
  ('cmsis_wait',[3,0,0,0],[{'waits':[1],'outputs':[0]}]),
  ('cmsis_wait',[3,0,15,0],[{'waits':[0,1],'outputs':[0,2],'ticks':[100,104,115]}]),
  ('cmsis_wait',[3,0,15,0],[{'waits':[1],'outputs':[1],'ticks':[100]}]),
  ('cmsis_wait',[0x80000000,0,5,0],[{}]),
  ('cmsis_wait',[3,0,5,0],[{'context':1}]),
 ]
 cases=[]
 for name,args,fixtures in rows:
  for fixture in fixtures:
   ms=[M(),M(True,segs,syms)];results=[m.run_case(name,args,fixture) for m in ms]
   assert results[0]==results[1],(name,args,fixture,results)
   cases.append({'entry':name,'arguments':args,'fixture':fixture,'result':results[0]})
 out={'status':'PASS','cases':len(cases),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'source_sha256':{p.name:v.sha(p) for p in [HERE/'verify_cmsis_notifications.py',ROOT/'g2/components/bootloader/flags_runtime/cmsis_notifications.c',ROOT/'g2/components/bootloader/flags_runtime/flags_runtime.h',ROOT/'g2/components/bootloader/flags_runtime/module.ld']},'comparisons':cases,
      'limits':['The 0x41623a ISR path is observed only through an injected 0x418fe8 provider; no ISR behavior is synthesized.','Clock samples and notification wake results are controlled fixtures; timeout values remain raw and no tick unit is inferred.','The fourth argument to 0x4162c4 is preserved in the ABI but stock body does not consume it.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'cases':out['cases']},indent=2))
if __name__=='__main__':main()
