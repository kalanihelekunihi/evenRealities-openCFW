#!/usr/bin/env python3
"""CASE 0x497c option erase arbitration/native child contract comparison."""
from pathlib import Path
import struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_option_erase_execute_candidate.c';obj=H/'erase_exec.oracle.o';stub=H/'erase_exec.oracle_stub.c';stubobj=H/'erase_exec.oracle_stub.o';elf=H/'erase_exec.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_option_wait(uint32_t a){(void)a;return 0;}\nvoid case_boot_option_mass_erase(uint32_t a){(void)a;}\nvoid case_boot_option_page_erase(uint32_t a,uint32_t b){(void)a;(void)b;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
for i in range(160):
 mode=4 if i%4==0 else 2;busy=1 if i%13==0 else 0;length=i%5;start=i%17;waitfail=i%7;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40022000,0x1000);u.mem_write(0x20000f98,bytes([busy]));u.mem_write(0x20003000,struct.pack('<4I',mode,0x8000,start,length));u.mem_write(0x20003100,struct.pack('<I',0x12345678));u.mem_write(0x40022014,struct.pack('<I',0xffffffff))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,0x20003100)
  targets=({0x08003f6c:'wait',0x08003e94:'mass',0x08003eec:'page'} if native else {sym['case_boot_option_wait']&~1:'wait',sym['case_boot_option_mass_erase']&~1:'mass',sym['case_boot_option_page_erase']&~1:'page'})
  calls=[];waits=[0]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);calls.append((kind,x,y if kind=='page' else None))
   if kind=='wait':waits[0]+=1;uc.reg_write(UC_ARM_REG_R0,1 if waitfail and waits[0]==waitfail else 0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x0800497c if native else sym['case_boot_option_erase_execute'])|1,0x20008000,count=2000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000f98,8)),bytes(u.mem_read(0x20003100,4)),bytes(u.mem_read(0x40022014,4))))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_OPTION_ERASE_EXECUTE',160)
