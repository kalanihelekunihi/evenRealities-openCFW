#!/usr/bin/env python3
"""CASE 0x8bd8 native/source validation with pinned table fixture."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_open_validate_candidate.c';obj=H/'sensor_validate.oracle.o';stub=H/'sensor_validate.oracle_stub.c';stubobj=H/'sensor_validate.oracle_stub.o';elf=H/'sensor_validate.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
table=struct.unpack('<12H',F[0xd380:0xd398]);values=','.join(str(x) for x in table)
stub.write_text('#include <stdint.h>\nconst uint16_t case_boot_sensor_prescale_table[12]={'+values+'};\nuint32_t case_boot_sensor_clock_5474(void){return 0;}\nuint32_t case_boot_sensor_clock_549c(void){return 0;}\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){uint32_t q=0;for(uint32_t i=32;;--i){uint32_t x=i==32?0:a>>i;if(x>=b){a-=i==32?0:b<<i;q+=i==32?0:1u<<i;}if(i==0)break;}return q;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x8bd8);bases=[0x40013800,0x40004400,0x40004800,0x40004c00,0x40005000,0x40013c00,0x40006000]
for i in range(128):
 hwbase=bases[i%len(bases)];desc=bytearray(rng.randbytes(160));hw=bytearray(rng.randbytes(48));clock=bytearray(rng.randbytes(0x100));struct.pack_into('<I',desc,0,hwbase)
 struct.pack_into('<I',desc,4,10+rng.randrange(10000));struct.pack_into('<I',desc,36,i%12);struct.pack_into('<I',desc,28,0x8000 if i%3==0 else 0)
 answer=0 if i%17==0 else 1000000+rng.randrange(1000000);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x20000);u.mem_map(0x40021000,0x1000)
  u.mem_write(0x20003000,bytes(desc));u.mem_write(hwbase,bytes(hw));u.mem_write(0x40021000,bytes(clock))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  targets=({0x08005474:'clock0',0x0800549c:'clock4'} if native else {sym['case_boot_sensor_clock_5474']&~1:'clock0',sym['case_boot_sensor_clock_549c']&~1:'clock4'})
  calls=[]
  def hook(uc,a,size,_):
   if a in targets:calls.append(targets[a]);uc.reg_write(UC_ARM_REG_R0,answer);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08008bd8 if native else sym['case_boot_sensor_open_validate'])|1,0x20008000,count=10000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,160)),bytes(u.mem_read(hwbase,48)),calls))
 assert pair[0]==pair[1],(i,hex(struct.unpack_from('<I',clock,0x54)[0]),pair)
print('PASS_CASE_SENSOR_OPEN_VALIDATE',128)
