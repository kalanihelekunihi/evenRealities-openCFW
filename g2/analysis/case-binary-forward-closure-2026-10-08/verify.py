from pathlib import Path
import sys,json,struct,itertools,hashlib
D=Path(__file__).resolve().parent;s=D.parent/'case-uart-receive-closure-2026-10-08/verify.py';text=s.read_text().split('rows=[]')[0];a=text.index('entries={w:');b=text.index('\ndef guest',a);text=text[:a]+'entries={}'+text[b:];ns={'__file__':str(s)};exec(text,ns)
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
P=0x20004000;DEST=0x200001b4;E=0x20006000;rows=[]
for n,reserved,destination,mode,declared,event in itertools.product([0,1,2,4,5,6,7,8,31,32,260,262],[0,1],[0,1,3],[0,1,2],[0,2,255,256,-1],[0,E]):
 length=max(n-(5 if mode==0 else 6),0) if declared==-1 else declared;prefix=bytes([0x40,reserved,destination,length&255,(length>>8)&255]);accepted=n>=5 and reserved==0 and destination<=1 and ((length&255)+5==n if mode==0 else length+6==n);vals=[]
 for entry in [0x08000e1c,ns['symbols']['case_forward_nonlocal']]:
  u=ns['guest'](0x20,1,0xff,0,0,0,0,0);u.mem_write(P,bytes((i*7+3)%256 for i in range(300)));u.mem_write(P,prefix);u.mem_write(DEST-16,b'\xa7'*336);u.mem_write(0x200000f0,struct.pack('<I',event));u.mem_write(0x200000f4,bytes(4));u.mem_write(E,struct.pack('<IIIIII',0,0,E+12,0xffffffff,E+12,E+12));u.mem_write(0x20000128,bytes(56));u.mem_write(0x2000019c,bytes(4));events=[];order=[]
  def code(u,a,size,d):
   assert a not in [0x0800c1cc,0x08009170],'unselected_waiter_or_logger'
   if a==0x0800a888:events.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);order.append('event_call')
  def write(u,access,a,size,v,d):
   if DEST<=a<DEST+n and (not order or order[-1]!='copy'):order.append('copy')
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_R2,mode);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  assert events==([[event,0x20 if mode==0 else 0x400]] if accepted else []);assert order==(['event_call','copy'] if accepted else [])
  assert bytes(u.mem_read(DEST,n))==(bytes(u.mem_read(P,n)) if accepted else b'\xa7'*n);assert bytes(u.mem_read(DEST-16,16))==b'\xa7'*16;assert bytes(u.mem_read(DEST+n,16))==b'\xa7'*16
  vals.append((bytes(u.mem_read(DEST-16,336)),bytes(u.mem_read(P,300)),bytes(u.mem_read(E,24)),events,order))
 assert vals[0]==vals[1];rows.append(dict(length=n,reserved=reserved,destination=destination,mode=mode,declared=length,event_handle=hex(event),accepted=accepted,event_before_copy=accepted,notification_failure_fixture=bool(accepted and not event)))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Actual original binary handler for selected nonlocal/non3D contract; original event-set provider executes with NULL or coherent empty event list. No stubs.','Allocated guarded buffers with n<=262; p[2] read precedes length check, no arbitrary pointer/capacity safety proved.','Event-before-copy order observed; no waiting consumer/context switch/IRQ interleave, actual packet acceptance or race proved.','Destination2 local commands/3D aging side effects/trailer-checksum semantics excluded.']),indent=2)+'\n');print('PASS',len(rows),'nonlocal validation/forwarding cases')
