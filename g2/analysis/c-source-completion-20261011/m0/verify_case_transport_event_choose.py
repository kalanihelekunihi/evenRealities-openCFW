#!/usr/bin/env python3
"""Native/source CASE 0xa836 event choose at allocation/create cuts."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_event_candidate_0a836.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 st=d/'st.c';st.write_text('#include <stdint.h>\nuint32_t case_boot_transport_event_allocate(uint32_t x){return x;}\nuint32_t case_boot_transport_event_create(uint32_t x){return x;}\n');so=d/'t.o';subprocess.run(flags+[str(st),'-o',str(so)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),str(so),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 orig={0x0800c48c:'allocate',0x0800c4aa:'create'};gen={sym['case_boot_transport_event_allocate']&~1:'allocate',sym['case_boot_transport_event_create']&~1:'create'}
 for i in range(160):
  descriptor=0 if i%8==0 else 0x20003000;storage=0 if i%3==0 else 0x20004000;size=[0,1,16,31,32,33,80][i%7];pairs=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20003000,struct.pack('<IIII',0,0,storage,size));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,descriptor)
   calls=[];targets=orig if native else gen
   def hook(uc,a,n,_):
    kind=targets.get(a)
    if kind is None:return
    x=uc.reg_read(UC_ARM_REG_R0);calls.append((kind,x));uc.reg_write(UC_ARM_REG_R0,0x11110000+(1 if kind=='create' else 2));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x0800a836 if native else sym['case_boot_transport_event'])|1,0x20008000,count=1000)
   pairs.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert pairs[0]==pairs[1],(i,descriptor,storage,size,pairs)
 print('PASS_CASE_TRANSPORT_EVENT_CHOOSE',160)
