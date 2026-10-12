#!/usr/bin/env python3
"""Bounded native/source callback slots 0c/10/20/30, null and active."""
from pathlib import Path
import hashlib,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
source=root/'g2/components/bootloader/initializer_callbacks/startup_initialize_leaves.c'
with tempfile.TemporaryDirectory() as directory:
 w=Path(directory);obj=w/'body.o';elf=w/'body.elf';binary=w/'body.bin'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000',str(obj),'-o',str(elf)],check=True)
 subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
 code=binary.read_bytes()
 with elf.open('rb') as f:
  sym=ELFFile(f).get_section_by_name('.symtab');addresses={s.name:s['st_value'] for s in sym.iter_symbols()}
 cases=[(0x41cd34,0x0c,'opencfw_boot_startup_hook0c'),(0x41cd4a,0x10,'opencfw_boot_startup_hook10'),(0x41cdca,0x20,'opencfw_boot_startup_hook20'),(0x41ce10,0x30,'opencfw_boot_startup_hook30')]
 for native,offset,name in cases:
  for live in (False,True):
   outputs=[]
   for original in (True,False):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x10000,0x2000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000)
    cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
    cpu.mem_write(0x20026e38+offset,(0x20008001 if live else 0).to_bytes(4,'little'))
    cpu.mem_write(0x20008000,b'\x70\x47')
    cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20009001);cpu.reg_write(a.UC_ARM_REG_R0,0x12345678)
    done=[];calls=[]
    def hook(machine,pc,size,unused):
     if pc==0x20008000:
      calls.append(True);machine.reg_write(a.UC_ARM_REG_R0,0xa5a53210)
     if pc==0x20009000:done.append(True);machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.emu_start((native if original else addresses[name])|1,0x20009002,count=100)
    assert done,(name,live,original)
    outputs.append((cpu.reg_read(a.UC_ARM_REG_R0),len(calls)))
   assert outputs[0]==outputs[1],(name,live,outputs)
 print('PASS native/source startup hooks',len(cases)*2,'cases')
