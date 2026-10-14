#!/usr/bin/env python3
"""Stock scheduler queue, deferred ISR packet, consumer and real event callbacks."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,itertools
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave039-list-cursor-contract';E=P/'final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20002c88;STOP=0x2000f000;GROUP=0x20001c90;rows=[]
def run(native,kind,seed,initial,flags,waitall,clear,count,cursor,current_priority):
 global GROUP
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0xe000e000,0x1000);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002888,bytes([seed])*0x400);saved=[0x45670000+i for i in range(8)];low=SP;trace=[];callback=(0x0800bf84 if kind=='clear' else 0x0800bf8c) if native else sy['vEventGroupClearBitsCallback' if kind=='clear' else 'vEventGroupSetBitsCallback']&~1
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def observe(uc,address,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP));assert low>=0x20002888
  if address==callback:trace.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
 u.hook_add(UC_HOOK_CODE,observe)
 preemption_writes=[]
 def scb(uc,access,address,size,value,data):
  if address==0xe000ed04:preemption_writes.append((size,value))
 u.hook_add(UC_HOOK_MEM_WRITE,scb)
 def invoke(address,args):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args+[0]*4):u.reg_write(r,v)
  for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
  w(SP,0);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(address|1,STOP,count=200000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
  assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
  return u.reg_read(UC_ARM_REG_R0)
 invoke(0x0800af70 if native else sy['case_boot_first_task_prepare'],[])
 invoke(0x0800ac84 if native else sy['case_boot_scheduler_initialize'],[])
 current=invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],[48])
 tasks=[invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],[48]) for _ in range(count)]
 GROUP=invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],[24])
 invoke(0x0800bf94 if native else sy['case_policy_task_list_initialize'],[GROUP+4]);w(GROUP,initial)
 w(current+44,current_priority);w(current+16,current)
 invoke(0x0800bfe2 if native else sy['case_policy_task_list_insert'],[0x20000ff4+current_priority*20,current+4])
 requested=[3,4][:count]
 for i,task in enumerate(tasks):
  w(task+44,1);w(task+4,100+i);w(task+16,task);w(task+24,requested[i]|(0x04000000 if waitall else 0)|(0x01000000 if clear else 0));w(task+36,task)
  invoke(0x0800bfb0 if native else sy['case_policy_task_list_insert_sorted'],[0x20001454,task+4])
  invoke(0x0800bfe2 if native else sy['case_policy_task_list_insert'],[GROUP+4,task+24])
 if cursor:w(GROUP+8,tasks[0]+24);w(0x20001458,tasks[0]+4)
 w(0x20000128,current);w(0x20000130,count+1);w(0x20000138,current_priority);w(0x2000013c,1);w(0x20000150,100)
 result=invoke(0x0800ce0c if native else sy['case_policy_irq_event_dispatch'],[callback|1,GROUP,flags,0]);assert result==1
 packet=bytes(u.mem_read(0x20001508,16));assert struct.unpack('<IIII',packet)==(0xfffffffe,callback|1,GROUP,flags)
 invoke(0x0800b0fc if native else sy['case_boot_timer_expired'],[])
 assert trace==[(GROUP,flags)] and u.reg_read(UC_ARM_REG_PRIMASK)==0
 before=initial|flags;matches=[(req&~before)==0 if waitall else (req&before)!=0 for req in requested];clear_mask=0
 for req,match in zip(requested,matches):
  if match and clear:clear_mask|=req
 assert struct.unpack('<I',bytes(u.mem_read(GROUP,4)))[0]==before&~clear_mask
 assert struct.unpack('<I',bytes(u.mem_read(GROUP+4,4)))[0]==count-sum(matches)
 assert struct.unpack('<I',bytes(u.mem_read(0x20001454,4)))[0]==count-sum(matches)
 assert struct.unpack('<I',bytes(u.mem_read(0x20000ff4+20,4)))[0]==sum(matches)+int(current_priority==1)
 for task,match in zip(tasks,matches):
  if match:
   assert struct.unpack('<I',bytes(u.mem_read(task+24,4)))[0]==before|0x82000000
   assert struct.unpack('<I',bytes(u.mem_read(task+40,4)))[0]==0
   assert struct.unpack('<I',bytes(u.mem_read(task+20,4)))[0]==0x20000ff4+20
 assert struct.unpack('<I',bytes(u.mem_read(0x200014f0,4)))[0]==0
 expected_preemption=int(current_priority<1 and any(matches));assert preemption_writes==([(4,0x10000000)] if expected_preemption else []);assert struct.unpack('<I',bytes(u.mem_read(0xe000ed04,4)))[0]==(0x10000000 if expected_preemption else 0)
 name=struct.unpack('<I',bytes(u.mem_read(0x20000fb4,4)))[0];assert name==(0x0800acdc if native else sy['case_boot_scheduler_name']);assert bytes(u.mem_read(name,5))==b'TmrQ\0'
 ram=bytearray(u.mem_read(0x20000000,0x2888));ram[0xfb4:0xfb8]=bytes(4);ram[0x150c:0x1510]=bytes(4);packet=packet[:4]+bytes(4)+packet[8:]
 return {'ram':bytes(ram).hex(),'packet':packet.hex(),'trace':trace,'stack_bytes':SP-low,'PENDSV_writes':preemption_writes}
for kind,seed,initial,flags,waitall,clear,count,cursor,current_priority in itertools.product(['set'],[0,0xa5],[0,1,3],[0,1,2,3,4],[False,True],[False,True],[1,2],[False,True],[0,1,2]):
 a=run(True,kind,seed,initial,flags,waitall,clear,count,cursor,current_priority);b=run(False,kind,seed,initial,flags,waitall,clear,count,cursor,current_priority);fields=[k for k in a if k!='stack_bytes' and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'seed':seed,'initial':initial,'flags':flags,'waitall':waitall,'clear':clear,'waiters':count,'cursor_first':cursor,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((seed,initial,flags,waitall,clear,count,cursor,fields))
 rows.append({'seed':seed,'initial':initial,'flags':flags,'waitall':waitall,'clear':clear,'waiters':count,'cursor_first':cursor,'current_priority':current_priority,'PENDSV_writes':a['PENDSV_writes'],'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes']})
r={'status':'PASS_STOCK_WAITER_SOFTWARE_PREEMPTION_REQUEST','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'limits':['Actualstockqueue/pool/heap/list/ISRsend/timerconsumer/eventcallback/clearor-setprovider bodies execute without cuts or injectedreturns','One/two valid priority1 waiters, currentpriority0/1/2 and live schedulerstate; ANY/ALL/clear/cursorcases; actualPENDSVrequest writes compared using passiveSCBregisterfixture. IRQdelivery/exceptionstack/contextswitch notemulated orvalidated','Callbackpointer and registryname namespaces normalized only after exact identity checks; allotherRAM below2888 and16-byte recordscompare','Bounded native1024-byte upperstackwindow, not full IRQ/reentrancy budget']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
