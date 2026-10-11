#!/usr/bin/env python3
"""Original/source wake-list deadline update comparison."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_wake_cleanup_candidate.c';obj=H/'application_policy_wake_cleanup.oracle.o';elf=H/'application_policy_wake_cleanup.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xb260)
for i in range(128):
 memory=bytearray(0x10000);listaddr=0x200014a4;node=0x20002000;task=0x20003000;deadline=rng.randrange(2**32)
 struct.pack_into('<I',memory,0x128+52,listaddr);struct.pack_into('<I',memory,0x14a4,1 if i&1 else 0)
 struct.pack_into('<I',memory,0x14a4+12,node);struct.pack_into('<I',memory,0x2000+12,task);struct.pack_into('<I',memory,0x3000+4,deadline)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(memory))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x0800b260 if native else sym['case_policy_task_wake_cleanup'])|1,0x20001000,count=100)
  pair.append(bytes(u.mem_read(0x20000128,0x40)))
 assert pair[0]==pair[1],i
print('PASS_CASE_POLICY_WAKE_CLEANUP',128)
