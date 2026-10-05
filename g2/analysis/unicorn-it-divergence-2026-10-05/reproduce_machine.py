#!/usr/bin/env python3
"""Offline diagnostic: execute three unchanged O2 function bodies, no C/compiler/stubs."""
import hashlib,json,struct
from pathlib import Path
import unicorn as u
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
fixture=json.loads((Path(__file__).with_name('machine-fixture.json')).read_text())
BODIES=[(b['address'],b['size']) for b in fixture['bodies']]
def bytes_at(a,n):
 b=next(b for b in fixture['bodies'] if b['address']==a and b['size']==n);raw=bytes.fromhex(b['hex']);assert hashlib.sha256(raw).hexdigest()==b['sha256'];return raw
def run(mode,due=2,limit=20000,trace=False,hook_range=(1,0)):
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 cpu.mem_map(0x10000,4096)
 for a,n in BODIES:cpu.mem_write(a,bytes_at(a,n))
 cpu.mem_map(0x20000000,0x80000);cpu.mem_map(0x8000000,4096)
 w=lambda a,v:cpu.mem_write(a,struct.pack('<I',v&0xffffffff))
 r=lambda a:struct.unpack('<I',cpu.mem_read(a,4))[0]
 delayed=0x20026000;overflow=0x20026080;ready=0x2006a49c;tasks=[0x20024000,0x20024100];current=0x20024300
 def init(a):
  for i,v in enumerate([0,a+8,0xffffffff,a+8,a+8]):w(a+4*i,v)
 def add(a,t,value):
  item=t+4;tail=r(a+16)
  for i,v in enumerate([value,a+8,tail,t,a]):w(item+4*i,v)
  w(tail+4,item);w(a+16,item);w(a,r(a)+1)
 for a in [delayed,overflow]+[ready+20*i for i in range(8)]:init(a)
 w(current+44,1);add(ready+20,current,0)
 for t in tasks[:due]:w(t+44,3);add(delayed,t,10)
 for a,v in {0x20074a20:current,0x20074a24:delayed,0x20074a28:overflow,0x20074a34:9,0x20074a38:1,0x20074a50:10}.items():w(a,v)
 cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,0x8000001);cpu.reg_write(UC_ARM_REG_BASEPRI,0x30)
 history=[];accesses=[]
 def code(uc,pc,size,data):history.append([hex(pc),hex(uc.reg_read(UC_ARM_REG_R2)),hex(uc.reg_read(UC_ARM_REG_XPSR))])
 def mem(uc,access,a,size,value,data):pass
 if trace:cpu.hook_add(u.UC_HOOK_CODE,code)
 if mode!='none':cpu.hook_add({'read':u.UC_HOOK_MEM_READ,'write':u.UC_HOOK_MEM_WRITE,'both':u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE}[mode],mem,begin=hook_range[0],end=hook_range[1])
 error=None
 try:cpu.emu_start(0x10001,0x8000000,count=limit)
 except u.UcError as e:error=str(e)
 return dict(mode=mode,due=due,count=limit,code_hook=trace,error=error,pc=hex(cpu.reg_read(UC_ARM_REG_PC)),registers={s:hex(cpu.reg_read(v)) for s,v in [('r0',UC_ARM_REG_R0),('r1',UC_ARM_REG_R1),('r2',UC_ARM_REG_R2),('r3',UC_ARM_REG_R3),('xpsr',UC_ARM_REG_XPSR)]},returned=cpu.reg_read(UC_ARM_REG_R0),tick=r(0x20074a34),top=r(0x20074a38),next_unblock=r(0x20074a50),lists={hex(a):bytes(cpu.mem_read(a,20)).hex() for a in [delayed,ready+20,ready+60]},tasks={hex(t):bytes(cpu.mem_read(t+4,44)).hex() for t in tasks[:due]},history=history)
if __name__=='__main__':
 rows=[run(mode,due,limit,trace) for due in [1,2] for limit in [0,20000] for trace in [False,True] for mode in ['none','read','write','both']]
 for record in rows:
  if record['due']==2 and record['mode']!='none':
   assert record['error']=='Invalid memory read (UC_ERR_READ_UNMAPPED)' and record['pc']=='0x10296'
   assert record['registers']['r2']=='0x0'
   assert struct.unpack('<IIIII',bytes.fromhex(record['lists']['0x2006a4d8']))[:2]==(1,0x2006a4e0)
  else:
   assert record['error'] is None and record['pc']=='0x8000000'
   assert (record['returned'],record['tick'],record['top'],record['next_unblock'])==(1,10,3,0xffffffff)
   assert struct.unpack('<IIIII',bytes.fromhex(record['lists']['0x20026000']))==(0,0x20026008,0xffffffff,0x20026008,0x20026008)
   count,index,value,head,tail=struct.unpack('<IIIII',bytes.fromhex(record['lists']['0x2006a4d8']))
   assert (count,index,value,head,tail)==(record['due'],0x2006a4e0,0xffffffff,0x20024004,0x20024004 if record['due']==1 else 0x20024104)
 out=ROOT/'g2/build/foundation/unicorn-it-divergence/machine-repro.json'
 out.write_text(json.dumps(dict(unicorn_version=u.__version__,elf_sha256=fixture['elf_sha256'],bodies=[dict(address=hex(a),size=n,sha256=hashlib.sha256(bytes_at(a,n)).hexdigest()) for a,n in BODIES],records=rows),indent=2)+'\n')
 for r in rows:print(r['due'],r['count'],r['code_hook'],r['mode'],r['error'],r['pc'])
