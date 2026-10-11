#!/usr/bin/env python3
"""Native/C bounded semaphore drain comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/process_event4.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'event4.o';p=Path(td)/'event4.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'g2_uart_sync_module':0x200749c4,'g2_uart_sync_semaphore':0x200749d4,'audio_uart_semaphore_take':0x101011,'audio_uart_module_pump':0x101021}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_process_event4')
 def run(native,n):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x200749c4,(0x20050000).to_bytes(4,'little'));u.mem_write(0x200749d4,(0x20060000).to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False];taken=[0]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   kind={0x44994e:'take',0x492288:'pump'}.get(pc) if native else {0x101010:'take',0x101020:'pump'}.get(pc)
   if kind:
    calls.append((kind,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1) if kind=='take' else None))
    if kind=='take':taken[0]+=1;result=0 if taken[0]<=n else 1
    else:result=0
    cpu.reg_write(A.UC_ARM_REG_R0,result);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x45d4b8 if native else entry)|1,0,count=1000);assert done[0]
  return calls
 for n in (0,1,2,3,5):
  a=run(True,n);b=run(False,n);assert a==b,(n,a,b)
 print('PASS_AUDIO_UART_PROCESS_EVENT4 5')
