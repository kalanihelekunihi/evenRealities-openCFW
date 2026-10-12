#!/usr/bin/env python3
"""Bounded native/source TLSF generic highest-set-bit helper."""
from pathlib import Path
import hashlib,random,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
 work=Path(directory);obj=work/'fls.o';elf=work/'fls.elf';binary=work/'fls.bin'
 source=root/'g2/components/bootloader/allocator/tlsf_fls_generic_native.c'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_tlsf_fls_generic',str(obj),'-o',str(elf)],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
 code=binary.read_bytes();rng=random.Random(4169)
 cases=[0,1,2,3,0x7fffffff,0x80000000,0xffffffff]+[1<<i for i in range(32)]+[rng.getrandbits(32) for _ in range(128)]
 for word in cases:
  outputs=[]
  for original,entry in ((True,0x4169a4),(False,0x10000)):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x10000,0x1000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000)
   cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
   cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20002001);cpu.reg_write(a.UC_ARM_REG_R0,word)
   done=[]
   def hook(machine,pc,size,unused):
    if pc==0x20002000:done.append(True);machine.emu_stop()
   cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start(entry|1,0x20002002,count=100)
   assert done
   outputs.append(cpu.reg_read(a.UC_ARM_REG_R0))
  assert outputs[0]==outputs[1],(word,outputs)
 print('PASS native/source TLSF generic FLS',len(cases),'cases')
