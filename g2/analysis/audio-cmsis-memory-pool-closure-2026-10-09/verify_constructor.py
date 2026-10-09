from pathlib import Path
import json,struct,itertools,hashlib
D=Path(__file__).resolve().parent
exec((D/'verify.py').read_text().split('rows=[]\ndef compare')[0])
POOL=0x20040000;BUFFER=0x20042000;CUR=0x20038000;WAITER=0x20038400;DL=0x20038c00
ATTR=0x20040200;NAME=0x20040300

def constructor(native,capacity=3,size=12,cb_size=116,mp_size=None,array_offset=0,ipsr=0,attrs_null=False,cb_null=False,array_null=False,follow=False,full_heap=False,heap_ops=None,full_failure=False,logging=False):
 rounded=((size+3)&0xffffffff)>>2;array_size=(capacity*rounded*4)&0xffffffff
 if mp_size is None:mp_size=array_size
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*[(x&0xffffffff) for x in v]))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
 for L in [READY+20*47,DL,0x2000a400,0x20073d24,0x20073d4c]:init(L)
 end=READY+20*47+8;w(CUR+4,0,end,end,CUR,READY+20*47);w(end+4,CUR+4);w(end+8,CUR+4);w(READY+20*47,1);w(CUR+24,9);w(CUR+36,CUR);w(CUR+44,47)
 w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a28,0x2000a400);w(0x20074a30,1);w(0x20074a34,100);w(0x20074a38,47);w(0x20074a3c,1);w(0x20074a50,0xffffffff)
 u.mem_write(POOL,b'\xa5'*132);u.mem_write(BUFFER,b'\xa5'*8192);u.mem_write(NAME,b'offline\0');w(ATTR,NAME,0,0 if cb_null else POOL,cb_size,0 if array_null else BUFFER+array_offset,mp_size)
 boundary=[];seen=[];calls=[];last_pc=[];w(0x200742f0,0xdeadbeef if logging else 0)
 def code(u,a,n,d):
  if full_failure and last_pc and a==last_pc[-1]:boundary.append({'kind':'nonreturning_failure_spin'});u.emu_stop();return
  last_pc.append(a)
  if full_failure and a==0x473036:boundary.append({'kind':'before_opaque_formatter','buffer':hex(u.reg_read(UC_ARM_REG_R0)),'format':hex(u.reg_read(UC_ARM_REG_R1))});u.emu_stop();return
  if not full_heap and a in [0x456110,0x456210,sym['pvPortMalloc']&~1,sym['vPortFree']&~1]:boundary.append({'kind':'before_heap_provider','provider':'malloc' if a in [0x456110,sym['pvPortMalloc']&~1] else 'free','argument':u.reg_read(UC_ARM_REG_R0)});u.emu_stop();return
  if heap_ops is not None and (a==(sym['audio_heap_assert_failure']&~1) or a==0x5fa0a4 and (u.reg_read(UC_ARM_REG_LR)&~1) in [0x4561a6,0x456200,0x45622c,0x456240]):boundary.append({'kind':'before_heap_assert'});u.emu_stop();return
  if not full_failure and a in [0x46d85e,sym['audio_heap_malloc_failed']&~1]:boundary.append({'kind':'before_malloc_failed_hook'});u.emu_stop();return
  if a==0x4420bc:boundary.append({'kind':'before_port_yield'});u.emu_stop();return
  if native:assert 0x100000<=a<0x110000,hex(a);seen.append(a)
 u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_IPSR,ipsr) if ipsr else None
 def invoke(entry,args):
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);pc=entry|1
  for _ in range(100000):
   u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
   if pc==0x2007f000 or boundary:return u.reg_read(UC_ARM_REG_R0)
  raise AssertionError('instruction limit')
 if heap_ops is not None:
  pointers=[]
  for op,argument in heap_ops:
   if op=='alloc':
    value=invoke(sym['pvPortMalloc'] if native else 0x456110,[argument]);pointers.append(value if not boundary else None)
    if not boundary:
     assert value&7==0
     header=value-8;charged=word(header+4)&0x7fffffff
     assert word(header)==0 and word(header+4)&0x80000000
     assert charged>=argument+8
   elif op=='free':value=invoke(sym['vPortFree'] if native else 0x456210,[0 if argument=='null' else pointers[argument]])
   else:value=invoke(sym['audio_main_heap_initialize'] if native else 0x456280,[])
   calls.append({'operation':[op,argument],'value':value if op=='alloc' and not boundary else None,'free_bytes':word(0x20074660),'minimum_free':word(0x20074664),'alloc_count':word(0x20074668),'free_count':word(0x2007466c),'boundary':list(boundary)})
   if boundary:break
  if native:assert seen
  return {'calls':calls,'boundary':boundary,'heap_state_sha256':hashlib.sha256(bytes(u.mem_read(0x20004558,0x2f000))+bytes(u.mem_read(0x20074158,8))+bytes(u.mem_read(0x2007465c,20))).hexdigest(),'suspend':word(0x20074a58),'critical_nesting':word(0x2000309c),'basepri':u.reg_read(UC_ARM_REG_BASEPRI)}
 value=invoke(sym['osMemoryPoolNew'] if native else 0x449c14,[capacity,size,0 if attrs_null else ATTR]);calls.append({'call':'new','value':None if boundary else value})
 if not boundary:
  if ipsr or not capacity or not size:assert value==0
  elif value:
   object_address=value; assert (value==POOL or full_heap) and word(object_address+4)==object_address+36 and word(object_address+12)==array_size
   assert word(object_address+20)==size and word(object_address+24)==capacity and word(object_address+28)==0
   assert word(object_address+36+56)==capacity
   assert word(object_address+32)==0x5eed0000|int(cb_null or attrs_null)|(2 if array_null or attrs_null else 0)
   if follow:
    allocated=[]
    for i in range(capacity):
     block=invoke(sym['osMemoryPoolAlloc'] if native else 0x449d3e,[object_address,0]);assert block==word(object_address+8)+size*i;allocated.append(block);calls.append({'call':'alloc','value':block})
    assert invoke(sym['osMemoryPoolAlloc'] if native else 0x449d3e,[object_address,0])==0;calls.append({'call':'exhausted','value':0})
    for block in reversed(allocated):calls.append({'call':'free','value':invoke(sym['osMemoryPoolFree'] if native else 0x449dd4,[object_address,block])})
    for block in allocated:
     returned=invoke(sym['osMemoryPoolAlloc'] if native else 0x449d3e,[object_address,0]);assert returned==block;calls.append({'call':'realloc','value':returned})
 if native:assert seen
 return {'calls':calls,'boundary':boundary,'pool_hex':bytes(u.mem_read(POOL,132)).hex(),'heap_state_sha256':hashlib.sha256(bytes(u.mem_read(0x20004558,0x2f000))+bytes(u.mem_read(0x20074158,8))+bytes(u.mem_read(0x2007465c,20))).hexdigest(),'array_sha256':hashlib.sha256(bytes(u.mem_read(BUFFER,8192))).hexdigest(),'critical_nesting':word(0x2000309c),'basepri':u.reg_read(UC_ARM_REG_BASEPRI)}
