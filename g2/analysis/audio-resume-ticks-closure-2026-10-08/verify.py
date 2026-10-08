from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-resume-ticks/resume.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
READY=0x2006a49c;PENDING=0x20073d24;DL=0x20006400;OL=0x20006500;EV=0x20006600;CUR=0x20006000;P=0x20006100;TIMEOUT=0x20006200;rows=[]
for nt,suspended,pp,tp,tick,initial_yield,pending in itertools.product([1,2,3],[1,2],[0,1,2],[0,1,2],[100,0xfffffffe],[0,1],[0,1]):
 vals=[]
 for native in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
  def append(L,I,owner,value):
   S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
  for L in [READY,READY+20,READY+40,PENDING,DL,OL,EV]:init(L)
  w(CUR+0x2c,1);append(READY+20,CUR+4,CUR,0)
  if pending:
   deadline=(tick+1)&0xffffffff;w(P+0x2c,pp);w(P+0x68,0x800000);u.mem_write(P+0x6c,b'\x02');append(OL if deadline<tick else DL,P+4,P,deadline);append(PENDING,P+24,P,0)
  deadline=(tick+2)&0xffffffff;w(TIMEOUT+0x2c,tp);u.mem_write(TIMEOUT+0x6c,b'\x01');append(OL if deadline<tick else DL,TIMEOUT+4,TIMEOUT,deadline);append(EV,TIMEOUT+24,TIMEOUT,7)
  w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a28,OL);w(0x20074a30,2+pending);w(0x20074a34,tick);w(0x20074a38,1);w(0x20074a40,nt);w(0x20074a44,initial_yield);w(0x20074a50,word(word(DL+12)) if word(DL) else 0xffffffff);w(0x20074a58,suspended);boundary=[];ticks=[]
  def hook(u,a,n,d):
   if a==(sym['audio_tick_expiry_selected']&~1 if native else 0x45504c):ticks.append(word(0x20074a34))
   if a==0x4420bc:boundary.append(hex(a));u.emu_stop()
   assert a not in [0x454de0,0x45507a,0x4420f6],'unexpected kernel assert continuation'
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start((sym['audio_resume_pending_ticks_selected'] if native else 0x454dcc)|1,0x2007f000,count=100000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  processed=suspended==1;expired=processed and nt>=2;mustyield=processed and bool(initial_yield or pending and pp>=1 or expired and tp>=1)
  assert bool(boundary)==mustyield;assert len(ticks)==(nt if processed else 0);assert word(0x20074a34)==((tick+nt)&0xffffffff if processed else tick);assert word(0x20074a40)==(0 if processed else nt);assert word(0x20074a58)==suspended-1
  if pending:assert word(P+0x14)==(READY+20*pp if processed else DL);assert word(P+0x28)==(0 if processed else PENDING);assert word(P+0x68)==0x800000 and u.mem_read(P+0x6c,1)==b'\x02'
  assert word(TIMEOUT+0x14)==(READY+20*tp if expired else OL if tick==0xfffffffe else DL);assert word(TIMEOUT+0x28)==(0 if expired else EV);assert u.mem_read(TIMEOUT+0x6c,1)==b'\x01'
  vals.append((boundary,None if boundary else u.reg_read(UC_ARM_REG_R0),ticks,bytes(u.mem_read(CUR,0x620)),bytes(u.mem_read(READY,60)),bytes(u.mem_read(PENDING,20)),bytes(u.mem_read(0x20074a20,64)),u.reg_read(UC_ARM_REG_BASEPRI)))
 assert vals[0]==vals[1],(nt,suspended,pp,tp,tick,initial_yield,pending);rows.append(dict(pending_ticks=nt,suspend_count=suspended,pending_priority=pp,timeout_priority=tp,tick=hex(tick),initial_yield=initial_yield,pending_task=pending,timeout_expired=expired,boundary=vals[0][0],replayed_from_ticks=[hex(t) for t in vals[0][2]]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Original full selected resume with pending-ready transfer and accumulated tick replay versus independent C resume/tick provider.','Real critical/next-unblock peers, constructed task/list state, tick wrap included; no child-result stubs.','Yield stops before port first instruction; no exception return or real scheduler timing.','Pending notification task is moved before tick replay and removed from timeout list; received marker/value unchanged by this provider.']),indent=2)+'\n');print('PASS',len(rows),'resume/tick replay comparisons')
