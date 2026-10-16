#!/usr/bin/env python3
"""Execute the assembled source logger graph against native on the board layout.
Invoked by verify_native_board.py --thread-init-logs-graph after layout authentication.
"""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NATIVE={'r1_native_service_hardware_initialize':0x45c84,'r1_native_storage_hardware_initialize':0x45d00,'nrf_log_init':0x79af4,'nrf_log_default_backends_init':0x7968c,'nrf_log_frontend_hexdump':0x79918,'nrf_log_frontend_dequeue':0x796a8,'nrf_log_panic':0x79b1c,**{'nrf_log_frontend_std_'+str(i):a for i,a in enumerate((0x799c0,0x799c8,0x799d6,0x799e6,0x799f8,0x79a0c,0x79a28))}}
RANGES=[(0x2000737c,8),(0x200079b8,12),(0x200079c4,4),(0x200079c8,8),(0x200079d0,8),(0x2002c4b4,4096),(0x2002d4b4,192),(0x2002d574,128),(0x2002d5f4,24),(0x2002d60c,4128),(0x2002e62c,696),(0x20016ac4,32),(0x20006820,20),(0x2002c2fc,12),(0x2000653c,2),(0x20006906,1),(0x200068ec,2),(0x200068f4,16),(0x20016bc8,8192),(0x20018bc8,236)]
def verify(stock,candidate,syms,baseline):
 # This graph executes IPSR instructions. Clone the authenticated canonical
 # images into Cortex-M-class engines, rather than intercepting those opcodes.
 originals=(stock,candidate);clones=[];cloned_baseline={}
 for original in originals:
  clone=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for start,end,permissions in original.mem_regions():
   clone.mem_map(start,end-start+1,permissions);clone.mem_write(start,bytes(original.mem_read(start,end-start+1)))
  clones.append(clone);cloned_baseline[id(clone)]=baseline[id(original)]
 stock,candidate=clones;baseline=cloned_baseline
 receipt=BASE/'board/thread-init-logs-verification.json';receipt.unlink(missing_ok=True);states={};comparisons=0;workflows=0;accepted=0;write_calls=0;timestamp_calls=0;standard_messages=0;hexdump_messages=0
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,4096)
  except UcError:pass
 try:candidate.mem_map(0xd0000,0x10000)
 except UcError:pass
 def hook(u,a,size,user):
  if u is candidate:assert not 0x20000<=a<0xe0000 and not 0x1100000<=a<0x1101000,('Unexpected source provider',hex(a))
  f=states[id(u)]
  if a==(0x5639c if u is stock else syms['r1_native_rtc_snapshot']&~1):
   assert u.reg_read(UC_ARM_REG_R0)==0x20003100 and u.reg_read(UC_ARM_REG_R1)==0 and u.reg_read(UC_ARM_REG_R3)==0;assert bytes(u.mem_read(u.reg_read(UC_ARM_REG_R2),64))==bytes(64);assert struct.unpack('<I',bytes(u.mem_read(0x20007380,4)))[0]==f['epoch'];f['trace'].append(('timestamp',f['epoch']))
  if f['pending'] and a==f['pending'][0]:
   _,payload=f['pending'];done=u.reg_read(UC_ARM_REG_R0);assert done<=len(payload);f['trace'].append(('rtt-write',len(payload),payload[:done]));f['pending']=None
  if a==(0x31a18 if u is stock else syms['SEGGER_RTT_WriteNoLock']&~1):
   assert f['pending'] is None and u.reg_read(UC_ARM_REG_R0)==0;f['pending']=(u.reg_read(UC_ARM_REG_LR)&~1,bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2))))
 hooks=[(u,u.hook_add(UC_HOOK_CODE,hook)) for u in (stock,candidate)]
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 def call(name,args=()):
  nonlocal comparisons
  results=[]
  for u in (stock,candidate):
   states[id(u)]['trace']=[];u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<4I',*(list(args[4:])+[0]*4)[:4]));u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   try:u.emu_start((NATIVE[name] if u is stock else syms[name])|1,0x20000100,count=2000000)
   except Exception as error:raise AssertionError((name,'native' if u is stock else 'source',hex(u.reg_read(UC_ARM_REG_PC)),states[id(u)]['trace'][-3:])) from error
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(name,hex(u.reg_read(UC_ARM_REG_PC)));assert states[id(u)]['pending'] is None
   result=u.reg_read(UC_ARM_REG_R0) if name in ('nrf_log_init','nrf_log_frontend_dequeue') else None;results.append((result,list(states[id(u)]['trace']),tuple(bytes(u.mem_read(a,z)) for a,z in RANGES)))
  assert results[0]==results[1],(name,args,[(i,results[0][i],results[1][i]) for i in range(2) if results[0][i]!=results[1][i]]+[(hex(RANGES[i][0]),a[:32].hex(),b[:32].hex()) for i,(a,b) in enumerate(zip(results[0][2],results[1][2])) if a!=b]);comparisons+=1;return results[0]
 try:
  for offset,mode,clock,export,deferred,drain in itertools.product((-720,0,330),range(8),(0,1),(0,1),(0,1),(False,True)):
   workflows+=1
   for u in (stock,candidate):
    u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0xe000e000,bytes(4096));u.reg_write(UC_ARM_REG_PRIMASK,0);u.mem_write(0x20007a18,bytes(4));states[id(u)]={'trace':[],'pending':None,'epoch':1700000000};u.mem_write(0x20003000,struct.pack('<9I',0,0,0,0,(0x5639c if u is stock else syms['r1_native_rtc_snapshot'])|1,0,0,0,0));u.mem_write(0x20003100,struct.pack('<6I',0xc07a0,0x20003000,0,0,0,0));u.mem_write(0x20007690,struct.pack('<I',0x20003100));u.mem_write(0x20006828,struct.pack('<I',0x99c8c));u.mem_write(0x20007380,struct.pack('<I',1700000000));u.mem_write(0x20016acc,struct.pack('<hB',offset,1))
   assert call('nrf_log_init',(0,32768))[0]==0;call('nrf_log_default_backends_init')
   for u in (stock,candidate):u.mem_write(0x2002d60c,bytes([0 if deferred else 1]))
   def account(result):
    nonlocal accepted,write_calls,timestamp_calls
    for event in result[1]:
     if event[0]=='timestamp':timestamp_calls+=1
     else:write_calls+=1;accepted+=len(event[2])
   for u in (stock,candidate):u.mem_write(0x200068ec,bytes([mode]));u.mem_write(0x2000653c,bytes([clock]));u.mem_write(0x20006906,bytes([export]))
   for name in ('r1_native_service_hardware_initialize','r1_native_storage_hardware_initialize'):
    standard_messages+=bool(mode&2)
    if drain:
     for u in (stock,candidate):u.mem_write(0x2002e62c+24+16,bytes(u.mem_read(0x2002e62c+24+12,4)))
    account(call(name))
   if deferred:
    for i in range(64):
     if drain:
      for u in (stock,candidate):u.mem_write(0x2002e62c+24+16,bytes(u.mem_read(0x2002e62c+24+12,4)))
     result=call('nrf_log_frontend_dequeue');account(result)
     if not result[0]:break
    else:raise AssertionError('dequeue did not drain')
   account(call('nrf_log_frontend_dequeue'));call('nrf_log_panic')
 finally:
  for u,h in hooks:u.hook_del(h);u.mem_write(0x20000000,baseline[id(u)])
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),pipeline_driver_sha256=sha(Path(__file__)),comparisons=comparisons,workflows=workflows,standard_messages=standard_messages,hexdump_messages=hexdump_messages,accepted_rtt_bytes_per_implementation=accepted,rtt_write_calls_per_implementation=write_calls,timestamp_callbacks_per_implementation=timestamp_calls,actual_rtc_snapshot_and_default_clock_get=True,wrapper_calls=workflows*2,provider_interception=False,engine='UC_MODE_THUMB|UC_MODE_MCLASS',wrapper_report_sha256=sha(BASE/'native-thread-init-logs/report.json'),scope='Actual service/storage wrappers in all modes0..7 with clock/export state -> structured cache and Nordic frontend/pool/backend/serial/calendar/RTT; native descriptor identities retained',limitations=['Clock/RTC registration binding and counter updates are controlled fixtures; actual native/source RTC snapshot, registry, timestamp adapter, default get and logger backend record/API execute. Optional host consumption occurs only between public calls; no live debugger/RTC or physical timing proof.','Only small structured records below event/BLE export thresholds are composed; threshold publication, complete startup and physical task concurrency remain gates.','Unresolved board providers are test-only traps and are not executed. Whole-image linking, original compiler identity, duplicate layout and byte equality remain gates.'],instruction_identity_proven=False)
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'thread init logger graph comparisons;',accepted,'accepted RTT bytes');return result
