#!/usr/bin/env python3
"""Stock scheduler queue, deferred ISR packet, consumer and real event callbacks."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,itertools
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave069-deferred-callable-types';E=P/'final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20002c88;STOP=0x2000f000;GROUP=0x20001c90;rows=[]
def run(native,kind,seed,initial,flags):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_write(0x20002888,bytes([seed])*0x400);saved=[0x45670000+i for i in range(8)];low=SP;trace=[];callback=(0x0800bf84 if kind=='clear' else 0x0800bf8c) if native else sy['vEventGroupClearBitsCallback' if kind=='clear' else 'vEventGroupSetBitsCallback']&~1
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def observe(uc,address,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP));assert low>=0x20002888
  if address==callback:trace.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
 u.hook_add(UC_HOOK_CODE,observe)
 def invoke(address,args):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args+[0]*4):u.reg_write(r,v)
  for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
  w(SP,0);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(address|1,STOP,count=200000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
  assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
  return u.reg_read(UC_ARM_REG_R0)
 invoke(0x0800ac84 if native else sy['case_boot_scheduler_initialize'],[])
 group=invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],[24]);assert group==GROUP
 invoke(0x0800bf94 if native else sy['case_policy_task_list_initialize'],[GROUP+4]);w(GROUP,initial)
 result=invoke(0x0800ce0c if native else sy['case_policy_irq_event_dispatch'],[callback|1,GROUP,flags,0]);assert result==1
 packet=bytes(u.mem_read(0x20001508,16));assert struct.unpack('<IIII',packet)==(0xfffffffe,callback|1,GROUP,flags)
 invoke(0x0800b0fc if native else sy['case_boot_timer_expired'],[])
 assert trace==[(GROUP,flags)] and u.reg_read(UC_ARM_REG_PRIMASK)==0
 assert struct.unpack('<I',bytes(u.mem_read(GROUP,4)))[0]==(initial&~flags if kind=='clear' else initial|flags)
 assert struct.unpack('<I',bytes(u.mem_read(0x200014f0,4)))[0]==0
 name=struct.unpack('<I',bytes(u.mem_read(0x20000fb4,4)))[0];assert name==(0x0800acdc if native else sy['case_boot_scheduler_name']);assert bytes(u.mem_read(name,5))==b'TmrQ\0'
 ram=bytearray(u.mem_read(0x20000000,0x2888));ram[0xfb4:0xfb8]=bytes(4);ram[0x150c:0x1510]=bytes(4);packet=packet[:4]+bytes(4)+packet[8:]
 return {'ram':bytes(ram).hex(),'packet':packet.hex(),'trace':trace,'stack_bytes':SP-low}
for kind,seed,initial,flags in itertools.product(['clear','set'],[0,0xa5,0xff],[0,0x123456,0xffffff],[0,1,3,0x80,0x123456,0xffffff]):
 a=run(True,kind,seed,initial,flags);b=run(False,kind,seed,initial,flags);fields=[k for k in a if k!='stack_bytes' and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'kind':kind,'seed':seed,'initial':initial,'flags':flags,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((kind,seed,initial,flags,fields))
 rows.append({'kind':kind,'seed':seed,'initial':initial,'flags':flags,'trace':a['trace'],'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes']})
r={'status':'PASS_STOCK_DEFERRED_EVENT_CALLBACK_CONSUMER_GRAPH','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'limits':['Actualstockqueue/pool/heap/list/ISRsend/timerconsumer/eventcallback/clearor-setprovider bodies execute without cuts or injectedreturns','No waiting eventtasks; runnable-waiter/scheduler/IRQ races excluded','Callbackpointer and registryname namespaces normalized only after exact identity checks; allotherRAM below2888 and16-byte recordscompare','Bounded native1024-byte upperstackwindow, not full IRQ/reentrancy budget']};(H/'deferred-high-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
