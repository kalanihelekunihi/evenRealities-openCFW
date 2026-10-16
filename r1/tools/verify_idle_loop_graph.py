#!/usr/bin/env python3
"""Actual idle/cleanup/expected-time/watchdog/scheduler graph; sleep fixture only."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError,UC_HOOK_CODE,UC_HOOK_MEM_INVALID,UC_HOOK_MEM_READ
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(stock,candidate,syms,baseline,fixture_allow,real_sleep=False):
 receipt=BASE/('board/idle-real-sleep-verification.json' if real_sleep else 'board/idle-loop-verification.json');receipt.unlink(missing_ok=True);states={};comparisons=0;faults=0;sleep_calls=0;watchdog_feeds=0;rtc_reads=0;wfe_calls=0;step_calls=0;handles=[]
 for u in (stock,candidate):
  for address in (0xe000e000,0x40010000,0x40011000):
   try:u.mem_map(address,0x1000)
   except UcError:pass
 sleep_source=syms['vPortSuppressTicksAndSleep']&~1;fixture_allow.add(sleep_source)
 def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
 def append(u,a,item,owner):
  sentinel=a+8;previous=word(u,sentinel+8);u.mem_write(item,struct.pack('<5I',0,sentinel,previous,owner,a));put(u,previous+4,item);put(u,sentinel+8,item);put(u,a,word(u,a)+1)
 def hook(u,a,size,user):
  f=states[id(u)]
  if a==(0x84fea if u is stock else syms['r1_native_task_idle_cleanup']&~1):
   if f['iterations']==3:f['stopped']=True;u.emu_stop();return
   f['iterations']+=1
  if a in (0x95be8,syms['r1_native_watchdog_hw_feed_thunk']&~1):f['hooks']+=1
  if a==(0x95de4 if u is stock else sleep_source):
   f['sleep'].append(u.reg_read(UC_ARM_REG_R0))
   if not real_sleep:u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  if real_sleep and a==(0x9653c if u is stock else syms['vTaskStepTick']&~1):f['steps']+=1
  if real_sleep and bytes(u.mem_read(a,2))==b'\x20\xbf':f['wfe']+=1;u.reg_write(UC_ARM_REG_PC,(a+2)|1)
 def rtc_read(u,access,a,size,value,user):
  if real_sleep and a==0x40011504:
   f=states[id(u)];put(u,a,(0xfffffe+f['rtc_reads'])&0xffffff);f['rtc_reads']+=1
 def invalid(u,access,address,size,value,user):
  if address==0xffffffff and value==0:states[id(u)]['fault']=True
  return False
 for u in (stock,candidate):handles.append((u,u.hook_add(UC_HOOK_CODE,hook)));handles.append((u,u.hook_add(UC_HOOK_MEM_INVALID,invalid)));handles.append((u,u.hook_add(UC_HOOK_MEM_READ,rtc_read)))
 try:
  for priority,top,extra,tick,next_time,device,primask in itertools.product((0,15),(0,15),(0,1),(0,1,99,0xfffffffe,0xffffffff),(0,1,2,100,0xffffffff),(0,1,2),(0,1)):
   results=[]
   for u in (stock,candidate):
    f={'iterations':0,'hooks':0,'sleep':[],'fault':False,'stopped':False,'rtc_reads':0,'wfe':0,'steps':0};states[id(u)]=f;u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x20001000,bytes(8192));u.mem_write(0x2000781c,bytes(64));u.mem_write(0x2002ad94,bytes(1220));u.mem_write(0x40010000,bytes(4096));put(u,0xe000ed04,0);u.mem_write(0x40011000,bytes(4096));u.mem_write(0xe000e100,bytes(0x200));put(u,0xe000e200,1)
    for i in range(56):init_list(u,0x2002ad94+i*20)
    for a in (0x2002b1f4,0x2002b208,0x2002b21c,0x2002b230,0x2002b244):init_list(u,a)
    put(u,0x2000102c,priority);put(u,0x20001028,0);append(u,0x2002ad94+priority*20,0x20001004,0x20001000)
    if extra:put(u,0x2000182c,0);append(u,0x2002ad94,0x20001804,0x20001800)
    for a,v in ((0x2000781c,0x20001000),(0x20007824,1+extra),(0x20007828,tick),(0x2000782c,top),(0x20007844,next_time),(0x2000784c,55),(0x20007854,0x2002b1f4),(0x20007858,0x2002b208),(0x20007694,0x20007644 if device else 0)):put(u,a,v)
    u.mem_write(0x20007634,bytes((int(device==2),0)));u.mem_write(0x20007949,b'\x01');u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,0)
    if device:
     u.emu_start((0x56694 if u is stock else syms['r1_native_named_wdt_register'])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((0x84fe8 if u is stock else syms['r1_native_idle_task'])|1,0x20000100,count=1000000)
    except UcError:assert f['fault'],(u is stock,hex(u.reg_read(UC_ARM_REG_PC)),device)
    assert f['fault'] or f['stopped'];assert f['hooks']==(f['iterations'] if not f['fault'] else 1)
    if device==2:assert word(u,0x40010600)==0x6e524635
    results.append((f['iterations'],f['hooks'],f['sleep'],f['fault'],bytes(u.mem_read(0x20001000,8192)),bytes(u.mem_read(0x20007810,76)),bytes(u.mem_read(0x2002ad94,1220)),bytes(u.mem_read(0xe000ed04,4)),bytes(u.mem_read(0x40010000,4096)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI),f['rtc_reads'],f['wfe'],bytes(u.mem_read(0x40011000,4096)),bytes(u.mem_read(0x2002c2fc,12)),bytes(u.mem_read(0xe000e100,0x200)),f['steps']))
   assert results[0]==results[1],(priority,top,extra,tick,next_time,device,primask,[(x[:4],x[-2:]) for x in results]);comparisons+=1;faults+=results[0][3];sleep_calls+=len(results[0][2]);watchdog_feeds+=results[0][1] if device==2 else 0;rtc_reads+=results[0][11];wfe_calls+=results[0][12];step_calls+=results[0][-1]
 finally:
  fixture_allow.discard(sleep_source)
  for u,h in handles:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),idle_driver_sha256=sha(Path(__file__)),idle_report_sha256=sha(BASE/'rtos-idle/report.json'),termination_report_sha256=sha(BASE/'rtos-task-termination/report.json'),comparisons=comparisons,assertion_comparisons=faults,sleep_fixture_calls_per_implementation=sleep_calls,actual_watchdog_feed_calls_per_implementation=watchdog_feeds,intercepted_providers=[] if real_sleep else ['vPortSuppressTicksAndSleep'],real_sleep=real_sleep,tickless_report_sha256=sha(BASE/'rtos-tickless-port/report.json'),sleep_kernel_report_sha256=sha(BASE/'rtos-sleep-kernel/report.json'),scope='Actual full idle C task, empty cleanup, expected idle, watchdog hook/device/registry/nrfx feed and scheduler suspend/resume; three iterations or matching tick-order assertion; scheduler/list/TCB memory, PendSV and watchdog RR writes',limitations=['Only port sleep is a fixture; it returns without changing time. Cleanup list is empty here; allocated self-deletion/reclamation is independently tested. No native context transfer, physical sleep/watchdog or whole-image identity proof.'])
 if real_sleep:
  result['actual_sleep_calls_per_implementation']=result.pop('sleep_fixture_calls_per_implementation');result.update(rtc_read_fixtures_per_implementation=rtc_reads,wfe_fixtures_per_implementation=wfe_calls,actual_tick_step_calls_per_implementation=step_calls,provider_interception=False,scope='Actual idle/RTC port/sleep-status/tick-step/watchdog/critical/scheduler graph; no provider interception; RTC counter reads and WFE wake are explicit instruction/MMIO fixtures',limitations=['Counter values advance by controlled MMIO reads; WFE is skipped as an explicit hardware wake fixture. No SoftDevice-enabled wait path is entered in this graph. No physical RTC/wake, watchdog, native context transfer or image byte identity proof.'])
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'idle graph comparisons;',faults,'assertions;',sleep_calls,'actual sleep calls;' if real_sleep else 'sleep fixtures;',watchdog_feeds,'actual watchdog feeds')
