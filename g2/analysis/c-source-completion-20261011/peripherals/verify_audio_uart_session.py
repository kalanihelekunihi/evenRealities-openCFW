#!/usr/bin/env python3
"""Controlled native/C UART session state and child-call comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_session_full_candidate/session.c'
STOCK=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 directory=Path(directory);obj=directory/'session.o';path=directory/'session.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'g2_audio_uart_ring_state':0x20073ed4,'g2_audio_uart_storage':0x200731b0,
       'g2_audio_uart_initialized':0x20075014,'g2_audio_uart_resumed':0x20075015,
       'codec_ring_initialize':0x101011,'codec_channel_callback':0x101021,
       'codec_channel_enable':0x101031,'codec_channel_disable':0x101041,
       'codec_uart_baud':0x101051,'codec_rx_callback':0x101061,
       'audio_log_flags':0x101071,'audio_log_extended':0x101081,
       'audio_log_simple':0x101091}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={key}=0x{value:x}' for key,value in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as stream:
  elf=ELFFile(stream);segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,entry,initialized,resumed,status):
  unit=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  unit.mem_map(0x438000,(len(STOCK)+4095)&~4095);unit.mem_map(0x100000,0x20000);unit.mem_map(0x20000000,0x100000);unit.mem_write(0x438000,STOCK)
  if not native:
   for address,data in segments:unit.mem_write(address,data)
  unit.mem_write(0x20075014,bytes((initialized,resumed)))
  unit.reg_write(A.UC_ARM_REG_SP,0x200f0000);unit.reg_write(A.UC_ARM_REG_LR,0x101181)
  targets=({0x598160:'ring',0x55e8f0:'callback',0x55e5bc:'enable',0x55e630:'disable',0x43d0ce:'flags'} if native else
           {0x101010:'ring',0x101020:'callback',0x101030:'enable',0x101040:'disable',0x101070:'flags'})
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=targets.get(pc)
   if kind is None:return
   r=[cpu.reg_read(getattr(A,f'UC_ARM_REG_R{i}')) for i in range(3)]
   if kind=='ring':calls.append((kind,*r))
   elif kind=='callback':calls.append((kind,r[0],'rx_callback'))
   elif kind in ('enable','disable'):calls.append((kind,r[0]))
   else:calls.append((kind,))
   cpu.reg_write(A.UC_ARM_REG_R0,status if kind in ('enable','disable') else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  unit.hook_add(UC_HOOK_CODE,hook)
  start=(0x58fb52 if entry=='open' else 0x58fc0c) if native else symbols['audio_uart_session_open' if entry=='open' else 'audio_uart_session_close']
  unit.emu_start(start|1,0,count=350)
  assert done[0],(native,entry,initialized,resumed,status)
  return unit.reg_read(A.UC_ARM_REG_R0),calls,bytes(unit.mem_read(0x20075014,2))
 total=0
 for entry in ('open','close'):
  for initialized in (0,1):
   for resumed in (0,1):
    for status in (0,7):
     original=run(True,entry,initialized,resumed,status);candidate=run(False,entry,initialized,resumed,status)
     assert original==candidate,(entry,initialized,resumed,status,original,candidate)
     total+=1
 print('PASS_AUDIO_UART_SESSION',total)
