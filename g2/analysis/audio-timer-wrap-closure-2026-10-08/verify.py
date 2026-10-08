from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer-wrap/wrap.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;L=0x20006200;O=0x20006300;BT=0x20006400;T=BT+8;BA=0x20006480;A=BA+8;END=0x20006600;OTHER=0x20006700;OUTPUT=0x20006a00;USER=0x53c2a4;rows=[];last=0xfffffff0
for present,autoreload,overflow,now,deleted,suspend_count in itertools.product([0,1],[0,1],[0,1],[0,15,last,last+1],[0,1],[0,1]):
 vals=[]
 for native in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def call(a,args=(),stack=(),bounded=False):
   for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000)
   if stack:w(0x2007e000,*stack)
   u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(a|1,0x2007f000,count=100000);assert bounded and boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
  def append(L,I,owner,value):
   S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
  w(0x20074a3c,1);w(0x20074a30,0);w(0x20074a34,last);w(0x20074ab8,last);w(0x20074ab0,Q);w(0x20074aa8,L);w(0x20074aac,O);call(0x441696,[1,16,Q+80,0],[Q]);init(L);init(O)
  w(BT,0,0x80000038);w(BA,0,0x80000018);w(A,USER|1,0x12345678);w(T+0x18,50);w(T+0x1c,A|1);w(T+0x20,0x449399);u.mem_write(T+0x28,bytes([present|2|(4 if autoreload else 0)]));w(T+4,last,L+8,L+8,T,0)
  if present:append(L,T+4,T,last)
  if overflow:append(O,OTHER+4,OTHER,25)
  w(0x20074158,END,0);w(END,0,0);w(0x2007465c,END);w(0x20074660,0);w(OUTPUT,0xa5a5a5a5);boundary=[];expired=[];frees=[]
  def hook(u,a,n,d):
   if a==0x456210:frees.append(u.reg_read(UC_ARM_REG_R0))
   if a==0x47e83a:expired.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
   if a==USER:boundary.append((hex(a),u.reg_read(UC_ARM_REG_R0)));u.emu_stop()
   assert a not in [0x4420bc,0x47e97a],'unexpected yield/command drain'
  u.hook_add(UC_HOOK_CODE,hook)
  if deleted:call(0x44953e,[T]);assert u.reg_read(UC_ARM_REG_R0)==0
  assert frees==([A] if deleted else []);w(0x20074a58,suspend_count);w(0x20074a34,now);call(sym['audio_timer_sample_time_selected'] if native else 0x47e916,[OUTPUT],bounded=True)
  wrapping=now<last;callback=wrapping and present
  if callback:
   assert boundary==[(hex(USER),0x12345678)] and expired==[(last,0xffffffff)];assert word(OUTPUT)==0xa5a5a5a5 and word(0x20074ab8)==last;assert word(0x20074aa8)==L and word(L)==0
   if autoreload:assert word(T+0x14)==O and word(T+4)==34 and u.mem_read(T+0x28,1)[0]&1
   else:assert word(T+0x14)==0 and not u.mem_read(T+0x28,1)[0]&1
  else:
   assert not boundary and word(OUTPUT)==int(wrapping) and word(0x20074ab8)==now and u.reg_read(UC_ARM_REG_R0)==now;assert word(0x20074aa8)==(O if wrapping else L)
  assert word(0x20074a58)==suspend_count
  assert word(Q+56)==deleted # sampled-time helper does not drain queued Delete
  vals.append((boundary,expired,frees,word(OUTPUT),None if boundary else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(Q,0x800)),bytes(u.mem_read(0x20074158,8)),bytes(u.mem_read(0x2007465c,20)),bytes(u.mem_read(0x20074aa8,20))))
 assert vals[0]==vals[1],(present,autoreload,overflow,now,deleted);rows.append(dict(suspend_count=suspend_count,old_timer=present,autoreload=autoreload,overflow_timer=overflow,now=hex(now),delete_queued=deleted,boundary=vals[0][0],expired_arguments=[[hex(a),hex(b)] for a,b in vals[0][1]],switched_output=hex(vals[0][3]),return_value=vals[0][4]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual sample-time/switch-lists and independent C wrapper/loop with shared original tick-get and expire/reload/adapter peers.','Constructed coherent current/overflow timers; real queued-delete auxiliary free can precede sample-time call. No live task timing asserted.','Old-list callback stops before user first instruction, before list swap/last-time/output update; no callback return fabricated.','Autoreload branch executes real insertion into overflow before callback; no repeated callback body or catch-up scheduler execution.']),indent=2)+'\n');print('PASS',len(rows),'timer wrap comparisons')
