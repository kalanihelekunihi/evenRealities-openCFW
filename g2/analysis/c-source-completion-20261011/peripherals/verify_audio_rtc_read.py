#!/usr/bin/env python3
"""Original-byte RTC calendar read against C with latch and IRQ cut."""
from pathlib import Path
import struct,subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/audio_log_format_source_candidate/rtc_read.c';B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 o=Path(td)/'rtc.o';p=Path(td)/'rtc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000','--defsym=g2_gpio_critical_save=0x101011','--defsym=audio_rtc_latch=0x101021','-o',str(p),str(o)],check=True,stderr=subprocess.DEVNULL)
 with p.open('rb') as f:
  e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_rtc_read_calendar')
 def run(native,timereg,datereg):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x10000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x40004820,struct.pack('<I',timereg));u.mem_write(0x40004824,struct.pack('<I',datereg));u.mem_write(0x20040000,bytes([0xa5])*40)
  u.reg_write(A.UC_ARM_REG_R0,0x20040000);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kind=({0x473940:'critical',0x4d3b9a:'latch'} if native else {0x101010:'critical',0x101020:'latch'}).get(pc)
   if kind is None:return
   calls.append(kind)
   if kind=='critical':cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x4d3c0a if native else entry)|1,0,count=10000);assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(0x20040000,40)),calls
 count=0
 for year,month,day,hour,minute,second,hundredths,invalid in itertools.product((0,0x12,0x99),(1,0x12),(1,0x31),(0,0x23),(0,0x59),(0,0x59),(0,0x99),(0,1)):
  time=(hour<<24)|(minute<<16)|(second<<8)|hundredths
  date=(invalid<<31)|(year<<16)|(month<<8)|day
  a=run(True,time,date);b=run(False,time,date)
  assert a==b,(hex(time),hex(date),a,b)
  count+=1
 print('PASS_AUDIO_RTC_READ',count)
