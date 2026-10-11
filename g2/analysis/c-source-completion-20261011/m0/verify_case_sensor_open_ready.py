#!/usr/bin/env python3
"""CASE 0x8ec4 bounded native/source ready, timeout, and error paths."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011';srcs=[S/'application_boot_sensor_open_ready_candidate.c',S/'application_policy_adc_register_candidate.c'];objs=[H/'sensor_ready.oracle.o',H/'sensor_ready_tick.oracle.o'];elf=H/'sensor_ready.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
for s,o in zip(srcs,objs):subprocess.run(flags+[str(s),'-o',str(o)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x8ec4)
for i in range(96):
 kind=i%4;desc=bytearray(rng.randbytes(160));hw=bytearray(rng.randbytes(48));struct.pack_into('<I',desc,0,0x40013800)
 mask=1<<(i%12);flags_word=struct.unpack_from('<I',hw,28)[0];flags_word|=mask;flags_word=(flags_word|0x800) if kind==3 else flags_word;struct.pack_into('<I',hw,28,flags_word)
 control=struct.unpack_from('<I',hw,0)[0];struct.pack_into('<I',hw,0,control|4 if kind==3 else control)
 actual=1;expected=0 if kind==0 else 1;start=rng.getrandbits(32);timeout=100 if kind==3 else 0 if kind==1 else 5;tick=(start+20)&0xffffffff
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
  u.mem_write(0x20000120,struct.pack('<I',tick));u.mem_write(0x20003000,bytes(desc));u.mem_write(0x40013800,bytes(hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  for reg,val in [(UC_ARM_REG_R0,0x20003000),(UC_ARM_REG_R1,mask),(UC_ARM_REG_R2,expected),(UC_ARM_REG_R3,start)]:u.reg_write(reg,val)
  u.mem_write(0x20007fc0,struct.pack('<I',timeout))
  u.emu_start((0x08008ec4 if native else sym['case_boot_sensor_open_ready'])|1,0x20008000,count=1500)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,160)),bytes(u.mem_read(0x40013800,48))))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SENSOR_OPEN_READY',96)
