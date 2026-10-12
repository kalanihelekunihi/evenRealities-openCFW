#!/usr/bin/env python3
"""Bounded stock/source LittleFS CRC at 0x4157c0."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
 work=Path(directory);obj=work/'lfs.o';elfpath=work/'lfs.elf'
 source=root/'g2/components/bootloader/filesystem/upstream/lfs_util.c'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-DNDEBUG','-DLFS_NO_DEBUG','-DLFS_NO_WARN','-DLFS_NO_ERROR','-DLFS_NO_ASSERT','-DLFS_NO_INTRINSICS','-I',str(source.parents[1]/'freestanding_include'),'-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','lfs_crc',str(obj),'-o',str(elfpath)],check=True)
 with elfpath.open('rb') as f:
  elf=ELFFile(f)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']]
  names={sym.name:sym['st_value'] for sec in elf.iter_sections() if sec.header.sh_type=='SHT_SYMTAB' for sym in sec.iter_symbols()}
 cases=0
 for crc in (0,0xffffffff,0x12345678):
  for length in (0,1,2,4,8,31,64):
   data=bytes((17*i+length)&255 for i in range(64));outputs=[]
   for original in (True,False):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x10000,0x3000);cpu.mem_map(0x410000,0x30000);cpu.mem_map(0x20000000,0x30000)
    cpu.mem_write(0x410000,stock)
    for address,segment in segments:cpu.mem_write(address,segment)
    cpu.mem_write(0x20010000,data)
    cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
    cpu.reg_write(a.UC_ARM_REG_R0,crc);cpu.reg_write(a.UC_ARM_REG_R1,0x20010000);cpu.reg_write(a.UC_ARM_REG_R2,length)
    done=[]
    def hook(machine,pc,size,unused):
     if pc==0x20002000:done.append(True);machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE,hook)
    entry=0x4157c0 if original else names['lfs_crc']
    cpu.emu_start(entry|1,0x20002002,count=10000)
    assert done
    outputs.append(cpu.reg_read(a.UC_ARM_REG_R0))
   assert outputs[0]==outputs[1],(crc,length,outputs)
   cases+=1
 print('PASS native/source LittleFS CRC',cases,'cases')
