#!/usr/bin/env python3
"""Native/C UART receive callback child ABI comparison."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/sync_callback.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'callback.o';p=Path(td)/'callback.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'g2_uart_thread_transport':0x20074b14,'g2_uart_thread_event':0x20074b10,'audio_uart_transport_write':0x101011,'g2_log_event_set_task':0x101021}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_sync_callback')
 def run(native,length):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  for a,v in ((0x20074b14,0x20050000),(0x20074b10,0x20060000)):u.mem_write(a,v.to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_R0,0x20070000);u.reg_write(A.UC_ARM_REG_R1,length);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   what={0x57e05e:'write',0x4495e4:'signal'}.get(pc) if native else {0x101010:'write',0x101020:'signal'}.get(pc)
   if what:
    r=tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
    if what=='write':
     sp=cpu.reg_read(A.UC_ARM_REG_SP);calls.append((what,r[:3],int.from_bytes(cpu.mem_read(r[3],4),'little'),int.from_bytes(cpu.mem_read(sp,4),'little')))
    else:calls.append((what,r[:2]))
    cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x5417a4 if native else entry)|1,0,count=200);assert done[0]
  return calls
 for n in (0,1,10,255,1024):
  a=run(True,n);b=run(False,n);assert a==b,(n,a,b)
 print('PASS_AUDIO_UART_SYNC_CALLBACK 5')
