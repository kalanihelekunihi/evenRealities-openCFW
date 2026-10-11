#!/usr/bin/env python3
"""Native/C CMSIS mutex and event creation with controlled allocation children."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/cmsis_new.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'cmsis.o';p=Path(td)/'cmsis.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'audio_irq_context':0x101011,'audio_uart_mutex_dynamic_create':0x101021,'audio_uart_mutex_static_create':0x101031,'audio_uart_event_dynamic_create':0x101041,'audio_uart_event_static_create':0x101051}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 old={0x44900e:'irq',0x4416d6:'mutex_dynamic',0x4416f0:'mutex_static',0x47ebd8:'event_dynamic',0x47eb94:'event_static'}
 new={0x101010:'irq',0x101020:'mutex_dynamic',0x101030:'mutex_static',0x101040:'event_dynamic',0x101050:'event_static'}
 def run(native,kind,irq,mode,flags,alloc):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  attr=0 if mode=='none' else 0x20040000
  if attr:
   words={4:flags,8:0x20050000 if mode in ('static','short') else 0,12:(80 if kind=='mutex' else 32) if mode=='static' else (8 if mode=='short' else 0)}
   for off,v in words.items():u.mem_write(attr+off,v.to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_R0,attr);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   what=(old if native else new).get(pc)
   if what:
    calls.append(('irq',) if what=='irq' else ((what,) if what=='event_dynamic' else ((what,cpu.reg_read(A.UC_ARM_REG_R0)) if what!='mutex_static' else (what,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))))
    cpu.reg_write(A.UC_ARM_REG_R0,irq if what=='irq' else (0x20060000 if alloc else 0));cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);entry={'mutex':0x44971c,'event':0x449590}[kind] if native else syms['audio_uart_'+kind+'_new'];u.emu_start(entry|1,0,count=1000);assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls
 count=0
 for kind,irq,mode,flags,alloc in itertools.product(('mutex','event'),(0,1),('none','dynamic','static','short'),(0,1,8), (0,1)):
  a=run(True,kind,irq,mode,flags,alloc);b=run(False,kind,irq,mode,flags,alloc);assert a==b,(kind,irq,mode,flags,alloc,a,b);count+=1
 print('PASS_AUDIO_UART_CMSIS_NEW',count)
