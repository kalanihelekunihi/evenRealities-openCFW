#!/usr/bin/env python3
"""Bounded original-byte/C codec allocation mutex and pool call comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/codec_heap_allocate_source_candidate/allocate.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'allocate.o';e=t/'allocate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 names={'g2_codec_heap_mutex':0x200748f8,'g2_codec_heap_pool':0x20074abc,'audio_file_mutex_acquire':0x101011,'audio_file_mutex_release':0x101021,'g2_file_pool_allocate':0x101031,'g2_file_heap_error_log':0x101041,'g2_file_close_error':0x101051}
 args=['--defsym='+k+'='+hex(v) for k,v in names.items()]
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*args,'-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def string(u,a):return bytes(u.mem_read(a,100)).split(b'\0',1)[0].decode('ascii')
 def run(native,lock,bytes_,allocation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
  u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  put(u,0x200748f8,0x20007700);put(u,0x20074abc,0x20008800)
  u.reg_write(A.UC_ARM_REG_R0,bytes_);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  children=({0x4497b6:'acquire',0x44981c:'release',0x4d0722:'allocate',0x4733ee:'error_log',0x4d09b4:'error'} if native else {0x101010:'acquire',0x101020:'release',0x101030:'allocate',0x101040:'error_log',0x101050:'error'})
  calls=[];done=[False]
  def code(c,pc,_size,_data):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   kind=children.get(pc)
   if kind is None:return
   r0=c.reg_read(A.UC_ARM_REG_R0);r1=c.reg_read(A.UC_ARM_REG_R1);r2=c.reg_read(A.UC_ARM_REG_R2)
   if kind=='error_log':args=(string(c,r0),)
   elif kind=='error':args=(string(c,r0),string(c,r1),r2)
   else:args=(r0,r1) if kind in ('acquire','allocate') else (r0,)
   calls.append((kind,args))
   c.reg_write(A.UC_ARM_REG_R0,lock if kind=='acquire' else allocation if kind=='allocate' else 0)
   c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x474cd2 if native else sym['codec_allocate'])|1,0,count=300)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls
 n=0
 for lock in (0,1,0xffffffff):
  for bytes_ in (0,1,16,1000,0xffffffff):
   for allocation in (0,0x20009000):
    a=run(True,lock,bytes_,allocation);b=run(False,lock,bytes_,allocation)
    assert a==b,(lock,bytes_,allocation,a,b)
    n+=1
 print('PASS_AUDIO_CODEC_HEAP_ALLOCATE',n)
