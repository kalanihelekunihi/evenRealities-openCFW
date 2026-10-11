#!/usr/bin/env python3
"""Bounded original-byte comparison for FreeRTOS eTaskGetState 0x454b88."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/thread_terminate_source_candidate/state.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'state.o';p=Path(td)/'state.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'g2_audio_current_task':0x20074a20,'g2_audio_delayed_list0':0x20074a24,'g2_audio_delayed_list1':0x20074a28,'g2_audio_suspended_list':0x20073d4c,'g2_audio_terminated_list':0x20073d38,'stock_enter_critical':0x101011,'stock_exit_critical':0x101021,'offline_assert':0x101031}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_task_state')
 def run(native,case):
  current,container,notice,notify=case;thread=0x20040000
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  def wr(a,v):u.mem_write(a,v.to_bytes(4,'little'))
  wr(0x20074a20,thread if current else 0x20040100);wr(0x20074a24,0x20073d70);wr(0x20074a28,0x20073d84)
  wr(thread+20,container);wr(thread+40,notice);u.mem_write(thread+108,bytes([notify]))
  u.reg_write(A.UC_ARM_REG_R0,thread);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  old={0x4420d0:'enter',0x4420e8:'exit'};new={0x101010:'enter',0x101020:'exit'};calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind: calls.append(kind);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x454b88 if native else entry)|1,0,count=1000);assert done[0],case
  return u.reg_read(A.UC_ARM_REG_R0),calls
 count=0
 for case in itertools.product((0,1),(0x20073d70,0x20073d84,0x20073d4c,0x20073d38,0,0x20073e00),(0,1),(0,1,2)):
  a=run(True,case);b=run(False,case);assert a==b,(case,a,b);count+=1
 print('PASS_AUDIO_TASK_STATE',count)
