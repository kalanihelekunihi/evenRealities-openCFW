#!/usr/bin/env python3
"""Actual overflow/selector/logging graph, bounded at the terminal loop."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_CODE
from unicorn.arm_const import *
from verify_logger_pipeline import RANGES,NATIVE
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(stock,candidate,syms,baseline):
 receipt=BASE/'board/stack-overflow-verification.json';receipt.unlink(missing_ok=True);states={};hooks=[];comparisons=0;accepted=0;dequeues=0
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,4096)
  except UcError:pass
 source_entry=syms['vApplicationStackOverflowHook']&~1;source_code=bytes(candidate.mem_read(source_entry,128));offset=next(i for i in range(0,128,2) if source_code[i:i+2]==b'\xfe\xe7');source_terminal=source_entry+offset
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def hook(u,a,size,user):
  f=states[id(u)]
  if a==(0x95c42 if u is stock else source_terminal):f['terminal']=True;u.emu_stop();return
  if a==(0x796a8 if u is stock else syms['nrf_log_frontend_dequeue']&~1):f['dequeues']+=1
  if f['pending'] and a==f['pending'][0]:
   _,payload=f['pending'];done=u.reg_read(UC_ARM_REG_R0);assert done<=len(payload);f['rtt'].append(payload[:done]);f['pending']=None
  if a==(0x31a18 if u is stock else syms['SEGGER_RTT_WriteNoLock']&~1):f['pending']=(u.reg_read(UC_ARM_REG_LR)&~1,bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2))))
 for u in (stock,candidate):hooks.append((u,u.hook_add(UC_HOOK_CODE,hook)))
 def call(name,args):
  for u in (stock,candidate):
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):u.reg_write(reg,value)
   u.emu_start((NATIVE[name] if u is stock else syms[name])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100
 try:
  for mode,deferred,clock,selector,primask,name in itertools.product(range(8),(0,1),(0,1),(0,1),(0,1),('timer','task_name_longer_than_sixteen')):
   for u in (stock,candidate):
    u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0xe000e000,bytes(4096));u.reg_write(UC_ARM_REG_CONTROL,0);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_BASEPRI,0);u.mem_write(0x20007a18,bytes(4));states[id(u)]={'terminal':False,'dequeues':0,'pending':None,'rtt':[]};u.mem_write(0x20003000,struct.pack('<9I',0,0,0,0,(0x5639c if u is stock else syms['r1_native_rtc_snapshot'])|1,0,0,0,0));u.mem_write(0x20003100,struct.pack('<6I',0xc07a0,0x20003000,0,0,0,0));u.mem_write(0x20007690,struct.pack('<I',0x20003100));u.mem_write(0x20006828,struct.pack('<I',0x99c8c));u.mem_write(0x20007380,struct.pack('<I',1700000000));u.mem_write(0x20016acc,struct.pack('<hB',0,1))
   call('nrf_log_init',(0,32768));call('nrf_log_default_backends_init',())
   results=[]
   for u in (stock,candidate):
    f=states[id(u)];u.mem_write(0x2002d60c,bytes([0 if deferred else 1]));u.mem_write(0x200068ec,bytes([mode]));u.mem_write(0x2000653c,bytes([clock]));u.mem_write(0x20005000,bytes(112));u.mem_write(0x20005034,name.encode()+b'\0');u.mem_write(0x20005030,struct.pack('<I',0x20005200));u.mem_write(0x20005200,bytes(16));u.mem_write(0x2000781c,struct.pack('<I',0x20005000));u.mem_write(0x20007850,bytes(4));u.reg_write(UC_ARM_REG_IPSR,14 if selector else 0);u.reg_write(UC_ARM_REG_BASEPRI,64 if selector else 0);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,0x20005034);entry=(0x965ac if selector else 0x95bfc) if u is stock else syms['vTaskSwitchContext' if selector else 'vApplicationStackOverflowHook'];u.emu_start(entry|1,0x20000100,count=3000000);assert f['terminal'] and f['pending'] is None and f['dequeues']>=1;assert u.reg_read(UC_ARM_REG_BASEPRI)==(64 if selector else 0) and u.reg_read(UC_ARM_REG_PRIMASK)==primask
    extra=[(0x200068ec,4),(0x200068f4,16),(0x20016bc8,8192),(0x20018bc8,236),(0x20005000,112)];results.append((f['rtt'],f['dequeues'],[bytes(u.mem_read(a,z)) for a,z in RANGES+extra],u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK)))
   assert results[0]==results[1],(mode,deferred,clock,selector,primask,name,[(x[:2],x[-2:]) for x in results],[(i,hex((RANGES+extra)[i][0])) for i,(a,b) in enumerate(zip(results[0][2],results[1][2])) if a!=b]);comparisons+=1;accepted+=sum(map(len,results[0][0]));dequeues+=results[0][1]
 finally:
  for u,h in hooks:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 receipt.write_text(json.dumps(dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),overflow_driver_sha256=sha(Path(__file__)),overflow_report_sha256=sha(BASE/'native-stack-overflow/report.json'),comparisons=comparisons,accepted_rtt_bytes_per_implementation=accepted,dequeue_calls_per_implementation=dequeues,provider_interception=False,scope='Actual direct/selector overflow callback, structured cache/clock and Nordic init/std1/dequeue/formatter/pool/RTT graph; all modes, deferred/immediate, clock flag, names, masks; terminal loop boundary',limitations=['Clock/RTC registration is a controlled fixture binding to actual C snapshot/default-clock providers. Memory-backed RTT writes are not host delivery. Overflow is terminal so ABI return restoration is not claimed. No physical task failure/concurrency or image byte identity proof.']),indent=2)+'\n');print(comparisons,'overflow graph comparisons;',accepted,'accepted RTT bytes;',dequeues,'dequeues; no provider interception')
