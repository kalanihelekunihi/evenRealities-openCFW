from pathlib import Path
import itertools,struct,json,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer-aux/aux.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;L=0x20006200;BT=0x20006400;T=BT+8;BA=0x20006480;A=BA+8;END=0x20006600;USER=0x53c2a4;cases=[];rows=[]
for ts,ad,qstate,ipsr in itertools.product([0,1],[0,1],['empty','full','absent'],[0,15]):
 for phase in ['drain','due']:cases.append((ts,ad,qstate,ipsr,phase))
for ts in [0,1]:cases.append((ts,1,'empty',0,'due_reuse'))
for ts,ad,qstate,ipsr,phase in cases:
 vals=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def invoke(at,args=(),stack=(),allow_boundary=False):
   for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000)
   if stack:w(0x2007e000,*stack)
   u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(at|1,0x2007f000,count=100000);assert allow_boundary and boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  w(0x20074a3c,1);w(0x20074a30,0);w(0x20074a34,100);w(0x20074ab8,100);w(0x20074ab0,0 if qstate=='absent' else Q);w(0x20074aa8,L)
  invoke(0x441696,[1,16,Q+80,0],[Q]);w(BT,0,0x80000038);w(BA,0,0x80000018);w(A,USER|1,0x12345678);w(T+0x18,50);w(T+0x1c,A|ad);w(T+0x20,0x449399);u.mem_write(T+0x28,bytes([1|(2 if ts else 0)]));I=T+4;S=L+8;w(L,1,S,0xffffffff,I,I);w(I,150,S,S,T,L);w(0x20074158,END,0);w(END,0,0);w(0x2007465c,END);w(0x20074660,0);w(0x2007466c,0)
  if qstate=='full':invoke(0x47e7b0,[T,3,0,0],[0]);assert u.reg_read(UC_ARM_REG_R0)==1
  frees=[];boundary=[]
  def code(u,a,n,d):
   if a==0x456210:frees.append(u.reg_read(UC_ARM_REG_R0))
   if a==USER:boundary.append([hex(a),u.reg_read(UC_ARM_REG_R0)]);u.emu_stop()
   assert a not in [0x4420bc,0x47ea90,0x45504c],'unselected yield/wrap/tick'
  u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_IPSR,ipsr);invoke(0x44953e if original else sym['audio_timer_delete_selected'],[T]);status=u.reg_read(UC_ARM_REG_R0);success=ipsr==0 and qstate=='empty';assert status==(0xfffffffa if ipsr else 0 if success else 0xfffffffd)
  assert frees==([A] if success and ad else []);assert word(T+0x1c)==A|ad;assert word(L)==1;assert u.mem_read(T+0x28,1)==bytes([1|(2 if ts else 0)])
  after_delete_free=word(0x20074660);assert after_delete_free==(24 if success and ad else 0);u.reg_write(UC_ARM_REG_IPSR,0)
  if phase=='due_reuse':
   invoke(0x456110,[8]);assert u.reg_read(UC_ARM_REG_R0)==A;w(A,USER|1,0xcafebabe)
  if phase=='drain':
   if qstate!='absent':invoke(0x47e97a if original else sym['audio_timer_drain_stop_delete'])
   expected_frees=([A] if success and ad else [])+([T] if success and not ts else []);assert frees==expected_frees
  else:
   w(0x20074a34,150);invoke(0x47e88c if original else sym['audio_timer_due_single_selected'],[150,0],allow_boundary=True);assert boundary==[[hex(USER),0xcafebabe if phase=='due_reuse' else 0x12345678]];assert word(L)==0;assert not(u.mem_read(T+0x28,1)[0]&1)
  vals.append((status,frees,boundary,after_delete_free,bytes(u.mem_read(Q,0x620)),bytes(u.mem_read(0x20074158,8)),bytes(u.mem_read(0x2007465c,20)),word(0x20074ab8),u.reg_read(UC_ARM_REG_BASEPRI)))
 assert vals[0]==vals[1],(ts,ad,qstate,ipsr,phase,vals[0][:4],vals[1][:4]);rows.append(dict(timer_static=ts,aux_dynamic=ad,queue=qstate,ipsr=ipsr,phase=phase,delete_status=hex(vals[0][0]),frees=vals[0][1],callback_boundary=vals[0][2],aux_bytes_released_before_daemon=vals[0][3]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Original/independent CMSIS delete and due-single-shot adapter, sealed independent drain; actual kernel/time/heap/list peers. No result stubs.','Due phase runs real process-or-block due branch through expired timer and adapter to user callback entry; separate phase fixture from drain, no invented callback return.','Taskcount0/running1, constructed heap/queue/timer; ticks100 then150 synthetic, not measured scheduling or hardware failure.','Two reuse cases run actual malloc8 on released auxiliary block and change argument; not a demonstrated reachable runtime interleaving.']),indent=2)+'\n');print('PASS',len(rows))
