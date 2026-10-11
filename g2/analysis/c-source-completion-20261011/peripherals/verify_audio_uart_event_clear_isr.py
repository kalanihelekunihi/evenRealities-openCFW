#!/usr/bin/env python3
"""Native/C timer-pend bridge for ISR event clear."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/event_clear_isr.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'isr.o';p=Path(td)/'isr.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--defsym=g2_audio_timer_command_queue=0x20074ab0','--defsym=opencfw_event_queue_send_isr=0x101011','--defsym=audio_uart_event_clear_task=0x101021','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,flags,success):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20074ab0,(0x20060000).to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_R0,0x20050000);u.reg_write(A.UC_ARM_REG_R1,flags);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  captured=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   if pc==(0x441952 if native else 0x101010):
    q=cpu.reg_read(A.UC_ARM_REG_R0);msg=cpu.reg_read(A.UC_ARM_REG_R1);wake=cpu.reg_read(A.UC_ARM_REG_R2);pos=cpu.reg_read(A.UC_ARM_REG_R3)
    words=[int.from_bytes(cpu.mem_read(msg+i*4,4),'little') for i in range(4)]
    words[1]='callback' if words[1]==(0x47ee29 if native else syms['audio_uart_event_clear_callback']) else words[1]
    captured.append((q,tuple(words),wake,pos));cpu.reg_write(A.UC_ARM_REG_R0,success);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x47ed52 if native else syms['audio_uart_event_clear_isr'])|1,0,count=1000);assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),captured
 count=0
 for flags,success in itertools.product((0,1,4,0x123456),(0,1)):
  a=run(True,flags,success);b=run(False,flags,success);assert a==b,(flags,success,a,b);count+=1
 print('PASS_AUDIO_UART_EVENT_CLEAR_ISR',count)
