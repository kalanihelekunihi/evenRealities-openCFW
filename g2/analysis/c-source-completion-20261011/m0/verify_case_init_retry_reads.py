#!/usr/bin/env python3
"""Native/source retry-read state and calls at physical transaction cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_init_retry_reads_candidate.c';obj=H/'application_init_retry_reads.oracle.o';stub=H/'application_init_retry_reads.oracle_stub.c';stubobj=H/'application_init_retry_reads.oracle_stub.o';elf=H/'application_init_retry_reads.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_bus_output_prepare(void){}\nuint32_t case_motion_input_transaction(uint32_t a,uint32_t b,uint32_t c,uint8_t*d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_bus_config_input_transaction(uint32_t a,uint32_t b,uint32_t c,uint8_t*d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_legacy_logger(const char*a,...){(void)a;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x90ac)
for i in range(80):
 which=i&1;count=i%4+1;index=rng.randrange(16);succeed=(i//2)%10;logging=i%3==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,b'\x11'*8)
  diag=0x20000000 if which==0 else 0x2000007c
  u.mem_write(diag,struct.pack('<IIIII',0,0,4,5,int(logging)))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,index);u.reg_write(UC_ARM_REG_R1,count);u.reg_write(UC_ARM_REG_R2,0x20002000)
  cuts=({0x0800a2e6:'prepare',0x08000420:'transaction',0x08000310:'config',0x08009170:'log'} if native else {sym['case_bus_output_prepare']&~1:'prepare',sym['case_motion_input_transaction']&~1:'transaction',sym['case_bus_config_input_transaction']&~1:'config',sym['case_legacy_logger']&~1:'log'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   if k in ('transaction','config'):
    n=sum(t[0] in ('transaction','config') for t in trace)
    trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
    uc.reg_write(UC_ARM_REG_R0,1 if n==succeed else 0)
   elif k=='log':trace.append((k,uc.reg_read(UC_ARM_REG_R0)))
   else:trace.append((k,))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  source='case_init_motion_read' if which==0 else 'case_init_secondary_config_read'
  entry=0x08008fa8 if which==0 else 0x080090ac
  u.emu_start((entry if native else sym[source])|1,0x20008000,count=1000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20002000,8)),bytes(u.mem_read(diag,20)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_INIT_RETRY_READS',80)
