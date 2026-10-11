#!/usr/bin/env python3
"""Native/C 0x439be4 byte-copy side effects across alignments and lengths; r0 not compared."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/byte_copy.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'copy.o';p=Path(td)/'copy.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_checksum_copy')
 def run(native,da,sa,n):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  dest=0x20040000+da;source=0x20050000+sa
  u.mem_write(0x20040000,b'\xaa'*128);u.mem_write(0x20050000,bytes(range(128)))
  u.reg_write(A.UC_ARM_REG_R0,dest);u.reg_write(A.UC_ARM_REG_R1,source);u.reg_write(A.UC_ARM_REG_R2,n);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x439be4 if native else entry)|1,0x101ff0,count=1000)
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(0x20040000,128))
 count=0
 for da,sa,n in itertools.product(range(4),range(4),(0,1,2,3,4,5,7,8,15,16,17,31,32,63)):
  a=run(True,da,sa,n);b=run(False,da,sa,n);
  assert a[1]==b[1],(da,sa,n)
  count+=1
 print('PASS_AUDIO_UART_BYTE_COPY',count)
