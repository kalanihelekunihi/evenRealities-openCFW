#!/usr/bin/env python3
"""Compare 0xa598 application entry lower-call order through option read."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/application_entry_candidate.c'
names=['clock_restore','input_initialize','pin_initialize','power_initialize','bus_initialize','sensor_initialize','console_initialize','read_option_words']
addrs=[0x08004eec,0x08008438,0x08006a40,0x08002888,0x08006bb0,0x08006c00,0x080068f0,0x08004a00]
more=['log','option_prepare','option_unlock','option_write','option_commit_a','option_commit_b','option_commit_c','service_start','transport_start','scheduler_start']
stub=HERE/'application_entry_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n'+''.join('__attribute__((noinline,used)) void case_boot_'+n+'(void){__asm__ volatile("nop");}\n' for n in names[:7])+ '__attribute__((noinline,used)) void case_boot_read_option_words(uint32_t *p){(void)p;__asm__ volatile("nop");}\n'+''.join('__attribute__((noinline,used)) void case_boot_'+n+'(void){__asm__ volatile("nop");}\n' for n in more)+'void case_application_initialize_2fc8(void){}\n')
objs=[]
for source in (SRC,stub):
 obj=HERE/(source.stem+'.oracle.o');objs.append(obj)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(source),'-o',str(obj)],check=True)
elf=HERE/'application_entry_oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-e','case_application_entry_a598','-Ttext=0x00100000',*[str(x) for x in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for original in (True,False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
 lookup={addr:i for i,addr in enumerate(addrs if original else [sym['case_boot_'+n]&~1 for n in names])}
 seen=[]
 def cut(u,a,size,user):
  if a in lookup:
   seen.append(lookup[a]);
   if lookup[a]==7:u.emu_stop()
   else:u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,cut)
 u.emu_start((0x0800a598 if original else sym['case_application_entry_a598'])|1,0x20001000,count=10000)
 assert seen==list(range(8)),(original,seen,hex(u.reg_read(UC_ARM_REG_PC)))
print('PASS_CASE_APPLICATION_ENTRY_PREFIX',8)
