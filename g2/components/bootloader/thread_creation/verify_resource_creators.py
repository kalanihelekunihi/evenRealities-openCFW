#!/usr/bin/env python3
"""Constructor control/layout comparison with explicit allocator/kernel cuts."""
import argparse,importlib.util,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('base',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(timer_new=0x4163b2,mutex_new=0x416610,timer_id_get=0x4196c2,timer_callback_dispatcher=0x41639a)
ATTR=0x20031200;CB=0x20031400;POOL=0x20032000
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.events=[];self.context=0;self.alloc=POOL;self.alloc_calls=0;self.fail_alloc=False
 def code(self,uc,pc,size,user):
  if pc in (0x41b3e4,0x41b3fc):self.events.append(['critical',hex(pc)]);self.ret();return
  if pc==0x08002500:self.events.append(['callback',self.args()[0]]);self.ret(0xdead);return
  if pc==0x41602a:self.ret(self.context);return
  if pc==0x419730:
   n=self.args()[0];self.alloc_calls+=1;result=0 if self.fail_alloc is True or self.fail_alloc==self.alloc_calls else self.alloc;self.alloc+=64;self.events.append(['allocate',n,result]);self.ret(result);return
  if pc==0x419830:self.events.append(['free',self.args()[0]]);self.ret();return
  if pc==0x419684:self.events.append(['timer-initialize']);self.ret();return
  if pc in (0x419d08,0x419c9c):
   count,size,storage,cb=self.args();type_word=self.u(uc.reg_read(v.a.UC_ARM_REG_SP)) if pc==0x419c9c else storage
   result=cb if pc==0x419c9c else POOL+256
   self.events.append(['queue-create',hex(pc),count,size,type_word,result]);self.ret(result);return
  if pc==0x419ec0:
   self.events.append(['queue-put',self.args()]);self.ret(1);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={}
 fixtures=[]
 for callback,kind,cb,size,context,fail in itertools.product([0,0x42e6f5],[0,1,256],[0,CB],[0,43,44,51,52],[0,1],[False,True]):
  fixtures.append(('timer_new',[callback,kind,0xabcdef,ATTR],dict(cb=cb,size=size,context=context,fail=fail,bits=0)))
 for bits,cb,size,context in itertools.product([0,1,8,9,0x100],[0,CB],[0,79,80],[0,1]):
  fixtures.append(('mutex_new',[ATTR],dict(cb=cb,size=size,context=context,fail=False,bits=bits)))
 fixtures.extend([('timer_new',[0x42e6f5,0,0,0],dict(cb=0,size=0,context=0,fail=2,bits=0)),('timer_new',[0x42e6f5,0,0,ATTR],dict(cb=0,size=0,context=0,fail=2,bits=0))])
 fixtures.extend([('timer_new',[0x42e6f5,0,0,0],dict(cb=0,size=0,context=0,fail=False,bits=0)),('mutex_new',[0],dict(cb=0,size=0,context=0,fail=False,bits=0))])
 for tagged in [0,1,CB+44,(CB+44)|1]:
  fixtures.append(('timer_callback_dispatcher',[CB],dict(cb=0,size=0,context=0,fail=False,bits=0,tagged=tagged)))
  fixtures.append(('timer_id_get',[CB],dict(cb=0,size=0,context=0,fail=False,bits=0,tagged=tagged)))
 for entry,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];results=[]
  for m in pair:
   m.context=f['context'];m.fail_alloc=f['fail'];m.cpu.mem_write(CB,b'\xcc'*80);m.cpu.mem_write(POOL,b'\xcc'*512)
   for i,val in enumerate([0x433b50,f['bits'],f['cb'],f['size']]):m.w(ATTR+i*4,val)
   if 'tagged' in f:m.w(CB+28,f['tagged']);m.w(CB+44,0x08002501);m.w(CB+48,0xfedcba98)
   m.cpu.reg_write(v.a.UC_ARM_REG_R7,0x56789abc)
   ret=m.run(entry,args)['return'];results.append(dict(return_value=ret,events=m.events,cb=bytes(m.cpu.mem_read(CB,80)).hex(),pool=bytes(m.cpu.mem_read(POOL,512)).hex()))
  assert results[0]==results[1],(entry,args,f,results)
  trace.update(pair[0].trace);cases.append(dict(entry=entry,fixture=f,result=results[0]))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str((HERE/n).relative_to(ROOT)):v.sha(HERE/n) for n in ['resource_creators.c','resource_creators.h','resource_creators_module.ld','verify_resource_creators.py']},original_trace=trace,comparisons=cases,limits=['Actual timer/mutex wrapper and local timer/mutex constructor bodies execute. Allocator/free, timer-service initialization, queue factories and queue-put are explicit controlled providers in this direct profile.','Synthetic aligned storage and allocator success/failure; no physical timer callback execution, peripheral behavior or byte identity. Normal path lower providers are exercised separately by the integrated scheduler fixture.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
