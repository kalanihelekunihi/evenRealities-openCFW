#!/usr/bin/env python3
"""Bounded CASE 0x9d70/0xbb4c stock/C callback state and call oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];D=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objects=[]
for name in ('application_boot_transport_clock_callback_candidate','application_boot_transport_toggle_callback_candidate'):
 target=H/(name+'.oracle.o');subprocess.run(flags+[str(D/(name+'.c')),'-o',str(target)],check=True);objects.append(target)
stub=H/'transport_callbacks.oracle_stub.c';stubobj=H/'transport_callbacks.oracle_stub.o';elf=H/'transport_callbacks.oracle.elf'
stub.write_text('#include <stdint.h>\nvoid case_boot_transport_stop_clock(uint32_t x){(void)x;}\nvoid case_boot_transport_stop_link(uint32_t x){(void)x;}\nuint32_t case_policy_log(uint32_t x){return x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objects],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x9d70)
for entry in ('9d70','bb4c'):
 for i in range(128):
  mode=rng.randrange(6);quiet=rng.randrange(2);toggle=rng.randrange(4);pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087e,bytes([mode]));u.mem_write(0x200000bf,bytes([quiet]));u.mem_write(0x200000c4,bytes([toggle]));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   targets=({0x08006b80:'clock',0x08006b98:'link',0x08009170:'log'} if native else {sym['case_boot_transport_stop_clock']&~1:'clock',sym['case_boot_transport_stop_link']&~1:'link',sym['case_policy_log']&~1:'log'})
   calls=[]
   def hook(uc,a,size,_):
    kind=targets.get(a)
    if kind is None:return
    calls.append((kind,uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   start=(0x08000000+int(entry,16) if native else sym['case_boot_transport_cb_'+entry])|1
   u.emu_start(start,0x20008000,count=1000)
   pair.append((calls,bytes(u.mem_read(0x2000087c,3)),bytes(u.mem_read(0x200000c4,1))))
  assert pair[0]==pair[1],(entry,i,mode,quiet,toggle,pair)
print('PASS_CASE_TRANSPORT_CALLBACKS',256)
