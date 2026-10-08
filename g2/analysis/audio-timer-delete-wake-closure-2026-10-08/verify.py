from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer-aux/aux.elf');receipt_path=root/'g2/analysis/audio-timer-aux-lifetime-closure-2026-10-08/reproduction-receipt.json';receipt=json.loads(receipt_path.read_text());assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256'];segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;CUR=0x20006200;DAEMON=0x20006300;DL=0x20006400;BT=0x20006600;T=BT+8;BA=0x20006680;A=BA+8;END=0x20006800;READY=0x2006a49c;SUSPEND=0x20073d4c;PENDING=0x20073d24;rows=[]
for priority,suspended,dynamic,kind,waiter in itertools.product([46,47,54],[0,1],[0,1],['delayed','suspended'],[0,1]):
 vals=[]
 for native in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
  def append(L,I,owner,value):
   S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
  for L in [READY+20*46,READY+20*47,READY+20*54,DL,SUSPEND,PENDING]:init(L)
  w(CUR+0x2c,47);append(READY+20*47,CUR+4,CUR,0);w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a30,1+waiter);w(0x20074a34,100);w(0x20074a38,47);w(0x20074a3c,1);w(0x20074a58,suspended);w(0x20074a50,150 if waiter and kind=='delayed' else 0xffffffff);w(0x20074ab0,Q)
  def call(a,args=(),stack=(),bounded=False):
   for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000)
   if stack:w(0x2007e000,*stack)
   u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(a|1,0x2007f000,count=100000);assert bounded and boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  call(0x441696,[1,16,Q+80,0],[Q])
  if waiter:
   w(DAEMON+0x2c,priority);append(DL if kind=='delayed' else SUSPEND,DAEMON+4,DAEMON,150);append(Q+0x24,DAEMON+24,DAEMON,64-priority)
  w(BT,0,0x80000038);w(BA,0,0x80000018);w(A,0x53c2a5,0x12345678);w(T+0x1c,A|dynamic);w(T+0x20,0x449399);u.mem_write(T+0x28,b'\x02');w(0x20074158,END,0);w(END,0,0);w(0x2007465c,END);w(0x20074660,0);frees=[];boundary=[];wake=[]
  def hook(u,a,n,d):
   if a==0x456210:frees.append(u.reg_read(UC_ARM_REG_R0))
   if a==0x455370:wake.append(u.reg_read(UC_ARM_REG_R0))
   if a==0x4420bc:boundary.append('before_port_yield');u.emu_stop()
   assert a not in [0x45537e,0x4420f6,0x47e97a],'unexpected assertion/command drain'
  u.hook_add(UC_HOOK_CODE,hook);call(sym['audio_timer_delete_selected'] if native else 0x44953e,[T],bounded=True)
  yields=waiter and priority>47;assert bool(boundary)==bool(yields);assert frees==([A] if dynamic and not yields else []);assert word(Q+56)==1 and word(Q+0x24)==0;assert wake==([Q+0x24] if waiter else [])
  if waiter:
   assert word(DAEMON+0x14)==((DL if kind=='delayed' else SUSPEND) if suspended else READY+20*priority)
   assert word(DAEMON+0x28)==(PENDING if suspended else 0)
  assert word(0x20074a58)==suspended;assert u.reg_read(UC_ARM_REG_BASEPRI)==(0x30 if yields else 0)
  vals.append((boundary,None if boundary else u.reg_read(UC_ARM_REG_R0),frees,wake,bytes(u.mem_read(Q,0x820)),bytes(u.mem_read(READY+20*46,40)),bytes(u.mem_read(READY+20*54,20)),bytes(u.mem_read(SUSPEND,20)),bytes(u.mem_read(PENDING,20)),bytes(u.mem_read(0x20074a20,64))))
 assert vals[0]==vals[1],(priority,suspended,dynamic,kind,waiter);rows.append(dict(sender_priority=47,waiter_priority=priority,suspended=suspended,aux_dynamic=dynamic,state_list=kind,waiter=waiter,boundary=vals[0][0],return_value=vals[0][1],frees=vals[0][2],wake_calls=vals[0][3]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,reused_source=receipt['source'],reused_source_sha256=receipt['source_sha256'],reused_build_receipt=str(receipt_path.relative_to(root)),reused_build_receipt_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Previously sealed independent delete wrapper versus original CMSIS delete, common real queue-copy/event wake/free providers; new nonempty waiter/actual priority integration fixtures.','Synthetic coherent sender47 and blocked daemon46/47/54, finite/indefinite state, suspended0/1. No context handover or live scheduling simulated.','Higher-priority wake stops before port-yield first instruction, while auxiliary remains allocated; no fake yield/exception return.','This explains an ordering constraint and does not establish or refute hardware lifetime defects.']),indent=2)+'\n');print('PASS',len(rows),'delete/waiter wake comparisons')
