from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-timer-daemon-order/daemon.elf');elfhash=hashlib.sha256(elf.read_bytes()).hexdigest();segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;L=0x20006200;OVERFLOW=0x20006300;BT=0x20006400;T=BT+8;BA=0x20006480;A=BA+8;END=0x20006600;USER=0x53c2a4;rows=[]
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 return u
def w(u,a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def invoke(u,at,args=(),stack=()):
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
 if stack:w(u,0x2007e000,*stack)
 u.emu_start(at|1,0x2007f000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000

def run(native,static,aux_dynamic,command,now,reuse,empty,autoreload=False,wrap=False):
 u=machine();w(u,0x20074a3c,1);w(u,0x20074a30,0);w(u,0x20074a34,now);w(u,0x20074ab8,0xffffffff if wrap else now);w(u,0x20074ab0,Q);w(u,0x20074aa8,L);w(u,0x20074aac,OVERFLOW)
 invoke(u,0x441696,[1,16,Q+80,0],[Q]);w(u,BT,0,0x80000038);w(u,BA,0,0x80000018);w(u,A,USER|1,0x12345678);w(u,T+0x18,50);w(u,T+0x1c,A|aux_dynamic);w(u,T+0x20,0x449399);u.mem_write(T+0x28,bytes([1|(2 if static else 0)|(4 if autoreload else 0)]));I=T+4;S=L+8
 if empty:w(u,L,0,S,0xffffffff,S,S);w(u,I,150,0,0,T,0);u.mem_write(T+0x28,bytes([2 if static else 0]))
 else:w(u,L,1,S,0xffffffff,I,I);w(u,I,150,S,S,T,L)
 OS=OVERFLOW+8;w(u,OVERFLOW,0,OS,0xffffffff,OS,OS);
 if wrap:
  w(u,L,0,S,0xffffffff,S,S);w(u,OVERFLOW,1,OS,0xffffffff,I,I);w(u,I,10,OS,OS,T,OVERFLOW)
 w(u,0x20074158,END,0);w(u,END,0,0);w(u,0x2007465c,END);w(u,0x20074660,0);w(u,0x2007466c,0)
 frees=[]
 def free(u,a,n,d):
  if a==0x456210:frees.append(u.reg_read(UC_ARM_REG_R0))
 u.hook_add(UC_HOOK_CODE,free)
 if command==5:invoke(u,0x44953e,[T]);assert u.reg_read(UC_ARM_REG_R0)==0
 elif command==3:invoke(u,0x47e7b0,[T,3,0,0],[0]);assert u.reg_read(UC_ARM_REG_R0)==1
 if reuse:
  invoke(u,0x456110,[8]);assert u.reg_read(UC_ARM_REG_R0)==A;w(u,A,USER|1,0xcafebabe)
 before=dict(queue_count=word(u,Q+56),list_count=word(u,L),aux_freed=A in frees,aux_word=word(u,A),aux_arg=word(u,A+4))
 trace=[];boundary=[];in_iteration=[]
 next_entry=(sym['audio_timer_next_expiry']&~1) if native else 0x47e8f2
 def code(u,a,n,d):
  if a==next_entry:
   if in_iteration:boundary.append(dict(kind='next_iteration'));u.emu_stop();return
   in_iteration.append(True);trace.append('next_expiry')
  if a in [0x47e88c,sym['audio_timer_process_or_block']&~1]:trace.append('process_or_block')
  if a==0x47e97a:trace.append('drain_commands')
  if a==USER:boundary.append(dict(kind='user_callback_entry',address=hex(a),argument=u.reg_read(UC_ARM_REG_R0)));u.emu_stop();return
  if a==0x442030:
   trace.append('restricted_queue_wait_entry')
   if command==0:boundary.append(dict(kind='restricted_wait_entry',queue=u.reg_read(UC_ARM_REG_R0),ticks=u.reg_read(UC_ARM_REG_R1),wait_indefinitely=u.reg_read(UC_ARM_REG_R2)));u.emu_stop();return
  assert a!=0x45504c,'unselected tick processing'
  if a==0x47ea90:
   assert wrap,'unselected tick wrap';trace.append('switch_lists')
 u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R0,0);u.emu_start((sym['audio_timer_daemon'] if native else 0x47e878)|1,0x2007f000,count=300000);assert boundary
 after=dict(queue_count=word(u,Q+56),list_count=word(u,L),current_list=word(u,0x20074aa8),overflow_list=word(u,0x20074aac),timer_status=bytes(u.mem_read(T+0x28,1)).hex(),timer_id=word(u,T+0x1c),frees=frees,free_bytes=word(u,0x20074660),last_tick=word(u,0x20074ab8),scheduler_suspended=word(u,0x20074a30),basepri=u.reg_read(UC_ARM_REG_BASEPRI))
 return dict(before=before,trace=trace,boundary=boundary,after=after,state_digest=hashlib.sha256(bytes(u.mem_read(Q,0x620))+bytes(u.mem_read(0x20074158,8))+bytes(u.mem_read(0x2007465c,20))).hexdigest())
for static,aux_dynamic,command,now in itertools.product([0,1],[0,1],[3,5],[149,150,151]):
 c=dict(static=static,aux_dynamic=aux_dynamic,command=command,now=now,reuse=False,empty=False);o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n)
 if now>=150:
  assert o['boundary'][0]['kind']=='user_callback_entry' and o['before']['queue_count']==o['after']['queue_count']==1 and 'drain_commands' not in o['trace']
  if command==5 and aux_dynamic:assert o['before']['aux_freed']
 else:assert o['boundary'][0]['kind']=='next_iteration' and o['after']['queue_count']==0 and o['after']['list_count']==0
 rows.append(dict(inputs=c,**o))
