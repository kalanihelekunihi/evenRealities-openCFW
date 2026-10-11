#!/usr/bin/env python3
"""Bounded native/C TinyFrame timer removal with no cancellation callback."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/uart_thread_source_candidate/module_expire.c'
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'module.o';p=Path(td)/'module.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];entry=next(x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name=='audio_uart_module_timer_expire')
 def run(native,active,slot,count,callback=False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  m=0x20040000;t=m+0x6430+slot*0x18
  u.mem_write(m+0x7158,bytes([count]));u.mem_write(t+4,active.to_bytes(4,'little'))
  u.mem_write(t+8,(0x20050101).to_bytes(4,'little'))
  u.mem_write(t+16,(0x12345678 if callback else 0).to_bytes(4,'little'))
  u.mem_write(t+20,(0x89abcdef if callback else 0).to_bytes(4,'little'))
  calls=[]
  def cut(uc,address,size,user):
   if address==0x101100:
    record=uc.reg_read(A.UC_ARM_REG_R1)
    calls.append((uc.reg_read(A.UC_ARM_REG_R0),uc.mem_read(record+8,4),
                  uc.mem_read(record+16,8)))
    uc.reg_write(A.UC_ARM_REG_PC,uc.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,cut)
  for reg,val in ((A.UC_ARM_REG_R0,m),(A.UC_ARM_REG_R1,slot),(A.UC_ARM_REG_R2,t),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101ff1)):u.reg_write(reg,val)
  u.emu_start((0x49183e if native else entry)|1,0x101ff0,count=200)
  return (u.mem_read(m+0x7158,1),u.mem_read(t,24),calls)
 n=0
 for active in (0,0x20050101):
  for slot in range(4):
   for count in range(0,6):
    a=run(True,active,slot,count);b=run(False,active,slot,count)
    assert a==b,(active,slot,count,a,b)
    n+=1
 for slot in range(3):
  for count in range(1,5):
   a=run(True,0x101101,slot,count,True)
   b=run(False,0x101101,slot,count,True)
   assert a==b,('callback',slot,count,a,b)
   n+=1
 print('PASS_AUDIO_UART_MODULE_EXPIRE',n)
