from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=b[32:];receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
POOL=0x20006000;Q=0x20007000;BUFFER=0x20008000;CUR=0x20009000;WAITER=0x20009400;READY=0x2006a49c;DL=0x20009c00

def run(native,capacity=3,size=12,tokens=None,created=0,free_slots=(),operations=(),status=0x5eed0000,ipsr=0,primask=0,basepri=0,running=1,invalidate_after_take=False,waiter=None,suspended=0):
 if tokens is None:tokens=capacity-created+len(free_slots)
 assert 0<=tokens<=capacity
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*[(x&0xffffffff) for x in v]))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
 def append(L,I,owner,value):
  tail=word(L+16);w(I,value,L+8,tail,owner,L);w(tail+4,I);w(L+16,I);w(L,word(L)+1)
 for L in {READY+20*p for p in [12,46,47,54]}|{DL,0x2000a400,0x20073d24,0x20073d4c}:init(L)
 w(CUR+24,56-47);w(CUR+36,CUR);w(CUR+44,47);append(READY+20*47,CUR+4,CUR,0)
 w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a28,0x2000a400);w(0x20074a30,3);w(0x20074a34,100);w(0x20074a38,47);w(0x20074a3c,1);w(0x20074a50,0xffffffff)
 boundary=[];observed=[];icsr=[];invalidate_done=[];call_rows=[]
 def invoke(entry,args):
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);pc=entry|1
  for _ in range(50000):
   u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
   if pc==0x2007f000 or boundary:return u.reg_read(UC_ARM_REG_R0)
  raise AssertionError('instruction-step limit')
 # Actual stock static queue initialization, before observation/native guards.
 u.reg_write(UC_ARM_REG_SP,0x2007e000);w(0x2007e000,Q);invoke(0x441696,[capacity,0,BUFFER,0])
 # invoke reset SP but preserves stack fifth argument initialized above.
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 w(Q+56,tokens);u.mem_write(BUFFER,b'\xa5'*(capacity*size+16))
 head=0
 for slot in reversed(free_slots):w(BUFFER+slot*size,head);head=BUFFER+slot*size
 w(POOL,head,Q,BUFFER,capacity*size,0,size,capacity,created,status)
 if waiter is not None:
  w(WAITER+44,waiter);append(DL,WAITER+4,WAITER,500);append(Q+36,WAITER+24,WAITER,56-waiter);w(0x20074a50,500)
 w(0x20074a58,suspended);w(0x20074a3c,running);u.reg_write(UC_ARM_REG_IPSR,ipsr) if ipsr else None;u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri)
 def code(u,a,n,d):
  if a==0x4420bc:boundary.append('before_port_yield');u.emu_stop();return
  assert a not in [0x441800,0x45537e,0x4420f6,0x5fa0a4] or not native,('unexpected boundary',hex(a))
  if native:assert 0x100000<=a<0x110000,('native escaped',hex(a));observed.append(a)
 def write(u,ac,a,n,v,d):
  if a==0xe000ed04:icsr.append(v)
  if invalidate_after_take and a==Q+56 and v==tokens-1 and not invalidate_done:w(POOL+32,0);invalidate_done.append(True)
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.ctl_flush_tb()
 old={'alloc':0x449d3e,'free':0x449dd4,'create':0x449e98,'pop':0x449eb8,'push':0x449eca,'count':0x441e66,'count_isr':0x441e8a}
 names={'alloc':'osMemoryPoolAlloc','free':'osMemoryPoolFree','create':'CreateBlock','pop':'AllocBlock','push':'FreeBlock','count':'uxQueueMessagesWaiting','count_isr':'uxQueueMessagesWaitingFromISR'}
 for operation in operations:
  kind=operation[0];arg=operation[1] if len(operation)>1 else 0
  p=0 if kind.endswith('_null') else POOL;kind=kind.removesuffix('_null')
  if kind in ['free','push']:
   address=BUFFER+arg*size if isinstance(arg,int) and 0<=arg<capacity else {'null':0,'before':BUFFER-4,'after':BUFFER+capacity*size,'interior':BUFFER+1,'last':BUFFER+capacity*size-1}[arg]
   args=[p,address]
  elif kind=='alloc':args=[p,arg]
  elif kind in ['count','count_isr']:args=[Q]
  else:args=[p]
  before_tokens=word(Q+56);before_n=word(POOL+28);before_head=word(POOL);before_status=word(POOL+32);value=invoke(sym[names[kind]] if native else old[kind],args)
  if boundary:value=None
  if kind=='alloc' and not boundary:
   irq=bool(ipsr or running and (u.reg_read(UC_ARM_REG_PRIMASK) or u.reg_read(UC_ARM_REG_BASEPRI)))
   valid=p and (before_status&0x5eed0000)==0x5eed0000
   if not valid or irq and arg or not before_tokens:assert value==0 and word(Q+56)==before_tokens
   else:
    assert word(Q+56)==before_tokens-1
    if invalidate_after_take:assert value==0
    elif before_head:assert value==before_head and word(POOL+28)==before_n
    elif before_n<capacity:assert value==BUFFER+size*before_n and word(POOL+28)==before_n+1
    else:assert value==0
  if kind in ['count','count_isr']:assert value==word(Q+56)
  call_rows.append({'operation':operation,'return_value':value if kind!='push' else None,'tokens':word(Q+56),'head':hex(word(POOL)),'created':word(POOL+28),'status':hex(word(POOL+32)),'buffer_hex':bytes(u.mem_read(BUFFER,capacity*size+16)).hex(),'boundary':list(boundary),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'primask':u.reg_read(UC_ARM_REG_PRIMASK)})
  if boundary:break
 if native:assert observed
 regions=[(POOL,36),(Q,80),(BUFFER,capacity*size+16),(CUR,0x2000),(READY,1120),(0x20073d24,80),(0x2000309c,4),(0x20074a20,0x100)]
 return {'calls':call_rows,'icsr_writes':icsr,'state_sha256':hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in regions)).hexdigest(),'current_state_container':hex(word(CUR+20)),'current_event_container':hex(word(CUR+40)),'invalidated':bool(invalidate_done)}
