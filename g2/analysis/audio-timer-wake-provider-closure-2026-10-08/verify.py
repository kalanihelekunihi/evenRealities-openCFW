from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:]
receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
Q=0x20006000;CUR=0x20006200;DL=0x20006400;READY=0x2006a49c;SUSPEND=0x20073d4c;PENDING=0x20073d24;rows=[]
def fixture(priority,suspended,kind,ready_existing=False,pending_existing=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
 def append(L,I,owner,value):
  S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
 for L in {READY+20*p for p in [46,47,54]}|{DL,SUSPEND,PENDING,Q+16,Q+36}:init(L)
 w(CUR+44,47);append(READY+20*47,CUR+4,CUR,0)
 if ready_existing:
  t=0x20006280;w(t+44,priority);append(READY+20*priority,t+4,t,0);w(READY+20*priority+4,t+4)
 if pending_existing:
  t=0x20006300;w(t+44,priority);append(DL,t+4,t,100);append(PENDING,t+24,t,64-priority);w(PENDING+4,t+24)
 w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a30,10);w(0x20074a34,50);w(0x20074a38,max(47,priority) if ready_existing else 47);w(0x20074a3c,1);w(0x20074a58,suspended);w(0x20074a50,100 if pending_existing else 150)
 return u,w,word,append

def execute(native,mode,priority=54,suspended=1,kind='delayed',event_index=0,ready_existing=False,pending_existing=False,tx=0,rx=0,receivers=1,senders=0):
 u,w,word,append=fixture(priority,suspended,kind,ready_existing,pending_existing);tasks=[]
 if mode=='wake':receivers=1;senders=0
 for L,count,base in [(Q+36,receivers,0x20006500),(Q+16,senders,0x20006600)]:
  for i in range(count):
   t=base+64*i;tasks.append(t);w(t+44,priority);append(DL if kind=='delayed' else SUSPEND,t+4,t,150+i);append(L,t+24,t,64-priority)
  if event_index and count:w(L+4,base+24)
 if mode=='unlock':u.mem_write(Q+68,struct.pack('bb',rx,tx))
 trace=[]
 def hook(u,a,n,d):
  if native:assert 0x100000<=a<0x110000,'source execution escaped native region'
  if a in [0x455370,sym['opencfw_ready_remove_event_list']&~1]:
   assert u.reg_read(UC_ARM_REG_BASEPRI)==0x30;trace.append(['event_unblock',u.reg_read(UC_ARM_REG_R0)])
  names={0x4420d0:'enter_critical',0x4420e8:'exit_critical',0x4555e6:'missed_yield',sym['stock_enter_critical']&~1:'enter_critical',sym['stock_exit_critical']&~1:'exit_critical',sym['stock_missed_yield']&~1:'missed_yield'}
  if a in names:trace.append([names[a]])
  assert a not in [0x4420bc,0x45537e,0x4420f6],'unexpected yield/assert boundary'
 u.hook_add(UC_HOOK_CODE,hook)
 u.reg_write(UC_ARM_REG_BASEPRI,0x30 if mode=='wake' else 0);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R0,Q+36 if mode=='wake' else Q)
 at=(sym['opencfw_ready_remove_event_list'] if mode=='wake' else sym['audio_public_queue_unlock']) if native else (0x455370 if mode=='wake' else 0x441f88)
 u.emu_start(at|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 changed=1 if mode=='wake' else min(max(tx,0),receivers)+min(max(rx,0),senders)
 assert word(PENDING)==(int(pending_existing)+changed if suspended else int(pending_existing))
 if mode=='unlock':assert bytes(u.mem_read(Q+68,2))==b'\xff\xff'
 assert word(0x20074a44)==int(priority>47 and changed>0)
 assert u.reg_read(UC_ARM_REG_BASEPRI)==(0x30 if mode=='wake' else 0)
 regions=[(0x2000309c,4),(Q,0x780),(READY+20*46,20*9),(PENDING,80),(0x20074a20,0x100)]
 digest=hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in regions)).hexdigest()
 return {'return_value':u.reg_read(UC_ARM_REG_R0) if mode=='wake' else None,'trace':trace,'state_digest':digest,'pending_count':word(PENDING),'yield_pending':word(0x20074a44),'next_unblock_tick':word(0x20074a50),'suspend_count':word(0x20074a58),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'task_states':[{'tcb':hex(t),'state_container':hex(word(t+20)),'event_container':hex(word(t+40))} for t in tasks]}
for priority,suspended,kind,event_index,ready_existing,pending_existing in itertools.product([46,47,54],[0,1,2],['delayed','suspended'],[0,1],[False,True],[False,True]):
 c=dict(mode='wake',priority=priority,suspended=suspended,kind=kind,event_index=event_index,ready_existing=ready_existing,pending_existing=pending_existing);o=execute(False,**c);n=execute(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for tx,rx,receivers,senders,priority in itertools.product([-1,0,1,2,127],[-1,0,1,2,127],[0,1,2],[0,1,2],[46,47,54]):
 c=dict(mode='unlock',priority=priority,suspended=1,tx=tx,rx=rx,receivers=receivers,senders=senders);o=execute(False,**c);n=execute(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Pinned public source bodies compiled unchanged except exported queue-unlock name and stock queue-set/ABI macros.','Synthetic coherent lists,TCB prefix and scheduler globals; no physical context handover.','Critical/mask/missed-yield helpers now compile to source; fatal-exit/assert targets remain original execution-cut dependencies never entered by valid cases.','Final semantic RAM/list/return/mask and call-order comparison, not instruction-level store order or byte equality.']},indent=2)+'\n');print('PASS',len(rows),'wake/unlock comparisons')
