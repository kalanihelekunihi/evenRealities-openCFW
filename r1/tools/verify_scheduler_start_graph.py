#!/usr/bin/env python3
"""Actual static idle/timer startup graph bounded before port first-context work."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(stock,candidate,syms,baseline,fixture_allow,real_port=False):
 receipt=BASE/('board/port-start-verification.json' if real_port else 'board/scheduler-start-verification.json');receipt.unlink(missing_ok=True);config=BASE/'native-task-lifecycle/configuration-evidence.json';rows=json.loads(config.read_text())['rows'];port_source=syms['vPortStartFirstTask' if real_port else 'xPortStartScheduler']&~1;fixture_allow.add(port_source);states={};handles=[];comparisons=0;workflows=0
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def code(u,a,size,user):
  if a==((0x27238 if real_port else 0x979dc) if u is stock else port_source):states[id(u)]=True;u.emu_stop()
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
  if apps:
   for row in rows:tasks.append((int(row['control_block'],16),int(row['stack'],16),row['stack_bytes'],int(row['task_entry'],16),row['task_symbol'],row['priority']))
  for cb,stack,size,native,symbol,priority in tasks:
   sp=word(u,cb);assert word(u,cb+44)==priority and word(u,cb+84)==size//4 and bytes(u.mem_read(cb+104,8))==bytes((0,0,0,0,0,2,0,0));assert word(u,sp+64)==0x1000000 and word(u,sp+36)==0 and word(u,sp+32)==0xfffffffd;assert word(u,sp+60)==((native if u is stock else syms[symbol])|1) and word(u,sp+56)==((0x854e0 if u is stock else syms['prvTaskExitError'])|1)
   data=bytearray(u.mem_read(stack,size))
   if u is candidate:
    struct.pack_into('<I',data,sp+60-stack,native|1);struct.pack_into('<I',data,sp+56-stack,0x854e1)
    if stack>=0x2002b258:struct.pack_into('<I',arena,sp+60-0x2002b258,native|1);struct.pack_into('<I',arena,sp+56-0x2002b258,0x854e1)
   if stack<0x2002b258:app_records.append((bytes(u.mem_read(cb,112)),bytes(data)))
  return (bytes(arena),app_records,bytes(u.mem_read(0x20007810,96)),bytes(u.mem_read(0x2002ad94,1220)),bytes(u.mem_read(0x200077fc,20)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI),bytes(u.mem_read(0xe000e000,4096)) if real_port else None,bytes(u.mem_read(0x40011000,4096)) if real_port else None,bytes(u.mem_read(0x40000000,4096)) if real_port else None,bytes(u.mem_read(0x2002c154,20)) if real_port else None,bytes(u.mem_read(0x20007938,8)) if real_port else None,bytes(u.mem_read(0x2002c2fc,12)) if real_port else None)
 try:
  for apps,preinit,pattern,primask in itertools.product((0,1),(0,1),(0,0xa5),(0,1)):
   for u in (stock,candidate):
    states[id(u)]=False;u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2002b258,bytes([pattern])*0xb58);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,0)
    if real_port:
     u.mem_write(0xe000e000,bytes(4096));u.mem_write(0x40011000,bytes(4096));u.mem_write(0x40000000,bytes(4096));u.mem_write(0xe000ed00,struct.pack('<I',0x410fc241));u.mem_write(0xe000e400,b'\x40')
   if apps:
    for row in rows:call('r1_thread_create_'+row['letter'],creators[row['letter']])
   if preinit:
    call('r1_native_timer_infrastructure',0x84e58);assert snapshot(stock,apps,False)==snapshot(candidate,apps,False);comparisons+=1
   for u in (stock,candidate):
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((0x964c8 if u is stock else syms['vTaskStartScheduler'])|1,0x20000100,count=2000000);assert states[id(u)] and 0x2003e000<u.reg_read(UC_ARM_REG_SP)<=0x2003f000 and u.reg_read(UC_ARM_REG_SP)&7==0
    assert word(u,0x20007848)==0x2002b4d0 and word(u,0x20007860)==0x2002b940 and word(u,0x2000785c)==0x2002b258;assert word(u,0x20007824)==2+5*apps and word(u,0x20007840)==2+5*apps and word(u,0x2000781c)==0x2002b940 and word(u,0x2000782c)==53;assert word(u,0x20007828)==0 and word(u,0x20007830)==1 and word(u,0x20007844)==0xffffffff and u.reg_read(UC_ARM_REG_BASEPRI)==64;assert bytes(u.mem_read(0x200077fc,20))==bytes(20)
    if real_port:assert word(u,0x20007814)==0 and u.mem_read(0x20007810,1)[0]==0 and word(u,0x20007818)==4 and word(u,0x40011508)==31 and word(u,0x40011304)==1 and word(u,0xe000ed88)==0xf00000 and word(u,0xe000ef34)==0xc0000000 and word(u,0xe000ed10)==16
   assert snapshot(stock,apps,True)==snapshot(candidate,apps,True),(apps,preinit,pattern,primask);comparisons+=1;workflows+=1
 finally:
  fixture_allow.discard(port_source)
  for u,h in handles:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),startup_driver_sha256=sha(Path(__file__)),startup_report_sha256=sha(BASE/'rtos-scheduler-start/report.json'),application_configuration_sha256=sha(config),comparisons=comparisons,workflows=workflows,provider_interception=False,execution_boundary='Before xPortStartScheduler native0x979dc and source provider entry',unexecuted_providers=['xPortStartScheduler','r1_native_timer_task'],scope='Actual pinned scheduler/timer startup, typed static memory callbacks, queue/critical/list/constructors/port stack builders; empty or five-app graph, fresh/preinitialized timer queue, dirty storage and masks; initial handles/TCBs/stacks/state',limitations=['No port-start/first-context transfer or timer-task code executes. Initial frame PC/LR fields are normalized only after exact native/source pointer checks. Static construction consumes no heap. No physical boot/scheduling or image instruction equality proof.'])
 if real_port:result.update(port_report_sha256=sha(BASE/'rtos-port-start/report.json'),real_port=True,execution_boundary='Before vPortStartFirstTask native0x27238 and source provider entry',unexecuted_providers=['vPortStartFirstTask','r1_native_timer_task'],scope='Actual kernel/system-task construction, Nordic port start, RTC1 setup and full SDK LF-clock request/critical/clock hardware bodies; no provider interception; bounded before native first-context work',limitations=['NVIC priority readback uses explicit0xe0 writable-bit fixture. Memory-backed clock/RTC registers do not prove physical progression. No first-context transfer or timer runtime executes; only exact initial frame PC/LR normalization.'])
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'scheduler startup graph comparisons;',workflows,'workflows; stopped before first-task transfer; no provider interception' if real_port else 'workflows; stopped before port entry; no provider interception')
