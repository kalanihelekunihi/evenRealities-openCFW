from pathlib import Path
import json,struct,itertools,hashlib,sys
D=Path(__file__).resolve().parent;s=D.parent/'audio-thread-flags-closure-2026-10-08/verify.py';text=s.read_text().split('for id,flags,old,state,ipsr,mask,basepri,running')[0];ns={'__file__':str(s)};exec(text,ns)
from unicorn import *
from unicorn.arm_const import *
T=0x20006000;CUR=0x20007000;DL=0x20005000;READY=0x2006a49c;PENDING=0x20073d24;rows=[]
def linked(u,base,pairs):
 end=base+8;u.mem_write(base,struct.pack('<IIIII',len(pairs),end,0xffffffff,pairs[0][0] if pairs else end,pairs[-1][0] if pairs else end))
 for i,(p,owner) in enumerate(pairs):u.mem_write(p+4,struct.pack('<IIII',pairs[i+1][0] if i+1<len(pairs) else end,pairs[i-1][0] if i else end,owner,base))
for flags,old,priority,current,suspended,mask,basepri in itertools.product([0,0x400000,0x800000,0xc00000],[0,0x100],[0,1,2],[0,1,2],[0,1],[0,1],[0,0x10,0x30]):
 vals=[]
 for entry in [0x449238,ns['symbols']['audio_thread_flags_set'],ns['symbols']['audio_public_flags_set']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(ns['raw'])+4095)&~4095);u.mem_write(0x438000,ns['raw']);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in ns['segments']:u.mem_write(a,b)
  u.mem_write(T,bytes(128));u.mem_write(CUR,bytes(128));u.mem_write(T+44,struct.pack('<I',priority));u.mem_write(CUR+44,struct.pack('<I',current));u.mem_write(T+0x68,struct.pack('<IB',old,1));u.mem_write(0x20074a20,struct.pack('<I',CUR));u.mem_write(0x20074a3c,struct.pack('<I',1));u.mem_write(0x20074a58,struct.pack('<I',suspended));u.mem_write(0x20074a38,struct.pack('<I',current));linked(u,DL,[(T+4,T)]);linked(u,PENDING,[])
  for p in range(3):linked(u,READY+p*20,[(CUR+4,CUR)] if p==current else [])
  u.reg_write(UC_ARM_REG_IPSR,15);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);writes=[]
  def write(u,access,a,n,v,data):
   if T<=a<T+112 or DL<=a<DL+20 or READY<=a<READY+60 or PENDING<=a<PENDING+20:assert u.reg_read(UC_ARM_REG_BASEPRI)==0x30,'unprotected_wake_list_write'
   if a==0xe000ed04:writes.append(v);assert u.reg_read(UC_ARM_REG_BASEPRI)==basepri
  u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_R0,T);u.reg_write(UC_ARM_REG_R1,flags);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;assert u.reg_read(UC_ARM_REG_R0)==old|flags;assert struct.unpack('<IB',u.mem_read(T+0x68,5))==(old|flags,2);assert u.reg_read(UC_ARM_REG_BASEPRI)==basepri;assert u.reg_read(UC_ARM_REG_PRIMASK)==mask;assert writes==([0x10000000] if priority>current else [])
  assert struct.unpack('<I',u.mem_read(T+0x14,4))[0]==(DL if suspended else READY+priority*20);assert struct.unpack('<I',u.mem_read(T+0x28,4))[0]==(PENDING if suspended else 0);assert struct.unpack('<I',u.mem_read(DL,4))[0]==int(bool(suspended));assert struct.unpack('<I',u.mem_read(PENDING,4))[0]==int(bool(suspended))
  vals.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(T,128)),bytes(u.mem_read(CUR,128)),bytes(u.mem_read(DL,20)),bytes(u.mem_read(PENDING,20)),bytes(u.mem_read(READY,60)),bytes(u.mem_read(0x20074a20,64)),writes))
 assert vals[0]==vals[1]==vals[2],('wake',flags,priority,current,suspended);rows.append(dict(flags=hex(flags),old=hex(old),priority=priority,current_priority=current,scheduler_suspended=suspended,primask=mask,basepri=basepri,state_owner='delayed' if suspended else 'ready',event_owner='pending-ready' if suspended else 'unlinked',pendsv_requested=priority>current))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Actual original/public waiting notification1 path compared with independent index0/action0/1 ISR reconstruction.','Coherent synthetic current/blocked TCBs, delayed/ready/pending-ready lists; scheduler suspension0/1. No actual audio task initialization/dispatch or exception/task switching.','List/value writes BASEPRI30; input BASEPRI/PRIMASK restored; PendSV request only, not exception delivery.','Kernel assertions, other actions/indices, destruction, scheduler resume of pending-ready and timeout expiry excluded.']),indent=2)+'\n');print('PASS',len(rows),'waiting notification wake/ownership cases')
