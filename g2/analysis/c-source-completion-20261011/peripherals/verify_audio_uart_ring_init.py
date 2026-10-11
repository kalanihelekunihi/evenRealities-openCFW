#!/usr/bin/env python3
"""Native/C ring init comparison including real native memset helper."""
from pathlib import Path
import subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/ring_init.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'ring.o';p=Path(td)/'ring.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,capacity,element,mode):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  d=0x20040000;s=0x20050000;sp=0x200f0000
  u.mem_write(d,bytes([0xa5]*64));u.mem_write(s,bytes([0xa5]*256))
  for r,v in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3),(d,s,capacity,element)):u.reg_write(r,v)
  for i,v in enumerate((mode,0x1234,0x5678)):u.mem_write(sp+i*4,v.to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_SP,sp);u.reg_write(A.UC_ARM_REG_LR,0x101ff1)
  u.emu_start((0x57e3a4 if native else syms['audio_uart_transport_initialize'])|1,0x101ff0,count=5000)
  return bytes(u.mem_read(d,64)),bytes(u.mem_read(s,256))
 count=0
 for cap,elem,mode in itertools.product((5,6,32,128),(1,2,4),(2,3)):
  a=run(True,cap,elem,mode);b=run(False,cap,elem,mode);assert a==b,(cap,elem,mode,a,b);count+=1
 print('PASS_AUDIO_UART_RING_INIT',count)
