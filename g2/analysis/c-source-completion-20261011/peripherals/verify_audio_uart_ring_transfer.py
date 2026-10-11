#!/usr/bin/env python3
"""Bounded native/C ring transfer comparison; valid and framed cases."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4]; S=R/'g2/components/audio/uart_thread_source_candidate'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 objs=[]
 for name in ('ring_transfer','ring_copy','byte_copy'):
  o=Path(td)/(name+'.o');objs.append(str(o))
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S/(name+'.c')),'-o',str(o)],check=True)
 fatal=Path(td)/'fatal.c';fatal.write_text('void offline_assert(void) { for (;;) {} }\n')
 o=Path(td)/'fatal.o';objs.append(str(o))
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(fatal),'-o',str(o)],check=True)
 elf=Path(td)/'candidate.elf'
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(elf),*objs],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 def run(native,read,framed,cap,head,tail,request,available,frame_length=None):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  d=0x20040000;buf=0x20041000;store=0x20042000
  for off,val in ((0,head),(4,tail),(8,cap),(24,store)):
   u.mem_write(d+off,val.to_bytes(4,'little'))
  u.mem_write(d+28,bytes([framed]));u.mem_write(buf,bytes((i*13+7)&255 for i in range(128)))
  u.mem_write(store,bytes((i*17+11)&255 for i in range(128)))
  if frame_length is not None:
   header=frame_length.to_bytes(4,'little')
   for i,byte in enumerate(header):u.mem_write(store+(head+i)%cap,bytes([byte]))
  address=(0x57e220 if read else 0x57e0f0) if native else syms['audio_uart_ring_read' if read else 'audio_uart_ring_write']
  for reg,val in ((A.UC_ARM_REG_R0,d),(A.UC_ARM_REG_R1,buf),(A.UC_ARM_REG_R2,request),(A.UC_ARM_REG_R3,available),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101ff1)):
   u.reg_write(reg,val)
  u.emu_start(address|1,0x101ff0,count=2000)
  return (u.reg_read(A.UC_ARM_REG_R0),u.mem_read(d,36),u.mem_read(buf,128),u.mem_read(store,128))
 n=0
 for read in (False,True):
  for framed in (0,1):
   for cap in (16,32):
    for head,tail in ((0,0),(3,7),(cap-3,cap-2)):
     for request in (1,2,4,6):
      for available in (4,8):
       if framed and read:
        # Header bytes are native ring data; skip invalid length/fatal cases.
        continue
       if framed and not read and available<request+4:continue
       if not read and request>available and not framed:continue
       if read and request>available:continue
       a=run(True,read,framed,cap,head,tail,request,available)
       b=run(False,read,framed,cap,head,tail,request,available)
       assert a==b,(read,framed,cap,head,tail,request,available,a[0],b[0])
       n+=1
 for cap in (16,32):
  for head in (0,2,cap-3):
   for frame_length in (1,2,4,6):
    available=4+frame_length
    a=run(True,True,1,cap,head,(head+available)%cap,8,available,frame_length)
    b=run(False,True,1,cap,head,(head+available)%cap,8,available,frame_length)
    assert a==b,('framed-read',cap,head,frame_length,a[0],b[0])
    n+=1
 print('PASS_AUDIO_UART_RING_TRANSFER',n)