rows=[]
def compare(c):
 o=constructor(False,**c);n=constructor(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for capacity,size in itertools.product([1,3,5],[4,8,12,208]):compare(dict(capacity=capacity,size=size,follow=True))
for capacity,size,cb_size,array_offset in itertools.product([1,3],[1,3,4,5,12,205],[36,115,116,132],[0,1]):compare(dict(capacity=capacity,size=size,cb_size=cb_size,array_offset=array_offset))
for mp_size in [0,35,36,40]:compare(dict(capacity=3,size=12,mp_size=mp_size))
for c in [dict(attrs_null=True),dict(cb_null=True,cb_size=0),dict(array_null=True,mp_size=0),dict(ipsr=16),dict(capacity=0),dict(size=0)]:compare(c)
for capacity,size,attrs_null,cb_null,array_null in itertools.product([1,3],[4,12,208],[False,True],[False,True],[False,True]):
 compare(dict(capacity=capacity,size=size,attrs_null=attrs_null,cb_null=cb_null,array_null=array_null,cb_size=0 if cb_null else 116,mp_size=0 if array_null else capacity*size,full_heap=True,follow=True))
(D/'constructor-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Full static constructor/native queue initialization; dynamic allocations stop before existing heap provider, no allocator stub.','Nonnull malformed attribute geometry acceptance probes mapped ample synthetic memory; not safe valid-use or observed hardware corruption.','Followed lifecycle cases use slot size multiple of4; odd-size raw-stride behavior observed by construction, not arbitrarily declared safe.']},indent=2)+'\n');print('PASS',len(rows),'static constructor/ownership comparisons')
