#!/usr/bin/env python3
"""Original-byte calendar conversion versus standalone C provider."""
from pathlib import Path
import struct,subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/audio_log_format_source_candidate/epoch.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'epoch.o';path=Path(td)/'epoch.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as f:
  e=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_time_epoch_seconds')
 def run(native,record):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20040000,struct.pack('<10I',*record));u.reg_write(A.UC_ARM_REG_R0,0x20040000);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x44a108 if native else entry)|1,0,count=1000);assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0)
 count=0
 for year,month,day,hour,minute,second,hundredths in itertools.product((0,1,4,24,99),(1,2,3,6,12),(1,28,31),(0,12,23),(0,59),(0,59),(0,49,50,99)):
  record=[0,0,0,year,month,day,hour,minute,second,hundredths]
  a=run(True,record);b=run(False,record)
  assert a==b,(record,a,b)
  count+=1
 print('PASS_AUDIO_TIME_EPOCH',count)
