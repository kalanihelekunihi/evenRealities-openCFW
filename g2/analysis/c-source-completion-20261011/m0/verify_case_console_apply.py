#!/usr/bin/env python3
"""CASE 0x4100 console apply native/source pin register and status oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_console_apply_candidate.c';obj=H/'console_apply.oracle.o';stub=H/'console_apply.oracle_stub.c';stubobj=H/'console_apply.oracle_stub.o';elf=H/'console_apply.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_adc_ready(uint32_t a){(void)a;return 0;}\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x4100)
values=[0x10000010,0x10000000,0x00000002,0x00000004,0x80000001,0xb0001000,0xb8004000,0xb4002000,0x80012340]
for i in range(256):
 desc=bytearray(rng.randbytes(104));hw=bytearray(rng.randbytes(64));value=values[i%len(values)];selector=[0,1,2,3,4,8,16,31][i%8];config=struct.pack('<3I',value,selector,rng.getrandbits(27))
 special=i%17==0;base=0x80000000 if special else 0x40012400;struct.pack_into('<I',desc,0,base);struct.pack_into('<I',desc,16,0x80000000 if special else 0);struct.pack_into('<I',desc,28,i%8+1);desc[84]=1 if i%23==0 else 0;ready=1 if i%19==0 else 0
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20003000,bytes(desc));u.mem_write(0x20004000,config);u.mem_write(0x20000124,struct.pack('<I',200000));u.mem_map(0x40012000,0x1000);u.mem_write(0x40012400,bytes(hw));u.mem_map(0x80000000,0x1000);u.mem_write(0x80000000,bytes(hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,0x20004000)
  targets={0x0800678a:'ready',0x08000160:'divide'} if native else {sym['case_policy_adc_ready']&~1:'ready',sym['case_policy_sensor_divide']&~1:'divide'};calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);calls.append((kind,x,y if kind=='divide' else None))
   if kind=='ready':uc.reg_write(UC_ARM_REG_R0,ready)
   else:uc.reg_write(UC_ARM_REG_R0,x//y);uc.reg_write(UC_ARM_REG_R1,x%y)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08004100 if native else sym['case_boot_console_apply'])|1,0x20008000,count=3000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,104)),bytes(u.mem_read(base,64)),bytes(u.mem_read(0x40012708,4))))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_CONSOLE_APPLY',256)
