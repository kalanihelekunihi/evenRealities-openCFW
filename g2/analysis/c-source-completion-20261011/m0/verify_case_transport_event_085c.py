#!/usr/bin/env python3
"""Native/source CASE 0x085c received frame at public command cuts."""
from pathlib import Path
import random,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_event_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 st=d/'st.c';st.write_text('#include <stdint.h>\nuint32_t case_legacy_command_candidate(const uint8_t *a,uint32_t b){(void)a;(void)b;return 0;}\nuint32_t case_binary_command_candidate(const uint8_t *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\n');so=d/'t.o';subprocess.run(flags+[str(st),'-o',str(so)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),str(so),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 orig={0x08000928:'legacy',0x08000e1c:'binary'};gen={sym['case_legacy_command_candidate']&~1:'legacy',sym['case_binary_command_candidate']&~1:'binary'}
 rng=random.Random(0x085c)
 for i in range(256):
  kind=i%8
  if kind==0:frame=b'\xde\x02\x34'
  elif kind==1:frame=b'DE1234'
  elif kind==2:frame=b'de00ee'
  elif kind==3:frame=b'\x5a\xa5\x7f\x02\x11\x22\x00'
  elif kind==4:frame=b'\x5a\xa5\xcf\x02\x00\x11\x22\x00'
  elif kind==5:frame=b'\x5a\xa5\x7f\x01\x11\x22\x00'
  elif kind==6:frame=b'\x5a\xa5\xcf\x01\x00\x11\x22\x00'
  else:frame=rng.randbytes(12)
  n=len(frame) if i%17 else 1;retry=[0,29,30,255][i%4];pairs=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x2000010a,struct.pack('<H',n));u.mem_write(0x20000893,bytes([retry]));u.mem_write(0x20000974,frame+bytes(32));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   calls=[];targets=orig if native else gen
   def hook(uc,a,size,_):
    kind=targets.get(a)
    if kind is None:return
    x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2)
    calls.append((kind,x,y,z if kind=='binary' else None));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x0800085c if native else sym['case_boot_transport_event_085c'])|1,0x20008000,count=3000)
   pairs.append((bytes(u.mem_read(0x20000974,len(frame)+32)),bytes(u.mem_read(0x20000893,1)),calls))
  assert pairs[0]==pairs[1],(i,frame,n,retry,pairs)
 print('PASS_CASE_TRANSPORT_EVENT_085C',256)
