#!/usr/bin/env python3
"""Execute the native device initcall stage with actual canonical C registrars."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(stock,candidate,syms,baseline,fixture_allow,real_heap=False,real_scheduler=False):
 receipt=BASE/('board/initcall-scheduler-verification.json' if real_scheduler else 'board/initcall-heap-verification.json' if real_heap else 'board/initcall-stage-verification.json')
 receipt.unlink(missing_ok=True)
 from verify_native_initcalls import CALLS
 registrar_entries={a:i for i,(_,a) in enumerate(CALLS)};registrar_entries.update({syms[n]&~1:i for i,(n,_) in enumerate(CALLS)})
 states={};comparisons=0;allocations=0;hooks=[];names=[];changed_bytes=set();name_pointer_fields=set()
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,0x1000)
  except UcError:pass
 # Normalize only authenticated cold function-pointer pairs. Data addresses stay exact.
 translations={}
 for off in range(0,0x30000,4):
  a,b=(struct.unpack_from('<I',baseline[id(u)],off)[0] for u in (stock,candidate))
  if a!=b and 0x27000<=a<0xc5000 and 0x1000000<=b<0x1010000:
   translations[off]=(a,b)
 def call_target(u,lr):
  first,second=struct.unpack('<2H',bytes(u.mem_read((lr&~1)-4,4)));assert first&0xf800==0xf000 and second&0xd000==0xd000
  sign=(first>>10)&1;i1=1^((second>>13)&1)^sign;i2=1^((second>>11)&1)^sign;offset=(sign<<24)|(i1<<23)|(i2<<22)|((first&0x3ff)<<12)|((second&0x7ff)<<1)
  if sign:offset-=1<<25
  return ((lr&~1)+offset)&0xffffffff
 assert call_target(stock,0x97b39)==0x855a0
 scheduler={0x9659c:'suspend',0x98b24:'resume',syms['vTaskSuspendAll']&~1:'suspend',syms['xTaskResumeAll']&~1:'resume'}
 def hook(u,a,size,user):
  nonlocal allocations
  if real_heap and a in scheduler:
   states[id(u)]['scheduler'].append((scheduler[a],u.reg_read(UC_ARM_REG_PRIMASK)))
   if not real_scheduler:u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
  if a in registrar_entries:states[id(u)]['registrars'].append((registrar_entries[a],u.reg_read(UC_ARM_REG_PRIMASK)))
  if a not in (0x855a0,syms['pvPortMalloc']&~1):return
  f=states[id(u)];size=u.reg_read(UC_ARM_REG_R0);index=len(f['allocations']);
  if real_heap:
   lr=u.reg_read(UC_ARM_REG_LR);assert size==80 and index<2 and call_target(u,lr)==(0x855a0 if u is stock else syms['pvPortMalloc']&~1);assert u is candidate or lr==0x97b39;f['callers'].append(lr);f['allocations'].append((size,0x2001e598+index*104,u.reg_read(UC_ARM_REG_PRIMASK)));allocations+=1;return
  assert size==80 and index<2;result=0 if f['fail']&(1<<index) else 0x20028000+index*128;f['allocations'].append((size,result,u.reg_read(UC_ARM_REG_PRIMASK)));allocations+=1;u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 for u in (stock,candidate):hooks.append((u,u.hook_add(UC_HOOK_CODE,hook)))
 if not real_scheduler:fixture_allow.update({syms[n]&~1 for n in ('vTaskSuspendAll','xTaskResumeAll')} if real_heap else {syms['pvPortMalloc']&~1})
 def normalized(u):
  data=bytearray(u.mem_read(0x20000000,0x30000))
  if u is candidate:
   for off,(a,b) in translations.items():
    word=struct.unpack_from('<I',data,off)[0]
    if word==b:struct.pack_into('<I',data,off,a)
  pointer=struct.unpack('<I',bytes(u.mem_read(0x20007680,4)))[0];records=[]
  while pointer:
   assert len(records)<25
   name,ops=struct.unpack('<2I',bytes(u.mem_read(pointer,8)));records.append((pointer,bytes(u.mem_read(name,64)).split(b'\0')[0].decode(),ops));pointer=struct.unpack('<I',bytes(u.mem_read(pointer+20,4)))[0]
  return bytes(data),records
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 try:
  for entry,mask,fail,pattern in itertools.product(('r1_module_init_table_run','r1_native_boot_initcall_dispatch'),(0,1),((0,) if real_heap else range(4)),(0,0xa5)):
   results=[]
   for u in (stock,candidate):
    states[id(u)]={'fail':fail,'allocations':[],'registrars':[],'scheduler':[],'callers':[]};u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2001e588 if real_heap else 0x20028000,bytes([pattern])*(51200 if real_heap else 256));u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    a=({'r1_module_init_table_run':0x5cb6c,'r1_native_boot_initcall_dispatch':0x4e1e4}[entry] if u is stock else syms[entry])
    try:u.emu_start(a|1,0x20000100,count=2000000)
    except UcError as exc:raise AssertionError((entry,u is stock,hex(u.reg_read(UC_ARM_REG_PC)),states[id(u)])) from exc
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((normalized(u),states[id(u)]['allocations'],u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI),states[id(u)]['registrars'],states[id(u)]['scheduler']))
   original,compiled=results[0][0][0],results[1][0][0];original_base=baseline[id(stock)][:0x30000];compiled_base=bytearray(baseline[id(candidate)][:0x30000])
   for off,(a,b) in translations.items():struct.pack_into('<I',compiled_base,off,a)
   compiled=bytearray(compiled)
   for off in range(0,0x30000,4):
    a,b=(struct.unpack_from('<I',data,off)[0] for data in (original,compiled))
    if 0xc0600<=a<0xc0850 and 0x1000000<=b<0x1010000:
     an=bytes(stock.mem_read(a,64)).split(b'\0')[0];bn=bytes(candidate.mem_read(b,64)).split(b'\0')[0];assert an==bn and 0<len(an)<64,(hex(off),an,bn);struct.pack_into('<I',compiled,off,a);name_pointer_fields.add(off)
   if real_heap:
    assert len(states[id(stock)]['callers'])==len(states[id(candidate)]['callers'])==2
    for index in range(2):
     off=0x1e590+index*104;a,b=(struct.unpack_from('<I',data,off)[0] for data in (original,compiled));assert a==states[id(stock)]['callers'][index] and b==states[id(candidate)]['callers'][index];struct.pack_into('<I',compiled,off,a)
    assert struct.unpack_from('<5I',original,0x77fc)==(0x2002ad78,50976,50976,2,0)
    assert results[0][5]==[(name,1 if entry=='r1_native_boot_initcall_dispatch' else mask) for name in ('suspend','resume','suspend','resume')]
   changed={i for i in range(0x30000) if original[i]!=original_base[i] or compiled[i]!=compiled_base[i]};changed_bytes.update(changed)
   assert all(original[i]==compiled[i] for i in changed),(entry,mask,fail,pattern,[(hex(0x20000000+i),original[i],compiled[i]) for i in sorted(changed) if original[i]!=compiled[i]][:20])
   assert results[0][0][1]==results[1][0][1] and results[0][1:]==results[1][1:],(entry,mask,fail,pattern,results[0][1:],results[1][1:]);assert len(results[0][0][1])==25 and len(results[0][1])==2
   assert results[0][4]==[(i,1 if entry=='r1_native_boot_initcall_dispatch' else mask) for i in range(13)]
   assert results[0][2]==(0 if entry=='r1_native_boot_initcall_dispatch' else mask);names=[r[1] for r in results[0][0][1]];comparisons+=1
 finally:
  fixture_allow.clear()
  for u,h in hooks:u.hook_del(h)
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),stage_driver_sha256=sha(Path(__file__)),comparisons=comparisons,allocations_per_implementation=allocations//2,registry_records=25,registrars_executed_per_case=13,registry_names=names,ram_bytes_monitored_per_case=0x30000,distinct_changed_bytes_compared=len(changed_bytes),cold_pointer_translations=len(translations),name_pointer_fields_compared=len(name_pointer_fields),scope='Actual initcall table/boot dispatch, all13 registrars, canonical CMSIS semaphoreNew/FreeRTOS queue creation/reset/list and critical providers; all changed bytes across lower192KiB RAM,25 registry records and masks compare',limitations=['Allocator return/storage is a bounded fixture, covering both independent failures. Unmodeled cold RAM is retained per implementation; all mutations compare after per-field cold function-pointer and runtime authenticated name-pointer normalization. Prekernel execution is controlled; peripheral open calls, complete firmware boot, real heap, hardware and whole-image identity remain gates.'])
 if real_heap:
  result.update(heap_report_sha256=sha(BASE/'native-heap/report.json'),actual_heap_executed=True,scope='Actual initcall/CMSIS/queue/heap/critical composition;25 records,51200-byte heap, allocator accounting, source/native caller BL targets, all changed lower192KiB RAM and masks',limitations=['Scheduler suspend/resume are bounded fixtures. Native and source call-site LR values are authenticated and normalized only at the two allocated block caller fields. Controlled prekernel stage does not establish subsequent open order, complete boot, scheduler concurrency, hardware or byte identity.'])
 if real_scheduler:
  result.update(scheduler_report_sha256=sha(BASE/'rtos-scheduler-resume/report.json'),actual_scheduler_suspend_resume_executed=True,scope='Actual initcall/CMSIS/queue/heap/scheduler suspend-resume/critical composition; no provider interception,25 records and all changed lower192KiB RAM',limitations=['Native/source caller BL targets and two caller-LR header fields are authenticated/normalized. Controlled prekernel stage has no pending tasks or ticks; complete scheduler startup, context switching, full TCB allocation, hardware and whole-image equality remain gates.'])
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'full initcall-stage comparisons;',allocations//2,'allocation calls;25 records; actual heap:',real_heap)
