#!/usr/bin/env python3
"""Original/C bounded byte-copy cases for native 0x44b5a0."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/dashboard_copy_limited.c'
with tempfile.TemporaryDirectory() as td:
 epath=Path(td)/'copy.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_dashboard_copy_limited',str(S),'-o',str(epath)],check=True)
 with epath.open('rb') as f:
  e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,source,n,offset):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  dst=0x20081000;src=0x20080000+offset
  u.mem_write(src,source+b'X'*64);u.mem_write(dst,b'Z'*64)
  for reg,val in ((UC_ARM_REG_R0,dst),(UC_ARM_REG_R1,src),(UC_ARM_REG_R2,n),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_dashboard_copy_limited'] if c else 0x44b5a0)|1,0x600000,count=10000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dst,64))
 cases=0
 for off in range(4):
  for n in (0,1,2,3,4,7,16,31):
   for source in (b'abcdefghijklmnopqrstuvwxzy0123456789',b'abc\0efghijklmnopqrstuvwx',b'\0abcdefghijk'):
    a=run(False,source,n,off);b=run(True,source,n,off)
    assert a==b,(off,n,source,a,b)
    cases+=1
 print('PASS_DASHBOARD_COPY_NATIVE',cases)
