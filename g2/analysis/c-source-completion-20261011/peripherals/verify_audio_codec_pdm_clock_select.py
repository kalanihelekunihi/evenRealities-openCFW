#!/usr/bin/env python3
"""Native-byte/C comparison for PDM revision and source clock branches."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/codec_pdm_clock_select_source_candidate/select.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'select.o';q=t/'shim.o';e=t/'select.elf';shim=t/'shim.c'
 shim.write_text('#include <stdint.h>\nuint32_t g2_codec_clock_mux_request(uint32_t source,uint32_t delay_us) {(void)source;(void)delay_us;return 0;}\n')
 f=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror']
 subprocess.run(f+['-c',str(S),'-o',str(o)],check=True);subprocess.run(f+['-c',str(shim),'-o',str(q)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(e),str(o),str(q)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as ef:
  elf=ELFFile(ef);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def run(native,source,revision,current,enabled,instance):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40201000,0x5000);u.mem_map(0x40020000,0x1000)
  if native:u.mem_write(0x438000,STOCK)
  else:
   for a,b in segs:u.mem_write(a,b)
  reg=0x40201000+(instance<<12);put(u,reg,0x89abcdef & ~0xf | (current<<1)|enabled);put(u,0x400204e8,revision);put(u,0x400200c0,0x2468ace0)
  u.reg_write(A.UC_ARM_REG_R0,instance);u.reg_write(A.UC_ARM_REG_R1,(source<<8)|3);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  writes=[];calls=[];done=[False]
  child=0x539bbc if native else sym['g2_codec_clock_mux_request']&~1
  def code(v,pc,_s,_d):
   if pc==0x101180:done[0]=True;v.emu_stop()
   elif pc==child:
    calls.append((v.reg_read(A.UC_ARM_REG_R0),v.reg_read(A.UC_ARM_REG_R1)))
    v.reg_write(A.UC_ARM_REG_R0,0);v.reg_write(A.UC_ARM_REG_PC,v.reg_read(A.UC_ARM_REG_LR))
  def write(_u,_a,a,size,value,_d):
   if 0x40201000<=a<0x40206000 or a==0x400200c0:writes.append((a,size,value&((1<<(8*size))-1)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x591d7a if native else sym['g2_pdm_clock_select'])|1,0,count=1000)
  assert done[0]
  return writes,calls
 n=0
 for source in range(4):
  for revision in range(4):
   for current in range(8):
    for enabled in (0,1):
     for instance in (0,1):
      a=run(True,source,revision,current,enabled,instance);b=run(False,source,revision,current,enabled,instance)
      assert a==b,(source,revision,current,enabled,instance,a,b)
      n+=1
 print('PASS_AUDIO_CODEC_PDM_CLOCK_SELECT',n)
