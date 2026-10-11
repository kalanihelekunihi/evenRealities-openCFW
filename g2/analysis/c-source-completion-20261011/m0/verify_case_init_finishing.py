#!/usr/bin/env python3
"""Native/source finishing calls for LED, USB reset and sensor PMIC setup."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_init_finishing_candidate.c';obj=H/'application_init_finishing.oracle.o';stub=H/'application_init_finishing.oracle_stub.c';stubobj=H/'application_init_finishing.oracle_stub.o';elf=H/'application_init_finishing.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_init_pmic_write(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\nuint32_t case_init_pmic_reset(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\nvoid case_init_wait(uint32_t a){(void)a;}\nvoid case_policy_led_left_clear(uint32_t a){(void)a;}\nvoid case_policy_led_right_clear(uint32_t a){(void)a;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
nativecuts={0x080039c8:'write',0x080039e4:'reset',0x08004958:'wait',0x08006b80:'left',0x08006b98:'right'}
sourcecuts={sym['case_init_pmic_write']&~1:'write',sym['case_init_pmic_reset']&~1:'reset',sym['case_init_wait']&~1:'wait',sym['case_policy_led_left_clear']&~1:'left',sym['case_policy_led_right_clear']&~1:'right'}
for name,entry in [('led_show',0x38a0),('usb_reset',0x2b40),('sensor_finish',0x35f0)]:
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  cuts=nativecuts if native else sourcecuts;trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is not None:
    trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if k in ('reset','write') else (k,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08000000+entry if native else sym['case_init_'+name])|1,0x20008000,count=500)
  pair.append(trace)
 assert pair[0]==pair[1],(name,pair)
print('PASS_CASE_INIT_FINISHING',3)
