#!/usr/bin/env python3
"""Native/source CASE 0x1334 aging reset at event/log provider cuts."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_aging_begin_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 st=d/'st.c';st.write_text('#include <stdint.h>\nint32_t case_policy_event_signal(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\nuint32_t case_policy_log(uint32_t a,...){(void)a;return 0;}\n');so=d/'t.o';subprocess.run(flags+[str(st),'-o',str(so)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),str(so),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 orig={0x0800aaf0:'signal',0x08009170:'log'};gen={sym['case_policy_event_signal']&~1:'signal',sym['case_policy_log']&~1:'log'}
 for i in range(128):
  quiet=i&1;seed=bytes(((j*13+i*7)&255) for j in range(0x70));pairs=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x200000b0,seed);u.mem_write(0x200000bf,bytes([quiet]));u.mem_write(0x200000d4,struct.pack('<II',0x20004000+i,0x20005000+i));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   calls=[];targets=orig if native else gen
   def hook(uc,a,n,_):
    kind=targets.get(a)
    if kind is None:return
    x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1)
    calls.append((kind,x,y if kind=='signal' else None));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08001334 if native else sym['case_boot_aging_begin'])|1,0x20008000,count=2000)
   pairs.append((bytes(u.mem_read(0x200000b0,0x70)),calls))
  assert pairs[0]==pairs[1],(i,pairs)
 print('PASS_CASE_AGING_BEGIN',128)
