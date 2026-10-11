#!/usr/bin/env python3
"""Native/source CASE 0x0610 bus write control at physical child cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_bus_write_candidate.c';obj=H/'policy_bus_write.oracle.o';stub=H/'policy_bus_write.oracle_stub.c';stubobj=H/'policy_bus_write.oracle_stub.o';elf=H/'policy_bus_write.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names=['case_bus_prepare','case_bus_finish','case_bus_send','case_bus_start','case_bus_poll','case_bus_read']
stub.write_text('#include <stdint.h>\n'+''.join('uint32_t '+n+'(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n' for n in names))
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
native={0x0800a310:'prepare',0x0800a24a:'finish',0x0800a2c4:'send',0x0800a19a:'start',0x0800c43c:'poll',0x0800c412:'parity'}
source={sym[n]&~1:k for k,n in zip(['prepare','finish','send','start','poll','parity'],names)}
rng=random.Random(0x0610)
for i in range(96):
 bus=0x42 if i%9 else 2;channel=rng.randrange(8);count=i%3+1;values=bytes(rng.randrange(256) for _ in range(count));failstage=(i//3)%7;pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,values)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,bus);u.reg_write(UC_ARM_REG_R1,channel);u.reg_write(UC_ARM_REG_R2,count);u.reg_write(UC_ARM_REG_R3,0x20002000)
  cuts=native if original else source;trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
   trace.append((k,r0,r1) if k=='send' else (k,r0) if k in ('start','parity') else (k,))
   if k=='poll':
    n=sum(t[0]=='poll' for t in trace)-1
    expected=(((bus&~15)+channel)&255) if n==0 else values[n-1]
    uc.mem_write(r0,struct.pack('<I',((expected*2)&255).bit_count()&1 if n==0 else expected.bit_count()&1))
    if failstage==n:uc.reg_write(UC_ARM_REG_R0,0)
    else:uc.reg_write(UC_ARM_REG_R0,1)
   elif k=='parity':uc.reg_write(UC_ARM_REG_R0,(r0&255).bit_count()&1 ^ (1 if failstage==4+sum(t[0]=='parity' for t in trace)-1 else 0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08000610 if original else sym['case_policy_bus_write'])|1,0x20008000,count=700)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x2000007c,12)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_POLICY_BUS_WRITE',96)
