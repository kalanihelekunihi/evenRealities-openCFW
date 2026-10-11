#!/usr/bin/env python3
"""Controlled native/C osEventFlagsClear comparison."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/event_clear.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'clear.o';p=Path(td)/'clear.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'audio_irq_context':0x101011,'audio_uart_event_get_isr':0x101021,'audio_uart_event_clear_isr':0x101031,'audio_uart_event_clear_task':0x101041}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_event_clear')
 old={0x44900e:'irq',0x47ed64:'get',0x47ed52:'clear_isr',0x47ed10:'clear_task'}
 new={0x101010:'irq',0x101020:'get',0x101030:'clear_isr',0x101040:'clear_task'}
 def run(native,case):
  handle,flags,irq,success=case
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x1000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.reg_write(A.UC_ARM_REG_R0,0x20040000 if handle else 0);u.reg_write(A.UC_ARM_REG_R1,flags);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   kind=(old if native else new).get(pc)
   if kind:
    calls.append((kind,) if kind=='irq' else (kind,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1) if kind!='get' else None))
    cpu.reg_write(A.UC_ARM_REG_R0,{'irq':irq,'get':0x12345678,'clear_isr':success,'clear_task':0x87654321}[kind]);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x449642 if native else entry)|1,0,count=1000);assert done[0],case
  return u.reg_read(A.UC_ARM_REG_R0),calls,int.from_bytes(u.mem_read(0xe000ed04,4),'little')
 count=0
 for case in itertools.product((0,1),(0,1,7,0x1000000,0xff000000),(0,1),(0,1)):
  a=run(True,case);b=run(False,case);assert a==b,(case,a,b);count+=1
 print('PASS_AUDIO_UART_EVENT_CLEAR',count)
