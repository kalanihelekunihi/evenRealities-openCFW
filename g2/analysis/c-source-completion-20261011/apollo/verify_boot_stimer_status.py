#!/usr/bin/env python3
"""Bounded original/source status-read oracle for stock 0x41f4c0."""
from pathlib import Path
import hashlib,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
source=root/'g2/components/bootloader/initializer_callbacks/stimer_irq.c'
with tempfile.TemporaryDirectory() as directory:
 w=Path(directory);obj=w/'body.o';elf=w/'body.elf';binary=w/'body.bin'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','--gc-sections','-Ttext=0x10000','-e','opencfw_boot_stimer_irq_status',str(obj),'-o',str(elf)],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
 code=binary.read_bytes()
 with elf.open('rb') as f:entry=ELFFile(f).header['e_entry']
 n=0
 for status in (0,1,2,3,0xffffffff,0x80000000,0x45):
  for enable in (0,1,3,0xffffffff,0x80000000):
   for masked in (0,1):
    outputs=[]
    for original in (True,False):
     cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     cpu.mem_map(0x10000,0x1000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000);cpu.mem_map(0x40008000,0x1000)
     cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
     cpu.mem_write(0x40008900,enable.to_bytes(4,'little'));cpu.mem_write(0x40008904,status.to_bytes(4,'little'))
     cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20008001);cpu.reg_write(a.UC_ARM_REG_R0,masked)
     done=[]
     def hook(machine,pc,size,unused):
      if pc==0x20008000:done.append(True);machine.emu_stop()
     cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start((0x41f4c0 if original else entry)|1,0x20008002,count=100)
     assert done
     outputs.append(cpu.reg_read(a.UC_ARM_REG_R0))
    assert outputs[0]==outputs[1],(status,enable,masked,outputs)
    n+=1
 print('PASS native/source STIMER status',n,'cases')
