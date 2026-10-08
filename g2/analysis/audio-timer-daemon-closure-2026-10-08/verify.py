from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer-daemon/daemon.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
# Locked creation ADR uses aligned PC: ((0x47E6B2+4)&~3)+0x1C5 = 0x47E879.
assert ((0x47e6b2+4)&~3)+0x1c5==0x47e879
Q=0x20006000;L=0x20006200;BT=0x20006400;T=BT+8;BA=0x20006480;A=BA+8;END=0x20006600;USER=0x53c2a4;cases=[(ts,ad,cmd,now,False) for ts,ad,cmd,now in itertools.product([0,1],[0,1],[0,3,5],[149,150,151])]+[(ts,1,5,now,True) for ts,now in itertools.product([0,1],[150,151])];rows=[]
for ts,ad,cmd,now,reuse in cases:
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
  w(0x20074a3c,1);w(0x20074a30,0);w(0x20074a34,100);w(0x20074ab8,100);w(0x20074ab0,Q);w(0x20074aa8,L)
  call(0x441696,[1,16,Q+80,0],[Q]);w(BT,0,0x80000038);w(BA,0,0x80000018);w(A,USER|1,0x12345678);w(T+0x18,50);w(T+0x1c,A|ad);w(T+0x20,0x449399);u.mem_write(T+0x28,bytes([1|(2 if ts else 0)]));I=T+4;S=L+8;w(L,1,S,0xffffffff,I,I);w(I,150,S,S,T,L);w(0x20074158,END,0);w(END,0,0);w(0x2007465c,END);w(0x20074660,0)
  frees=[];boundary=[];calls=[]
  def hook(u,a,n,d):
   if a==0x456210:frees.append(u.reg_read(UC_ARM_REG_R0))
   if a in [0x47e88c,0x47e83a,0x47e97a,0x442030]:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if a!=0x47e97a else None))
   if a in [USER,0x455320,0x4420bc]:boundary.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if a==0x455320 else None));u.emu_stop()
   assert a not in [0x47ea90,0x45504c],'unexpected wrap/tick'
  u.hook_add(UC_HOOK_CODE,hook)
  if cmd==5:call(0x44953e,[T]);assert u.reg_read(UC_ARM_REG_R0)==0
  elif cmd==3:call(0x47e7b0,[T,3,0,0],[0]);assert u.reg_read(UC_ARM_REG_R0)==1
  assert frees==([A] if cmd==5 and ad else [])
  if reuse:call(0x456110,[8]);assert u.reg_read(UC_ARM_REG_R0)==A;w(A,USER|1,0xcafebabe)
  calls.clear();w(0x20074a34,now);before_queue=bytes(u.mem_read(Q,96));call(sym['audio_daemon_one_iteration'] if native else 0x47e878,bounded=True)
  assert bytes(u.mem_read(Q+56,12))==before_queue[56:68] # command occupancy/length/size retained; lock bytes can change on wait
  assert word(Q+56)==int(bool(cmd));assert all(a!='0x47e97a' for a,_,_ in calls)
  if now>=150:
   assert boundary==[(hex(USER),0xcafebabe if reuse else 0x12345678,None)];assert word(L)==0 and not u.mem_read(T+0x28,1)[0]&1
   assert calls==[('0x47e88c',150,0),('0x47e83a',150,now)]
  else:
   assert boundary[0][0]==('0x4420bc' if cmd else '0x455320');assert word(L)==1 and u.mem_read(T+0x28,1)[0]&1
  vals.append((frees,boundary,calls,bytes(u.mem_read(Q,0x620)),bytes(u.mem_read(0x20074158,8)),bytes(u.mem_read(0x2007465c,20)),word(0x20074ab8),u.reg_read(UC_ARM_REG_BASEPRI)))
 assert vals[0]==vals[1],(ts,ad,cmd,now,reuse,vals[0][:3],vals[1][:3]);rows.append(dict(timer_static=ts,aux_dynamic=ad,queued_command=cmd,tick=now,reuse=reuse,frees=vals[0][0],boundary=vals[0][1],calls=vals[0][2],command_still_queued=bool(cmd)))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual daemon task starts at0x47E878 and runs original expiry/process path; independent one-iteration wrapper and next-expiry helper use original process/drain peers.','Due cases stop at real user callback first instruction before command drain; pre-due cases stop at restricted block or yield first instruction.','Constructed entry-of-iteration state and ticks; no previously blocked daemon continuation, live preemption or hardware lifetime failure.','Real delete/queue/allocator peers run; synthetic callback reuse uses same valid callback pointer and a changed argument.']),indent=2)+'\n');print('PASS',len(rows),'daemon ordering comparisons')
