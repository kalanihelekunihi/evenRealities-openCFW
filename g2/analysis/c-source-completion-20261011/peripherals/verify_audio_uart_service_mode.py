#!/usr/bin/env python3
"""Native/C service mode getter comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/service_small.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'mode.o';p=Path(td)/'mode.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--defsym=g2_audio_service_mode=0x20075024','--defsym=audio_uart_sync_reset0=0x101011','--defsym=audio_uart_sync_reset1=0x101021','--defsym=audio_uart_sync_reset2=0x101031','--defsym=audio_uart_sync_callback=0x101041','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_service_mode')
 def run(native,value):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20075024,bytes([value]));u.reg_write(A.UC_ARM_REG_LR,0x101ff1);u.reg_write(A.UC_ARM_REG_SP,0x200f0000)
  u.emu_start((0x45a570 if native else entry)|1,0x101ff0,count=20);return u.reg_read(A.UC_ARM_REG_R0)
 for i in range(256):assert run(True,i)==run(False,i)==i
 print('PASS_AUDIO_UART_SERVICE_MODE 256')
