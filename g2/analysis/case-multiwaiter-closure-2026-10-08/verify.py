from pathlib import Path
import struct,itertools,json,hashlib,sys
D=Path(__file__).resolve().parent;s=D.parent/'case-event-waiters-closure-2026-10-08/verify.py';text=s.read_text().split('for old,flags,request,all_bits,clear,depth')[0];ns={'__file__':str(s)};exec(text,ns)
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
E=ns['E'];DL=ns['DL'];RL=ns['RL'];K=ns['K'];CUR=0x20007000;rows=[]
def link(u,base,items):
 sentinel=base+8;u.mem_write(base,struct.pack('<IIIII',len(items),sentinel,0xffffffff,items[0][0] if items else sentinel,items[-1][0] if items else sentinel))
 for i,(p,owner) in enumerate(items):u.mem_write(p+4,struct.pack('<IIII',items[i+1][0] if i+1<len(items) else sentinel,items[i-1][0] if i else sentinel,owner,base))
for requests,old,flags,clear_profile,all_profile,prio_profile,current,depth in itertools.product([(8,0x40),(0x48,8),(8,8),(8,0x40,0x48)],[0,8],[8,0x40,0x48],[0,1,2,3],[0,1],[0,1,2],[0,1,2],[0,1]):
 n=len(requests);tasks=[0x20006800+i*0x80 for i in range(n)];priorities=[0 if prio_profile==0 else i%2 if prio_profile==1 else 1+i%2 for i in range(n)];clears=[clear_profile==1 or clear_profile==2 and i==0 or clear_profile==3 and i==n-1 for i in range(n)];matches=[((old|flags)&r)==r if all_profile else bool((old|flags)&r) for r in requests];clear_union=0
 for r,m,c in zip(requests,matches,clears):
  if m and c:clear_union|=r
 expected=(old|flags)&~clear_union;yield_expected=any(m and p>current for m,p in zip(matches,priorities));vals=[]
 for entry in [0x0800c4de,ns['ns']['symbols']['case_event_set_waiters']]:
  u=ns['ns']['guest'](0x20,1,0xff,0,0,0,int(depth>0),0);u.mem_map(0xe000e000,0x1000);u.mem_write(K,bytes(56));u.mem_write(K,struct.pack('<I',CUR));u.mem_write(K+8,struct.pack('<I',n+1));u.mem_write(K+16,struct.pack('<II',current,1));u.mem_write(CUR,bytes(96));u.mem_write(CUR+44,struct.pack('<I',current));u.mem_write(0x2000019c,struct.pack('<I',depth));u.mem_write(E,struct.pack('<I',old))
  for t,p in zip(tasks,priorities):u.mem_write(t,bytes(96));u.mem_write(t+44,struct.pack('<I',p))
  link(u,E+4,[(t+24,t) for t in tasks]);link(u,DL,[(t+4,t) for t in tasks])
  for p in range(3):link(u,RL+p*20,[(CUR+4,CUR)] if p==current else [])
  for t,r,c in zip(tasks,requests,clears):u.mem_write(t+24,struct.pack('<I',r|(0x04000000 if all_profile else 0)|(0x01000000 if c else 0)))
  calls=[];pendsv=[]
  def code(u,a,n,data):
   if a==0x0800c1cc:
    assert struct.unpack('<I',u.mem_read(K+48,4))[0]>0;calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
  def write(u,access,a,n,v,data):
   if a==0xe000ed04:pendsv.append(v);assert u.reg_read(UC_ARM_REG_PRIMASK)==1
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_R0,E);u.reg_write(UC_ARM_REG_R1,flags);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  assert u.reg_read(UC_ARM_REG_R0)==expected;assert calls==[[t+24,(old|flags)|0x02000000] for t,m in zip(tasks,matches) if m];assert pendsv==([0x10000000] if yield_expected else [])
  assert struct.unpack('<I',u.mem_read(E+4,4))[0]==sum(not m for m in matches);assert struct.unpack('<I',u.mem_read(DL,4))[0]==sum(not m for m in matches)
  for p in range(3):assert struct.unpack('<I',u.mem_read(RL+p*20,4))[0]==int(p==current)+sum(m and pr==p for m,pr in zip(matches,priorities))
  for t,p,m in zip(tasks,priorities,matches):assert struct.unpack('<I',u.mem_read(t+40,4))[0]==(0 if m else E+4);assert struct.unpack('<I',u.mem_read(t+20,4))[0]==(RL+p*20 if m else DL)
  assert u.reg_read(UC_ARM_REG_PRIMASK)==int(depth>0);assert struct.unpack('<I',u.mem_read(0x2000019c,4))[0]==depth
  vals.append((expected,bytes(u.mem_read(E,24)),bytes(u.mem_read(DL,20)),bytes(u.mem_read(RL,60)),bytes(u.mem_read(0x20006800,0x200)),bytes(u.mem_read(CUR,96)),bytes(u.mem_read(K,56)),calls,pendsv))
 assert vals[0]==vals[1];rows.append(dict(requests=list(requests),initial_bits=old,set_bits=flags,wait_all=bool(all_profile),clear_flags=clears,priorities=priorities,current_priority=current,critical_depth=depth,matches=matches,final_bits=expected,pendsv_requested=yield_expected))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['ns']['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['ns']['elf'].read_bytes()).hexdigest(),limits=['Actual original/native event-set and real task/list/scheduler peers; two/three coherent synthetic blocked TCBs and current ready TCB.','PendSV request writes verified; no exception delivery or task/context switch emulated.','Pending ticks and pending-ready list empty; no physical timer/concurrency, deletion/cancellation or real task trace.']),indent=2)+'\n');print('PASS',len(rows),'multiwaiter/priority comparisons')
