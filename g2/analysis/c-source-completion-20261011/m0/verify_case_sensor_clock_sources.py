#!/usr/bin/env python3
"""CASE 0x5474/0x549c native/source clock calculations with pinned table fixture."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_clock_sources_candidate.c';obj=H/'sensor_clock_sources.oracle.o';stub=H/'sensor_clock_sources.oracle_stub.c';stubobj=H/'sensor_clock_sources.oracle_stub.o';elf=H/'sensor_clock_sources.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
values=','.join(str(x) for x in F[0xd3e8:0xd408]);stub.write_text('#include <stdint.h>\nconst uint8_t case_boot_clock_shift_table[32]={'+values+'};\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){uint32_t q=0;for(uint32_t i=32;;--i){uint32_t x=i==32?0:a>>i;if(x>=b){a-=i==32?0:b<<i;q+=i==32?0:1u<<i;}if(i==0)break;}return q;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x549c)
for i in range(192):
 mode=i%8;ctrl=(rng.getrandbits(32)&~0x38)|(mode<<3);pll=rng.getrandbits(32);base=rng.getrandbits(32);tick=rng.getrandbits(32);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000)
  u.mem_write(0x20000124,struct.pack('<I',tick));u.mem_write(0x40021000,struct.pack('<4I',base,0,ctrl,pll))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  op=i%2;u.emu_start(([0x08005474,0x0800549c][op] if native else sym[['case_boot_sensor_clock_5474','case_boot_sensor_clock_549c'][op]])|1,0x20008000,count=10000)
  pair.append(u.reg_read(UC_ARM_REG_R0))
 assert pair[0]==pair[1],(i,mode,pair)
print('PASS_CASE_SENSOR_CLOCK_SOURCES',192)
