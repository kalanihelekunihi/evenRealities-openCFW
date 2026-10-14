#!/usr/bin/env python3
"""Actual CASE heap initialization/allocation/coalescing/free graph at native SP."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,random
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave033-native-timer-message-width';E=P/'final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20002c88;STOP=0x2000f000;HEAP_START=0x20001c88;HEAP_END=0x20002888;rows=[];sizes=[0,1,7,8,9,16,17,64,512,1024,2040,3000,3040,3064,3065,3072,0x7fffffff,0x80000000,0xffffffff]
cases=[{'sizes':[s],'order':'forward'} for s in sizes]+[{'sizes':[1,7,8,9,16,32,64,256,512],'order':o} for o in ['forward','reverse','shuffle']]+[{'sizes':[1000]*4,'order':o} for o in ['forward','reverse']]+[{'sizes':[24]*80,'order':o} for o in ['forward','reverse','shuffle']]
def run(native,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);saved=[0x45670000+i for i in range(8)];low=SP;accesses=[]
 def observe(uc,address,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP));assert low>=HEAP_END,('stack_heap_overlap',native,c,hex(low))
 def access(uc,kind,address,size,value,data):
  if address in [0x20000180,0x20000184,0x20000190,0x20000198,0x20000158] and len(accesses)<64:accesses.append((hex(address),size,'read' if kind==16 else 'write',hex(uc.reg_read(UC_ARM_REG_PC))))
 u.hook_add(UC_HOOK_CODE,observe);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,access)
 def invoke(address,arg):
  u.reg_write(UC_ARM_REG_R0,arg)
  for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(address|1,STOP,count=200000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
  assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
  return u.reg_read(UC_ARM_REG_R0)
 pointers=[];snapshots=[]
 for i,size in enumerate(c['sizes']):
  p=invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],size);pointers.append(p)
  if p:
   assert p%8==0 and HEAP_START+8<=p<HEAP_END
   u.mem_write(p,bytes((i+j*13)&255 for j in range(size)))
  snapshots.append(hashlib.sha256(bytes(u.mem_read(0x20000000,HEAP_END-0x20000000))).hexdigest())
 order=list(range(len(pointers)))
 if c['order']=='reverse':order.reverse()
 elif c['order']=='shuffle':random.Random(0xb3e8).shuffle(order)
 for i in order:
  invoke(0x0800c030 if native else sy['case_boot_heap_free'],pointers[i]);snapshots.append(hashlib.sha256(bytes(u.mem_read(0x20000000,HEAP_END-0x20000000))).hexdigest())
 ram=bytes(u.mem_read(0x20000000,HEAP_END-0x20000000));assert struct.unpack_from('<I',ram,0x180)[0]==3064 and struct.unpack_from('<I',ram,0x194)[0]==HEAP_START and struct.unpack_from('<I',ram,HEAP_START-0x20000000+4)[0]==3064;assert u.reg_read(UC_ARM_REG_PRIMASK)==0
 return {'pointers':pointers,'snapshots':snapshots,'final_ram_sha256':hashlib.sha256(ram).hexdigest(),'stack_bytes':SP-low,'accesses':accesses}
for i,c in enumerate(cases):
 a=run(True,c);b=run(False,c);fields=[k for k in a if k not in ['stack_bytes','accesses'] and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'case':c,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((i,c,fields))
 rows.append({'case':c,'pointers':a['pointers'],'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes'],'native_accesses':a['accesses'],'source_accesses':b['accesses']})
r={'status':'PASS_FULL_HEAP_ALLOCATE_FREE_COALESCE_NATIVE_SP','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'native_max_stack_bytes':max(x['native_stack_bytes'] for x in rows),'source_max_stack_bytes':max(x['source_stack_bytes'] for x in rows),'limits':['Real heap/scheduler-suspend/resume/coalescing bodies, no providers cut or return injection','RAM snapshots exclude native1024-byte top stack window; prove bounded SP stays above heap footer, not global IRQ/reentrancy budget','Valid client writes within allocated requested lengths; no doublefree/corruptmetadata qualification here']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['native_max_stack_bytes'],r['source_max_stack_bytes'])
