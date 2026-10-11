#!/usr/bin/env python3
"""Bounded stock comparison for valid CASE parser command routing."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011'
stub=HERE/'record_dispatch_oracle_stubs.c';stub.write_text('''#include <stdint.h>
void case_record_log(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}
void case_record_hex_log(const uint8_t*a,uint32_t n){(void)a;(void)n;}
void case_record_forward(const uint8_t*a,uint32_t n){(void)a;(void)n;}
void case_record_copy_5a(uint8_t*d,const uint8_t*s,uint32_t n){for(uint32_t i=0;i<n;i++)d[i]=s[i];}
''')
objs=[]
for source in [SRC/'record_scan_prefix_candidate.c',SRC/'record_dispatch_candidate.c',stub]:
 obj=HERE/(source.stem+'.dispatch.o');objs.append(obj)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
elf=HERE/'record_dispatch_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],'-o',str(elf)],check=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for side,command,param in itertools.product((0,1),(7,8,0x46,0x59,0x5b,0x3e),(0,1,4)):
 data=bytearray([0x11]*0x118);data[0:4]=bytes([0x5a,0xa5,0xff,6]);data[4]=command;data[7]=1;data[8]=param
 data[10]=(4+sum(data[4:10]))&0xff
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000664,bytes(data));u.mem_write(0x200000bf,b'\x01')
  u.reg_write(UC_ARM_REG_R0,side);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x08001e94 if original else sym['case_record_dispatch_1e94'])|1,0x20001000,count=100000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000,(original,side,command,param,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append((u.reg_read(UC_ARM_REG_R0),u.mem_read(0x20000664,0x118),u.mem_read(0x200000f4,4)))
 assert pair[0]==pair[1],(side,command,param,[(x[0],x[1][:12].hex(),x[2].hex()) for x in pair])
 checked+=1
print('PASS_CASE_RECORD_VALID_SIMPLE',checked)
for side,command,submode in itertools.product((0,1),(0x13,0x58),range(3)):
 data=bytearray([0x11]*0x118)
 if command==0x13:
  length=12;data[4]=command;data[7]=6 if submode else 1;data[8]=1;data[9]=1;data[10]=0x20;data[11]=0x31;data[12]=75;data[13]=0;data[14]=3
 else:
  length=0x25;data[4]=command;data[7]=0x20 if submode else 1;data[13]=2;data[14]=0x40;data[16:24]=bytes(range(1,9))
 data[0:4]=bytes([0x5a,0xa5,0xff,length]);data[4+length]=(length-2+sum(data[4:4+length]))&0xff
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000664,bytes(data));u.mem_write(0x200000bf,b'\x01')
  u.reg_write(UC_ARM_REG_R0,side);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x08001e94 if original else sym['case_record_dispatch_1e94'])|1,0x20001000,count=100000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000,(original,side,command,submode,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000664,0x118)),bytes(u.mem_read(0x20000870,0x70)),bytes(u.mem_read(0x200000b0,8))))
 if pair[0]!=pair[1]:
  for name,a,b in zip(('return','input','state','seq'),pair[0],pair[1]):
   if a!=b:print('DIFF',side,hex(command),submode,name,[(i,hex(x),hex(y)) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:20] if isinstance(a,bytes) else (a,b))
  raise AssertionError('parser extended mismatch')
 checked+=1
print('PASS_CASE_RECORD_VALID_EXTENDED',checked)
for valid in (False,True):
 data=bytearray(0x118);length=16;data[:4]=bytes([0x5a,0xa5,0xff,length]);data[4]=0x5a;data[7]=9;data[8:16]=bytes(range(1,9));data[16]=((sum(data[8:16])+(0 if valid else 1))&255);data[4+length]=(length-2+sum(data[4:4+length]))&255
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000664,bytes(data));u.mem_write(0x200000bf,b'\x01');u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x08001e94 if original else sym['case_record_dispatch_1e94'])|1,0x20001000,count=100000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000664,0x118)),bytes(u.mem_read(0x2000077c,16)),bytes(u.mem_read(0x2000089c,16))))
 assert pair[0]==pair[1],(valid,[(x[0],x[2].hex(),x[3].hex()) for x in pair])
 checked+=1
print('PASS_CASE_RECORD_COPY_5A',checked)
