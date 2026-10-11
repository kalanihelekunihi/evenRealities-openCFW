#!/usr/bin/env python3
"""CASE 0x8420 / 0xc5ac original/C bounded child-call comparisons."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_systick_vector_candidate.c'
obj=H/'systick_vector.oracle.o';stub=H/'systick_vector.oracle_stub.c';stubobj=H/'systick_vector.oracle_stub.o';elf=H/'systick_vector.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_task_lookup(uint32_t x){return x;}\nuint32_t case_kernel_irq_save(void){return 0;}\nvoid case_kernel_irq_restore(uint32_t x){(void)x;}\nuint32_t case_policy_task_pended(void){return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x8420)
for i in range(192):
 vector=i<96;answer=[0,1,2,3][i%4];control=rng.getrandbits(32);tick=i%3==0
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x1000)
  u.mem_write(0xe000e010,control.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800ca4c:'mode',0x0800c5ac:'dispatch',0x080000f4:'save',0x0800ca78:'tick',0x080000fc:'restore'} if native else {sym['case_policy_task_lookup']&~1:'mode',sym['case_boot_systick_dispatch']&~1:'dispatch',sym['case_kernel_irq_save']&~1:'save',sym['case_policy_task_pended']&~1:'tick',sym['case_kernel_irq_restore']&~1:'restore'})
  if not vector:targets.pop(0x0800c5ac if native else sym['case_boot_systick_dispatch']&~1)
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0)))
   uc.reg_write(UC_ARM_REG_R0,answer if kind=='mode' else 0x42 if kind=='save' else int(tick) if kind=='tick' else 0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=(0x08008420 if vector else 0x0800c5ac) if native else sym['case_vector_systick_8420' if vector else 'case_boot_systick_dispatch']
  u.emu_start(entry|1,0x20008000,count=300)
  pair.append((calls,bytes(u.mem_read(0xe000ed04,4))))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SYSTICK_VECTOR',192)
