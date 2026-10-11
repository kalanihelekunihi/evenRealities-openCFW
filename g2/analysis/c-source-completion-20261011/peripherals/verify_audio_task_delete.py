#!/usr/bin/env python3
"""Bounded original-byte/C task delete comparison; controlled RTOS children."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/thread_terminate_source_candidate/delete.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'delete.o';p=Path(td)/'delete.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'g2_audio_current_task':0x20074a20,'g2_audio_task_count':0x20074a30,'g2_audio_task_deletion_count':0x20074a4c,'g2_audio_tasks_waiting_cleanup':0x20074a2c,'g2_audio_scheduler_running':0x20074a3c,'g2_audio_scheduler_suspended':0x20074a58,'g2_audio_terminated_list':0x20073d38,'stock_enter_critical':0x101011,'stock_exit_critical':0x101021,'stock_yield':0x101031,'stock_list_remove':0x101041,'audio_public_list_insert':0x101051,'audio_queue_next_unblock':0x101061,'audio_task_cleanup':0x101071,'offline_assert':0x101081}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_task_delete')
 old={0x4420d0:'enter',0x4420e8:'exit',0x4420bc:'yield',0x4560e8:'remove',0x45609a:'insert',0x455876:'unblock',0x455836:'cleanup',0x5fa0a4:'assert'}
 new={0x101010:'enter',0x101020:'exit',0x101030:'yield',0x101040:'remove',0x101050:'insert',0x101060:'unblock',0x101070:'cleanup',0x101080:'assert'}
 def run(native,case):
  self_delete,notified,scheduler,null_handle=case;thread=0x20040000
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  def wr(a,v):u.mem_write(a,v.to_bytes(4,'little'))
  wr(0x20074a20,thread if self_delete else 0x20040100);wr(0x20074a30,5);wr(0x20074a4c,7);wr(0x20074a2c,3);wr(0x20074a3c,scheduler);wr(0x20074a58,0);wr(thread+40,notified)
  u.reg_write(A.UC_ARM_REG_R0,0 if null_handle else thread);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind:
    calls.append((kind,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)) if kind in ('remove','insert','cleanup') else (kind,))
    cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x454aae if native else entry)|1,0,count=1000);assert done[0],case
  return calls,tuple(int.from_bytes(u.mem_read(a,4),'little') for a in (0x20074a30,0x20074a4c,0x20074a2c))
 count=0
 for case in itertools.product((0,1),(0,1),(0,1),(0,1)):
  if case[3] and not case[0]:continue
  a=run(True,case);b=run(False,case);assert a==b,(case,a,b);count+=1
 print('PASS_AUDIO_TASK_DELETE',count)
