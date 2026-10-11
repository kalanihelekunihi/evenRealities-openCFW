#!/usr/bin/env python3
"""Original-byte/C PCM registration comparison with controlled logger cuts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/pcm_register_source_candidate/register.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'register.o';e=t/'register.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_pcm_registration_rows=0x20073c20','--defsym=audio_log_flags=0x101011','--defsym=audio_log_extended=0x101021','--defsym=audio_log_simple=0x101031','-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def string(u,a):return bytes(u.mem_read(a,180)).split(b'\0',1)[0].decode('ascii')
 def run(native,owner,mode,callback,slot,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
  if native:u.mem_write(0x438000,STOCK)
  else:
   for a,b in segs:u.mem_write(a,b)
  address=0x20073c20+(mode&255)*12
  for i,v in enumerate(slot):put(u,address+4*i,v)
  u.reg_write(A.UC_ARM_REG_R0,owner);u.reg_write(A.UC_ARM_REG_R1,mode);u.reg_write(A.UC_ARM_REG_R2,callback);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  cuts=({0x43d0ce:'flags',0x43d574:'extended',0x43ce9e:'simple'} if native else {0x101010:'flags',0x101020:'extended',0x101030:'simple'})
  events=[];reads=[0];done=[False]
  def hook(c,pc,_size,_data):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   kind=cuts.get(pc)
   if kind is None:return
   r=[c.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=c.reg_read(A.UC_ARM_REG_SP)
   if kind=='flags':events.append((kind,));ret=flags[reads[0]%len(flags)];reads[0]+=1
   elif kind=='extended':
    line=word(c,sp);fmt=string(c,word(c,sp+4));args=((word(c,sp+8),word(c,sp+12)) if line==208 else (word(c,sp+8),) if line==198 else ())
    events.append((kind,r[0],string(c,r[1]),string(c,r[2]),string(c,r[3]),line,fmt,args));ret=0
   else:
    fmt=string(c,r[1]);args=((r[3],word(c,sp)) if 'registered: ID' in fmt else (r[3],) if 'occupied' in fmt else ())
    events.append((kind,r[0],fmt,string(c,r[2]),args));ret=0
   c.reg_write(A.UC_ARM_REG_R0,ret);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x57ab78 if native else sym['audio_register'])|1,0,count=600)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(address,12)),events
 n=0
 for owner in (0,7,0x10b):
  for mode in (0,1,2,256):
   for callback in (0,0x58f5e1):
    for slot in ((0,0x11223344,0),(7,0x8899aabb,0x58f4e5)):
     for flags in ((0,),(1,),(2,),(4,),(7,),(0,4,0)):
      a=run(True,owner,mode,callback,slot,flags);b=run(False,owner,mode,callback,slot,flags)
      assert a==b,(owner,mode,callback,slot,flags,a,b)
      n+=1
 print('PASS_AUDIO_PCM_REGISTER',n)
