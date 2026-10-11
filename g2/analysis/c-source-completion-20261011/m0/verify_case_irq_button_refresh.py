#!/usr/bin/env python3
"""CASE 0x3a84 original/C bounded button-refresh child-cut comparison."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_irq_button_refresh_candidate.c';obj=H/'irq_button_refresh.oracle.o';stub=H/'irq_button_refresh.oracle_stub.c';stubobj=H/'irq_button_refresh.oracle_stub.o';elf=H/'irq_button_refresh.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nint32_t case_init_read_product_byte(uint32_t *x){(void)x;return 0;}\nuint32_t case_legacy_logger(const char *x,...){(void)x;return 0;}\nuint32_t case_init_pmic_write(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3a84)
for i in range(128):
 state=bytearray(rng.randbytes(0x80));state[1]=i%64;state[3]=i%3==0;state[49]=i%5==0;state[51]=i%7==0;state[77]=i%4==0;state[79]=i%6==0
 state[56:58]=struct.pack('<H',i%4);state[84:86]=struct.pack('<H',i%3)
 quiet=i%2;sample=(i*17)%130;status=i%9==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000bf,bytes([quiet]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08009ebc:'sample',0x08009170:'log',0x080039c8:'write'} if native else {sym['case_init_read_product_byte']&~1:'sample',sym['case_legacy_logger']&~1:'log',sym['case_init_pmic_write']&~1:'write'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0)
   if kind=='sample':uc.mem_write(r0,struct.pack('<I',sample));calls.append((kind,));result=int(status)
   elif kind=='log':
    val=bytes(uc.mem_read(r0,80)).split(b'\0',1)[0]
    calls.append((kind,val,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)));result=0
   else:calls.append((kind,r0,uc.reg_read(UC_ARM_REG_R1)));result=0
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08003a84 if native else sym['case_boot_irq_button_refresh'])|1,0x20008000,count=1200)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x80))))
 assert pair[0]==pair[1],(i,pair[0][0],pair[1][0],[(x,a,b) for x,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b][:8])
print('PASS_CASE_IRQ_BUTTON_REFRESH',128)
