#!/usr/bin/env python3
"""Native/C local time context comparison with controlled time children."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];SOURCE=R/'g2/components/audio/audio_log_format_source_candidate/context.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'context.o';path=Path(td)/'context.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_time_snapshot':0x101011,'audio_time_epoch_seconds':0x101021,'g2_audio_log_timezone':0x200036fc}
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],'-o',str(path),str(obj)],check=True,stderr=subprocess.DEVNULL)
 with path.open('rb') as f:
  e=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_log_context')
 def run(native,seconds,zone):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_write(0x438000,STOCK);u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x200036fc,struct.pack('<I',0x20040000));u.mem_write(0x20040000,bytes(8)+bytes([zone&255])+bytes(31))
  u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  calls=[];done=[False]
  def hook(cpu,pc,_size,_user):
   if pc==0x101180:done[0]=True;cpu.emu_stop();return
   kinds={0x47ef10:'snapshot',0x44a108:'epoch'} if native else {0x101010:'snapshot',0x101020:'epoch'}
   kind=kinds.get(pc)
   if kind is None:return
   r0=cpu.reg_read(A.UC_ARM_REG_R0);calls.append(kind)
   if kind=='snapshot':cpu.mem_write(r0,bytes(range(40)))
   else:cpu.reg_write(A.UC_ARM_REG_R0,seconds)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x44a1c6 if native else entry)|1,0,count=1000)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls
 count=0
 for zone in (-128,-64,-1,0,1,24,127):
  for seconds in (0,1,900,0x7fffffff,0xffffffff):
   a=run(True,seconds,zone);b=run(False,seconds,zone)
   assert a==b,(seconds,zone,a,b)
   count+=1
 print('PASS_AUDIO_LOG_CONTEXT',count)
