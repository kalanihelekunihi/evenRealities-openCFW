from pathlib import Path
import struct,json,hashlib,itertools,sys
D=Path(__file__).resolve().parent;s=D.parent/'case-uart-receive-closure-2026-10-08/verify.py';text=s.read_text().split('rows=[]')[0];a=text.index('entries={w:');b=text.index('\ndef guest',a);text=text[:a]+'entries={}'+text[b:];ns={'__file__':str(s)};exec(text,ns)
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
FRAME=0x20000974;COUNT=0x2000010a;E=0x20006000;rows=[]
def fixture(count,prefix,retry,depth):
 u=ns['guest'](0x20,1,0xff,0,0,0,int(depth>0),0);u.mem_write(FRAME-16,b'\xa7'*1232);u.mem_write(FRAME,bytes(prefix));u.mem_write(COUNT,struct.pack('<H',count));u.mem_write(0x20000893,bytes([retry]));u.mem_write(0x2000019c,struct.pack('<I',depth));u.mem_write(0x200000f0,struct.pack('<I',E));return u
def run(u,entry,poll=False,snapshot=0,depth=0):
 endpoint=[];writes=[]
 def code(u,a,n,d):
  if a in [0x08000928,0x08000e1c]:endpoint.extend([hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);endpoint.extend([u.reg_read(UC_ARM_REG_R2)] if a==0x08000e1c else []);u.emu_stop()
  if poll and a==0x08006e9a:u.emu_stop()
 def write(u,access,a,n,v,d):
  if a==E:
   assert u.reg_read(UC_ARM_REG_PRIMASK)==1,'unmasked_thread_event_clear';writes.append([a,n,v,1])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001)
 if poll:u.reg_write(UC_ARM_REG_R0,snapshot);u.reg_write(UC_ARM_REG_R4,0x200000b8);u.reg_write(UC_ARM_REG_R5,snapshot);u.reg_write(UC_ARM_REG_R7,0)
 u.emu_start(entry|1,0x20000000,count=50000);assert endpoint or u.reg_read(UC_ARM_REG_PC) in [0x20000000,0x08006e9a]
 assert u.reg_read(UC_ARM_REG_PRIMASK)==int(depth>0);assert struct.unpack('<I',u.mem_read(0x2000019c,4))[0]==depth
 return(endpoint,bytes(u.mem_read(FRAME-16,1232)),bytes(u.mem_read(COUNT,2)),bytes(u.mem_read(0x20000893,1)),bytes(u.mem_read(E,4)),writes)
prefixes=[(0xde,0xab,0xcd,0,0,0),(ord('D'),ord('E'),ord('A'),ord('b'),ord('C'),ord('D')),(ord('d'),ord('e'),ord('!'),ord('?'),10,0),(0x5a,0xa5,0x7f,0,0,0),(0x5a,0xa5,0x7f,2,0x3d,0),(0x5a,0xa5,0xcf,0,0,0),(0x5a,0xa5,0xcf,2,0,0),(0x5a,0,0x7f,2,0,0),(0,0,0,0,0,0)]
for count,prefix,retry in itertools.product([0,1,2,3,4,5,6,7,8,9,59,60,61,1199,1200],prefixes,[0,29,30,255]):
 vals=[run(fixture(count,prefix,retry,0),entry) for entry in [0x0800085c,ns['symbols']['case_dispatch_received_frame']]];assert vals[0]==vals[1],('dispatch',count,prefix,retry);rows.append(dict(kind='dispatcher',count=count,prefix=list(prefix),retry=retry,boundary=vals[0][0]))
for x in list(range(256))+[0xffffffff,0x7fffffff]:
 vals=[]
 for entry in [0x08009b94,ns['symbols']['case_hex_digit']]:
  u=fixture(0,prefixes[0],0,0);u.reg_write(UC_ARM_REG_R0,x);run(u,entry);vals.append(u.reg_read(UC_ARM_REG_R0))
 assert vals[0]==vals[1];rows.append(dict(kind='hex_digit',input=x,result=vals[0]))
for snapshot,bits,count,prefix,depth in itertools.product([0,8],[0,8,0x48],[0,1,5,7],prefixes,[0,1]):
 vals=[]
 for entry in [0x08006e86,ns['symbols']['case_poll_frame_action']]:
  u=fixture(count,prefix,29,depth);u.mem_write(E,struct.pack('<I',bits));vals.append(run(u,entry,True,snapshot,depth))
 assert vals[0]==vals[1],('poll',snapshot,bits,count,prefix,depth)
 assert struct.unpack('<I',vals[0][4])[0]==(bits&~8 if snapshot&8 else bits)
 if not vals[0][0] and snapshot&8:assert vals[0][2]==b'\0\0'
 rows.append(dict(kind='poll_bit8_fragment',snapshot=snapshot,bits=bits,count=count,prefix=list(prefix),critical_depth=depth,boundary=vals[0][0]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),counts={k:sum(r['kind']==k for r in rows) for k in sorted({r['kind'] for r in rows})},comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Original/native dispatcher and hex helper; commands08000928/08000e1c stop before first instruction, not modelled returns.','Original poll fragment starts6e86 with seeded snapshot/callee-saved state and stops6e9a; rest of task/startup/loop excluded.','Actual original thread clear wrapper/critical providers execute; event word writes PRIMASK1 and restored coherent nesting checked.','Synthetic allocated frame/count<=1200 and independent snapshot/current-bit inputs; no real IRQ/producer-consumer interleave, close/delete/drain proof.']),indent=2)+'\n');print('PASS',len(rows),'frame dispatcher/polling cases')
