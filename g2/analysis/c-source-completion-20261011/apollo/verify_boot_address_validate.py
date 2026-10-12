#!/usr/bin/env python3
"""Bounded stock/source range-cache oracle with device-info child cut."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
 work=Path(directory);obj=work/'source.o';stub=work/'child.S';stubobj=work/'child.o';elfpath=work/'source.elf'
 source=root/'g2/components/bootloader/application_storage/address_validate_430a60.c'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-I',str(source.parent),'-c',str(source),'-o',str(obj)],check=True)
 stub.write_text('.syntax unified\n.thumb\n.global opencfw_boot_device_info_query\n.thumb_func\nopencfw_boot_device_info_query:\n bx lr\n')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-c',str(stub),'-o',str(stubobj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_address_validate',str(obj),str(stubobj),'-o',str(elfpath)],check=True)
 with elfpath.open('rb') as f:
  elf=ELFFile(f)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
  names={sym.name:sym['st_value'] for sec in elf.iter_sections() if sec.header.sh_type=='SHT_SYMTAB' for sym in sec.iter_symbols()}
 cases=0
 for cached,address,length,query_range in itertools.product((0,0x4000,0x10000),(0x3fff,0x4000,0x8000),(0,0x3fff,0x4000,0xffff),(0x8000,)):
  outputs=[]
  for original in (True,False):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x10000,0x2000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000)
   cpu.mem_write(0x410000,stock)
   for addr,data in segments:cpu.mem_write(addr,data)
   cpu.mem_write(0x200270c8,struct.pack('<I',cached))
   cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
   cpu.reg_write(a.UC_ARM_REG_R0,address);cpu.reg_write(a.UC_ARM_REG_R1,length)
   calls=[];done=[]
   child=(0x41d792 if original else names['opencfw_boot_device_info_query']&~1)
   def hook(machine,pc,size,unused):
    if pc==child:
     calls.append((machine.reg_read(a.UC_ARM_REG_R0),machine.reg_read(a.UC_ARM_REG_R1)))
     ptr=machine.reg_read(a.UC_ARM_REG_R1)
     machine.mem_write(ptr+44,struct.pack('<I',query_range))
     machine.reg_write(a.UC_ARM_REG_R0,0)
     machine.reg_write(a.UC_ARM_REG_PC,machine.reg_read(a.UC_ARM_REG_LR))
    elif pc==0x20002000:done.append(True);machine.emu_stop()
   cpu.hook_add(UC_HOOK_CODE,hook)
   entry=0x430a60 if original else names['opencfw_boot_address_validate']
   cpu.emu_start(entry|1,0x20002002,count=300)
   assert done,(original,cached,address,length)
   outputs.append((cpu.reg_read(a.UC_ARM_REG_R0),bytes(cpu.mem_read(0x200270c8,4)),len(calls),calls[0][0] if calls else None))
  assert outputs[0]==outputs[1],(cached,address,length,query_range,outputs)
  cases+=1
 print('PASS native/source Boot address validate',cases,'cases with device-info child cut')
