#!/usr/bin/env python3
"""Native/source PMIC write transaction traces at physical bus cuts."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_init_pmic_write_candidate.c';obj=H/'application_init_pmic_write.oracle.o';stub=H/'application_init_pmic_write.oracle_stub.c';stubobj=H/'application_init_pmic_write.oracle_stub.o';elf=H/'application_init_pmic_write.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_pmic_bus_start(void){}\nvoid case_pmic_bus_write_byte(uint32_t a){(void)a;}\nuint32_t case_pmic_bus_ack(void){return 0;}\nvoid case_pmic_bus_stop(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x29a4)
for i in range(96):
 which=i&1;reg=rng.randrange(256);value=rng.randrange(256);retry=(i//2)%4;later_failure=(i//8)%3;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000114,b'\xff')
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,reg);u.reg_write(UC_ARM_REG_R1,value)
  cuts=({0x0800a4b4:'start',0x0800a46c:'byte',0x0800a4fa:'ack',0x0800a4dc:'stop'} if native else {sym['case_pmic_bus_start']&~1:'start',sym['case_pmic_bus_write_byte']&~1:'byte',sym['case_pmic_bus_ack']&~1:'ack',sym['case_pmic_bus_stop']&~1:'stop'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   if k=='byte':trace.append((k,uc.reg_read(UC_ARM_REG_R0)))
   else:trace.append((k,))
   if k=='ack':
    n=sum(t[0]=='ack' for t in trace)-1
    fail=n<retry or (later_failure and n==retry+later_failure)
    uc.reg_write(UC_ARM_REG_R0,int(bool(fail)))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  source='case_init_pmic_device_write' if which==0 else 'case_init_pmic_device_reset'
  entry=0x080029a4 if which==0 else 0x08002a00
  u.emu_start((entry if native else sym[source])|1,0x20008000,count=3000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000114,1)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_PMIC_DEVICE_WRITE',96)
