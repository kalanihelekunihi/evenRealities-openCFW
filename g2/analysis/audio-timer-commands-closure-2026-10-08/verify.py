from pathlib import Path
import itertools,struct,json,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer/timer.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;L=0x20006200;B=0x20006400;T=B+8;END=B+128;rows=[]
for static,attached,autoreload,commands in itertools.product([0,1],[0,1],[0,1],[[],[3],[5],[3,5]]):
 vals=[]
 for entry in [0x47e97a,sym['audio_timer_drain_stop_delete']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def invoke(at,args,stack=()):
   for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000)
   if stack:w(0x2007e000,*stack)
   u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(at|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
  w(0x20074a3c,1);w(0x20074a30,0);w(0x20074a34,100);w(0x20074ab8,100);w(0x20074ab0,Q);w(0x20074aa8,L)
  invoke(0x441696,[10,16,Q+80,0],[Q])
  w(B,0,0x80000038);w(T+0x18,50);w(T+0x1c,0);w(T+0x20,0);u.mem_write(T+0x28,bytes([(2 if static else 0)|(1 if attached else 0)|(4 if autoreload else 0)]))
  S=L+8;I=T+4;w(L,attached,S,0xffffffff,I if attached else S,I if attached else S)
  if attached:w(I,150,S,S,T,L)
  w(0x20074158,END,0);w(END,0,0);w(0x2007465c,END);w(0x20074660,0);w(0x2007466c,0)
  timer_before=bytes(u.mem_read(T,44));list_before=bytes(u.mem_read(L,20))
  for command in commands:
   invoke(0x47e7b0,[T,command,0,0],[0]);assert u.reg_read(UC_ARM_REG_R0)==1
  assert bytes(u.mem_read(T,44))==timer_before and bytes(u.mem_read(L,20))==list_before
  before_status=bytes(u.mem_read(T+0x28,1));assert before_status==bytes([(2 if static else 0)|(1 if attached else 0)|(4 if autoreload else 0)])
  frees=[];removes=[]
  def code(u,a,n,d):
   if a==0x456210:frees.append(u.reg_read(UC_ARM_REG_R0))
   if a==0x4560e8:removes.append(u.reg_read(UC_ARM_REG_R0))
   assert a not in [0x47ea90,0x4420bc,0x45504c],'unselected tick wrap/yield/tick'
  u.hook_add(UC_HOOK_CODE,code);invoke(entry,[])
  freed=5 in commands and not static;assert frees==([T] if freed else []);assert removes==([I] if commands and attached else []);assert struct.unpack('<I',u.mem_read(Q+56,4))[0]==0;assert struct.unpack('<I',u.mem_read(L,4))[0]==(attached if not commands else 0);assert struct.unpack('<I',u.mem_read(0x20074660,4))[0]==(56 if freed else 0)
  if commands and not freed:assert u.mem_read(T+0x28,1)==bytes([(2 if static else 0)|(4 if autoreload else 0)])
  vals.append((frees,removes,bytes(u.mem_read(Q,0x600)),bytes(u.mem_read(0x20074158,8)),bytes(u.mem_read(0x2007465c,20)),u.reg_read(UC_ARM_REG_BASEPRI),bytes(u.mem_read(0x2000309c,4))))
 assert vals[0]==vals[1],(static,attached,autoreload,commands);rows.append(dict(static=static,initially_linked=attached,autoreload=autoreload,commands=commands,sent_without_timer_mutation=True,frees=vals[0][0],removals=vals[0][1]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual generic command enqueue and queue initializer, selected daemon drain3/5 versus independent command state machine; actual queue/list/free/time peers shared. No stubs.','Synthetic coherent timer/list/heap; empty task waitlists, taskcount0/running1, tick100 unchanged, no timer expiry/callback/tick wrap.','No real daemon scheduling or CMSIS auxiliary callback-block ownership; producers are executed before consumer synthetically.']),indent=2)+'\n');print('PASS',len(rows))
