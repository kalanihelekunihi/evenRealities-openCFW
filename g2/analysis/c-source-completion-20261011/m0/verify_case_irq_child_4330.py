#!/usr/bin/env python3
"""CASE 0x4330 original/C serial IRQ MMIO and state oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_irq_child_4330_candidate.c';provider=R/'g2/components/case/startup_candidate_20261011/application_policy_adc_register_candidate.c'
obj=H/'irq_child_4330.oracle.o';prv=H/'irq_child_4330.provider.o';elf=H/'irq_child_4330.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
for a,b in [(src,obj),(provider,prv)]:subprocess.run(flags+[str(a),'-o',str(b)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(prv),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x4330);bits=[0,2,4,8,0x80,0x100,0x200,0x10,0x2000,0x21e]
for i in range(256):
 state=bytearray(rng.randbytes(0x80));state[:4]=struct.pack('<I',0x40013800);state[26]=i%2;state[48:52]=struct.pack('<I',0 if i%3 else 0x20003400)
 device=bytearray(rng.randbytes(0x80));mask=bits[i%len(bits)];device[:4]=struct.pack('<I',mask|((i%5)==0)*2);device[4:8]=struct.pack('<I',mask);device[12:16]=struct.pack('<I',i%8);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000);u.mem_write(0x20003000,bytes(state));u.mem_write(0x40013800,bytes(device))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  u.emu_start((0x08004330 if native else sym['case_irq_child_4330'])|1,0x20008000,count=1000)
  pair.append((bytes(u.mem_read(0x20003000,0x80)),bytes(u.mem_read(0x40013800,0x80))))
 assert pair[0]==pair[1],(i,hex(mask),state[48:52],device[:16],[(j,a,b) for j,(a,b) in enumerate(zip(pair[0][0],pair[1][0])) if a!=b][:8],[(j,a,b) for j,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b][:8])
print('PASS_CASE_IRQ_CHILD_4330',256)
