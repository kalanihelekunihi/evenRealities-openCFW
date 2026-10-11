#!/usr/bin/env python3
"""Compare native/C RTC MMIO transaction and delay with controlled counter."""
from pathlib import Path
import struct,subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/audio_log_format_source_candidate/rtc_latch.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'latch.o';p=Path(td)/'latch.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--defsym=audio_rtc_delay=0x101011','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_rtc_latch')
 def run(native,mode,control,clock,repeats):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x10000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  for a,v in ((0x4000400c,mode),(0x400083c0,control),(0x40008010,clock)):
   u.mem_write(a,struct.pack('<I',v))
  u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  writes=[];calls=[];reads=[0];done=[False]
  def code(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   load_sites=(0x4d3bf2,0x4d3bf4) if native else tuple((entry&~1)+x for x in (0x58,0x5a,0x60,0x62,0x68,0x6a,0x70,0x72))
   if pc in load_sites:
    cpu.mem_write(0x400083c4,struct.pack('<I',0 if reads[0]<=2*repeats else 1));reads[0]+=1
   if pc==(0x4807a0 if native else 0x101010):
    calls.append(('delay',cpu.reg_read(A.UC_ARM_REG_R0)))
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  def write(_cpu,_access,address,size,value,_user):
   if 0x40000000<=address<0x40010000:writes.append((address,size,value&((1<<(size*8))-1)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x4d3b9a if native else entry)|1,0,count=10000);assert done[0],(native,mode,control,clock,repeats,hex(u.reg_read(A.UC_ARM_REG_PC)),reads[0],hex(entry),writes[-8:])
  return writes,calls,reads[0]
 count=0
 for mode,control,clock,repeats in itertools.product((0,128,255),(0,1,2,0xffffffff),(0,0x10000),(0,1,3)):
  a=run(True,mode,control,clock,repeats);b=run(False,mode,control,clock,repeats)
  assert a==b,(mode,control,clock,repeats,a,b)
  count+=1
 print('PASS_AUDIO_RTC_LATCH',count)
