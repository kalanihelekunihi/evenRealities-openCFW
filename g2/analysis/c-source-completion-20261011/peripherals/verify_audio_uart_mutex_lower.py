#!/usr/bin/env python3
"""Native/C FreeRTOS mutex wrappers with controlled queue children."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/mutex_lower.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'mutex.o';p=Path(td)/'mutex.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 defs={'audio_queue_create_dynamic':0x101011,'audio_queue_create_static':0x101021,'audio_uart_queue_send':0x101031}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 old={0x441636:'dynamic',0x4415ca:'static',0x4417ee:'send'};new={0x101010:'dynamic',0x101020:'static',0x101030:'send'}
 def run(native,kind,type_,allocated):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20040000,bytes([0xa5]*80));u.reg_write(A.UC_ARM_REG_R0,type_);u.reg_write(A.UC_ARM_REG_R1,0x20050000);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101ff0:done[0]=True;cpu.emu_stop();return
   name=(old if native else new).get(pc)
   if name:
    calls.append((name,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1),cpu.reg_read(A.UC_ARM_REG_R2)))
    cpu.reg_write(A.UC_ARM_REG_R0,(0x20040000 if allocated else 0) if name!='send' else 1);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=(0x4416d6 if kind=='dynamic' else 0x4416f0) if native else syms['audio_uart_mutex_'+kind+'_create']
  u.emu_start(entry|1,0,count=1000);assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20040000,80))
 count=0
 for case in itertools.product(('dynamic','static'),(1,4,0x101),(0,1)):
  a=run(True,*case);b=run(False,*case);assert a==b,(case,a,b);count+=1
 print('PASS_AUDIO_UART_MUTEX_LOWER',count)
