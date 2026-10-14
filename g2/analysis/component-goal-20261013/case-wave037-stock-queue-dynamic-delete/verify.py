#!/usr/bin/env python3
"""Real native16-byte timer sender, queue receiver and command consumer."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,itertools,subprocess
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave033-native-timer-message-width';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();E=H/'fixture.elf';cmd=json.loads((P/'final/receipt.json').read_text())['link_command'].copy();cmd.insert(1,'-ucase_boot_scheduler_counter_read');cmd[-1]=str(E);subprocess.run(cmd,check=True)
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
Q=0x20002600;BUF=0x20002800;SP=0x20002c88;STOP=0x2000f000;TIMER=0x20002100;LIST=0x20002000;SECOND=0x20002400;rows=[]
def run(native,op,seed,capacity,last):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_write(0x20002888,bytes([seed])*0x400)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 saved=[0x45670000+i for i in range(8)];low=SP;callbacks=[]
 def observe(uc,address,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP));assert low>=0x20002888
  if address==(0x0800ca6c if native else sy['case_boot_scheduler_counter_read']&~1) and uc.reg_read(UC_ARM_REG_R0)==TIMER:callbacks.append(TIMER)
 u.hook_add(UC_HOOK_CODE,observe)
 def invoke(address,arguments):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],arguments+[0]*4):u.reg_write(r,v)
  for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
  w(SP,0);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(address|1,STOP,count=200000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
  assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
  return u.reg_read(UC_ARM_REG_R0)
 invoke(0x0800ac84 if native else sy['case_boot_scheduler_initialize'],[])
 Q_actual=struct.unpack('<I',bytes(u.mem_read(0x20000164,4)))[0];assert Q_actual==0x200014b8
 TIMER_actual=invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],[capacity]);assert TIMER_actual==0x20001c90
 w(0x20000134,5);w(0x2000016c,5);w(TIMER_actual+24,7);w(TIMER_actual+32,(0x0800ca6c if native else sy['case_boot_scheduler_counter_read'])|1);u.mem_write(TIMER_actual+40,b'\0')
 global TIMER,Q,BUF
 TIMER=TIMER_actual;Q=Q_actual;BUF=0x20001508;start=0
 result=invoke(0x0800cd80 if native else sy['case_policy_task_event_send'],[TIMER,op,4,0]);assert result==1
 queued=bytes(u.mem_read(BUF+start*16,16));assert struct.unpack('<III',queued[:12])==(op,4,TIMER)
 padding_word=struct.unpack_from('<I',queued,12)[0];return_pc=padding_word&~1;call_pc=return_pc-4;h1,h2=struct.unpack('<HH',bytes(u.mem_read(call_pc,4)));assert h1&0xf800==0xf000 and h2&0xd000==0xd000
 sign=(h1>>10)&1;i1=1^((h2>>13)&1)^sign;i2=1^((h2>>11)&1)^sign;offset=(sign<<24)|(i1<<23)|(i2<<22)|((h1&0x3ff)<<12)|((h2&0x7ff)<<1)
 if sign:offset-=1<<25
 call_target=call_pc+4+offset;assert call_target==(0x0800cc0c if native else sy['case_policy_task_sleep_exit']&~1)
 assert (0x0800b3e8<=call_pc<0x0800b4a0) if native else ((sy['case_boot_transport_heap_allocate']&~1)<=call_pc<(sy['case_boot_transport_heap_allocate']&~1)+0x180)
 padding_provenance={'raw_word':hex(padding_word),'call_PC':hex(call_pc),'BL_target':hex(call_target),'meaning':'Saved return site after heap allocator scheduler-resume call'}
 queued=queued[:12]+bytes(4)
 invoke(0x0800b0fc if native else sy['case_boot_timer_expired'],[])
 name=struct.unpack('<I',bytes(u.mem_read(0x20000fb4,4)))[0];assert name==(0x0800acdc if native else sy['case_boot_scheduler_name']);assert bytes(u.mem_read(name,5))==b'TmrQ\0'
 ram=bytearray(u.mem_read(0x20000000,0x2888));ram[TIMER-0x20000000+32:TIMER-0x20000000+36]=bytes(4);ram[0xfb4:0xfb8]=bytes(4);ram[0x1514:0x1518]=bytes(4)
 assert struct.unpack_from('<I',ram,0x14f0)[0]==0 and not callbacks and u.reg_read(UC_ARM_REG_PRIMASK)==0
 assert struct.unpack_from('<I',ram,0x180)[0]==3064
 assert struct.unpack_from('<I',ram,0x194)[0]==0x20001c88
 assert struct.unpack_from('<I',ram,0x1c8c)[0]==3064
 return {'ram':bytes(ram).hex(),'queued':queued.hex(),'callbacks':callbacks,'stack_bytes':SP-low,'padding_provenance':padding_provenance}
for op,seed,capacity,last in itertools.product([5],[0,0xa5,0xff],[48,56,64,96],[False]):
 a=run(True,op,seed,capacity,last);b=run(False,op,seed,capacity,last);fields=[k for k in a if k not in ['stack_bytes','padding_provenance'] and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'op':op,'seed':seed,'allocation_bytes':capacity,'last':last,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((op,seed,capacity,last,fields))
 rows.append({'op':op,'seed':seed,'allocation_bytes':capacity,'last':last,'queued':a['queued'],'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes'],'native_padding_provenance':a['padding_provenance'],'source_padding_provenance':b['padding_provenance']})
r={'status':'PASS_STOCK_QUEUE_DYNAMIC_TIMER_DELETE_GRAPH','cases':len(rows),'production_ELF_sha256':sha(P/'final/case.elf'),'fixture_ELF_sha256':sha(E),'link_command':cmd,'comparisons':rows,'limits':['Actual stock scheduler/pool/list/registry initialize and dynamic heapallocated timer delete op5 through16byte sender/receiver/consumer/free/coalescing; negativecallbacks/overdue-autoreload/blocking/IRQ excluded','Real sender16-byte frame, queueproviders, timerconsumer and sortedlist helpers execute without cuts or injectedreturns','Only immutable timercallback, registryname, and independently BL-target-verified heap-resume returnsite pointer in fourth queued word namespaces normalized; allotherRAM below nativeheapfooter2888 andqueued16byte recordscompare; top1024stackwindow excluded','Bounded synchronous stack use; no global IRQ/reentrancy budget proof']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
