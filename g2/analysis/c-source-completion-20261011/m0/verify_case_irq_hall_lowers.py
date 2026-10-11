#!/usr/bin/env python3
"""CASE 0x3848 / 0x2a5c original/C hall lower oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_irq_hall_lowers_candidate.c';obj=H/'irq_hall_lowers.oracle.o';stub=H/'irq_hall_lowers.oracle_stub.c';stubobj=H/'irq_hall_lowers.oracle_stub.o';elf=H/'irq_hall_lowers.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_led_left_clear(uint32_t x){(void)x;}\nvoid case_policy_led_right_clear(uint32_t x){(void)x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3848)
for i in range(160):
 state=bytearray(rng.randbytes(0x80));state[1]=i%128;state[16]=(i//3)%2;state[17]=(i//5)%2;state[50]=(i*9)%128;state[78]=(i*7)%128;state[0]=i%256;mode=i%3;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000bb,bytes([i%3]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,mode)
  targets=({0x08006b80:'left',0x08006b98:'right'} if native else {sym['case_policy_led_left_clear']&~1:'left',sym['case_policy_led_right_clear']&~1:'right'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08003848 if native else sym['case_boot_irq_hall_prepare'])|1,0x20008000,count=200)
  pair.append(calls)
 assert pair[0]==pair[1],(i,mode,pair)
print('PASS_CASE_IRQ_HALL_PREPARE',160)
