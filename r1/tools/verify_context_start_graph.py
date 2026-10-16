#!/usr/bin/env python3
"""Actual static idle/timer startup graph bounded before port first-context work."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(stock,candidate,syms,baseline,fixture_allow):
 real_port=True;phase="first";peer_active=False
 receipt=BASE/'board/context-start-verification.json';receipt.unlink(missing_ok=True);config=BASE/'native-task-lifecycle/configuration-evidence.json';rows=json.loads(config.read_text())['rows'];port_source=syms['vPortStartFirstTask' if real_port else 'xPortStartScheduler']&~1;fixture_allow.add(port_source);states={};handles=[];comparisons=0;workflows=0
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def code(u,a,size,user):
  op=bytes(u.mem_read(a,2))
  if (phase=='first' and op==b'\x00\xdf') or (phase in ('svc','pendsv') and op==b'\x70\x47'):states[id(u)]=True;u.emu_stop()
 def priority_read(u,access,a,size,value,user):
  if real_port and a==0xe000e400:u.mem_write(a,bytes([u.mem_read(a,1)[0]&0xe0]))
 for u in (stock,candidate):
  for address in (0x40011000,0x40000000):
   try:u.mem_map(address,0x1000)
   except UcError:pass
  try:u.mem_map(0xe000e000,0x1000)
  except UcError:pass
  handles.append((u,u.hook_add(UC_HOOK_CODE,code)));handles.append((u,u.hook_add(UC_HOOK_MEM_READ,priority_read)))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 creators={'a':0x43b8c,'f':0x46924,'g':0x46a44,'b':0x44ef0,'e':0x4509c}
 def call(name,native):
  for u in (stock,candidate):
   u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((native if u is stock else syms[name])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
 def snapshot(u,apps,started):
  arena=bytearray(u.mem_read(0x2002b258,0xb58));app_records=[]
  tasks=[(0x2002b4d0,0x2002b540,1024,0x84fe8,'r1_native_idle_task',0),(0x2002b940,0x2002b9b0,1024,0x85510,'r1_native_timer_task',53)] if started else []
  if peer_active:tasks.append((0x20001000,0x20002000,256,0x12345678,None,53))
  if apps:
   for row in rows:tasks.append((int(row['control_block'],16),int(row['stack'],16),row['stack_bytes'],int(row['task_entry'],16),row['task_symbol'],row['priority']))
  for cb,stack,size,native,symbol,priority in tasks:
   sp=word(u,cb);assert word(u,cb+44)==priority and word(u,cb+84)==size//4 and bytes(u.mem_read(cb+104,8))==bytes((0,0,0,0,0,2,0,0));assert word(u,sp+64)==0x1000000 and word(u,sp+36)==0 and word(u,sp+32)==0xfffffffd;assert word(u,sp+60)==((native if u is stock or symbol is None else syms[symbol])|1) and word(u,sp+56)==((0x854e0 if u is stock else syms['prvTaskExitError'])|1)
   data=bytearray(u.mem_read(stack,size))
   if u is candidate:
    struct.pack_into('<I',data,sp+60-stack,native|1);struct.pack_into('<I',data,sp+56-stack,0x854e1)
    if stack>=0x2002b258:struct.pack_into('<I',arena,sp+60-0x2002b258,native|1);struct.pack_into('<I',arena,sp+56-0x2002b258,0x854e1)
   if stack<0x2002b258:app_records.append((bytes(u.mem_read(cb,112)),bytes(data)))
  return (bytes(arena),app_records,bytes(u.mem_read(0x20007810,96)),bytes(u.mem_read(0x2002ad94,1220)),bytes(u.mem_read(0x200077fc,20)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI),bytes(u.mem_read(0xe000e000,4096)) if real_port else None,bytes(u.mem_read(0x40011000,4096)) if real_port else None,bytes(u.mem_read(0x40000000,4096)) if real_port else None,bytes(u.mem_read(0x2002c154,20)) if real_port else None,bytes(u.mem_read(0x20007938,8)) if real_port else None,bytes(u.mem_read(0x2002c2fc,12)) if real_port else None)
 try:
  for apps,preinit,pattern,primask,peer in itertools.product((0,1),(0,1),(0,0xa5),(0,1),(0,1)):
   phase="first";peer_active=False
   for u in (stock,candidate):
    states[id(u)]=False;u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2002b258,bytes([pattern])*0xb58);u.reg_write(UC_ARM_REG_CONTROL,0);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,0)
    if real_port:
     u.mem_write(0xe000e000,bytes(4096));u.mem_write(0x40011000,bytes(4096));u.mem_write(0x40000000,bytes(4096));u.mem_write(0xe000ed00,struct.pack('<I',0x410fc241));u.mem_write(0xe000e400,b'\x40')
   if apps:
    for row in rows:call('r1_thread_create_'+row['letter'],creators[row['letter']])
   if preinit:
    call('r1_native_timer_infrastructure',0x84e58);assert snapshot(stock,apps,False)==snapshot(candidate,apps,False);comparisons+=1
   for u in (stock,candidate):
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((0x964c8 if u is stock else syms['vTaskStartScheduler'])|1,0x20000100,count=2000000);assert states[id(u)] and u.reg_read(UC_ARM_REG_MSP)==0x2003beb8 and u.reg_read(UC_ARM_REG_PRIMASK)==0 and u.reg_read(UC_ARM_REG_FAULTMASK)==0
    assert word(u,0x20007848)==0x2002b4d0 and word(u,0x20007860)==0x2002b940 and word(u,0x2000785c)==0x2002b258;assert word(u,0x20007824)==2+5*apps and word(u,0x20007840)==2+5*apps and word(u,0x2000781c)==0x2002b940 and word(u,0x2000782c)==53;assert word(u,0x20007828)==0 and word(u,0x20007830)==1 and word(u,0x20007844)==0xffffffff and u.reg_read(UC_ARM_REG_BASEPRI)==224;assert bytes(u.mem_read(0x200077fc,20))==bytes(20)
    if real_port:assert word(u,0x20007814)==0 and u.mem_read(0x20007810,1)[0]==0 and word(u,0x20007818)==4 and word(u,0x40011508)==31 and word(u,0x40011304)==1 and word(u,0xe000ed88)==0xf00000 and word(u,0xe000ef34)==0xc0000000 and word(u,0xe000ed10)==16
   assert snapshot(stock,apps,True)==snapshot(candidate,apps,True),(apps,preinit,pattern,primask);comparisons+=1
   phase='svc'
   for u in (stock,candidate):
    states[id(u)]=False;u.reg_write(UC_ARM_REG_IPSR,11);u.reg_write(UC_ARM_REG_MSP,0x2003be98);u.reg_write(UC_ARM_REG_LR,0xfffffff9);u.emu_start((0x27218 if u is stock else syms['SVC_Handler'])|1,0x20000100,count=100000);assert states[id(u)] and u.reg_read(UC_ARM_REG_LR)==0xfffffffd and u.reg_read(UC_ARM_REG_PSP)==word(u,0x2002b940)+36 and u.reg_read(UC_ARM_REG_BASEPRI)==0
   assert snapshot(stock,apps,True)==snapshot(candidate,apps,True);assert [stock.reg_read(r) for r in saved]==[candidate.reg_read(r) for r in saved];comparisons+=1
   if peer:
    phase='construct'
    for u in (stock,candidate):
     u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_MSP,0x2003f000);u.mem_write(0x20003000,b'peer\0');u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(0x12345679,0x20003000,64,0)):u.reg_write(reg,value)
     u.mem_write(0x2003f000,struct.pack('<3I',53,0x20002000,0x20001000));u.emu_start((0x98418 if u is stock else syms['r1_native_task_create_static'])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_R0)==0x20001000
    peer_active=True;assert snapshot(stock,apps,True)==snapshot(candidate,apps,True);comparisons+=1
   phase='pendsv'
   for iteration in range(4):
    for u in (stock,candidate):
     states[id(u)]=False;u.reg_write(UC_ARM_REG_IPSR,14);u.reg_write(UC_ARM_REG_MSP,0x2003be98);u.reg_write(UC_ARM_REG_LR,0xfffffffd);u.emu_start((0x2725c if u is stock else syms['PendSV_Handler'])|1,0x20000100,count=2000000);assert states[id(u)] and u.reg_read(UC_ARM_REG_LR)==0xfffffffd and u.reg_read(UC_ARM_REG_BASEPRI)==0;expected=0x20001000 if peer and iteration%2 else 0x2002b940;assert word(u,0x2000781c)==expected and u.reg_read(UC_ARM_REG_PSP)==word(u,expected)+36
    assert snapshot(stock,apps,True)==snapshot(candidate,apps,True);assert [stock.reg_read(r) for r in saved]==[candidate.reg_read(r) for r in saved];comparisons+=1
   workflows+=1
 finally:
  fixture_allow.discard(port_source)
  for u,h in handles:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),context_driver_sha256=sha(Path(__file__)),context_report_sha256=sha(BASE/'rtos-context-port/report.json'),startup_report_sha256=sha(BASE/'rtos-scheduler-start/report.json'),port_report_sha256=sha(BASE/'rtos-port-start/report.json'),comparisons=comparisons,workflows=workflows,provider_interception=False,svc_dispatch_fixture_per_workflow=1,exception_return_executed=False,pendsv_calls_per_workflow=4,scope='Actual construction/port/first-task until SVC0, explicit handler-entry fixture, actual SVC software restore then four PendSV save/select/restore bodies; optional equal-priority peer rotates through actual ready lists',limitations=['SVC0 dispatch and exception-entry state are explicit fixtures; BX-LR exception return is bounded, not executed. No task code runs. Peer task entry is an unexecuted controlled pointer. Only exact initial frame PC/LR fields are normalized. Native exception return, physical scheduling and complete vector/image identity remain gates.'])
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'context graph comparisons;',workflows,'workflows; four actual PendSV/selector bodies each; explicit exception boundaries')
