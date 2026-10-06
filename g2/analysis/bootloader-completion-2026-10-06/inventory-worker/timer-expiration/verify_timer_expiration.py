#!/usr/bin/env python3
"""Bounded original/source checks for 0x419406 and 0x41965c.

Timer auto-reload at 0x4193de and C timer callbacks are explicit provider cuts;
list unlink executes as original/source code. All RAM, lists and callbacks are
synthetic. No physical timer, scheduler or hardware behavior is modeled.
"""
import argparse, importlib.util, json, struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
LIST_A=0x20030000;LIST_B=0x20030040
T0=0x20030400;T1=0x20030440;T2=0x20030480
CB0=0x2003c000;CB1=0x2003c004;CB2=0x2003c008
STOP=0x08000000;SP=0x2002f000

class Machine(v.Machine):
 def __init__(self,source=False,segments=(),symbols=None):
  super().__init__(source,segments,symbols)
 def code(self,uc,pc,size,user):
  if pc in (CB0,CB1,CB2):
   self.events.append(['callback',hex(pc),self.args()[0]])
   self.ret();return
  super().code(uc,pc,size,user)
 def call(self,entry,args):
  sym={'expire':'opencfw_bl_timer_expire','rollover':'opencfw_bl_timer_rollover'}[entry]
  pc=(self.symbols[sym]&~1) if self.source else {'expire':0x419406,'rollover':0x41965c}[entry]
  for reg,value in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],args+[0]*4):self.cpu.reg_write(reg,value)
  self.cpu.reg_write(a.UC_ARM_REG_SP,SP);self.cpu.reg_write(a.UC_ARM_REG_LR,STOP|1)
  self.finished=False;self.cpu.emu_start(pc|1,STOP+2,count=100000)
 def word(self,address,value=None):
  if value is not None:self.w(address,value)
  return self.u(address)

def init_list(m,addr):
 sentinel=addr+8
 for off,val in [(0,0),(4,sentinel),(8,0xffffffff),(12,sentinel),(16,sentinel)]:m.w(addr+off,val)
def add_timer(m,addr,deadline,flags,cb,list_addr,period=10):
 sentinel=list_addr+8;node=addr+4
 # Singly populated list fixture; stock list insertion layout is item+4.
 for off,val in [(0,deadline),(4,sentinel),(8,sentinel),(12,addr),(16,list_addr)]:m.w(node+off,val)
 m.w(sentinel+4,node);m.w(sentinel+8,node)
 m.w(list_addr,1);m.w(list_addr+4,sentinel)
 m.w(addr+0x28,flags);m.w(addr+0x20,cb|1);m.w(addr+0x18,period)
 m.w(0x20027178,list_addr)

def snapshot(m):
 return {'events':m.events,'globals':bytes(m.cpu.mem_read(0x20027178,8)).hex(),
  'lists':bytes(m.cpu.mem_read(LIST_A,0x50)).hex(),
  'timers':bytes(m.cpu.mem_read(T0,0xc0)).hex()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(args.elf)
 pair=lambda:[Machine(),Machine(True,segments,symbols)]
 trace={};cases=[]
 fixtures=[]
 for flags in [0,1,2,3,4,5,0x84,0xff]:
  fixtures.append(('expire',[100,131] if flags&4 else [0x12345678,0x23456789],flags))
 fixtures += [('rollover',[],None)]
 for entry,callargs,flags in fixtures:
  machines=pair()
  for m in machines:
   init_list(m,LIST_A);init_list(m,LIST_B)
   if entry=='expire':
    add_timer(m,T0,callargs[0],flags,CB0,LIST_A)
   else:
    add_timer(m,T0,0xfffffff0,0x04,CB0,LIST_A,8)
    # Append second active item exactly as a sorted-list node.
    n=T1+4;s=LIST_A+8;prev=T0+4
    for off,val in [(0,0xfffffff8),(4,s),(8,prev),(12,T1),(16,LIST_A)]:m.w(n+off,val)
    m.w(prev+4,n);m.w(s+8,n);m.w(LIST_A,2)
    m.w(T1+0x18,8);m.w(T1+0x28,0);m.w(T1+0x20,CB1|1)
    add_timer(m,T2,0xdeadbeef,0,CB2,LIST_B,8)
    m.w(0x20027178,LIST_A);m.w(0x2002717c,LIST_B)
   m.events=[]
  try:
   machines[0].call(entry,callargs);machines[1].call(entry,callargs)
  except Exception:
   print('timer fixture failure',entry,flags,[(m.source,hex(m.cpu.reg_read(a.UC_ARM_REG_PC)),m.args()) for m in machines]);raise
  out=[snapshot(m) for m in machines]
  assert out[0]==out[1],(entry,flags,out)
  trace.update(machines[0].trace)
  cases.append({'entry':entry,'args':callargs,'flags':flags,'state':out[0]})
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 sources=[ROOT/'g2/components/bootloader/thread_creation/timer_expiration.c',ROOT/'g2/components/bootloader/thread_creation/timer_expiration.h',ROOT/'g2/components/bootloader/thread_creation/timer_commands.c',ROOT/'g2/components/bootloader/thread_creation/timer_commands.h',ROOT/'g2/components/bootloader/thread_creation/timer_wait.c',ROOT/'g2/components/bootloader/thread_creation/timer_wait.h',HERE/'timer_expiration_test.ld',HERE/'verify_timer_expiration.py']
 result={'status':'PASS','cases':len(cases),'distinct_original_trace_bytes':len(used),'original_sha256':v.SHA,'elf_sha256':v.sha(args.elf),'source_sha256':{str(p.relative_to(ROOT)):v.sha(p) for p in sources},'original_trace':trace,'comparisons':cases,'limits':['The source and original execute periodic reinsertion at 0x4193de; timer callback pointers remain explicit synthetic callbacks receiving timer*. Synthetic queue/tick/list context only.','No task scheduling, physical timer/interrupt behavior, concurrent list mutation, or callback body is modeled.','M4-compatible source ELF, not a whole bootloader or byte-equality claim.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
