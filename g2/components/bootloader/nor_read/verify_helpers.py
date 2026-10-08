#!/usr/bin/env python3
"""Original-instruction comparison; lower HAL, mutex, scheduler and delay cuts."""
import argparse,importlib.util,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
s=importlib.util.spec_from_file_location('v',HERE/'verify_nor_read.py');n=importlib.util.module_from_spec(s);s.loader.exec_module(n);v=n.v
ENTRIES={'lock':(0x41fe9c,'opencfw_provider_41fe9c'),'unlock':(0x41fed4,'opencfw_provider_41fed4'),'before':(0x41ff08,'opencfw_bl_nor_read_before'),'after':(0x41ff1e,'opencfw_bl_nor_read_after'),'latency':(0x41ff34,'opencfw_hal_mspi_control_latency'),'configure':(0x420e8c,'opencfw_bl_nor_read_configure'),'busy':(0x42074e,'opencfw_bl_nor_busy'),'wait':(0x4207a2,'opencfw_bl_nor_wait'),'delay':(0x4207f4,'opencfw_bl_nor_read_delay')}
v.ENTRIES.update({k:a for k,(a,_) in ENTRIES.items()})
class Machine(v.Machine):
 def __init__(self,*a,fixture=None,native_kernel=False,**kw):
  super().__init__(*a,**kw);self.fixture=fixture or {};self.polls=0;self.native_kernel=native_kernel
  self.kernel_pc=(self.symbols['opencfw_boot_kernel_state']&~1) if self.source and native_kernel else 0x416088
  self.status_pc=(self.symbols.get('opencfw_bl_mspi_status_transfer',0x4205f5)&~1) if self.source else 0x4205f4
  self.delay_pc=(self.symbols.get('opencfw_bl_delay_raw',0x41f9e7)&~1) if self.source else 0x41f9e6
  if self.source:
   for name,(_,symbol) in ENTRIES.items():
    if symbol in self.symbols:self.symbols['opencfw_boot_'+name]=self.symbols[symbol]
 def code(self,uc,pc,size,user):
  a=self.args();f=self.fixture
  if pc in [0x4166aa,0x416710,0x41fe28,0x41fe48,self.delay_pc,0x416378]:
   self.events.append([hex(0x41f9e6 if pc==self.delay_pc else pc),a[0]]+([a[1]] if pc==0x4166aa else []));self.ret(f.get('mutex_status',0));return
  if pc==self.kernel_pc:
   self.events.append(['kernel-state'])
   if self.native_kernel:
    if not self.source:self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
    return
   self.ret(f.get('kernel',2));return
  if pc==0x420e08:self.events.append(['configure',bytes(uc.mem_read(a[0],24)).hex()]);self.ret(f.get('configure_status',0));return
  if pc==0x4251c0:self.events.append(['control',a[0],a[1],bytes(uc.mem_read(a[2],24 if a[1]==0x10 else 1)).hex()]);self.ret(f.get('control_status',0));return
  if pc==self.status_pc:
   assert a[:3]==[5,0,0] and self.u(uc.reg_read(v.a.UC_ARM_REG_SP))==1
   status=f.get('transfer_status',0);byte=1 if self.polls<f.get('busy_polls',0) else f.get('status_byte',0);self.polls+=1;uc.mem_write(a[3],bytes([byte]));self.events.append(['status',status,byte]);self.ret(status);return
  if pc==0x426c10:uc.mem_write(a[0],bytes([a[1]&255])*a[2]);self.ret(a[0]);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--kernel-wait-only',action='store_true');a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={}
 native_kernel=('opencfw_boot_kernel_state' in syms and syms.get('opencfw_bl_kernel_state')==syms['opencfw_boot_kernel_state'])
 def check(name,args,f):
  if a.kernel_wait_only and name not in ('wait','delay'):return
  pair=[Machine(fixture=f,native_kernel=native_kernel),Machine(True,segs,dict(syms),fixture=f,native_kernel=native_kernel)]
  for m in pair:m.w(0x200270e0,f.get('mutex',0x20003000));m.w(0x200270dc,0x20006000);m.cpu.mem_write(0x200271c5,bytes([f.get('mode',0)]));m.cpu.mem_write(0x20000224,bytes(range(24)))
  if native_kernel:
   raw=f.get('kernel',2);assert raw in (0,1,2,3)
   for m in pair:
    m.w(0x20027150,0 if raw in (0,1) else 1);m.w(0x2002716c,1 if raw==3 else 0);m.w(0x200270d4,1 if raw==1 else 0)
  got=[m.run(name,args) for m in pair];out=[{'events':r['events'],'template':bytes(m.cpu.mem_read(0x20000224,48)).hex(),'polls':m.polls,**({'return':r['return']} if name in ['busy','wait','delay'] else {})} for m,r in zip(pair,got)];assert out[0]==out[1],(name,args,f,out);trace.update(pair[0].trace);cases.append(dict(function=name,args=args,fixture=f,result=out[0]))
 for name in ['lock','unlock','before','after']:
  for mutex,status,mode in itertools.product([0,0x20003000],[0,1,0xffffffff],[0,1,2]):check(name,[],dict(mutex=mutex,mutex_status=status,mode=mode))
 for value,status in itertools.product([0,1,2,255,256,257,0xffffffff],[0,7]):check('latency',[value],dict(control_status=status))
 for config,control in itertools.product([0,1,7],[0,7]):check('configure',[],dict(configure_status=config,control_status=control))
 for status,byte in itertools.product([0,1,7],[0,1,2,255]):check('busy',[],dict(transfer_status=status,status_byte=byte))
 for count,busy,kernel in itertools.product([0,1,3],[0,1,199,200,201,203,999],[0,2,3]):check('wait',[count],dict(busy_polls=busy,kernel=kernel))
 for busy,kernel in itertools.product([0,200,201,699,700],[0,2]):check('delay',[],dict(busy_polls=busy,kernel=kernel))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))};r=dict(status='PASS',native_kernel_state_profile=native_kernel,kernel_wait_only=a.kernel_wait_only,cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'runtime_helpers.c',HERE/'runtime_helpers.h',HERE/'helpers_module.ld',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['Lower mutex/HAL/status-transfer/delay/scheduler providers controlled; exact operation ordering, status counts, config bytes and logger severity/line compared. Physical time, real mutex blocking, peripheral coherence and cancelled task behavior unproved.','Void returns incidental; only busy/wait/delay public statuses compared. Strings/format varargs not compared.','When native_kernel_state_profile is true, original416088/source kernel-state and runtime flag queries execute on the same explicit RAM flags; lower status-transfer/raw-delay/task-delay providers remain synthetic. No hardware access, byte identity or complete boot.']);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
