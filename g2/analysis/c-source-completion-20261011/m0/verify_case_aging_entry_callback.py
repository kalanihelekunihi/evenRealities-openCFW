#!/usr/bin/env python3
"""Bounded stock/C CASE 0xb7ec callback comparison with child cuts."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_cb_b7ec_candidate.c'
obj=H/'aging_entry.oracle.o';stub=H/'aging_entry.oracle_stub.c';stubobj=H/'aging_entry.oracle_stub.o';elf=H/'aging_entry.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_transport_left_aging(uint32_t x){return x;}\nuint32_t case_boot_transport_right_aging(uint32_t x){return x;}\nuint32_t case_policy_service_idle(void){return 0;}\nuint32_t case_policy_log(uint32_t x){return x;}\nuint32_t case_legacy_logger(const char *s,...){return (uint32_t)(uintptr_t)s;}\n__attribute__((noreturn)) void case_init_display_reset(void){for(;;);}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xb7ec)
for i in range(256):
 device=bytearray(0x40);shared=bytearray(0x80);state=bytearray(0x100)
 device[2]=rng.randrange(2);device[3]=rng.randrange(2);device[4]=rng.randrange(2);device[5]=rng.randrange(4);device[6]=rng.choice([0,1,2,3]);device[7]=rng.choice([0,1,4]);shared[7]=rng.randrange(2)
 state[16]=rng.randrange(2);state[17]=rng.randrange(2);state[21]=rng.randrange(2)
 if device[6]==3 and device[3]==0:device[3]=1 # reset path is nonreturn and tested separately
 pair=[];traces=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000b8,bytes(shared));u.mem_write(0x200000f4,bytes(device));u.mem_write(0x2000087c,bytes(state))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x080023f4:'left',0x080024c0:'right',0x0800d154:'idle',0x08009170:'log'} if native else {sym['case_boot_transport_left_aging']&~1:'left',sym['case_boot_transport_right_aging']&~1:'right',sym['case_policy_service_idle']&~1:'idle',sym['case_policy_log']&~1:'log',sym['case_legacy_logger']&~1:'log'})
  calls=[];visited=[]
  def hook(uc,a,n,_):
   if i==4 and native and 0x0800b7ec<=a<0x0800b944:visited.append(hex(a))
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0)
   calls.append((kind,bytes(uc.mem_read(x,80)).split(b'\0')[0] if kind=='log' else x if kind in ('left','right') else None))
   uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b7ec if native else sym['case_boot_transport_cb_b7ec'])|1,0x20008000,count=3000)
  traces.append(visited)
  pair.append((calls,bytes(u.mem_read(0x200000b8,0x80)),bytes(u.mem_read(0x200000f4,0x40)),bytes(u.mem_read(0x2000087c,0x100))))
 assert pair[0]==pair[1],(i,device[:8],state[16:22],pair[0][0],pair[1][0],traces[0] if i==4 else '')
print('PASS_CASE_AGING_ENTRY_CALLBACK',256)
