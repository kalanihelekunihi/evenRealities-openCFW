#!/usr/bin/env python3
"""Check Thumb-1 long tail aliases preserve argument registers and stack."""
from pathlib import Path
import random,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
S=R/'g2/components/case/legacy_default_candidate_20261010'
sources=[S/'logger_aliases_candidate.c',S/'residual_r0_aliases_experiment.c']
stubs='''#include <stdint.h>
uint32_t g2_log_printf(const char *f,...){(void)f;return 0;}
void case_send(void){} void case_ack(void){} void log_hex_buffer(void){} void case_control_a(void){}
'''
names={
 'g2_log_printf':['case_legacy_logger','case_binary_3d_logger','case_binary_3e_logger','case_binary_3f_logger','case_binary_3f_program_log','case_binary_56_logger','case_binary_56_exit_log','case_binary_5e_logger','case_binary_5e_failure_log','case_binary_logger'],
 'case_send':['case_binary_14_send','case_binary_local_send','case_binary_send51','case_binary_send5f'],
 'case_ack':['case_binary_3e_ack','case_binary_3f_ack','case_binary_56_ack','case_binary_local_ack'],
 'log_hex_buffer':['case_binary_5e_hex'],'case_control_a':['case_legacy_gpio_bit0']}
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);fixture=d/'cut.c';fixture.write_text(stubs)
 objects=[]
 for src in sources+[fixture]:
  o=d/(src.stem+'.o');subprocess.run(flags+[str(src),'-o',str(o)],check=True);objects.append(o)
 elf=d/'aliases.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objects],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
 rng=random.Random(0x9170);cases=0
 for target,aliases in names.items():
  for alias in aliases:
   for i in range(32):
    regs=[rng.getrandbits(32) for _ in range(4)];stack=bytes(rng.getrandbits(8) for _ in range(24));captured=[]
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20007fc0,stack)
    for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),regs):u.reg_write(reg,val)
    u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
    def hook(uc,address,size,user):
     if address==(sym[target]&~1):
      captured.append(([uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],uc.reg_read(UC_ARM_REG_SP),uc.reg_read(UC_ARM_REG_LR),bytes(uc.mem_read(0x20007fc0,24))))
      uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(sym[alias]|1,0,count=30)
    assert captured==[(regs,0x20007fc0,0x20008001,stack)],(alias,i,captured)
    cases+=1
 print('PASS_CASE_LONG_TAIL_ALIAS_ABI',cases)
