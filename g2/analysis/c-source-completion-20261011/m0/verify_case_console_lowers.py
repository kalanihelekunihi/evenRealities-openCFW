#!/usr/bin/env python3
"""CASE 0x46a4 and 0x67b0 native/source console lower effects."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011';srcs=[S/'application_boot_console_reset_descriptor_candidate.c',S/'application_boot_console_write_field_candidate.c'];objs=[H/'console_reset.oracle.o',H/'console_field.oracle.o'];stub=H/'console_lower.oracle_stub.c';stubobj=H/'console_lower.oracle_stub.o';elf=H/'console_lower.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
for s,o in zip(srcs,objs):subprocess.run(flags+[str(s),'-o',str(o)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_bus_gpio_config(uint32_t a,volatile uint32_t*b){(void)a;(void)b;}\nvoid case_clock_priority_config(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nvoid case_boot_sensor_irq_enable(uint32_t a){(void)a;}\nvoid __aeabi_memclr4(void *p,uint32_t n){uint8_t *b=p;while(n--)*b++=0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x46a4)
for i in range(160):
 base=0x40012400 if i%3 else 0x40012800;clock=rng.getrandbits(32);apb=rng.getrandbits(32);field=rng.getrandbits(32);selector=rng.getrandbits(32);value=rng.getrandbits(32)
 for kind in ('reset','field'):
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20003000,struct.pack('<I',base));u.mem_map(0x40012000,0x1000);u.mem_write(0x40012414,struct.pack('<I',field));u.mem_map(0x40021000,0x1000);u.mem_write(0x40021040,struct.pack('<I',clock));u.mem_write(0x40021034,struct.pack('<I',apb))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000 if kind=='reset' else 0x40012400);u.reg_write(UC_ARM_REG_R1,selector);u.reg_write(UC_ARM_REG_R2,value)
   targets=({0x080001e6:'zero',0x08004d30:'gpio',0x08005024:'priority',0x0800500c:'irq'} if native else {sym['case_bus_gpio_config']&~1:'gpio',sym['case_clock_priority_config']&~1:'priority',sym['case_boot_sensor_irq_enable']&~1:'irq'})
   calls=[]
   def hook(uc,a,n,_):
    what=targets.get(a)
    if what is None:return
    x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2)
    if what=='zero':uc.mem_write(x,bytes(y))
    elif what=='gpio':calls.append((what,x,bytes(uc.mem_read(y,12))))
    elif what=='priority':calls.append((what,x,y,z))
    else:calls.append((what,x))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(0x080046a4 if kind=='reset' else 0x080067b0) if native else sym['case_boot_console_reset_descriptor' if kind=='reset' else 'case_boot_console_write_field']
   u.emu_start(entry|1,0x20008000,count=1000)
   pair.append((calls,bytes(u.mem_read(0x40021034,16)),bytes(u.mem_read(0x40012414,4))))
  assert pair[0]==pair[1],(i,kind,pair)
print('PASS_CASE_CONSOLE_LOWERS',320)
