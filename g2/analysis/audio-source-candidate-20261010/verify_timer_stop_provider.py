from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];src=R/'g2/components/audio/source_candidate_20261010/timer_stop_provider.c';G=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin');O=Path('/tmp/audio-timer-stop-provider');O.mkdir(exist_ok=True);ld=O/'link.ld';ld.write_text('audio_cmsis_irq_context = 0x44900f; stock_enter_critical = 0x4420d1; stock_exit_critical = 0x4420e9; audio_mask_save = 0x5fa0a5; audio_aux_command = 0x47e7b1; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
elf=O/'stop.elf';flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(G/'arm-none-eabi-gcc'),*flags,'-T',str(ld),str(src),'-o',str(elf)],check=True);segs=[]
with elf.open('rb') as f:
 e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segs.append((s['p_vaddr'],s.data()))
Q=0x20006000;T=0x20006408;RET=0x2007f000;cases=[]
for mode,ipsr,full,started in itertools.product(['null','inactive','active'],[0,15],[0,1],[0,1]):
 vals=[]
 for at in [0x4494d8,symbols['audio_timer_stop']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segs:u.mem_write(a,b)
  def W(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def call(a,args,stack=()):
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1)
   if stack:W(0x2007e000,*stack)
   u.emu_start(a|1,RET,count=100000);assert u.reg_read(UC_ARM_REG_PC)==RET
  W(0x20074a3c,started);W(0x20074a58,0);W(0x20074a30,0);W(0x20074a34,100);W(0x20074ab8,100);W(0x20074ab0,Q)
  call(0x441696,[1 if full else 10,16,Q+80,0],[Q]);W(T+0x18,50);u.mem_write(T+0x28,bytes([1 if mode=='active' else 0]))
  if full:
   W(0x20006800,0x11,0x22,0x33,0x44);call(0x4417ee,[Q,0x20006800,0,0])
  u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.reg_write(UC_ARM_REG_R0,0 if mode=='null' else T)
  calls=[]
  def hook(u,a,n,d):
   if a in (0x44900e,0x47eaf6,0x47e7b0):calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if a==0x47e7b0 else None))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(at|1,RET,count=100000);assert u.reg_read(UC_ARM_REG_PC)==RET
  vals.append({'result':u.reg_read(UC_ARM_REG_R0),'sp':u.reg_read(UC_ARM_REG_SP),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'queue':bytes(u.mem_read(Q,0x200)).hex(),'timer':bytes(u.mem_read(T,44)).hex(),'calls':calls})
 # Source includes its own active helper, so compare external calls only.
 for v in vals:v['calls']=[c for c in v['calls'] if c[0]!='0x47eaf6']
 assert vals[0]==vals[1],(mode,ipsr,full,started,[(k,vals[0][k],vals[1][k]) for k in vals[0] if vals[0][k]!=vals[1][k]])
 cases.append({'mode':mode,'ipsr':ipsr,'queue_full':full,'scheduler_started':started,'result':vals[0]['result']})
# Direct active getter, including independent critical/mask inputs.
active=[]
for status,depth,mask in itertools.product([0,1,2,3,0xff],[0,1,2],[0,0x20,0x80]):
 vals=[]
 for at in [0x47eaf6,symbols['audio_timer_is_active']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segs:u.mem_write(a,b)
  u.mem_write(T+0x28,bytes([status]));u.mem_write(0x2000309c,struct.pack('<I',depth));u.reg_write(UC_ARM_REG_BASEPRI,mask);u.reg_write(UC_ARM_REG_R0,T);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.emu_start(at|1,RET,count=1000);assert u.reg_read(UC_ARM_REG_PC)==RET
  vals.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_BASEPRI),bytes(u.mem_read(T,44)),bytes(u.mem_read(0x2000309c,4))))
 assert vals[0]==vals[1],(status,depth,mask,vals);active.append({'status':status,'depth':depth,'basepri':mask,'result':vals[0][0]})
null_cases=[]
for mask in [0,0x80]:
 vals=[]
 for at in [0x47eaf6,symbols['audio_timer_is_active']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segs:u.mem_write(a,b)
  u.reg_write(UC_ARM_REG_BASEPRI,mask);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);calls=[];writes=[]
  def hook(u,a,n,d):
   if a==0x5fa0a4:calls.append(hex(a))
  def invalid(u,access,a,n,value,d):
   writes.append((hex(a),n,value));u.emu_stop();return True
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,invalid)
  try:u.emu_start(at|1,0,count=1000)
  except UcError:
   if not writes:raise
  vals.append((calls,writes,u.reg_read(UC_ARM_REG_BASEPRI)))
 assert vals[0]==vals[1] and vals[0][0]==['0x5fa0a4'] and vals[0][1]==[('0xffffffff',4,0)],(mask,vals)
 null_cases.append({'initial_basepri':mask,'final_basepri':vals[0][2],'invalid_write':vals[0][1]})
out={'status':'PASS','fresh_stop_cases':len(cases),'fresh_active_getter_cases':len(active),'fresh_active_null_prefix_cases':len(null_cases),'total_fresh_cases':len(cases)+len(active)+len(null_cases),'original_entries':{'audio_timer_stop':'0x4494d8','audio_timer_is_active':'0x47eaf6'},'ota_sha256':hashlib.sha256(blob).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'gcc_sha256':hashlib.sha256((G/'arm-none-eabi-gcc').read_bytes()).hexdigest(),'lower_bindings':ld.read_text(),'stop_cases':cases,'active_cases':active,'active_null_cases':null_cases,'limits':['Public stop entry executes original IRQ context and command producer on both sides; active getter is independently source compared.','Synthetic queue/timer/task state; no timer daemon command consumption or callback cancellation.','Active getter null path executes original mask helper and compares attempted invalid write; exception delivery and subsequent loop remain untested.']}
(D/'timer-stop-provider-execution.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(cases),len(active),len(null_cases))
