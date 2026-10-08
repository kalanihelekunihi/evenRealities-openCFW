from pathlib import Path
import struct,itertools,json,hashlib,sys
D=Path(__file__).resolve().parent;s=D.parent/'case-uart-receive-closure-2026-10-08/verify.py';text=s.read_text().split('rows=[]')[0];a=text.index('entries={w:');b=text.index('\ndef guest',a);text=text[:a]+'entries={}'+text[b:];ns={'__file__':str(s)};exec(text,ns)
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
E=0x20006000;T=0x20006800;DL=0x20006400;RL=0x20000ff4;K=0x20000128;rows=[]
def link(u,base,items):
 sentinel=base+8;u.mem_write(base,struct.pack('<IIIII',len(items),sentinel,0xffffffff,items[0] if items else sentinel,items[-1] if items else sentinel))
 for i,p in enumerate(items):u.mem_write(p+4,struct.pack('<IIII',items[i+1] if i+1<len(items) else sentinel,items[i-1] if i else sentinel,T,base))
for old,flags,request,all_bits,clear,depth in itertools.product([0,8,0x40,0x48],[0,8,0x40,0x48],[8,0x40,0x48],[0,1],[0,1],[0,1]):
 vals=[];match=((old|flags)&request)==request if all_bits else bool((old|flags)&request)
 for entry in [0x0800c4de,ns['symbols']['case_event_set_waiters']]:
  u=ns['guest'](0x20,1,0xff,0,0,0,int(depth>0),0);u.mem_map(0xe000e000,0x1000);u.mem_write(K,bytes(56));u.mem_write(K,struct.pack('<I',0x20007000));u.mem_write(K+8,struct.pack('<I',2));u.mem_write(K+20,struct.pack('<I',1));u.mem_write(0x2000019c,struct.pack('<I',depth));u.mem_write(T,bytes(96));u.mem_write(E,struct.pack('<I',old));link(u,E+4,[T+24]);link(u,DL,[T+4]);link(u,RL,[]);u.mem_write(T+24,struct.pack('<I',request|(0x04000000 if all_bits else 0)|(0x01000000 if clear else 0)));calls=[]
  def code(u,a,n,d):
   if a==0x0800c1cc:
    assert struct.unpack('<I',u.mem_read(K+0x30,4))[0]>0,'waiter_remove_without_scheduler_suspend'
    calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
   assert a!=0x0800c0a0,'unexpected_yield'
  u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_R0,E);u.reg_write(UC_ARM_REG_R1,flags);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  expected=(old|flags)&~(request if match and clear else 0);assert u.reg_read(UC_ARM_REG_R0)==expected;assert struct.unpack('<I',u.mem_read(E+4,4))[0]==int(not match);assert struct.unpack('<I',u.mem_read(RL,4))[0]==int(match);assert struct.unpack('<I',u.mem_read(DL,4))[0]==int(not match);assert calls==([[T+24,(old|flags)|0x02000000]] if match else [])
  assert u.reg_read(UC_ARM_REG_PRIMASK)==int(depth>0);assert struct.unpack('<I',u.mem_read(0x2000019c,4))[0]==depth
  if match:
   assert struct.unpack('<I',u.mem_read(T+40,4))[0]==0,'event_item_still_linked'
   assert struct.unpack('<I',u.mem_read(T+20,4))[0]==RL,'task_state_not_ready_owned'
   assert struct.unpack('<I',u.mem_read(T+24,4))[0]==(old|flags)|0x82000000
  vals.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(E,24)),bytes(u.mem_read(T,96)),bytes(u.mem_read(DL,20)),bytes(u.mem_read(RL,20)),bytes(u.mem_read(K,56)),calls))
 assert vals[0]==vals[1];rows.append(dict(old_bits=hex(old),set_bits=hex(flags),requested=hex(request),wait_all=bool(all_bits),clear_on_exit=bool(clear),critical_depth=depth,matched=match,returned_bits=hex(expected)))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Actual original/native event-set with real task/list removal and ready-list insertion; no result stubs.','One synthetic coherent waiter and delayed/ready lists, equal priority0 current/blocked tasks; no actual task scheduling, timer, multiwaiter interleave or hardware trace.','Mask/depth0 and1 coherent fixtures; no higher-priority yield tested.','Public source retained for static semantics comparison only, not compiled third comparator.']),indent=2)+'\n');print('PASS',len(rows),'single-waiter actual-unblock comparisons')
