#!/usr/bin/env python3
"""Controlled native-byte/C locator call and output comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/tlsf_locate_free_candidate/locate.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'locate.o';e=t/'locate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 args=['--defsym=g2_file_close_error=0x101011','--defsym=g2_tlsf_fls=0x101021','--defsym=g2_tlsf_mapping_insert=0x101031','--defsym=g2_tlsf_block_size=0x101041','--defsym=g2_tlsf_remove_free_block=0x101051']
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*args,'-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
 def run(native,size,fl,sl,block,block_size):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  pool=0x20001000;u.reg_write(A.UC_ARM_REG_R0,pool);u.reg_write(A.UC_ARM_REG_R1,size);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  children=({0x4cff9a:'map',0x4cffc2:'search',0x4cfd70:'size',0x4d003a:'remove',0x4d09b4:'error'} if native else {sym['g2_tlsf_mapping_search']&~1:'map',sym['g2_tlsf_search_suitable_block']&~1:'search',0x101040:'size',0x101050:'remove',0x101010:'error'})
  calls=[];done=[False]
  def code(c,pc,_sz,_data):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   kind=children.get(pc)
   if kind is None:return
   r=[c.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if kind=='map':put(c,r[1],fl);put(c,r[2],sl);args=(r[0],)
   elif kind=='search':put(c,r[1],fl);put(c,r[2],sl);args=(r[0],)
   elif kind=='remove':args=(r[0],r[1],r[2],r[3])
   elif kind=='size':args=(r[0],)
   else:args=(r[2],)
   calls.append((kind,args))
   result={'map':0,'search':block,'size':block_size,'remove':0,'error':0}[kind]
   c.reg_write(A.UC_ARM_REG_R0,result);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x4d0484 if native else sym['g2_tlsf_find_suitable'])|1,0,count=300)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls
 n=0
 for size in (0,4,12,1000):
  for fl in (0,1,23,24,25):
   for sl in (0,3):
    for block in (0,0x20008000):
     for block_size in (0,1000):
      if block and block_size<size:continue # assertion path is separately source-defined
      a=run(True,size,fl,sl,block,block_size);b=run(False,size,fl,sl,block,block_size)
      assert a==b,(size,fl,sl,block,block_size,a,b)
      n+=1
 print('PASS_AUDIO_TLSF_LOCATE',n)
