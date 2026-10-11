#!/usr/bin/env python3
"""Native-byte/C TLSF bitmap search and locator comparisons."""
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
 def run(native,fl,sl,kind,chosen):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  pool,f,s=0x20001000,0x20006000,0x20006004;put(u,f,fl);put(u,s,sl)
  if kind=='same':
   put(u,pool+20+4*fl,1<<chosen);put(u,pool+0x74+128*fl+4*chosen,0x20008000)
  elif kind=='next':
   put(u,pool+16,1<<(fl+1));put(u,pool+20+4*(fl+1),1<<chosen);put(u,pool+0x74+128*(fl+1)+4*chosen,0x20008000)
  u.reg_write(A.UC_ARM_REG_R0,pool);u.reg_write(A.UC_ARM_REG_R1,f);u.reg_write(A.UC_ARM_REG_R2,s);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  done=[False]
  def code(c,pc,_size,_data):
   if pc==0x101180:done[0]=True;c.emu_stop()
  u.hook_add(UC_HOOK_CODE,code)
  u.emu_start((0x4cffc2 if native else sym['g2_tlsf_search_suitable_block'])|1,0,count=300)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),word(u,f),word(u,s)
 n=0
 for fl in range(4):
  for sl in range(4):
   for kind in ('same','next','none'):
    for chosen in range(sl,8):
     a=run(True,fl,sl,kind,chosen);b=run(False,fl,sl,kind,chosen)
     assert a==b,(fl,sl,kind,chosen,a,b)
     n+=1
 print('PASS_AUDIO_TLSF_SEARCH',n)
