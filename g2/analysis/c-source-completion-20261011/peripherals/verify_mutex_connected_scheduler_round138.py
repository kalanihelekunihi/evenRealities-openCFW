#!/usr/bin/env python3
"""Native/C FreeRTOS mutex wrappers with controlled queue children."""
from pathlib import Path
import subprocess,tempfile,itertools,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/mutex_lower.c';Q=R/'g2/components/audio/queue_dynamic_source_candidate/create.c';I=R/'g2/components/audio/cmsis_memory_pool_offline/initialize.c';J=R/'g2/components/audio/queue_cmsis_offline/queue.c';K=R/'g2/components/audio/uart_thread_source_candidate/queue_send.c';L=R/'g2/components/audio/queue_cmsis_offline/cmsis.c';D=Path(__file__).parent/'root-mutex-connected-round138';D.mkdir(exist_ok=True);B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(B).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'mutex.o';p=Path(td)/'mutex.elf'
 objects=[]
 for source in [S,Q,I,J,K,L]:
  obj=Path(td)/(source.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-Werror','-c',str(source),'-o',str(obj)],check=True);objects.append(str(obj))
 defs={'pvPortMalloc':0x101011,'stock_enter_critical':0x101021,'stock_exit_critical':0x101051,'stock_port_yield':0x101061,'opencfw_ready_remove_event_list':0x101071,'audio_queue_bad_argument':0x101081,'stock_priority_disinherit':0x101091,'stock_timeout_capture':0x1010a1,'stock_timeout_check':0x1010b1,'stock_scheduler_suspend':0x1010c1,'stock_scheduler_resume':0x1010d1,'stock_place_event':0x1010e1,'audio_public_queue_unlock':0x1010f1,'offline_assert':0x101041}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--gc-sections','-e','audio_uart_mutex_dynamic_create',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),*objects],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 old={0x456110:'malloc',0x4420d0:'enter',0x4420e8:'exit',0x45596e:'disinherit',0x4420bc:'yield'};new={0x101010:'malloc',0x101020:'enter',0x101050:'exit',0x101090:'disinherit',0x101060:'yield'}
 def run(native,type_,allocated,mutation,send_result,state):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20074a3c,(0 if state==0 else 1).to_bytes(4,'little'));u.mem_write(0x20074a58,(1 if state==2 else 0).to_bytes(4,'little'));u.mem_write(0x20040000,bytes([0xa5]*80));u.reg_write(A.UC_ARM_REG_R0,type_);u.reg_write(A.UC_ARM_REG_R1,0x20050000);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   name=(old if native else new).get(pc)
   if name:
    r=[cpu.reg_read(reg) for reg in [A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3]]
    calls.append((name,r[0]) if name=='malloc' else (name,) if name in ['enter','exit','scheduler','yield'] else (name,r[0]))
    if name=='enter' and mutation:cpu.mem_write(0x20040000,(0x20041000).to_bytes(4,'little'))
    if name=='disinherit' and mutation:cpu.mem_write(0x20040000+8,(0x12345678).to_bytes(4,'little'))
    cpu.reg_write(A.UC_ARM_REG_R0,(0x20040000 if allocated else 0) if name=='malloc' else send_result if name=='disinherit' else 1 if name=='scheduler' else 0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=0x4416d6 if native else syms['audio_uart_mutex_dynamic_create']
  u.emu_start(entry|1,0,count=3000);assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20040000,80))
 count=0
 for case in itertools.product((0,1,4,255,256,0xffffffff),(0,1),(0,1),(0,1,0xffffffff),range(3)):
  a=run(True,*case);b=run(False,*case);assert a==b,(case,a,b);count+=1
 receipt={'status':'PASS_CONNECTED_DYNAMIC_MUTEX_QUEUE_SCHEDULER_STATE','cases':count,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S,Q,I,J,K,L]},'payload_sha256':hashlib.sha256(B).hexdigest(),'limits':['Actual mutex/queue creation,reset,list initialization and full queue send execute; scheduler-state getter also executes for all3 states; allocation,critical enter/exit,disinherit/yield are controlled cuts. Full80byte queue state and callbacks compared.','Scheduler/list behavior,allocation provider,hardware and six image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
