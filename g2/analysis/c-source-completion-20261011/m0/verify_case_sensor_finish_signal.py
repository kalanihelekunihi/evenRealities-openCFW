#!/usr/bin/env python3
"""CASE 0xa888 native/source task and ISR notification dispatch."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_finish_signal_candidate.c';obj=H/'sensor_signal.oracle.o';stub=H/'sensor_signal.oracle_stub.c';stubobj=H/'sensor_signal.oracle_stub.o';elf=H/'sensor_signal.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nint32_t case_boot_sensor_finish_signal_isr(uint32_t a,uint32_t b,uint32_t *c){(void)a;(void)b;(void)c;return 0;}\nint32_t case_boot_sensor_finish_signal_task(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xa888)
for i in range(96):
 task=0 if i%13==0 else 0x20003000;bits=0x01000000 if i%11==0 else rng.randrange(1,0x10000);isr=i%2;answer=i%3;woken=i%4==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x1000)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,task);u.reg_write(UC_ARM_REG_R1,bits);u.reg_write(UC_ARM_REG_XPSR,0x01000000|(15 if isr else 0))
  targets=({0x0800c568:'isr',0x0800c4de:'task'} if native else {sym['case_boot_sensor_finish_signal_isr']&~1:'isr',sym['case_boot_sensor_finish_signal_task']&~1:'task'})
  calls=[]
  def hook(uc,a,size,_):
   if a not in targets:return
   kind=targets[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);calls.append((kind,r0,r1))
   if kind=='isr':uc.mem_write(uc.reg_read(UC_ARM_REG_R2),struct.pack('<I',1 if woken else 0))
   uc.reg_write(UC_ARM_REG_R0,answer);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800a888 if native else sym['case_boot_sensor_finish_signal'])|1,0x20008000,count=500)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0xe000ed04,4)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SENSOR_FINISH_SIGNAL',96)
