#!/usr/bin/env python3
"""Bounded original/source streaming callbacks with modeled sample-ready clear."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011';srcs=[S/'application_boot_sensor_stream_callbacks_candidate.c',S/'application_boot_sensor_simple_callbacks_candidate.c']
objs=[H/'sensor_stream_callbacks.oracle.o',H/'sensor_simple_callbacks_stream.oracle.o'];stub=H/'sensor_stream_callbacks.oracle_stub.c';stubobj=H/'sensor_stream_callbacks.oracle_stub.o';elf=H/'sensor_stream_callbacks.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
for s,o in zip(srcs,objs):subprocess.run(flags+[str(s),'-o',str(o)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_sensor_callback_finish(uint32_t x){(void)x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x8808)
for i in range(96):
 width=2 if i%2==0 else 1;entry=0x08008808 if width==2 else 0x08008a48;name='case_boot_sensor_callback_8808' if width==2 else 'case_boot_sensor_callback_8a48'
 desc=bytearray(rng.randbytes(160));hw=bytearray(rng.randbytes(48));out=bytearray(rng.randbytes(16))
 struct.pack_into('<I',desc,0,0x40013800);struct.pack_into('<I',desc,88,0x20004004);struct.pack_into('<I',desc,140,34 if i%7 else 32)
 struct.pack_into('<H',desc,94,[1,2,8][i%3]);struct.pack_into('<H',desc,104,[0,1,4][i%3]);struct.pack_into('<I',desc,108,i%3)
 f=struct.unpack_from('<I',hw,28)[0];f=(f&~63)|(32 if i%3==1 else 0)|(i%8);struct.pack_into('<I',hw,28,f)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
  u.mem_write(0x20003000,bytes(desc));u.mem_write(0x20004000,bytes(out));u.mem_write(0x40013800,bytes(hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  targets=({0x08006544:'finish',0x08005f42:'status'} if native else {sym['case_boot_sensor_callback_finish']&~1:'finish',sym['case_boot_sensor_callback_status']&~1:'status'})
  calls=[]
  def hook(uc,a,size,_):
   if a in targets:
    if targets[a]=='finish':calls.append((targets[a],uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def onread(uc,access,a,size,value,_):
   if a==0x40013824:
    flags=struct.unpack('<I',uc.mem_read(0x4001381c,4))[0]
    uc.mem_write(0x4001381c,struct.pack('<I',flags&~32))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,onread)
  u.emu_start((entry if native else sym[name])|1,0x20008000,count=3000)
  dd=bytearray(u.mem_read(0x20003000,160));pointer=struct.unpack_from('<I',dd,116)[0]
  valid=([0x08008759,0x08008999] if native else [sym['case_boot_sensor_callback_8758'],sym['case_boot_sensor_callback_8998']])
  if pointer in valid:struct.pack_into('<I',dd,116,1 if width==2 else 2)
  pair.append((bytes(dd),bytes(u.mem_read(0x20004000,16)),bytes(u.mem_read(0x40013800,48)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SENSOR_STREAM_CALLBACKS',96)
