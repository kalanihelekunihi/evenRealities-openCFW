from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];receipt=json.loads((D/'integration-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
Q=0x20006000;BUF=0x20007000;MSG=0x20008000;OUT=0x20008200;WOKEN=0x20008400;CUR=0x20009000;WAITER=0x20009400;DL=0x20009c00;READY=0x2006a49c;PENDING=0x20073d24;SUSPEND=0x20073d4c;rows=[]
def payload(i,size):return bytes((j*17+i*43+11)&255 for j in range(size))
def run(native,kind,capacity=1,size=12,prefill=0,position=0,wait=0,waiter=None,suspended=0,running=1,primask=0,basepri=0,ipsr=0,txlock=-1,taskcount=3,priority=0,null_queue=False,null_message=False,woken_initial=0,woken_null=False,execution_mode="stepped",tick=100,base=47,held=1,holder_null=False):
 boundary=[]
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
 def append(L,I,owner,value):
  end=L+8;tail=word(end+8);w(I,value,end,tail,owner,L);w(tail+4,I);w(end+8,I);w(L,word(L)+1)
 def invoke(at,args=(),stack=()):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
  if stack:w(0x2007e000,*stack)
  if execution_mode=='continuous':
   u.emu_start(at|1,0x2007f000,count=100000);return
  assert execution_mode=='stepped'
  pc=at|1
  for step in range(10000):
   u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
   if pc==0x2007f000 or boundary:break
  else:raise AssertionError('instruction-step budget exhausted')
 for L in {READY+20*p for p in [46,47,54]}|{DL,PENDING,SUSPEND,0x2000a400}:init(L)
 w(CUR+24,17);w(CUR+36,CUR);w(CUR+44,47);append(READY+20*47,CUR+4,CUR,0);w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a28,0x2000a400);w(0x20074a30,taskcount);w(0x20074a34,tick);w(0x20074a38,47);w(0x20074a3c,1);w(0x20074a50,0xffffffff)
 invoke(0x441696,[capacity,size,BUF,0],[Q]);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 for i in range(prefill):
  u.mem_write(MSG,payload(i,size));invoke(0x4417ee,[Q,MSG,0,0]);assert u.reg_read(UC_ARM_REG_R0)==1
 init(READY+20*base) if base!=47 else None;w(CUR+96,base,held);w(Q,0);w(Q+8,0 if holder_null else CUR);u.mem_write(MSG,payload(9,size));u.mem_write(OUT,b'\xa5'*256);w(WOKEN,woken_initial)
 if waiter is not None:
  w(WAITER+44,waiter);append(DL,WAITER+4,WAITER,500);append(Q+(16 if kind=='receive' else 36),WAITER+24,WAITER,64-waiter);w(0x20074a50,500)
 w(0x20074a58,suspended);w(0x20074a3c,running);u.mem_write(Q+69,struct.pack('b',txlock));u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_IPSR,ipsr) if ipsr else None
 assert u.reg_read(UC_ARM_REG_IPSR)==ipsr
 boundary=[];wake=[];native_instructions=[];writes=[];extra_payload_writes=[]
 def code(u,a,n,d):
  if a==0x4420bc:boundary.append({'kind':'before_port_yield','queue_count':word(Q+56)});u.emu_stop();return
  assert a not in [0x441800,0x45537e,0x4420f6,0x44196c,0x441990,0x4419b6],'unexpected fatal continuation'
  if native:assert 0x100000<=a<0x110000,('source execution escaped',hex(a));native_instructions.append(a)
  if a in [0x455370,sym['opencfw_ready_remove_event_list']&~1]:wake.append(u.reg_read(UC_ARM_REG_R0))
 def store(u,access,a,n,v,d):
  if kind=='receive' and OUT+size<=a<OUT+256:extra_payload_writes.append({'address':hex(a),'size':n,'value':v,'pc':hex(u.reg_read(UC_ARM_REG_PC))})
  if a==0xe000ed04:writes.append({'address':hex(a),'value':v})
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,store);u.ctl_flush_tb()
 original={'send':0x4417ee,'receive':0x441b0a,'isr_send':0x441952,'cmsis_put':0x449abe,'scheduler_state':0x4558a4,'irq_context':0x44900e};names={'send':'xQueueGenericSend','receive':'xQueueReceive','isr_send':'xQueueGenericSendFromISR','cmsis_put':'audio_cmsis_queue_put','scheduler_state':'audio_scheduler_state','irq_context':'audio_cmsis_irq_context'}
 q=0 if null_queue else Q;m=0 if null_message else MSG
 args={'send':[q,m,wait,position],'receive':[q,OUT,wait],'isr_send':[q,m,0 if woken_null else WOKEN,position],'cmsis_put':[q,m,priority,wait],'scheduler_state':[],'irq_context':[]}[kind]
 invoke(sym[names[kind]] if native else original[kind],args);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
 ret=None if boundary else u.reg_read(UC_ARM_REG_R0);count=word(Q+56)
 if kind=='scheduler_state':assert ret==(1 if not running else 0 if suspended else 2)
 elif kind=='irq_context':assert ret==int(bool(ipsr or running and (primask or basepri)))
 elif kind=='receive' and not boundary:
  assert ret==int(prefill>0) and count==max(prefill-1,0)
  if prefill and size:assert bytes(u.mem_read(OUT,size))==payload(0,size)
 elif kind in ['send','isr_send'] and not boundary:assert ret==int(prefill<capacity or position==2) and count==((prefill+1 if size==0 else min(prefill+1,capacity)) if position==2 else prefill+int(prefill<capacity)),(native,kind,capacity,size,prefill,position,ret,count)
 elif kind=='cmsis_put' and not boundary:
  irq=bool(ipsr or running and (primask or basepri));expected=-4 if null_queue or null_message or irq and wait else 0 if prefill<capacity else -2 if wait else -3;assert ret==(expected&0xffffffff),(args,expected,ret)
 regions=[(Q,80),(BUF,capacity*size),(OUT,256),(WOKEN,4),(CUR,0x2000),(READY+20*46,20*9),(PENDING,80),(0x2000309c,4),(0x20074a20,0x100)]
 return {'return_value':ret,'boundary':boundary,'queue_count':count,'woken':word(WOKEN),'wake_calls':wake,'icsr_writes':writes,'extra_payload_writes':extra_payload_writes,'rx_lock':int.from_bytes(u.mem_read(Q+68,1),'little',signed=True),'tx_lock':int.from_bytes(u.mem_read(Q+69,1),'little',signed=True),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'current_state_container':hex(word(CUR+20)),'current_event_container':hex(word(CUR+40)),'next_unblock_tick':word(0x20074a50),'suspend_count':word(0x20074a58),'ipsr':u.reg_read(UC_ARM_REG_IPSR),'state_digest':hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in regions)).hexdigest(),'mutex_holder':word(Q+8),'mutexes_held':word(CUR+100),'task_priority':word(CUR+44),'source_guard_pass':bool(native_instructions) if native else None}
def compare(c):
 o=run(False,**c);n=run(True,**c);assert n.pop('source_guard_pass');o.pop('source_guard_pass');assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))

for base,held,holder_null,waiter in itertools.product([12,47],[1,2],[False,True],[None,46,54]):compare(dict(kind='send',capacity=1,size=0,base=base,held=held,holder_null=holder_null,waiter=waiter))
(D/'integration-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Mutex-give chain executes native disinherit/list/critical/wake providers, stops before actual port yield.','Synthetic coherent held count/base priority and waiters; no exception return or full lifecycle proof.']},indent=2)+'\n');print('PASS',len(rows),'source-only mutex queue give comparisons')
