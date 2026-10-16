#!/usr/bin/env python3
"""Composed RTC source graph on the authenticated canonical board layout."""
import hashlib,itertools,json,struct,shutil,subprocess,tempfile
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();RTC=0x40024000;NVIC=0xe000e000
ENTRIES={'r1_native_rtc_cached_device':0x50dc0,'r1_native_rtc_register':0x563c4,'r1_stock_dispatch_08':0x85d1a,'r1_clock_initialize':0x8adc0,'r1_structured_log_timestamp_adapter':0x514bc,'RTC2_IRQHandler':0x31750}
def verify(stock,candidate,syms,baseline):
 states={};comparisons=0;events=0;workflows=0
 cache_report=BASE/'native-rtc-discovery/report.json';cache_obj=cache_report.parent/'rtc-discovery.o';assert sha(cache_obj)==json.loads(cache_report.read_text())['selected_object_sha256'] and syms['r1_rtc_lookup_name']==0x50dd8
 with tempfile.TemporaryDirectory() as directory:
  temp=Path(directory);copy=temp/'cache.o';shutil.copyfile(cache_obj,copy);datafile=temp/'name.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.rtc.lookup.name='+str(datafile),str(copy)],check=True);data=datafile.read_bytes();assert data==bytes(stock.mem_read(0x50dd8,8))==b'sys rtc\0';candidate.mem_write(0x50dd8,data)
 for u in (stock,candidate):
  for a in (RTC,NVIC):
   if not any(start<=a and end>=a+4095 for start,end,_ in u.mem_regions()):u.mem_map(a,4096)
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def write(u,access,a,size,value,user):
  if RTC<=a<RTC+4096 or NVIC<=a<NVIC+4096:
   states[id(u)]['trace'].append(('write',a,size,value))
   if a in (RTC+0x308,RTC+0x348):u.mem_write(a-4,struct.pack('<I',word(u,a-4)&~value))
 def hook(u,a,size,user):
  nonlocal events
  if a!=(0x8d8fc if u is stock else syms['r1_event_publish']&~1):return
  args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];assert args[0]==4 and args[2]==1;payload=word(u,args[1]);assert payload<24;events+=1;states[id(u)]['trace'].append(('publish',4,payload,1));u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 hooks=[]
 for u in (stock,candidate):hooks.extend([(u,u.hook_add(UC_HOOK_CODE,hook)),(u,u.hook_add(UC_HOOK_MEM_WRITE,write))])
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def state(u):
  record=bytearray(u.mem_read(0x2000737c,96));callback=struct.unpack_from('<I',record,68)[0]
  if callback:assert callback==((0x5a9d0 if u is stock else syms['r1_clock_second_changed'])|1);struct.pack_into('<I',record,68,0x5a9d1)
  sdk=bytearray(u.mem_read(0x20007950,8));callback=struct.unpack_from('<I',sdk,4)[0]
  if callback:assert callback==((0x56274 if u is stock else syms['r1_native_rtc_tick'])|1);struct.pack_into('<I',sdk,4,0x56275)
  return (bytes(record),bytes(sdk),bytes(u.mem_read(0x20006820,24)),bytes(u.mem_read(0x20016ac4,32)),bytes(u.mem_read(0x20037e88,32)),word(u,0x20007680),word(u,0x20007690),bytes(u.mem_read(RTC,4096)),bytes(u.mem_read(NVIC,4096)))
 def call(name,args=()):
  nonlocal comparisons
  results=[]
  for u in (stock,candidate):
   states[id(u)]['trace']=[];u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   result=None if name=='RTC2_IRQHandler' else u.reg_read(UC_ARM_REG_R0);results.append((result,list(states[id(u)]['trace']),state(u)))
  assert results[0]==results[1],(name,args,[(i,a,b) for i,(a,b) in enumerate(zip(results[0],results[1])) if a!=b]);comparisons+=1;return results[0][0]
 def reset():
  for u in (stock,candidate):
   u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(RTC,bytes(4096));u.mem_write(NVIC,bytes(4096));u.mem_write(0x200068ec,bytes(1));u.mem_write(0x20007680,bytes(4));u.mem_write(0x20007690,bytes(4));states[id(u)]={'trace':[]}
 try:
  for length,mask,cached in itertools.product((0,1,2,4),(0,1,2,8,15),(0,1,0x20002000,0xdeadbeef)):
   reset()
   for u in (stock,candidate):
    u.mem_write(0x20007690,struct.pack('<I',cached));u.mem_write(0x20007680,struct.pack('<I',0x20002000 if length else 0))
    for i in range(length):
     name=0x20003000+i*32;u.mem_write(name,b'sys rtc\0' if mask&(1<<i) else b'other\0');u.mem_write(0x20002000+i*24,struct.pack('<6I',name,0,0,0,0,0x20002000+(i+1)*24 if i+1<length else 0))
   expected=cached or next((0x20002000+i*24 for i in range(length) if mask&(1<<i)),0);assert call('r1_native_rtc_cached_device')==expected
   for u in (stock,candidate):u.mem_write(0x20003000,b'sys rtc\0');u.mem_write(0x20002000,struct.pack('<6I',0x20003000,0,0,0,0,0));u.mem_write(0x20007680,struct.pack('<I',0x20002000))
   expected=expected or 0x20002000;assert call('r1_native_rtc_cached_device')==expected
   for u in (stock,candidate):u.mem_write(0x20007680,struct.pack('<I',0xdead0000))
   assert call('r1_native_rtc_cached_device')==expected
  cache_comparisons=comparisons
  for offset,epoch,default,context in itertools.product((-720,0,480),(3599,86399,1700000000,0xffffffff),(False,True),(0,0x12345678)):
   reset();workflows+=1
   for u in (stock,candidate):u.mem_write(0x20003200,struct.pack('<HHI',offset&65535,0x1234,epoch))
   assert call('r1_native_rtc_register')==1;assert call('r1_native_rtc_cached_device')==0x200073c4;assert call('r1_stock_dispatch_08',(0x200073c4,))==0;assert call('r1_clock_initialize',(0 if default else 0x20003200,context))==1
   initial=0 if default else epoch;assert call('r1_structured_log_timestamp_adapter')==initial
   for tick in range(8):
    for u in (stock,candidate):u.mem_write(RTC+0x100,struct.pack('<I',1))
    call('RTC2_IRQHandler')
   assert call('r1_structured_log_timestamp_adapter')==(initial+1)&0xffffffff
   for u in (stock,candidate):assert word(u,0x20007380)==(initial+1)&0xffffffff and bytes(u.mem_read(0x2000737e,2))==bytes(2);u.mem_write(0x20007680,bytes(4))
   assert call('r1_native_rtc_cached_device')==0x200073c4
 finally:
  for u,h in hooks:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 receipt=BASE/'board/rtc-startup-verification.json';receipt.write_text(json.dumps(dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),startup_driver_sha256=sha(Path(__file__)),cache_name_bytes_compared=8,cache_report_sha256=sha(cache_report),comparisons=comparisons,cache_comparisons=cache_comparisons,workflows=workflows,publish_calls_per_implementation=events//2,scope='Actual registry registration/cache/open/SDK startup/default clock initialization/RTC getter/eight IRQ tick sequences, canonical error alias and clock callback; ordered writes/shared states compare',limitations=['Selected call order demonstrates composition, not the actual firmware boot call order. Clock mode is controlled zero; event-publish boundary and MMIO W1C behavior are fixtures. No physical timing, interrupt preemption or whole-image proof.']),indent=2)+'\n');print(comparisons,'RTC discovery/startup comparisons;',events//2,'publish calls')
