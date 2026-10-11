#!/usr/bin/env python3
"""Bounded original-byte/C task notification state and list comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/task_notify_source_candidate/notify.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'notify.o';e=t/'notify.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 d={'g2_audio_notify_assert_enabled':0x20074a34,'g2_audio_top_ready_priority':0x20074a38,'g2_audio_current_task':0x20074a20,'g2_audio_ready_lists':0x2006a49c,'audio_enter_critical':0x101011,'audio_exit_critical':0x101021,'audio_queue_next_unblock':0x101031,'audio_yield':0x101041}
 args=['--defsym='+k+'='+hex(v) for k,v in d.items()]
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*args,'-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
 def run(native,prior,action,value,previous,priority,current_priority):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  task,current,event,out=0x20002000,0x20003000,0x20004000,0x20005000
  ready=0x2006a49c+priority*20;sentinel=ready+8
  put(u,task+44,priority);put(u,task+104,0xa5a5000f);u.mem_write(task+108,bytes([prior]));put(u,current+44,current_priority);put(u,0x20074a20,current);put(u,0x20074a38,1);put(u,0x20074a34,0)
  put(u,event,1);put(u,event+4,task+4);put(u,task+8,event+8);put(u,task+12,event+8);put(u,task+20,event);put(u,event+12,task+4);put(u,event+16,task+4)
  put(u,ready,0);put(u,ready+4,sentinel);put(u,sentinel+4,sentinel);put(u,sentinel+8,sentinel)
  put(u,out,0xdeadbeef)
  u.reg_write(A.UC_ARM_REG_R0,task);u.reg_write(A.UC_ARM_REG_R1,0);u.reg_write(A.UC_ARM_REG_R2,value);u.reg_write(A.UC_ARM_REG_R3,action);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);put(u,0x200f0000,out if previous else 0);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  cuts=({0x4420d0:'enter',0x4420e8:'exit',0x455876:'next',0x4420bc:'yield'} if native else {0x101010:'enter',0x101020:'exit',0x101030:'next',0x101040:'yield'})
  calls=[];done=[False]
  def code(c,pc,_sz,_d):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   if pc in cuts:calls.append(cuts[pc]);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x455c48 if native else sym['audio_notify_task'])|1,0,count=600)
  assert done[0],(native,prior,action,hex(u.reg_read(A.UC_ARM_REG_PC)),calls)
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(task,112)),bytes(u.mem_read(event,24)),bytes(u.mem_read(ready,20)),word(u,out),word(u,0x20074a38),calls
 n=0
 for prior in (0,1,2):
  for action in (0,1,2,3,4,5):
   for value in (0,1,0x800000):
    for previous in (False,True):
     for priority,current_priority in ((1,1),(2,1),(1,2)):
      a=run(True,prior,action,value,previous,priority,current_priority);b=run(False,prior,action,value,previous,priority,current_priority)
      assert a==b,(prior,action,value,previous,priority,current_priority,a,b)
      n+=1
 print('PASS_AUDIO_TASK_NOTIFY',n)
