from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];src=R/'g2/components/audio/source_candidate_20261010/timer_start_provider.c';G=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin');O=Path('/tmp/audio-timer-start-provider');O.mkdir(exist_ok=True);ld=O/'link.ld';ld.write_text('audio_cmsis_irq_context = 0x44900f; audio_aux_command = 0x47e7b1; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
elf=O/'start.elf';flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(G/'arm-none-eabi-gcc'),*flags,'-T',str(ld),str(src),'-o',str(elf)],check=True);segs=[]
with elf.open('rb') as f:
 e=ELFFile(f);entry=e.get_section_by_name('.symtab').get_symbol_by_name('audio_timer_start')[0]['st_value']
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segs.append((s['p_vaddr'],s.data()))
Q=0x20006000;T=0x20006408;RET=0x2007f000;cases=[]
for timer_present,ticks,ipsr,full,started in itertools.product([0,1],[0,1,2000],[0,15],[0,1],[0,1]):
 vals=[]
 for at in [0x449498,entry]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segs:u.mem_write(a,b)
  def W(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def call(a,args,stack=()):
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1)
   if stack:W(0x2007e000,*stack)
   u.emu_start(a|1,RET,count=100000);assert u.reg_read(UC_ARM_REG_PC)==RET
  W(0x20074a3c,started);W(0x20074a58,0);W(0x20074a30,0);W(0x20074a34,100);W(0x20074ab8,100);W(0x20074ab0,Q)
  call(0x441696,[1 if full else 10,16,Q+80,0],[Q]);W(T+0x18,50);u.mem_write(T+0x28,b'\x01')
  if full:W(0x20006800,0x11,0x22,0x33,0x44);call(0x4417ee,[Q,0x20006800,0,0])
  u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_BASEPRI,0);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.reg_write(UC_ARM_REG_R0,T if timer_present else 0);u.reg_write(UC_ARM_REG_R1,ticks)
  calls=[]
  def hook(u,a,n,d):
   if a==0x44900e:calls.append((hex(a),))
   if a==0x47e7b0:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(at|1,RET,count=100000);assert u.reg_read(UC_ARM_REG_PC)==RET
  vals.append({'result':u.reg_read(UC_ARM_REG_R0),'sp':u.reg_read(UC_ARM_REG_SP),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'queue':bytes(u.mem_read(Q,0x200)).hex(),'timer':bytes(u.mem_read(T,44)).hex(),'calls':calls})
 assert vals[0]==vals[1],(timer_present,ticks,ipsr,full,started,[(k,vals[0][k],vals[1][k]) for k in vals[0] if vals[0][k]!=vals[1][k]])
 cases.append({'timer_present':timer_present,'ticks':ticks,'ipsr':ipsr,'queue_full':full,'scheduler_started':started,'result':vals[0]['result'],'calls':vals[0]['calls']})
out={'status':'PASS','fresh_cases':len(cases),'original_entry':'0x449498','source_entry':hex(entry),'ota_sha256':hashlib.sha256(blob).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'gcc_sha256':hashlib.sha256((G/'arm-none-eabi-gcc').read_bytes()).hexdigest(),'lower_bindings':ld.read_text(),'cases':cases,'limits':['Original IRQ-context and timer-command lower bodies execute for both entries; selected empty/full synthetic queue and task state.','No daemon command consumption, timer expiry, callback cancellation, elapsed real ticks or hardware timing.','M4 source execution; M55 selected archive object is compile-proven only.']}
(D/'timer-start-provider-execution.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(cases))
