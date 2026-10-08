from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-tick-expiry/tick.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
READY=0x2006a49c;CUR=0x20006000;SECOND=0x20006100;T0=0x20006200;DL=0x20006400;OL=0x20006500;EV=0x20006600
profiles=[[],[(0,0)],[(0,1)],[(0,2)],[(1,2)],[(0,0),(0,2)],[(0,1),(1,2)],[(0,1),(0,1)]];rows=[]
for tick,suspended,yield_pending,peer,event,profile in itertools.product([100,0xfffffffe,0xffffffff],[0,1,2],[0,1],[0,1],[0,1],profiles):
 vals=[];newtick=(tick+1)&0xffffffff
 for entry in [0x45504c,sym['audio_tick_expiry_selected']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
  def append(L,I,owner,value):
   S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
  for L in [READY,READY+20,READY+40,DL,OL,EV]:init(L)
  w(CUR+0x2c,1);append(READY+20,CUR+4,CUR,0)
  if peer:w(SECOND+0x2c,1);append(READY+20,SECOND+4,SECOND,0)
  target=OL if newtick==0 else DL
  for i,(offset,priority) in enumerate(profile):
   T=T0+128*i;w(T+0x2c,priority);w(T+0x68,0x800000);u.mem_write(T+0x6c,b'\x01');append(target,T+4,T,(newtick+offset)&0xffffffff)
   if event:append(EV,T+24,T,7)
  # Profiles with max-tick future item belong to overflow list, not old current list.
  if newtick==0xffffffff and profile and profile[-1][0]==1:
   # Rebuild coherent current/overflow partition using actual sorted task item values.
   init(DL);init(OL)
   for i,(offset,priority) in enumerate(profile):
    T=T0+128*i;value=(newtick+offset)&0xffffffff;append(OL if value<tick else DL,T+4,T,value)
  w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a28,OL);w(0x20074a34,tick);w(0x20074a38,1);w(0x20074a40,3);w(0x20074a44,yield_pending);w(0x20074a48,7);w(0x20074a58,suspended);w(0x20074a50,word(word(DL+12)) if word(DL) else 0xffffffff)
  def hook(u,a,n,d):assert a not in [0x5fa0a4,0x46d86c,0x4420bc],'unexpected assert/yield'
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=50000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
  moved=0
  for i,(offset,priority) in enumerate(profile):
   T=T0+128*i;due=not suspended and offset==0;moved+=due;assert word(T+0x14)==(READY+20*priority if due else target if newtick!=0xffffffff or offset==0 else OL)
   assert word(T+0x68)==0x800000 and bytes(u.mem_read(T+0x6c,1))==b'\x01';assert word(T+0x28)==(0 if due or not event else EV)
  expected=0 if suspended else int(bool(yield_pending or peer or any(offset==0 and priority>=1 for offset,priority in profile)))
  assert u.reg_read(UC_ARM_REG_R0)==expected;assert word(0x20074a34)==(tick if suspended else newtick);assert word(0x20074a40)==3+int(bool(suspended));assert word(0x20074a48)==7+int(not suspended and newtick==0)
  vals.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(CUR,0x640)),bytes(u.mem_read(READY,60)),bytes(u.mem_read(0x20074a20,64))))
 assert vals[0]==vals[1],(tick,suspended,yield_pending,peer,event,profile);rows.append(dict(tick=hex(tick),suspended=suspended,yield_pending=yield_pending,same_priority_peer=peer,event_list=event,profile=profile,moved=moved,return_value=vals[0][0]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Original full tick provider versus independent inline list/ready reconstruction; no result stubs.','Coherent synthetic TCB/list/global state; wrap invariant holds and overflow partition is constructed explicitly.','No real tick IRQ cadence, exception return, blocked-call completion, notification clearing or hardware scheduling.']),indent=2)+'\n');print('PASS',len(rows),'tick expiry comparisons')
