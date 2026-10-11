#!/usr/bin/env python3
"""Native/source CASE 0x5910/0x598c bus MMIO ready-path comparison."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_bus_start_frequency_candidate.c';obj=H/'boot_bus_start_frequency.oracle.o';stub=H/'boot_bus_start_frequency.oracle_stub.c';stubobj=H/'boot_bus_start_frequency.oracle_stub.o';elf=H/'boot_bus_start_frequency.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_adc_tick(void){return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x5910)
for i in range(96):
 operation=i%2;frequency=rng.getrandbits(32);width=rng.randrange(8);busy=i%11==0;registers=[rng.getrandbits(32) for _ in range(24)];registers[3]|=0x44;descriptor=[0x40002800]+[rng.getrandbits(32) for _ in range(10)];descriptor[10]=(descriptor[10]&~0xff)|(1 if busy else 0);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40002000,0x1000);u.mem_map(0x40021000,0x1000)
  u.mem_write(0x20003000,struct.pack('<11I',*descriptor));u.mem_write(0x40002800,struct.pack('<24I',*registers));u.mem_write(0x40021880,struct.pack('<I',0))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,frequency);u.reg_write(UC_ARM_REG_R2,width)
  address=(0x08005910 if operation==0 else 0x0800598c) if native else sym['case_boot_bus_start' if operation==0 else 'case_boot_bus_set_frequency']
  u.emu_start(address|1,0x20008000,count=2000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,44)),bytes(u.mem_read(0x40002800,96)),bytes(u.mem_read(0x40021880,4))))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_BUS_START_FREQUENCY',96)
