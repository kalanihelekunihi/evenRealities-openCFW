#!/usr/bin/env python3
"""Consecutive task factories using actual heap/critical/list/port providers."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_native_task_create':0x983b8,'r1_native_task_create_static':0x98418,'osThreadNew':0x7d818,'osThreadTerminate':0x7d8d6}
def verify(stock,candidate,syms,baseline):
 cmsis=True
 receipt=BASE/'board/task-termination-verification.json';receipt.unlink(missing_ok=True);comparisons=0;workflows=0;published=[]
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,0x1000)
  except UcError:pass
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def target(u,lr):
  first,second=struct.unpack('<2H',bytes(u.mem_read((lr&~1)-4,4)));assert first&0xf800==0xf000 and second&0xd000==0xd000;sign=(first>>10)&1;offset=(sign<<24)|((1^((second>>13)&1)^sign)<<23)|((1^((second>>11)&1)^sign)<<22)|((first&0x3ff)<<12)|((second&0x7ff)<<1)
  return ((lr&~1)+offset-(1<<25 if sign else 0))&0xffffffff
 def snapshot(u):
  heap=bytearray(u.mem_read(0x2001e588,51212));arena=bytearray(u.mem_read(0x20001000,0x5000))
  end=word(u,0x200077fc)
  if end:
   block=0x2001e588
   while block<end:
    value=word(u,block+4);size=value&0x7fffffff;assert size and not size&7 and block+size<=end
    if value&0x80000000:
     lr=word(u,block+8);assert target(u,lr)==(0x855a0 if u is stock else syms['pvPortMalloc']&~1)
     if u is stock:assert lr in (0x983cf,0x983d9)
     else:
      assert (syms['r1_native_task_create']&~1)<(lr&~1)<(syms['r1_native_task_create_static']&~1)
      struct.pack_into('<I',heap,block-0x2001e588+8,word(stock,block+8))
    block+=size
  for tcb,parameter,mode in published:
   sp=word(u,tcb);assert word(u,sp+64)==0x1000000 and word(u,sp+60)==0x12345679 and word(u,sp+36)==parameter and word(u,sp+32)==0xfffffffd
   assert bytes(u.mem_read(tcb+108,4))==bytes((0,mode,0,0)) and word(u,tcb+104)==0
   address=sp+56;lr=word(u,address);assert lr==((0x854e0 if u is stock else syms['prvTaskExitError'])|1)
   if u is candidate:
    if 0x2001e588<=address<0x2002ad88:struct.pack_into('<I',heap,address-0x2001e588,0x854e1)
    else:assert 0x20001000<=address<0x20006000;struct.pack_into('<I',arena,address-0x20001000,0x854e1)
  return (bytes(heap),bytes(arena),bytes(u.mem_read(0x200077fc,20)),bytes(u.mem_read(0x20007810,76)),bytes(u.mem_read(0x2002ad94,1220)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 try:
  for static1,static2,depth,priorities,pattern in itertools.product((False,True),(False,True),(32,64,128),((0,55),(55,0),(15,15)),(0,0xa5)):
   published.clear();effective=[]
   for u in (stock,candidate):
    u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0x2001e588,bytes([pattern])*51200);u.mem_write(0x20001000,bytes([0x93])*0x5000);u.mem_write(0x20003000,b'task_name_longer_than_thirty_two_characters\0');u.mem_write(0x20003100,b'b\0');u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_BASEPRI,0)
   for index,static in enumerate((static1,static2)):
    parameter=0x12340000+index;output=0x20002100+index*512;tcb=0x20002000+index*512;name=0x20003000+index*256;name_fn='r1_native_task_create_static' if static else 'r1_native_task_create';args=(0x12345679,name,depth,parameter,priorities[index],0x20004000+index*4096,tcb) if static else (0x12345679,name,depth,parameter,priorities[index],output);expected_depth=depth;expected_priority=priorities[index]
    if cmsis:
     attribute=0 if not static and depth==64 else 0x20003200+index*256;expected_depth=depth if attribute else 256;expected_priority=24 if not attribute or not priorities[index] else priorities[index]
     for u in (stock,candidate):u.mem_write(0x20003200+index*256,struct.pack('<9I',name,0,tcb if static else 0,112 if static else 0,0x20004000+index*4096 if static else 0,depth*4,priorities[index],1,0))
     name_fn='osThreadNew';args=(0x12345679,parameter,attribute)
    effective.append(expected_priority);results=[]
    for u in (stock,candidate):
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
     for i,value in enumerate(args[4:]):u.mem_write(0x2003f000+i*4,struct.pack('<I',value))
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     
     try:u.emu_start((ENTRIES[name_fn] if u is stock else syms[name_fn])|1,0x20000100,count=2000000)
     except UcError as e:raise AssertionError((name_fn,u is stock,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_LR)),syms[name_fn])) from e
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append(u.reg_read(UC_ARM_REG_R0) if static or cmsis else word(u,output));assert static or cmsis or u.reg_read(UC_ARM_REG_R0)==1
    assert results[0]==results[1];tcb=results[0];published.append((tcb,parameter,2 if static else 0));assert snapshot(stock)==snapshot(candidate),(static1,static2,depth,priorities,pattern,index)
    for u in (stock,candidate):assert word(u,tcb+84)==expected_depth and word(u,tcb+44)==expected_priority and word(u,tcb+88)==index+1 and word(u,0x20007824)==index+1 and word(u,0x20007840)==index+1
    comparisons+=1
   expected=published[1][0] if effective[1]>=effective[0] else published[0][0]
   for u in (stock,candidate):assert word(u,0x2000781c)==expected
   other=next(t[0] for t in published if t[0]!=expected)
   for target_tcb in (other,expected):
    for u in (stock,candidate):
     u.reg_write(UC_ARM_REG_R0,target_tcb);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((ENTRIES['osThreadTerminate'] if u is stock else syms['osThreadTerminate'])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and u.reg_read(UC_ARM_REG_R0)==0 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     assert word(u,0x20007824)==1 and word(u,0x20007820)==(1 if target_tcb==expected else 0)
    assert snapshot(stock)==snapshot(candidate),(static1,static2,depth,priorities,pattern,hex(target_tcb))
    comparisons+=1
   for repeat in range(2):
    for u in (stock,candidate):
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((0x84fe8 if u is stock else syms['r1_native_task_idle_cleanup'])|1,(0x8501a if u is stock else 0x20000100),count=2000000)
     assert u.reg_read(UC_ARM_REG_PC)==(0x8501a if u is stock else 0x20000100) and u.reg_read(UC_ARM_REG_SP)==0x2003f000
     if u is candidate:assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     else:assert u.reg_read(UC_ARM_REG_R4)==0x2000781c and u.reg_read(UC_ARM_REG_R6)==0x2002b230
     assert word(u,0x20007824)==0 and word(u,0x20007820)==0 and word(u,0x2002b230)==0
     if not static1 or not static2:assert word(u,0x20007800)==51184 and word(u,0x20007808)==2*(int(not static1)+int(not static2)) and word(u,0x2000780c)==2*(int(not static1)+int(not static2))
    assert snapshot(stock)==snapshot(candidate),(static1,static2,depth,priorities,pattern,'idle cleanup',repeat)
    comparisons+=1
   workflows+=1
 finally:
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 result=dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),termination_driver_sha256=sha(Path(__file__)),termination_report_sha256=sha(BASE/'rtos-task-termination/report.json'),thread_report_sha256=sha(BASE/'rtos-thread-new/report.json'),comparisons=comparisons,workflows=workflows,provider_interception=False,scope='Actual CMSIS creation and termination, native constructors, heap/free, critical, state and list providers; static/dynamic pairs, delete other task, defer current task, then reclaim through actual idle cleanup body and repeat empty cleanup',limitations=['Prekernel graph without native PendSV execution. Idle cleanup is compared at explicit native loop boundaries0x84fe8..0x8501a; no standalone native function ABI is claimed. The complete idle loop/hooks/tickless scheduling remain gated. Authenticated heap caller BL/initial stack LR normalization. No task entry execution, hardware or image byte equality proof.'])
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(comparisons,'task termination graph comparisons;',workflows,'workflows; no provider interception')
