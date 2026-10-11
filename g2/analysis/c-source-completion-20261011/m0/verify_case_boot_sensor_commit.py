#!/usr/bin/env python3
"""Bounded native/source CASE 0x856c descriptor calculation oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_commit_candidate.c';obj=H/'boot_sensor_commit.oracle.o';stub=H/'boot_sensor_commit.oracle_stub.c';stubobj=H/'boot_sensor_commit.oracle_stub.o';elf=H/'boot_sensor_commit.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
# Fixture values are read from the pinned stock image for comparison only;
# the candidate implementation retains both timing tables as external data.
dv=','.join(str(x) for x in F[0xd398:0xd3a0]);rt=','.join(str(x) for x in F[0xd3a0:0xd3a8])
stub.write_text('#include <stdint.h>\nconst uint8_t case_boot_sensor_divisor_table[8]={'+dv+'};\nconst uint8_t case_boot_sensor_rate_table[8]={'+rt+'};\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){uint32_t q=0;for(uint32_t i=32;;--i){uint32_t x=i==32?0:a>>i;if(x>=b){a-=i==32?0:b<<i;q+=i==32?0:1u<<i;}if(i==0)break;}return q;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x856c)
for i in range(96):
 control=rng.getrandbits(32);desc=bytearray(rng.randbytes(160));struct.pack_into('<I',desc,0,0x40013800);struct.pack_into('<I',desc,100,0 if i%4==0 else 0x20000000);hw=bytearray(rng.randbytes(16));struct.pack_into('<I',hw,8,control);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
  u.mem_write(0x20003000,bytes(desc));u.mem_write(0x40013800,bytes(hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  u.emu_start((0x0800856c if native else sym['case_boot_sensor_commit'])|1,0x20008000,count=2000)
  pair.append(bytes(u.mem_read(0x20003000,160)))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_SENSOR_COMMIT',96)
