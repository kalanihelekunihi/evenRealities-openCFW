#!/usr/bin/env python3
"""Native/source PMIC transaction trace and bytes at physical bus cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_pmic_read_candidate.c';obj=H/'application_boot_pmic_read.oracle.o';stub=H/'application_boot_pmic_read.oracle_stub.c';stubobj=H/'application_boot_pmic_read.oracle_stub.o';elf=H/'application_boot_pmic_read.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names=['start','write_byte','ack','stop','read_byte','ack_continue','ack_last']
stub.write_text('#include <stdint.h>\n'+''.join('uint32_t case_pmic_bus_'+n+'(uint32_t v){(void)v;return 0;}\n' for n in names))
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
nativecuts={0x0800a4b4:'start',0x0800a46c:'write_byte',0x0800a4fa:'ack',0x0800a4dc:'stop',0x0800a436:'read_byte',0x0800a3d2:'ack_continue',0x0800a414:'ack_last'}
sourcecuts={sym['case_pmic_bus_'+n]&~1:n for n in names}
rng=random.Random(0x28b4)
for i in range(96):
 which=i&1;count=i%5+1;selector=rng.randrange(256);fail=(i//2)%5;values=[rng.randrange(256) for _ in range(count)];pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,bytes([0xee]*8));u.mem_write(0x20000114,b'\xff')
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,selector);u.reg_write(UC_ARM_REG_R1,0x20002000);u.reg_write(UC_ARM_REG_R2,count)
  cuts=nativecuts if native else sourcecuts;trace=[];acks=0;reads=0
  def hook(uc,a,size,_):
   nonlocal_vars=None
   k=cuts.get(a)
   if k is None:return
   if k=='write_byte':trace.append((k,uc.reg_read(UC_ARM_REG_R0)))
   else:trace.append((k,))
   if k=='ack':
    index=sum(t[0]=='ack' for t in trace)-1
    uc.reg_write(UC_ARM_REG_R0,1 if fail==index+1 else 0)
   elif k=='read_byte':
    index=sum(t[0]=='read_byte' for t in trace)-1
    uc.reg_write(UC_ARM_REG_R0,values[index])
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  entry=0x080028b4 if which==0 else 0x0800292c
  source='case_policy_timer_device_read' if which==0 else 'case_init_pmic_device_read'
  u.emu_start((entry if native else sym[source])|1,0x20008000,count=1000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20002000,8)),bytes(u.mem_read(0x20000114,1)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_PMIC_DEVICE_READ',96)
