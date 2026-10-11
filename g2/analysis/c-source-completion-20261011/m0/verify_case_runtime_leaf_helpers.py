#!/usr/bin/env python3
"""Native/source CASE 0x01e6 zero fill and a794/a7a2 delay leaves."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_runtime_leaf_helpers_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 st=d/'st.c';st.write_text('#include <stdint.h>\nvoid case_boot_task_fill(uint32_t a,uint32_t n,uint8_t v){volatile uint8_t *p=(volatile uint8_t *)(uintptr_t)a;for(uint32_t i=0;i<n;i++)p[i]=v;}\n');so=d/'t.o';subprocess.run(flags+[str(st),'-o',str(so)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),str(so),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 for offset,name in [(0x1e6,'case_boot_zero_fill'),(0xa794,'case_boot_short_delay_a794'),(0xa7a2,'case_boot_short_delay_a7a2')]:
  for count in range(0,64):
   pairs=[]
   for native in (True,False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20003000,bytes(range(128)));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000 if offset==0x1e6 else count);u.reg_write(UC_ARM_REG_R1,count)
    u.emu_start((0x08000000+offset if native else sym[name])|1,0x20008000,count=5000)
    pairs.append(bytes(u.mem_read(0x20003000,128)))
   assert pairs[0]==pairs[1],(hex(offset),count)
 print('PASS_CASE_RUNTIME_LEAF_HELPERS',3*64)
