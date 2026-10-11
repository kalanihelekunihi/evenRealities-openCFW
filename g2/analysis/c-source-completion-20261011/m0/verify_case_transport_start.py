#!/usr/bin/env python3
"""Bounded CASE 0x6968 stock/C registration and handle-write oracle."""
from pathlib import Path
import subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_start_candidate.c'
obj=H/'transport_start.oracle.o';stub=H/'transport_start.oracle_stub.c';stubobj=H/'transport_start.oracle_stub.o';elf=H/'transport_start.oracle.elf'
callbacks=['9d70','bb4c','9684','b7ec','bb90','ab70','6e1c','7f2c','82ec']
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint8_t case_boot_transport_registration_storage[256];\nuint32_t case_boot_transport_register(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_boot_transport_worker(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\nuint32_t case_boot_transport_event(uint32_t a){(void)a;return 0;}\n'+''.join('void case_boot_transport_cb_'+c+'(void){}\n' for c in callbacks)+'void case_policy_task_7200(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native_cbs={0x08000000+int(c,16):c for c in callbacks};native_cbs[0x08007200]='7200'
candidate_cbs={sym['case_boot_transport_cb_'+c]&~1:c for c in callbacks};candidate_cbs[sym['case_policy_task_7200']&~1]='7200'
pair=[]
for native in (True,False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
 for a,b in seg:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
 base=0x0800d26c if native else sym['case_boot_transport_registration_storage']
 target=({0x0800aa48:'reg',0x0800a93c:'worker',0x0800a836:'event'} if native else {sym['case_boot_transport_register']&~1:'reg',sym['case_boot_transport_worker']&~1:'worker',sym['case_boot_transport_event']&~1:'event'})
 names=native_cbs if native else candidate_cbs;calls=[]
 def hook(uc,a,size,_):
  kind=target.get(a)
  if kind is None:return
  x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
  calls.append((kind,names.get(x&~1,hex(x)) if kind!='event' else x-base,y if kind!='event' else None,z if kind=='reg' else None,w-base if kind=='reg' else z-base if kind=='worker' else None))
  uc.reg_write(UC_ARM_REG_R0,0x1000+len(calls));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x08006968 if native else sym['case_boot_transport_start'])|1,0x20008000,count=2000)
 handles=tuple(struct.unpack('<I',u.mem_read(0x200000b8+o,4))[0] for o in range(16,60,4))
 pair.append((calls,handles))
assert pair[0]==pair[1],pair
print('PASS_CASE_TRANSPORT_START',len(pair[0][0]))
