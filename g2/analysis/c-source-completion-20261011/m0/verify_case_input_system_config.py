#!/usr/bin/env python3
"""Compare CASE input/system configuration at the three real child cuts."""
from pathlib import Path
import struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_input_system_config_candidate.c'
obj=H/'input_system_config.oracle.o';stub=H/'input_system_config.oracle_stub.c';stubobj=H/'input_system_config.oracle_stub.o';elf=H/'input_system_config.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_clock_gate_enable(uint32_t a){(void)a;}\nuint32_t case_transfer_control_5528(const uint8_t *a){(void)a;return 0;}\nuint32_t case_boot_clock_device_apply(const uint32_t *a,uint32_t b){(void)a;(void)b;return 0;}\n__attribute__((noreturn)) void case_boot_init_failure(void){for(;;){}}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
for name,entry in [('case_boot_input_initialize',0x08008438),('case_policy_system_reset',0x0800b600)]:
 results=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.reg_write(UC_ARM_REG_SP,0x20007f00);u.reg_write(UC_ARM_REG_LR,0x20008001)
  calls=[];targets={0x08005048:'gate',0x08005528:'plan',0x080052e4:'apply'} if native else {sym['case_boot_clock_gate_enable']&~1:'gate',sym['case_transfer_control_5528']&~1:'plan',sym['case_boot_clock_device_apply']&~1:'apply'}
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0)
   if kind=='gate':item=(kind,r0)
   elif kind=='plan':item=(kind,bytes(uc.mem_read(r0,56)))
   else:item=(kind,bytes(uc.mem_read(r0,16)),uc.reg_read(UC_ARM_REG_R1))
   calls.append(item);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((entry if native else sym[name])|1,0x20008000,count=2000)
  results.append(calls)
 assert results[0]==results[1],(name,results)
print('PASS_CASE_INPUT_SYSTEM_CONFIG',2)
