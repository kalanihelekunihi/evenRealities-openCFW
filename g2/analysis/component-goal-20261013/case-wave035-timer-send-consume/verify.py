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
Q=0x20002600;BUF=0x20002800;SP=0x20008000;STOP=0x2000f000;TIMER=0x20002100;LIST=0x20002000;SECOND=0x20002400;rows=[]
def run(native,op,seed,capacity,last):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_write(0x20007000,bytes([seed])*0x2000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 saved=[0x45670000+i for i in range(8)];low=SP;callbacks=[]
 def observe(uc,address,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP))
  if address==(0x0800ca6c if native else sy['case_boot_scheduler_counter_read']&~1) and uc.reg_read(UC_ARM_REG_R0)==TIMER:callbacks.append(TIMER)
 u.hook_add(UC_HOOK_CODE,observe)
 def invoke(address,arguments):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],arguments+[0]*4):u.reg_write(r,v)
  for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
  w(SP,0);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(address|1,STOP,count=200000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
  assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
  return u.reg_read(UC_ARM_REG_R0)
 for l in [LIST,SECOND]:invoke(0x0800bf94 if native else sy['case_policy_task_list_initialize'],[l])
 start=capacity-1 if last else 0;w(0x20000164,Q);w(0x20000170,LIST);w(0x20000174,SECOND);w(0x20000134,5);w(0x2000016c,5);w(Q,BUF);w(Q+4,BUF+start*16);w(Q+8,BUF+capacity*16);w(Q+12,BUF+((start-1)%capacity)*16);w(Q+56,0);w(Q+60,capacity);w(Q+64,16);u.mem_write(Q+68,b'\xff\xff');w(TIMER+24,7);w(TIMER+32,(0x0800ca6c if native else sy['case_boot_scheduler_counter_read'])|1);u.mem_write(TIMER+40,b'\2')
 result=invoke(0x0800cd80 if native else sy['case_policy_task_event_send'],[TIMER,op,4,0]);assert result==1
 queued=bytes(u.mem_read(BUF+start*16,16));assert struct.unpack('<III',queued[:12])==(op,4,TIMER)
 invoke(0x0800b0fc if native else sy['case_boot_timer_expired'],[])
 ram=bytearray(u.mem_read(0x20000000,0x3000));ram[0x2120:0x2124]=bytes(4)
 assert struct.unpack_from('<I',ram,0x2638)[0]==0 and not callbacks and u.reg_read(UC_ARM_REG_PRIMASK)==0,(native,op,seed,capacity,last,struct.unpack_from('<I',ram,0x2638)[0],callbacks,u.reg_read(UC_ARM_REG_PRIMASK))
 start_ops=[0,1,2,4,6,7,9];assert ram[0x2128]==(3 if op in start_ops else 2)
 assert struct.unpack_from('<I',ram,0x2000)[0]==int(op in start_ops)
 if op in start_ops:
  assert struct.unpack_from('<I',ram,0x2114)[0]==LIST
  assert struct.unpack_from('<I',ram,0x2104)[0]==(9 if op in [4,9] else 11)
 assert struct.unpack_from('<I',ram,0x2118)[0]==(4 if op in [4,9] else 7)
 return {'ram':bytes(ram).hex(),'queued':queued.hex(),'callbacks':callbacks,'stack_bytes':SP-low}
for op,seed,capacity,last in itertools.product(range(11),[0,0xa5,0xff],[2,4],[False,True]):
 a=run(True,op,seed,capacity,last);b=run(False,op,seed,capacity,last);fields=[k for k in a if k!='stack_bytes' and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'op':op,'seed':seed,'capacity':capacity,'last':last,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((op,seed,capacity,last,fields))
 rows.append({'op':op,'seed':seed,'capacity':capacity,'last':last,'queued':a['queued'],'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes']})
r={'status':'PASS_NATIVE16_TIMER_SEND_CONSUME_GRAPH','cases':len(rows),'production_ELF_sha256':sha(P/'final/case.elf'),'fixture_ELF_sha256':sha(E),'link_command':cmd,'comparisons':rows,'limits':['Commands0..10 static nonautoreload timer, future deadlines, empty queues/no waiters; dynamic-free/negativecallbacks/overdue-autoreload/blocking/IRQ paths excluded','Real sender16-byte frame, queueproviders, timerconsumer and sortedlist helpers execute without cuts or injectedreturns','Only immutable callback namespace pointer normalized; all other12288RAM bytes and queued16byte records compare','Bounded synchronous stack use; no global IRQ/reentrancy budget proof']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
