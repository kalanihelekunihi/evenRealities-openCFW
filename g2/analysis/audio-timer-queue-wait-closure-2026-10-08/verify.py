from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer-queue-wait/wait.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;CUR=0x20006200;AUDIO=0x20006300;PEER=0x20006400;RECEIVER=0x20006500;DL=0x20006600;OL=0x20006700;SUSPEND=0x20073d4c;READY=0x2006a49c;MSG=0x20006800;rows=[]
cases=[c for c in itertools.product([0,1],[0,1,50,0xffffffff],[0,1],[100,0xfffffff0],[0,1],[0,1]) if not(c[0] and c[5])]
for queued,wait,indefinite,tick,peer,receiver in cases:
 vals=[]
 for native in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
  def append(L,I,owner,value):
   S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
  def call(a,args=(),stack=()):
   for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000)
   if stack:w(0x2007e000,*stack)
   u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(a|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
  for L in [READY+20*47,READY+20*54,DL,OL,SUSPEND]:init(L)
  w(CUR+0x2c,54);w(AUDIO+0x2c,47);append(READY+20*54,CUR+4,CUR,0x11111111);append(READY+20*47,AUDIO+4,AUDIO,0)
  if peer:w(PEER+0x2c,54);append(READY+20*54,PEER+4,PEER,0)
  w(CUR+0x18,0x8000000a);w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a28,OL);w(0x20074a30,2+peer+receiver);w(0x20074a34,tick);w(0x20074a38,54);w(0x20074a3c,1);w(0x20074a50,0xffffffff);w(0x20074a58,1)
  call(0x441696,[1,16,Q+80,0],[Q]);w(MSG,3,0,0x20005000,0)
  if queued:call(0x4417ee,[Q,MSG,0,0])
  if receiver:
   w(RECEIVER+0x2c,53);deadline=(tick+500)&0xffffffff;append(OL if deadline<tick else DL,RECEIVER+4,RECEIVER,deadline);append(Q+0x24,RECEIVER+24,RECEIVER,8);w(0x20074a50,deadline if deadline>=tick else 0xffffffff)
  def hook(u,a,n,d):assert a not in [0x4420bc,0x45532c,0x4420f6],'unexpected yield/assert'
  u.hook_add(UC_HOOK_CODE,hook);call(sym['audio_timer_restricted_wait'] if native else 0x442030,[Q,wait,indefinite])
  assert word(Q+0x38)==queued and bytes(u.mem_read(Q+0x44,2))==b'\xff\xff';assert word(0x20074a58)==1 and u.reg_read(UC_ARM_REG_BASEPRI)==0
  if queued:assert word(CUR+0x14)==READY+20*54 and word(CUR+0x28)==0
  else:
   wake=(tick+wait)&0xffffffff;dest=SUSPEND if indefinite else OL if wake<tick else DL
   assert word(CUR+0x14)==dest and word(CUR+0x28)==Q+0x24;assert word(CUR+4)==(0x11111111 if indefinite else wake);assert word(CUR+0x18)==0x8000000a
  assert word(Q+0x24)==receiver+int(not queued);assert word(READY+20*54)==peer+queued
  vals.append((bytes(u.mem_read(Q,0x820)),bytes(u.mem_read(READY+20*47,20)),bytes(u.mem_read(READY+20*54,20)),bytes(u.mem_read(SUSPEND,20)),bytes(u.mem_read(0x20074a20,64))))
 assert vals[0]==vals[1],(queued,wait,indefinite,tick,peer,receiver);rows.append(dict(queued=queued,wait=hex(wait),indefinite=indefinite,tick=hex(tick),same_priority_peer=peer,existing_receiver=receiver,blocked=not bool(queued)))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Original restricted queue wait and independent event append/delayed-block C; shared actual critical/list and queue-unlock peers, real static queue init/copy.','Coherent synthetic daemon-priority54/audio-priority47 lists; scheduler suspended1. No exception return, task scheduling, producer or real tick cadence.','Queued-message cases have no existing waiting receiver; inconsistent stable queue state is excluded.','Provider does not itself request a context switch; process-or-block caller resume/yield remains a separate boundary.']),indent=2)+'\n');print('PASS',len(rows),'restricted queue wait comparisons')
