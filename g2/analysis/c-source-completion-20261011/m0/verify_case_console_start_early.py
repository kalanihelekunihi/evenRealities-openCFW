#!/usr/bin/env python3
"""CASE console start bounded early-state stock/C comparison."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_console_start_candidate.c';obj=H/'console_start.oracle.o';stub=H/'console_start.oracle_stub.c';stubobj=H/'console_start.oracle_stub.o';elf=H/'console_start.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_adc_open_config(uint32_t x){(void)x;return 0;}\nuint32_t case_policy_sensor_divide(uint32_t x,uint32_t y){(void)y;return x;}\nuint32_t case_policy_adc_tick(void){return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3fd0)
for i in range(128):
 descriptor=bytearray(rng.randbytes(0x90));hw=bytearray(rng.randbytes(0x100));struct.pack_into('<I',descriptor,0,0x40010000)
 descriptor[84]=1 if i%2 else 0;struct.pack_into('<I',hw,8,struct.unpack_from('<I',hw,8)[0]|1)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40010000,0x1000);u.mem_write(0x20002000,bytes(descriptor));u.mem_write(0x40010000,bytes(hw))
  u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08000734:'open'} if native else {sym['case_policy_adc_open_config']&~1:'open'})
  calls=[]
  def hook(uc,a,size,_):
   if a not in targets:return
   calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,3);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08003fd0 if native else sym['case_boot_console_start'])|1,0x20008000,count=300)
  pair.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20002000,0x90)),bytes(u.mem_read(0x40010000,0x100))))
 assert pair[0]==pair[1],(i,pair[0][:2],pair[1][:2],[(hex(j),a,b) for j,(a,b) in enumerate(zip(pair[0][2]+pair[0][3],pair[1][2]+pair[1][3])) if a!=b][:8])
print('PASS_CASE_CONSOLE_START_EARLY',128)
