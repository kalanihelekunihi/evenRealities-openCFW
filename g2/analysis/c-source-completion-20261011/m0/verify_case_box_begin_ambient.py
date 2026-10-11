#!/usr/bin/env python3
"""Compare native/source option selector stack slot at first child cut."""
from pathlib import Path
import random,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_box_begin_candidate.c'
stub='''#include <stdint.h>
void case_boot_read_option_words(uint32_t *w){(void)w;}
uint32_t case_boot_option_write(const uint32_t *w){(void)w;return 0;}
void case_boot_option_prepare(void){}
void case_boot_option_unlock(void){}
void case_boot_option_commit_a(void){}
void case_boot_option_commit_b(void){}
void case_boot_option_commit_c(void){}
uint32_t case_legacy_logger(const char *f,...){(void)f;return 0;}
void case_policy_sensor_delay(uint32_t t){(void)t;}
'''
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);fixture=d/'cut.c';fixture.write_text(stub)
 objects=[]
 for p in (src,fixture):
  o=d/(p.stem+'.o');subprocess.run(flags+[str(p),'-o',str(o)],check=True);objects.append(o)
 elf=d/'box.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objects],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
 rng=random.Random(0x38e0)
 for i in range(128):
  selector=rng.getrandbits(32);pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20007fc0-44,struct.pack('<I',selector))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   target=0x08004a00 if native else sym['case_boot_read_option_words']&~1
   def cut(uc,address,size,user):
    if address==target:
     p=uc.reg_read(UC_ARM_REG_R0)
     pair.append((p,struct.unpack('<I',uc.mem_read(p+4,4))[0]))
     uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,cut)
   u.emu_start((0x080038e0 if native else sym['case_policy_box_begin'])|1,0,count=300)
  assert pair==[(0x20007f90,selector)]*2,(i,hex(selector),pair)
 print('PASS_CASE_BOX_BEGIN_AMBIENT_SLOT',128)
