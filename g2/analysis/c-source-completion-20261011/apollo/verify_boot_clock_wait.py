#!/usr/bin/env python3
"""Bounded original/source oracle for stock clock-active wait 0x4216b2."""
from pathlib import Path
import hashlib, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
source=root/'g2/components/bootloader/clock_manager/clock_wait_4216b2.c'
with tempfile.TemporaryDirectory() as directory:
 w=Path(directory);mock=w/'mock.c';mock.write_text('''#include <stdint.h>\nvoid opencfw_bl_delay_us(uint32_t us) { volatile uint32_t *count=(volatile uint32_t *)0x20001000u; volatile uint8_t *active=(volatile uint8_t *)0x20002000u; volatile uint32_t *stop=(volatile uint32_t *)0x20001004u; if(us==10u) {++*count; if(*stop && *count==*stop) *active=0;} }\n''')
 for name,src in [('body',source),('mock',mock)]:
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-c',str(src),'-o',str(w/(name+'.o'))],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_bl_clock_wait_active',str(w/'body.o'),str(w/'mock.o'),'-o',str(w/'body.elf')],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(w/'body.elf'),str(w/'body.bin')],check=True)
 code=(w/'body.bin').read_bytes()
 from elftools.elf.elffile import ELFFile
 with (w/'body.elf').open('rb') as f:
  elf=ELFFile(f);entry=elf.header['e_entry']
 cases=[(0,0,0),(0,7,0),(1,0,0),(1,1,0),(1,2,0),(1,7,0),(1,7,1),(1,7,3)]
 for active,timeout,stop in cases:
  outputs=[]
  for original in (True,False):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x10000,0x1000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000)
   cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
   def write32(addr,n):cpu.mem_write(addr,int(n).to_bytes(4,'little'))
   def read32(addr):return int.from_bytes(cpu.mem_read(addr,4),'little')
   cpu.mem_write(0x20002000,bytes([active]));write32(0x20002004,timeout);write32(0x20001000,0);write32(0x20001004,stop)
   cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20008001);cpu.reg_write(a.UC_ARM_REG_R0,0x20002000);cpu.reg_write(a.UC_ARM_REG_R1,0x20002004)
   done=[]
   def hook(machine,pc,size,unused):
    if pc==0x20008000:done.append(True);machine.emu_stop();return
    if original and pc==0x41d1c0:
     assert machine.reg_read(a.UC_ARM_REG_R0)==10
     n=read32(0x20001000)+1;write32(0x20001000,n)
     if stop and n==stop:machine.mem_write(0x20002000,b'\x00')
     machine.reg_write(a.UC_ARM_REG_PC,machine.reg_read(a.UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   cpu.emu_start((0x4216b2 if original else entry)|1,0x20008002,count=300)
   assert done,(original,active,timeout,stop)
   outputs.append((read32(0x20002004),read32(0x20001000),cpu.mem_read(0x20002000,1)[0]))
  assert outputs[0]==outputs[1],(active,timeout,stop,outputs)
 print('PASS native/source clock active wait',len(cases),'cases')