rows=[]
def compare(c):
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for capacity,size,ipsr in itertools.product([1,3,5],[4,12,208],[0,16]):
 operations=[['alloc',0]]*(capacity+1)+[['free',i] for i in reversed(range(capacity))]+[['alloc',0]]*(capacity+1)
 compare(dict(capacity=capacity,size=size,ipsr=ipsr,operations=operations))
for ipsr,primask,basepri,running,tokens,wait in itertools.product([0,16],[0,1],[0,0x30],[0,1],[0,1],[0,1,5,0xffffffff]):
 compare(dict(capacity=1,created=1-tokens,ipsr=ipsr,primask=primask,basepri=basepri,running=running,operations=[['alloc',wait],['count'],['count_isr']]))
for status,ipsr in itertools.product([0,0x5eec0000,0x5eed0000,0x5eedffff],[0,16]):compare(dict(status=status,ipsr=ipsr,operations=[['alloc',0],['free',0]]))
for arg,ipsr,tokens in itertools.product(['null','before','after','interior','last',0],[0,16],[0,1,3]):compare(dict(created=3,tokens=tokens,ipsr=ipsr,operations=[['free',arg]]))
for ipsr in [0,16]:
 compare(dict(ipsr=ipsr,operations=[['alloc_null',0],['free_null',0]]))
 compare(dict(ipsr=ipsr,invalidate_after_take=True,operations=[['alloc',0]]))
 compare(dict(ipsr=ipsr,created=3,tokens=1,operations=[['alloc',0]]))
# Duplicate-free is a synthetic misuse probe, not a claim of valid API use.
for ipsr in [0,16]:compare(dict(ipsr=ipsr,created=3,tokens=0,operations=[['free',0],['free',0],['alloc',0],['alloc',0]]))
for ipsr,waiter in itertools.product([0,16],[46,47,54]):compare(dict(ipsr=ipsr,created=3,tokens=0,waiter=waiter,operations=[['free',0]]))
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Coherent pool fixtures and separate explicit invalid/misuse probes; no full boot or pool creation provider.','Status invalidation after token decrement is synthetic environmental mutation, not observed race.','Actual task yield boundary stops continuation; IRQ request is passive, no exception delivery.']},indent=2)+'\n');print('PASS',len(rows),'pool ownership/ISR/timeout comparisons')
