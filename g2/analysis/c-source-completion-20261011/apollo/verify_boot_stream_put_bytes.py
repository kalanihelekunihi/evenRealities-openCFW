#!/usr/bin/env python3
"""Bounded stock/source stream callback loop, including two-word AAPCS return."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
 work=Path(directory);obj=work/'stream.o';elf=work/'stream.elf';binary=work/'stream.bin'
 source=root/'g2/components/bootloader/initializer_callbacks/stream_put_bytes_41f2c8.c'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_stream_put_bytes',str(obj),'-o',str(elf)],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
 code=binary.read_bytes();cases=0
 for length,fail_at,initial in itertools.product((0,1,2,4),(None,0,1,3),(1,0x12345678)):
  outputs=[]
  for original,entry in ((True,0x41f2c8),(False,0x10000)):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x10000,0x1000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000)
   cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
   cpu.mem_write(0x20010000,bytes((4,8,15,16)))
   cpu.mem_write(0x20011008,struct.pack('<I',initial));cpu.mem_write(0x2001102c,struct.pack('<I',7))
   cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
   cpu.reg_write(a.UC_ARM_REG_R0,0x20001001);cpu.reg_write(a.UC_ARM_REG_R1,0x20011000)
   cpu.reg_write(a.UC_ARM_REG_R2,0x20010000);cpu.reg_write(a.UC_ARM_REG_R3,length)
   calls=[];done=[]
   def hook(machine,pc,size,unused):
    if pc==0x20001000:
     state=machine.reg_read(a.UC_ARM_REG_R0);byte=machine.reg_read(a.UC_ARM_REG_R1)
     calls.append((state,byte))
     next_value=0 if fail_at==len(calls)-1 else ((state+byte+1)&0xffffffff)
     machine.reg_write(a.UC_ARM_REG_R0,next_value)
     machine.reg_write(a.UC_ARM_REG_PC,machine.reg_read(a.UC_ARM_REG_LR))
    elif pc==0x20002000:done.append(True);machine.emu_stop()
   cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start(entry|1,0x20002002,count=1000)
   assert done,(original,length,fail_at,initial)
   outputs.append((cpu.reg_read(a.UC_ARM_REG_R0),cpu.reg_read(a.UC_ARM_REG_R1),bytes(cpu.mem_read(0x20011008,4)),bytes(cpu.mem_read(0x2001102c,4)),calls))
  assert outputs[0]==outputs[1],(length,fail_at,initial,outputs)
  cases+=1
 print('PASS native/source Boot stream put bytes',cases,'cases')
