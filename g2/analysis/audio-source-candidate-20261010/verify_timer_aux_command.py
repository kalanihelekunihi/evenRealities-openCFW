from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
stock=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=stock.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:]
src=R/'g2/components/audio/source_candidate_20261010/timer_aux_command_provider.c';G=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin');O=Path('/tmp/audio-aux-command');O.mkdir(exist_ok=True);ld=O/'link.ld';ld.write_text('audio_scheduler_state = 0x4558a5; xQueueGenericSend = 0x4417ef; xQueueGenericSendFromISR = 0x441953; audio_mask_save = 0x5fa0a5; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
elf=O/'aux.elf';flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(G/'arm-none-eabi-gcc'),*flags,'-T',str(ld),str(src),'-o',str(elf)],check=True)
segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;T=0x20006400;rows=[]
for queue_present,started,suspended,command,ticks,woken in itertools.product([0,1],[0,1],[0,1],[0,5,6,7],[0,2],[0,1]):
 vals=[]
 for entry in [0x47e7b0,sym['audio_aux_command']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def W(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def run(at,args,stack=()):
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_SP,0x2007e000)
   if stack:W(0x2007e000,*stack)
   u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(at|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
  W(0x20074a3c,started);W(0x20074a58,suspended);W(0x20074a30,0);W(0x20074a34,100);W(0x20074ab8,100)
  if queue_present:
   run(0x441696,[10,16,Q+80,0],[Q]);W(0x20074ab0,Q)
  else:W(0x20074ab0,0)
  W(T,0x9b9b9b9b);W(T+4,0x77777777);W(0x20006600,0)
  arg4=0x20006600 if woken else 0;packet=(command,0x12345678,T,arg4)
  # Empty queue and zero wait mean no task suspension is needed in admitted cases.
  run(entry,[T,command,0x12345678,arg4],[ticks])
  vals.append({'result':u.reg_read(UC_ARM_REG_R0),'sp':u.reg_read(UC_ARM_REG_SP),'queue':bytes(u.mem_read(Q,0x90)).hex() if queue_present else '', 'woken':bytes(u.mem_read(0x20006600,4)).hex(),'timer':bytes(u.mem_read(T,8)).hex()})
 assert vals[0]==vals[1],(queue_present,started,suspended,command,ticks,woken,vals)
 rows.append({'queue':queue_present,'started':started,'suspended':suspended,'command':command,'ticks':ticks,'woken_pointer':woken,'result':vals[0]['result']})
out={'status':'PASS','fresh_cases':len(rows),'original_entry':'0x47e7b0','source_entry':hex(sym['audio_aux_command']),'ota_sha256':hashlib.sha256(blob).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'gcc_sha256':hashlib.sha256((G/'arm-none-eabi-gcc').read_bytes()).hexdigest(),'lower_bindings':ld.read_text(),'cases':rows,'limits':['Null timer fatal path is excluded; source preserves original fatal-call/invalid-write/loop boundary but does not execute it.','Shared stock queue and scheduler lower bodies; this proves entry composition and packet bytes for empty queue without concurrent waiters, not source closure of lower providers.','Synthetic queue/task/RAM state, no real timer daemon wake or hardware.']}
(D/'timer-aux-command-execution.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows))
