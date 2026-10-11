#!/usr/bin/env python3
"""Native/source boot bus and sensor descriptor/call comparison at child cuts."""
from pathlib import Path
import subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_bus_sensor_initialize_candidate.c'
obj=H/'boot_descriptors.oracle.o';stub=H/'boot_descriptors.oracle_stub.c';stubobj=H/'boot_descriptors.oracle_stub.o';elf=H/'boot_descriptors.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names=['case_boot_bus_open','case_boot_bus_set_frequency','case_boot_bus_start','case_boot_init_failure','case_boot_sensor_open','case_boot_sensor_set_mode','case_boot_sensor_set_clock','case_boot_sensor_start','case_boot_sensor_bind']
stub.write_text('#include <stdint.h>\n'+'\n'.join('uint32_t '+n+'(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}' for n in names))
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native={'case_boot_bus_open':0x08005a74,'case_boot_bus_set_frequency':0x0800598c,'case_boot_bus_start':0x08005910,'case_boot_init_failure':0x08003e90,'case_boot_sensor_open':0x08006240,'case_boot_sensor_set_mode':0x08005eb6,'case_boot_sensor_set_clock':0x08005e6e,'case_boot_sensor_start':0x08005e2e,'case_boot_sensor_bind':0x080064ec}
argc={names[0]:1,names[1]:3,names[2]:1,names[3]:0,names[4]:1,names[5]:2,names[6]:2,names[7]:1,names[8]:3}
for entry,d,length in [('bus',0x20000948,40),('sensor',0x20000e24,64)]:
 for failure in (-1,0,1,2,3):
  pair=[]
  for is_native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   cuts={((native[n] if is_native else sym[n])&~1):n for n in names};trace=[];seen=0
   def hook(uc,a,size,_):
    nonlocal_dummy=None
    if a in cuts:
     n=cuts[a]
     args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))[:argc[n]]
     trace.append((n,args))
     index=sum(x[0]!='case_boot_init_failure' for x in trace)-1
     uc.reg_write(UC_ARM_REG_R0,1 if index==failure else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   address=(0x08006bb0 if entry=='bus' else 0x08006c00) if is_native else sym['case_boot_'+entry+'_initialize']
   u.emu_start(address|1,0x20008000,count=3000)
   pair.append((trace,bytes(u.mem_read(d,length))))
  assert pair[0]==pair[1],(entry,failure,pair)
print('PASS_CASE_BOOT_DESCRIPTORS',10)
