#!/usr/bin/env python3
"""CASE 0x2b4c serial copy native/source at read/write child cuts."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_box_copy_sn_candidate.c';obj=H/'copy_sn.oracle.o';stub=H/'copy_sn.oracle_stub.c';stubobj=H/'copy_sn.oracle_stub.o';elf=H/'copy_sn.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_box_read_serial(uint8_t*a){(void)a;}\nvoid case_policy_box_read_identity(uint8_t*a){(void)a;}\nvoid case_boot_option_prepare(void){}\nuint32_t case_boot_option_write(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nvoid case_boot_option_commit_c(void){}\nuint32_t case_policy_log(uint32_t a){return a;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
orig={0x08002f60:'serial',0x08002f88:'identity',0x08004bf4:'prepare',0x08004b94:'write',0x08004b20:'commit',0x08009170:'log'}
srcs={sym['case_policy_box_read_serial']&~1:'serial',sym['case_policy_box_read_identity']&~1:'identity',sym['case_boot_option_prepare']&~1:'prepare',sym['case_boot_option_write']&~1:'write',sym['case_boot_option_commit_c']&~1:'commit',sym['case_policy_log']&~1:'log'}
rng=random.Random(0x2b4c)
for i in range(128):
 serial=rng.randbytes(8);identity=rng.randbytes(16);fail=(i%4)-1;quiet=i%2;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000bf,bytes([quiet]));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=orig if native else srcs;calls=[];writes=[0]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind=='serial':uc.mem_write(x,serial);calls.append((kind,))
   elif kind=='identity':uc.mem_write(x,identity);calls.append((kind,))
   elif kind=='write':calls.append((kind,x,y,z,w));writes[0]+=1;uc.reg_write(UC_ARM_REG_R0,1 if writes[0]==fail else 0)
   elif kind=='log':calls.append((kind,bytes(uc.mem_read(x,90)).split(b'\0')[0]))
   else:calls.append((kind,))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08002b4c if native else sym['case_policy_box_copy_sn'])|1,0x20008000,count=3000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOX_COPY_SN',128)
