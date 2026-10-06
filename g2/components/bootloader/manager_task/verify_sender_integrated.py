#!/usr/bin/env python3
"""Compare boot policy and bounded manager-loop observations with original bytes."""
import argparse,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(manager_task=0x42e2f8,manager_needs_update=0x42e224)
FLAGS=[0,1,0x7fffffff,0x80000000,0xffffffff,2]
TICKS=[0,59999,60000,120000,0xfffffff0,16]
class Machine(v.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.cpu.mem_map(0x7fe000,4096);self.wait_count=0;self.tick_count=0;self.put_status=0
  self.setup_noop=(self.symbols['opencfw_boot_manager_setup_noop']&~1) if self.source else 0x42e276
  self.handler=(self.symbols['opencfw_boot_manager_flags_noop']&~1) if self.source else 0x42e39a
 def cstr(self,address):
  data=bytearray()
  for i in range(512):
   byte=self.cpu.mem_read(address+i,1)[0]
   if byte==0:return data.decode('ascii')
   data.append(byte)
  raise AssertionError('unterminated string')
 def code(self,uc,pc,size,user):
  r0,r1,r2,r3=self.args()
  if pc in [0x42e254,0x42e278,0x42e2ea]:self.events.append(['setup',hex(pc)]);self.ret();return
  if pc==0x08002120:self.events.append(['dfu-log',r0,r1]);self.ret();return
  if pc==0x4168a2:
   assert r2==r3==0;self.events.append(['queue-put',r0,bytes(uc.mem_read(r1,40)).hex(),r2,r3,self.put_status]);self.ret(self.put_status);return
  if pc==0x41623a:self.events.append(['flags-set',r0,r1]);self.ret(0x55);return
  if pc==0x4176ce:
   line=self.u(uc.reg_read(v.a.UC_ARM_REG_SP))
   if line in [0x164,0x169]:self.events.append(['dfu-log',r0,line]);self.ret();return
   sp=uc.reg_read(v.a.UC_ARM_REG_SP);line=self.u(sp);fmt=self.cstr(self.u(sp+4));event=['log',r0,self.cstr(r1),self.cstr(r2),self.cstr(r3),line,fmt]
   if line==0x40:event.append(self.u(sp+8))
   self.events.append(event);self.ret();return
  if pc==0x426c10:uc.mem_write(r0,bytes([r1&255])*r2);self.ret(r0);return
  sender=(self.symbols['opencfw_boot_dfu_send']&~1) if self.source else 0x42dca2
  if pc==sender:self.events.append(['dfu-message',bytes(uc.mem_read(r0,40)).hex()])
  if pc==0x4162c4:
   assert [r0,r1,r2]==[0xffffff,0,60000]
   self.events.append(['wait',r0,r1,r2])
   if self.wait_count==len(FLAGS):self.finished=True;uc.emu_stop();return
   self.ret(FLAGS[self.wait_count]);self.wait_count+=1;return
  if pc==0x4160e8:
   self.events.append(['tick',TICKS[self.tick_count]]);self.ret(TICKS[self.tick_count]);self.tick_count+=1;return
  if pc==self.setup_noop:self.events.append(['setup-noop'])
  if pc==self.handler:self.events.append(['noop-flags-handler',r0])
  super().code(uc,pc,size,user)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);trace={};cases=[]
 for flag in [0,0x55555555]:
  for queue in [0,0x62]:
   for put_status in [0,7]:
    pair=[Machine(),Machine(True,segments,symbols)]
    for m in pair:m.w(0x7fe000,flag);m.w(0x200004d8,queue);m.w(0x200004d4,0x63);m.put_status=put_status
    results=[m.run('manager_task',[0]) for m in pair]
    assert results[0]['events']==results[1]['events'],results
    expected_message=int(flag==0x55555555).to_bytes(4,'little').hex()+'00'*36
    assert [e for e in results[0]['events'] if e[0]=='dfu-message']==[['dfu-message',expected_message]]
    assert [e for e in results[0]['events'] if e[0]=='flags-set']==([['flags-set',0x63,0x400000]] if queue and put_status==0 else [])
    assert pair[0].tick_count==pair[1].tick_count==6
    trace.update(pair[0].trace);cases.append(dict(flag=hex(flag),queue=queue,put_status=put_status,events=results[0]['events']))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in list(HERE.iterdir())+[ROOT/'g2/components/bootloader/dfu_task'/name for name in ['context.c','context.h','task.h']] if p.is_file()},original_trace=trace,comparisons=cases,limits=['MRAM flag at7fe000 lies outside locked artifact and is synthetic input, not observed device state. Setup42e254/42e278/42e2ea, actual queue sender42dca2/source dfu_send execute; queue put4168a2, flags set41623a, logger, flag wait4162c4 and tick accessor4160e8 intercepted. Original memset426c10 modeled, source volatile zeroing executes.','Actual OTA comparator, branch,40-byte message construction, DFU sender queue-presence/put-result/flag-notification paths, manager wait-loop control flow and no-op flag handler execute. Queuehandle/threadhandle are fixture globals. Main task continues to wait even if sender returns failure. Loop bounded by seventh synthetic wait. Tick values/60000 timeout have raw tick units, no tick frequency established.','Six synthetic flag/tick pairs include return-error high-bit values and wrap. Baseline update has no external action; these observations do not validate actual scheduling, queue ownership, event delivery, timer rate or full boot.','M4 compatibility candidate, not byte-identical firmware.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
