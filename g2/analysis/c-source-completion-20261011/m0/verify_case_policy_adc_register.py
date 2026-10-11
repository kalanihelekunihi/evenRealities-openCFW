#!/usr/bin/env python3
"""Original/source register-reader comparisons for ADC tick, ready, special."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_adc_register_candidate.c';obj=H/'application_policy_adc_register.oracle.o';elf=H/'application_policy_adc_register.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x678a)
for name,addr in [('tick',0x08004eac),('ready',0x0800678a),('special',0x08006792)]:
 for i in range(128):
  value=rng.randrange(2**32);pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000120,struct.pack('<I',value))
   u.mem_map(0x40010000,0x1000);u.mem_write(0x40010000+(8 if name=='ready' else 12),struct.pack('<I',value))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,0x40010000)
   u.emu_start((addr if native else sym['case_policy_adc_'+name])|1,0x20001000,count=100)
   pair.append(u.reg_read(UC_ARM_REG_R0))
  assert pair[0]==pair[1],(name,i,value,pair)
 print('PASS_CASE_POLICY_ADC_'+name.upper(),128)
