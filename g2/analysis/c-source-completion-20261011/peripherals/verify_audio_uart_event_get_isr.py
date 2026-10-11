#!/usr/bin/env python3
"""Original-byte/C xEventGroupGetBitsFromISR incl BASEPRI restore."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/event_get_isr.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'get.o';p=Path(td)/'get.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_event_get_isr')
 def run(native,bits,basepri):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  event=0x20040000;u.mem_write(event,bits.to_bytes(4,'little'));u.reg_write(A.UC_ARM_REG_R0,event);u.reg_write(A.UC_ARM_REG_BASEPRI,basepri);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x47ed64 if native else entry)|1,0x101ff0,count=100)
  return u.reg_read(A.UC_ARM_REG_R0),u.reg_read(A.UC_ARM_REG_BASEPRI)
 count=0
 for bits,basepri in itertools.product((0,1,0x12345678,0xffffffff),(0,16,48,64)):
  a=run(True,bits,basepri);b=run(False,bits,basepri);assert a==b,(bits,basepri,a,b);count+=1
 print('PASS_AUDIO_UART_EVENT_GET_ISR',count)