for static in [0,1]:
 c=dict(static=static,aux_dynamic=1,command=5,now=150,reuse=True,empty=False);o=run(False,**c);n=run(True,**c);assert o==n and o['boundary'][0]['argument']==0xcafebabe;rows.append(dict(inputs=c,**o))
for empty in [False,True]:
 c=dict(static=1,aux_dynamic=0,command=0,now=149,reuse=False,empty=empty);o=run(False,**c);n=run(True,**c);assert o==n and o['boundary'][0]['kind']=='restricted_wait_entry';rows.append(dict(inputs=c,**o))

for static,command,now in itertools.product([0,1],[3,5],[150,151]):
 c=dict(static=static,aux_dynamic=1,command=command,now=now,reuse=False,empty=False,autoreload=True);o=run(False,**c);n=run(True,**c);assert o==n and o['after']['list_count']==1 and o['after']['queue_count']==1;rows.append(dict(inputs=c,**o))
for static,command in itertools.product([0,1],[3,5]):
 c=dict(static=static,aux_dynamic=1,command=command,now=0,reuse=False,empty=False,wrap=True);o=run(False,**c);n=run(True,**c);assert o==n and o['boundary'][0]['kind']=='next_iteration' and o['after']['current_list']==OVERFLOW and o['after']['overflow_list']==L and o['after']['queue_count']==0;rows.append(dict(inputs=c,**o))

assert hashlib.sha256(elf.read_bytes()).hexdigest()==elfhash
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=elfhash,comparisons=rows,limits=['Five native daemon/expiry/sample/process functions; actual original command-drain/queue/allocator/list/scheduler/adapter/reload/wrap providers remain explicit.','Actual callback first instruction,empty-queue wait entry or next iteration is an execution boundary; no callback/blocking return stubs.','Single-shot andselected autoreload/tick-wrap paths,zero modeled task count/running1 andconstructed list/queue/heap state. Live task wakeup,IRQ/TCB scheduling andhardware lifetime hazard remain unverified.']),indent=2)+'\n');print('PASS',len(rows),'actual-daemon-order cases')
