#!/usr/bin/env python3
"""Five actual application creators through CMSIS/native constructors and port."""
import hashlib,itertools,json,struct
from pathlib import Path
from unicorn import UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CONTEXTS={'a':(0x2000668c,0x43b8c),'f':(0x20006608,0x46924),'g':(0x200066d8,0x46a44),'b':(0x200065e0,0x44ef0),'e':(0x200065bc,0x4509c)}
def verify(stock,candidate,syms,baseline):
 receipt=BASE/'board/application-thread-verification.json';receipt.unlink(missing_ok=True);configuration=BASE/'native-task-lifecycle/configuration-evidence.json';rows=json.loads(configuration.read_text())['rows'];comparisons=0;workflows=0;created=[]
 for u in (stock,candidate):
  try:u.mem_map(0xe000e000,0x1000)
  except UcError:pass
 def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
 def snapshot(u):
  records=[]
  for row in rows:
   cb=int(row['control_block'],16);stack=int(row['stack'],16);data=bytearray(u.mem_read(stack,row['stack_bytes']));tcb=bytes(u.mem_read(cb,112));context,entry=CONTEXTS[row['letter']];assert syms[row['context']]==context
   if row['letter'] in created:
    sp=word(u,cb);assert word(u,context+8)==cb and word(u,cb+84)==row['stack_bytes']//4 and word(u,cb+44)==row['priority'];assert tcb[104:112]==bytes((0,0,0,0,0,2,0,0))
    assert word(u,sp+64)==0x1000000 and word(u,sp+36)==0 and word(u,sp+32)==0xfffffffd
    assert word(u,sp+60)==((int(row['task_entry'],16) if u is stock else syms[row['task_symbol']])|1) and word(u,sp+56)==((0x854e0 if u is stock else syms['prvTaskExitError'])|1)
    if u is candidate:struct.pack_into('<I',data,sp+60-stack,int(row['task_entry'],16)|1);struct.pack_into('<I',data,sp+56-stack,0x854e1)
   records.append((tcb,bytes(data),word(u,context+8)))
  return (records,bytes(u.mem_read(0x20007810,76)),bytes(u.mem_read(0x2002ad94,1220)),bytes(u.mem_read(0x200077fc,20)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI))
 saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 try:
  for order,mask,pattern in itertools.product(itertools.permutations(rows),(0,1),(0,0xa5)):
   created.clear()
   for u in (stock,candidate):
    u.mem_write(0x20000000,baseline[id(u)]);u.mem_write(0xe000ed04,bytes(4));u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,0)
    for row in rows:u.mem_write(int(row['control_block'],16),bytes([0x93 if pattern else 0])*112);u.mem_write(int(row['stack'],16),bytes([pattern])*row['stack_bytes'])
   for index,row in enumerate(order):
    name='r1_thread_create_'+row['letter'];context,entry=CONTEXTS[row['letter']]
    for u in (stock,candidate):
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((entry if u is stock else syms[name])|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     assert word(u,0x20007824)==index+1 and word(u,0x20007840)==index+1 and word(u,int(row['control_block'],16)+88)==index+1
    created.append(row['letter']);assert snapshot(stock)==snapshot(candidate),(name,mask,pattern,[r['letter'] for r in order]);comparisons+=1
   expected=int(next(r['control_block'] for r in rows if r['letter']=='b'),16)
   for u in (stock,candidate):assert word(u,0x2000781c)==expected and word(u,0x2000782c)==52 and bytes(u.mem_read(0x200077fc,20))==bytes(20)
   workflows+=1
 finally:
  for u in (stock,candidate):u.mem_write(0x20000000,baseline[id(u)])
 receipt.write_text(json.dumps(dict(application_sha256=sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'),board_report_sha256=sha(BASE/'board/report.json'),verification_driver_sha256=sha(ROOT/'r1/tools/verify_native_board.py'),creation_driver_sha256=sha(Path(__file__)),thread_report_sha256=sha(BASE/'rtos-thread-new/report.json'),configuration_sha256=sha(configuration),comparisons=comparisons,workflows=workflows,thread_creators=5,creation_orders=120,provider_interception=False,tcb_bytes_compared_per_snapshot=560,stack_bytes_compared_per_snapshot=sum(r['stack_bytes'] for r in rows),scope='Actual five application creators/CMSIS wrapper/native static factories/ready lists/critical/port, all120 orders and mask/dirty-memory variants; handles, TCBs, full stacks, counters and prekernel highest-priority selection',limitations=['Task code is not executed. Only authenticated initial-frame task-PC and return-LR fields are normalized. This verifies five creation callbacks, not firmware boot order, complete task set, scheduler/context switching, task cleanup or hardware execution.']),indent=2)+'\n');print(comparisons,'application thread comparisons;',workflows,'workflows; all120 creation orders; no provider interception')
