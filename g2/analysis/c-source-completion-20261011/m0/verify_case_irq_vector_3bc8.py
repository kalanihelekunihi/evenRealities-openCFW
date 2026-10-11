#!/usr/bin/env python3
"""CASE 0x3bc8 original/C bounded PMIC IRQ branch and child-call oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_irq_vector_3bc8_candidate.c';obj=H/'irq_vector_3bc8.oracle.o';stub=H/'irq_vector_3bc8.oracle_stub.c';stubobj=H/'irq_vector_3bc8.oracle_stub.o';elf=H/'irq_vector_3bc8.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_init_pmic_read(uint32_t x,uint8_t *y,uint32_t z){(void)x;(void)y;(void)z;return 0;}\nuint32_t case_legacy_logger(const char *x,...){(void)x;return 0;}\nvoid case_boot_irq_button_refresh(void){}\nvoid case_boot_irq_clear(uint32_t x){(void)x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3bc8)
for i in range(96):
 status=bytearray(rng.randbytes(0x40));status[12:16]=struct.pack('<I',(rng.getrandbits(32)&~1)|(i&1));status[16:20]=struct.pack('<I',(rng.getrandbits(32)&~1)|((i>>1)&1));mute=(i>>2)&1;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_write(0x40021800,bytes(status));u.mem_write(0x200000bf,bytes([mute]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x080035d4:'pmic',0x08009170:'log',0x08003a84:'refresh',0x08004d04:'clear'} if native else {sym['case_init_pmic_read']&~1:'pmic',sym['case_legacy_logger']&~1:'log',sym['case_boot_irq_button_refresh']&~1:'refresh',sym['case_boot_irq_clear']&~1:'clear'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
   if kind=='log':
    value=bytes(uc.mem_read(r0,32)).split(b'\0',1)[0];calls.append((kind,value))
   elif kind=='pmic':calls.append((kind,r0,r2))
   elif kind=='clear':calls.append((kind,r0))
   else:calls.append((kind,))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08003bc8 if native else sym['case_vector_irq_3bc8'])|1,0x20008000,count=300)
  pair.append(calls)
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_IRQ_VECTOR_3BC8',96)
