from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-stop/stop.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
CTX=[0x200040fc,0x20004120,0x20004044,0x20003ffc,0x20004020,0x20004068,0x20003f98,0x2000408c,0x20003664,0x20000658];B=0x20007000;Q=B+8;E=0x20006800;rows=[]
def guest():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(0x20074a3c,struct.pack('<I',1));u.mem_write(0x20074a30,bytes(4));return u
cases=[]
for reason,handles,ipsr in itertools.product([0,1,8,32,63,0xffffffff],[0,0x3ff,0x40,0x155],[0,15]):cases.append(('fanout',reason,handles,ipsr))
for index,handle,ipsr in itertools.product([1,3,12],[0,1],[0,15]):cases.append(('one',index,handle,ipsr))
for bits,allocation in itertools.product([0,8,16,24],['none','static','dynamic']):cases.append(('exit',bits,allocation,0))
for kind,a,b,ipsr in cases:
 vals=[]
 for entry in [{'fanout':0x4c96b6,'one':0x4c95bc,'exit':0x53cdc2}[kind],sym[{'fanout':'audio_stop_fanout','one':'audio_stop_one','exit':'audio_exit_no_timer'}[kind]]]:
  u=guest();boundary=[];trace=[]
  def w(at,*v):u.mem_write(at,struct.pack('<'+'I'*len(v),*v))
  for i,ctx in enumerate(CTX):
   t=0x20006000+i*128;w(ctx+8,t if kind=='fanout' and b&(1<<i) else 0);w(t+0x68,0x100);u.mem_write(t+0x6c,b'\x00')
  w(0x200040f4,E);w(E,a if kind=='exit' else 0,0,E+12,0xffffffff,E+12,E+12)
  if kind=='one':w(0x20006068,0x100);u.mem_write(0x2000606c,b'\x00')
  if kind=='exit':
   w(0x20074a98,0);w(0x20003fa4,0 if b=='none' else Q);w(B,0,0x800002b0);w(0x20074158,B+1024,0);w(B+1024,0,0);w(0x2007465c,B+1024);w(0x20074660,0);w(0x2007466c,0)
   if b!='none':
    # Real queue initializer builds the 50x12 object in synthetic allocated storage.
    u.reg_write(UC_ARM_REG_R0,50);u.reg_write(UC_ARM_REG_R1,12);u.reg_write(UC_ARM_REG_R2,Q+80);u.reg_write(UC_ARM_REG_R3,0);u.reg_write(UC_ARM_REG_SP,0x2007e000);w(0x2007e000,Q);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(0x441697,0x20000000,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
    u.mem_write(Q+0x46,bytes([b=='static']))
  def code(u,at,size,d):
   if at in [0x449238,0x4c9c3c,0x449bec,0x456210]:trace.append([hex(at),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),struct.unpack('<I',u.mem_read(E,4))[0]])
   if at in [0x44969c,0x449376]:boundary.extend([hex(at),*[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]]);u.emu_stop()
   assert at not in [0x45547c,0x4420bc,0x43d574,0x43ce9e],'unselected waiter/yield/logger'
  u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_R0,a if kind=='fanout' else 0x20006000 if kind=='one' and b else 0);u.reg_write(UC_ARM_REG_R1,a if kind=='one' else 0);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=40000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x20000000
  # Only defined argument registers at boundaries are compared (event wait4; delay1).
  if kind=='exit':boundary=boundary[:2];assert struct.unpack('<I',u.mem_read(E,4))[0]==a|8;assert struct.unpack('<I',u.mem_read(0x20003fa4,4))[0]==0;assert struct.unpack('<I',u.mem_read(0x20074660,4))[0]==(688 if b=='dynamic' else 0)
  if kind=='fanout':
   assert u.reg_read(UC_ARM_REG_R0)==(0x187a if a&32 else 0x1bfa)
   active=[i for i in range(10) if not(a&32 and 3<=i<=5)]
   assert [r[:3] for r in trace]==[['0x449238',0x20006000+i*128 if b&(1<<i) else 0,0x800000] for i in active]
  if kind=='one':assert boundary==['0x44969c',E,1<<a,1,20000]
  # For trace, R1 is undefined at ack/delete/free entry; retain defined registers only.
  trace=[r[:3] if r[0]=='0x449238' else [r[0],r[1],r[3]] for r in trace]
  vals.append((u.reg_read(UC_ARM_REG_R0) if kind=='fanout' else None,boundary,trace,bytes(u.mem_read(0x20006000,0x1600)),bytes(u.mem_read(0x20003fa4,4)),bytes(u.mem_read(0x20074158,8)),bytes(u.mem_read(0x2007465c,20)),bytes(u.mem_read(0x20074a58,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
 assert vals[0]==vals[1],(kind,a,b,ipsr,vals[0][:3],vals[1][:3]);rows.append(dict(kind=kind,input=a,handles_or_allocation=b,ipsr=ipsr,endpoint=vals[0][1],calls=vals[0][2]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Real flags/context/eventset/queuefree/scheduler peers common to both first-party reconstructions. No child result stubs.','Fanout/one synthetic nonwaiting TCB prefixes; exit empty event waitlist, timerNULL, task count0. Not live scheduler/producer state.','Wait/delay stops before child entry; no timeout, context switch, wire/hardware or actual producer quiescence.']),indent=2)+'\n');print('PASS',len(rows))
