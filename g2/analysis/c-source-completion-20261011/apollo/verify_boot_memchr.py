#!/usr/bin/env python3
"""Bounded stock/source pointer oracle for native memchr at 0x4225d0."""
from pathlib import Path
import hashlib,random,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR
R=Path(__file__).resolve().parents[4]
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as folder:
 t=Path(folder);obj=t/'memchr.o';elf=t/'memchr.elf';raw=t/'memchr.bin'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c99','-O2','-ffreestanding','-fno-builtin','-c',str(R/'g2/components/bootloader/runtime_memory/boot_memchr.c'),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','memchr',str(obj),'-o',str(elf)],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(raw)],check=True)
 data=raw.read_bytes();rng=random.Random(0x4225d0);cases=0
 for offset in range(4):
  for length in (0,1,2,3,4,5,7,8,9,15,16,17,31,32):
   for present in (False,True):
    buf=bytearray(rng.randbytes(64));target=0x7e
    for i in range(64):
     if buf[i]==target:buf[i]=0x5d
    if present and length:buf[offset+length//2]=target
    outputs=[]
    for original in (True,False):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x10000,0x1000);u.mem_map(0x410000,0x25000);u.mem_map(0x20000000,0x2000)
     u.mem_write(0x10000,data);u.mem_write(0x410000,stock);u.mem_write(0x20000100,bytes(buf))
     done=[]
     def hook(machine,pc,size,_):
      if pc==0x20001000:done.append(True);machine.emu_stop()
     u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x20001800);u.reg_write(UC_ARM_REG_LR,0x20001001)
     u.reg_write(UC_ARM_REG_R0,0x20000100+offset);u.reg_write(UC_ARM_REG_R1,target);u.reg_write(UC_ARM_REG_R2,length)
     u.emu_start((0x4225d0 if original else 0x10000)|1,0x20001002,count=1000)
     assert done,(original,offset,length,present)
     outputs.append(u.reg_read(UC_ARM_REG_R0))
    assert outputs[0]==outputs[1],(offset,length,present,outputs)
    cases+=1
 print('PASS native/source memchr',cases,'cases')
