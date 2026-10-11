#!/usr/bin/env python3
"""Bounded CASE 0xc48c/0xc4aa stock/C event storage initialization oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_event_storage_candidate.c'
obj=H/'transport_event_storage.oracle.o';stub=H/'transport_event_storage.oracle_stub.c';stubobj=H/'transport_event_storage.oracle_stub.o';elf=H/'transport_event_storage.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_transport_heap_allocate(uint32_t n){return n;}\nvoid case_policy_task_list_initialize(uint32_t x){(void)x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc48c)
for entry in ('allocate','create'):
 for i in range(128):
  before=rng.randbytes(40);alloc_success=i%5!=0;pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,before);u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   targets=({0x0800b3e8:'alloc',0x0800bf94:'list'} if native else {sym['case_boot_transport_heap_allocate']&~1:'alloc',sym['case_policy_task_list_initialize']&~1:'list'})
   calls=[]
   def hook(uc,a,n,_):
    kind=targets.get(a)
    if kind is None:return
    calls.append((kind,uc.reg_read(UC_ARM_REG_R0)))
    if kind=='alloc':uc.reg_write(UC_ARM_REG_R0,0x20002000 if alloc_success else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   address=(0x0800c48c if entry=='allocate' else 0x0800c4aa) if native else sym['case_boot_transport_event_'+entry]
   u.emu_start(address|1,0x20008000,count=1000)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20002000,40))))
  assert pair[0]==pair[1],(entry,i,pair)
print('PASS_CASE_TRANSPORT_EVENT_STORAGE',256)
