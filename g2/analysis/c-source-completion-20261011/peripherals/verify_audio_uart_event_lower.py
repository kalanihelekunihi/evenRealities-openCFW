#!/usr/bin/env python3
"""Original-byte/C event create and task clear lower comparison."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/event_lower.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'event.o';p=Path(td)/'event.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'pvPortMalloc':0x101011,'stock_enter_critical':0x101021,'stock_exit_critical':0x101031,'offline_assert':0x101041}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 old={0x456110:'alloc',0x4420d0:'enter',0x4420e8:'exit'};new={0x101010:'alloc',0x101020:'enter',0x101030:'exit'}
 def run(native,kind,initial,flags,alloc):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  event=0x20040000;u.mem_write(event,bytes([0xa5]*40));u.mem_write(event,initial.to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_R0,event if kind!='dynamic' else flags);u.reg_write(A.UC_ARM_REG_R1,flags);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   name=(old if native else new).get(pc)
   if name:
    calls.append((name,cpu.reg_read(A.UC_ARM_REG_R0)) if name=='alloc' else (name,))
    cpu.reg_write(A.UC_ARM_REG_R0,event if alloc and name=='alloc' else 0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  addr={'static':0x47eb94,'dynamic':0x47ebd8,'clear':0x47ed10}[kind] if native else syms['audio_uart_event_'+{'static':'static_create','dynamic':'dynamic_create','clear':'clear_task'}[kind]]
  u.emu_start(addr|1,0,count=1000);assert done[0],(kind,initial,flags,alloc)
  return u.reg_read(A.UC_ARM_REG_R0),calls,bytes(u.mem_read(event,40))
 count=0
 for kind in ('static','dynamic','clear'):
  for initial,flags,alloc in itertools.product((0,0x12345678,0xffffffff),(0,1,0x1234,0x00ffffff),(0,1)):
   if kind=='clear' and not flags:pass
   a=run(True,kind,initial,flags,alloc);b=run(False,kind,initial,flags,alloc);assert a==b,(kind,initial,flags,alloc,a,b);count+=1
 print('PASS_AUDIO_UART_EVENT_LOWER',count)
