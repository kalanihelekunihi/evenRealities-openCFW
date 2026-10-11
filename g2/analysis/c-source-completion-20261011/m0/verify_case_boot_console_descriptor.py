#!/usr/bin/env python3
"""Native/source CASE 0x68f0 console descriptor and call comparison."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_console_initialize_candidate.c';obj=H/'boot_console_descriptor.oracle.o';stub=H/'boot_console_descriptor.oracle_stub.c';stubobj=H/'boot_console_descriptor.oracle_stub.o';elf=H/'boot_console_descriptor.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_console_open(uint32_t a){return a;}\nuint32_t case_boot_console_apply(uint32_t a,const uint32_t*b){(void)a;(void)b;return 0;}\nvoid case_boot_console_start(uint32_t a){(void)a;}\nvoid case_boot_init_failure(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
N={'case_boot_console_open':0x08004480,'case_boot_console_apply':0x08004100,'case_boot_console_start':0x08003fd0,'case_boot_init_failure':0x08003e90}
for fail in range(4):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  cuts={(N[n] if native else sym[n]&~1):n for n in N};trace=[]
  def hook(uc,a,size,_):
   if a in cuts:
    n=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    trace.append((n,r0,bytes(uc.mem_read(r1,12))) if n=='case_boot_console_apply' else (n,r0) if n!='case_boot_init_failure' else (n,))
    uc.reg_write(UC_ARM_REG_R0,1 if (fail==1 and n=='case_boot_console_open') or (fail==2 and n=='case_boot_console_apply') else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080068f0 if native else sym['case_boot_console_initialize'])|1,0x20008000,count=3000)
  pair.append((bytes(u.mem_read(0x200008e4,80)),trace))
 assert pair[0]==pair[1],(fail,pair)
print('PASS_CASE_BOOT_CONSOLE_DESCRIPTOR',4)
