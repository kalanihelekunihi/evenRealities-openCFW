#!/usr/bin/env python3
"""Controlled original-byte/C UART session wrapper comparison."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/transaction_session_source_candidate/session.c'
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 directory=Path(directory);obj=directory/'session.o';path=directory/'session.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_uart_session_open':0x101011,'audio_uart_session_close':0x101021,
       'audio_uart_set_baud':0x101031,'audio_log_flags':0x101041,
       'audio_log_extended':0x101051,'audio_log_simple':0x101061}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={key}=0x{value:x}' for key,value in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,entry,status):
  unit=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  unit.mem_map(0x438000,(len(STOCK)+4095)&~4095);unit.mem_map(0x100000,0x20000);unit.mem_map(0x20000000,0x100000);unit.mem_write(0x438000,STOCK)
  if not native:
   for address,data in segments:unit.mem_write(address,data)
  unit.reg_write(A.UC_ARM_REG_SP,0x200f0000);unit.reg_write(A.UC_ARM_REG_LR,0x101181)
  targets=({0x58fb52:'open',0x58fc0c:'close',0x58fab6:'baud',0x43d0ce:'flags'} if native else
           {0x101010:'open',0x101020:'close',0x101030:'baud',0x101040:'flags'})
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=targets.get(pc)
   if kind is None:return
   calls.append((kind,cpu.reg_read(A.UC_ARM_REG_R0)) if kind=='baud' else (kind,))
   cpu.reg_write(A.UC_ARM_REG_R0,status if kind=='open' else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  unit.hook_add(UC_HOOK_CODE,hook)
  start=(0x57ba88 if entry=='init' else 0x57baec) if native else symbols['audio_transaction_init' if entry=='init' else 'audio_transaction_cleanup']
  unit.emu_start(start|1,0,count=200)
  assert done[0],(native,entry,status)
  return (unit.reg_read(A.UC_ARM_REG_R0) if entry=='init' else 0,calls)
 total=0
 for entry in ('init','cleanup'):
  for status in (0,1,0xfffffffe):
   original=run(True,entry,status);candidate=run(False,entry,status)
   assert original==candidate,(entry,status,original,candidate)
   total+=1
 print('PASS_AUDIO_TRANSACTION_SESSION',total)
