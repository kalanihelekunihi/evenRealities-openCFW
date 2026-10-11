#!/usr/bin/env python3
"""Bounded stock/C CASE 0x9cc8 state oracle; signals and logs are cut."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_sample_refresh_candidate.c'
obj=H/'aging_refresh.oracle.o';stub=H/'aging_refresh.oracle_stub.c';stubobj=H/'aging_refresh.oracle_stub.o';elf=H/'aging_refresh.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_transport_aging_status(void){return 0;}\nuint32_t case_policy_log(uint32_t x){return x;}\nuint32_t case_policy_log_number(uint32_t x,uint32_t y){return x+y;}\nuint32_t case_legacy_logger(const char *s,...){return (uint32_t)(uintptr_t)s;}\nint32_t case_boot_sensor_finish_signal(uint32_t a,uint32_t b){return (int32_t)(a+b);}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x9cc8)
for i in range(256):
 state=bytearray(0x100);shared=bytearray(0x80);device=bytearray(0x40)
 state[16]=rng.randrange(2);state[17]=rng.randrange(2);shared[0]=rng.choice([0,1,8,9,10,255]);shared[7]=rng.randrange(2);device[6]=rng.randrange(4)
 shared[56:60]=struct.pack('<I',0x12340000+i)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000b8,bytes(shared));u.mem_write(0x200000f4,bytes(device));u.mem_write(0x2000087c,bytes(state))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08009170:'log',0x0800a888:'signal'} if native else {sym['case_policy_log']&~1:'log',sym['case_policy_log_number']&~1:'log',sym['case_boot_sensor_finish_signal']&~1:'signal'})
  calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1)
   calls.append((kind,x if kind=='signal' else bytes(uc.mem_read(x, min(64, len(F)-(x-0x08000000)))).split(b'\0')[0],y if kind=='signal' else None))
   uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08009cc8 if native else sym['case_boot_transport_sample_refresh_mode4'])|1,0x20008000,count=2000)
  pair.append((calls,bytes(u.mem_read(0x200000b8,0x80)),bytes(u.mem_read(0x200000f4,0x40)),bytes(u.mem_read(0x2000087c,0x100))))
 assert pair[0]==pair[1],(i,pair[0][0],pair[1][0])
print('PASS_CASE_AGING_REFRESH_MODE4',256)
