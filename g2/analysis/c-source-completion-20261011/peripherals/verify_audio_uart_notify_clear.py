#!/usr/bin/env python3
"""Bounded native/C task notify-state clear, explicit task handle."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4]
S=R/'g2/components/audio/uart_thread_source_candidate/notify_clear.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 helper=Path(td)/'helpers.c'
 helper.write_text('void offline_assert(void){for(;;){}}\nvoid *receiver_current_task(void){return 0;}\nvoid stock_enter_critical(void){}\nvoid stock_exit_critical(void){}\n')
 objs=[]
 for name,src in (('candidate',S),('helpers',helper)):
  o=Path(td)/(name+'.o');objs.append(str(o))
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(src),'-o',str(o)],check=True)
 p=Path(td)/'candidate.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),*objs],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];entry=next(x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name=='audio_uart_wait_clear')
 def run(native,state):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  if native:
   def bypass(uc,address,size,user):
    if address in (0x4420d0,0x4420e8):uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,bypass)
  task=0x20040000;u.mem_write(task+0x6c,bytes([state]))
  u.reg_write(A.UC_ARM_REG_R0,task);u.reg_write(A.UC_ARM_REG_R1,0)
  u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x455f5e if native else entry)|1,0x101ff0,count=200)
  return (u.reg_read(A.UC_ARM_REG_R0),u.mem_read(task+0x6c,1))
 for state in range(256):
  a=run(True,state);b=run(False,state);assert a==b,(state,a,b)
 print('PASS_AUDIO_UART_NOTIFY_CLEAR',256)
