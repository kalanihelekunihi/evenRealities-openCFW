#!/usr/bin/env python3
"""Compare bounded NOR command wrappers against the locked stock instructions."""
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
spec=importlib.util.spec_from_file_location('bootverify',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ENTRY={'reset':0x42052a,'readmode':0x420f10,'timing':0x4201ba}
v.ENTRIES.update(ENTRY)
HANDLE_SLOT=0x200270dc;DEVICE_SLOT=0x200270d8;DEVICE=0x20026fd0;CONFIG=0x2000020c;TIMING=0x2000023c;HANDLE=0x20006000
PROVIDERS={0x4262e0:'transfer',0x415fae:'transfer_error',0x41f9d8:'delay',0x4176ce:'log',0x4250f0:'disable',0x424be4:'configure',0x425066:'enable',0x4251c0:'control',0x41ff34:'latency',0x41fadc:'publish',0x420002:'scan',0x426c10:'clear',0x415ff4:'clear'}

class M(v.Machine):
 def __init__(self,source=False,segments=(),symbols=None):
  super().__init__(source,segments,symbols);self.fixture={};self.events=[];self.transfer_ix=0
  if source:
   for k,n in [('reset','opencfw_boot_reset_commands'),('readmode','opencfw_boot_read_mode'),('timing','opencfw_boot_timing_apply')]:self.symbols['opencfw_boot_'+k]=self.symbols[n]
 def code(self,uc,pc,size,user):
  kind=PROVIDERS.get(pc)
  if kind is None:super().code(uc,pc,size,user);return
  r0,r1,r2,r3=self.args(); f=self.fixture
  if kind=='transfer':
   raw=bytes(uc.mem_read(r1,24)); ix=self.transfer_ix; statuses=f.get('transfer_statuses',[]);st=statuses[ix] if ix<len(statuses) else f.get('transfer_status',0);self.transfer_ix+=1
   self.events.append(['transfer',r0,r2,raw[:20].hex(),st]);self.ret(st)
  elif kind=='transfer_error':
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);self.events.append(['transfer_error',r0,r1,r2,r3,self.u(sp)]);self.ret()
  elif kind=='delay':self.events.append(['delay',r0]);self.ret()
  elif kind=='log':
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);vals=[self.u(sp+i*4) for i in range(0,10)]
   # Record the fixed ABI, source strings, line, format pointer, and six scalar varargs where present.
   def cstr(p):
    out=bytearray()
    for i in range(160):
     b=uc.mem_read(p+i,1)[0]
     if not b:break
     out.append(b)
    return out.decode(errors='replace')
   ev=['log',r0,cstr(r1),cstr(r2),cstr(r3),vals[0],cstr(vals[1])]
   if 'Time scan' in ev[-1]:ev.append(vals[2:8])
   self.events.append(ev);self.ret()
  elif kind in ('disable','enable'):
   st=f.get(kind+'_status',0);self.events.append([kind,r0,st]);self.ret(st)
  elif kind=='configure':
   st=f.get('configure_status',0);self.events.append([kind,r0,bytes(uc.mem_read(r1,32)).hex(),st]);self.ret(st)
  elif kind=='control':
   st=f.get('control_status',0);self.events.append([kind,r0,r1,uc.mem_read(r2,1)[0],st]);self.ret(st)
  elif kind=='latency':self.events.append([kind,r0]);self.ret(0)
  elif kind=='publish':self.events.append([kind,r0,r1]);self.ret(0)
  elif kind=='scan':
   st=f.get('scan_status',0);data=bytes.fromhex(f.get('scan_hex','010203040506'))
   if st==0:uc.mem_write(r0,data[:6])
   self.events.append([kind,st,data.hex()]);self.ret(st)
  elif kind=='clear':
   # These stock helpers are memset(dst, byte, length); actual instructions are immaterial to tested wrapper.
   uc.mem_write(r0,bytes([r1&255])*r2);self.ret(r0)
 def setup(self,fixture):
  self.fixture=fixture;self.events=[];self.transfer_ix=0
  self.w(HANDLE_SLOT,HANDLE);self.w(DEVICE_SLOT,DEVICE);self.w(DEVICE,0x12345678)
  self.cpu.mem_write(CONFIG,bytes(range(32)));self.cpu.mem_write(TIMING,bytes.fromhex(fixture.get('initial_timing','aabbccddeeff1122')))
 def invoke(self,name,args,fixture):
  self.setup(fixture)
  # Match the entry-SP-relative bytes that stock's local tail reads as bytes 6-7.
  self.cpu.mem_write(v.SP-10,bytes.fromhex(fixture.get('caller_stack_tail','a55a')))
  res=self.run(name,args);res['events']=self.events
  res['timing_bytes']=bytes(self.cpu.mem_read(TIMING,8)).hex()
  return res

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={}
 rows={'reset':[{'transfer_statuses':[0,0]},{'transfer_statuses':[5,0]},{'transfer_statuses':[0,6]},{'transfer_statuses':[5,6]}],
       'readmode':[{}, {'disable_status':2},{'configure_status':5},{'enable_status':7},{'control_status':9}],
       'timing':[{'scan_status':0,'scan_hex':'112233445566','caller_stack_tail':'a55a'},
                 {'scan_status':0,'scan_hex':'112233445566','caller_stack_tail':'3cc3'},
                 {'scan_status':1,'caller_stack_tail':'a55a'},
                 {'scan_status':1,'caller_stack_tail':'3cc3'}]}
 for name,fixtures in rows.items():
  for f in fixtures:
   ms=[M(),M(True,segs,syms)];results=[m.invoke(name,[],f) for m in ms]
   # Decompiled ABI reports a spurious 64-bit return for void routines; compare observable effects.
   left={k:results[0][k] for k in ('events','timing_bytes')};right={k:results[1][k] for k in ('events','timing_bytes')}
   assert left==right,(name,f,left,right)
   trace.update(ms[0].trace);cases.append({'function':name,'fixture':f,'observed':left})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 out={'status':'PASS','cases':len(cases),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'distinct_original_instruction_bytes':len(used),'original_trace':trace,'comparisons':cases,'limits':['MSPI blocking transfer, transfer error formatting, delays, HAL configure/control, device publication, logger, and scan algorithm are explicit synthetic providers.','Reset delay arguments are observed as raw values 1 and 50; units are not inferred.','The timing success path copies eight bytes from a six-byte cleared scan result in stock instructions; the fixtures explicitly seed the two untouched caller-stack bytes with a55a and3cc3 and compare the full eight-byte copy. Their hardware values and their equivalence across differently compiled callers remain unverified.','No physical hardware, flash, MSPI registers, timing scan, or logging sink is exercised.']}
 out['source_sha256']={p.name:v.sha(p) for p in [HERE/'verify_nor_commands.py',ROOT/'g2/components/bootloader/nor_commands/nor_commands.c',ROOT/'g2/components/bootloader/nor_commands/nor_commands.h',ROOT/'g2/components/bootloader/nor_commands/module.ld',ROOT/'g2/components/bootloader/nor_commands/nor_timing_wrapper.S']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','cases','distinct_original_instruction_bytes')},indent=2))
if __name__=='__main__':main()
