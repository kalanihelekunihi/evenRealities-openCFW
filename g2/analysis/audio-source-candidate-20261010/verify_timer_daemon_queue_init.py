from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];src=R/'g2/components/audio/source_candidate_20261010/timer_daemon_queue_init_provider.c';G=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin');O=Path('/tmp/audio-daemon-queue-init');O.mkdir(exist_ok=True);ld=O/'link.ld';ld.write_text('stock_enter_critical = 0x4420d1; stock_exit_critical = 0x4420e9; vListInitialise = 0x45607d; xQueueGenericCreateStatic = 0x4415cb; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
elf=O/'init.elf';flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(G/'arm-none-eabi-gcc'),*flags,'-T',str(ld),str(src),'-o',str(elf)],check=True);segs=[]
with elf.open('rb') as f:
 e=ELFFile(f);entry=e.get_section_by_name('.symtab').get_symbol_by_name('audio_daemon_initialize_queue')[0]['st_value']
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segs.append((s['p_vaddr'],s.data()))
rows=[]
for existing,depth,mask,fill in itertools.product([0,1],[0,1,2],[0,0x20,0x80],[0,0xa5]):
 vals=[]
 for at in [0x47eab8,entry]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x2006d7b4,bytes([fill])*128);u.mem_write(0x20072ee8,bytes([fill])*800);u.mem_write(0x20073d60,bytes([fill])*40);u.mem_write(0x20073d74,bytes([fill])*40)
  u.mem_write(0x2000309c,struct.pack('<I',depth));u.mem_write(0x20074ab0,struct.pack('<I',0x20006000 if existing else 0));u.reg_write(UC_ARM_REG_BASEPRI,mask);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
  calls=[]
  def hook(u,a,n,d):
   if a in (0x4420d0,0x4420e8):calls.append((hex(a),))
   elif a==0x45607c:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0)))
   elif a==0x4415ca:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3)))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(at|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
  vals.append({'calls':calls,'sp':u.reg_read(UC_ARM_REG_SP),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'depth':bytes(u.mem_read(0x2000309c,4)).hex(),'pointers':bytes(u.mem_read(0x20074aa8,12)).hex(),'lists':bytes(u.mem_read(0x20073d60,40)).hex(),'queue':bytes(u.mem_read(0x2006d7b4,128)).hex(),'buffer':bytes(u.mem_read(0x20072ee8,800)).hex()})
 assert vals[0]==vals[1],(existing,depth,mask,fill,[(k,vals[0][k][:120] if isinstance(vals[0][k],str) else vals[0][k],vals[1][k][:120] if isinstance(vals[1][k],str) else vals[1][k]) for k in vals[0] if vals[0][k]!=vals[1][k]])
 rows.append({'existing_queue':existing,'critical_depth':depth,'basepri':mask,'fill':fill,'calls':vals[0]['calls'],'queue_pointer':vals[0]['pointers'][-8:]})
out={'status':'PASS','fresh_cases':len(rows),'original_entry':'0x47eab8','source_entry':hex(entry),'ota_sha256':hashlib.sha256(blob).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'gcc_sha256':hashlib.sha256((G/'arm-none-eabi-gcc').read_bytes()).hexdigest(),'lower_bindings':ld.read_text(),'cases':rows,'limits':['Actual original critical/list/static queue callees on both sides; selected synthetic RAM and empty waiter state.','No daemon task creation, queue traffic, concurrency, allocation failure, or live scheduling.','M4 source execution, not selected M55 archive object execution.']}
(D/'timer-daemon-queue-init-execution.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows))
