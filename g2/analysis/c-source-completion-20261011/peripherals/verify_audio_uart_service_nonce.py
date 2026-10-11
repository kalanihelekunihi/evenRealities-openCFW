#!/usr/bin/env python3
"""Native/C four-byte product nonce snapshot comparison."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/service_nonce.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'nonce.o';p=Path(td)/'nonce.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--defsym=g2_uart_service_nonce=0x20074928','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_uart_service_nonce')
 def run(native,data,nonnull):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20074928,bytes(data));u.mem_write(0x20050000,b'\xaa'*4)
  u.reg_write(A.UC_ARM_REG_R0,0x20050000 if nonnull else 0);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x4ac776 if native else entry)|1,0x101ff0,count=100)
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(0x20050000,4))
 count=0
 for d,nonnull in itertools.product(((0,0,0,0),(1,2,3,4),(255,128,64,32),(17,34,51,68)),(0,1)):
  a=run(True,d,nonnull);b=run(False,d,nonnull);assert a==b,(d,nonnull,a,b);count+=1
 print('PASS_AUDIO_UART_SERVICE_NONCE',count)
