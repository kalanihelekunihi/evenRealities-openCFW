#!/usr/bin/env python3
"""Bounded native/source FreeRTOS list-end insertion oracle."""
from pathlib import Path
import hashlib, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
source=root/'g2/components/bootloader/thread_creation/list_insert_end.c'
with tempfile.TemporaryDirectory() as directory:
 w=Path(directory);obj=w/'body.o';elf=w/'body.elf';binary=w/'body.bin'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_list_insert_end',str(obj),'-o',str(elf)],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
 code=binary.read_bytes()
 with elf.open('rb') as f:entry=ELFFile(f).header['e_entry']
 for initial_count,offset in ((0,0),(1,0),(3,0),(0,0x80),(19,0x80)):
  outputs=[]
  for original in (True,False):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x10000,0x1000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000)
   cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
   list_addr=0x20001000;end=list_addr+8;prev=0x20001100+offset;item=0x20001200
   def put(addr,n):cpu.mem_write(addr,int(n).to_bytes(4,'little'))
   def get(addr):return int.from_bytes(cpu.mem_read(addr,4),'little')
   put(list_addr,initial_count);put(list_addr+4,end);put(end,0xffffffff);put(end+4,end);put(end+8,prev)
   put(prev+4,end);put(prev+8,end)
   cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20008001);cpu.reg_write(a.UC_ARM_REG_R0,list_addr);cpu.reg_write(a.UC_ARM_REG_R1,item)
   done=[]
   def hook(machine,pc,size,unused):
    if pc==0x20008000:done.append(True);machine.emu_stop()
   cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start((0x41b55a if original else entry)|1,0x20008002,count=100)
   assert done
   outputs.append((get(list_addr),get(list_addr+4),get(end+8),get(prev+4),tuple(get(item+4*i) for i in (1,2,4))))
  assert outputs[0]==outputs[1],(initial_count,offset,outputs)
 print('PASS native/source list insert end',5,'cases')
