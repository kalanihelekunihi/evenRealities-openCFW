#!/usr/bin/env python3
"""Bounded native/source volatile three-read and PRIMASK oracle."""
from pathlib import Path
import hashlib
import struct
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_READ
from unicorn import arm_const as a

root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
    work=Path(directory)
    source=root/'g2/components/bootloader/runtime_memory/boot_triple_snapshot.c'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(work/'snapshot.o')],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_triple_snapshot',str(work/'snapshot.o'),'-o',str(work/'snapshot.elf')],check=True)
    subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(work/'snapshot.elf'),str(work/'snapshot.bin')],check=True)
    code=(work/'snapshot.bin').read_bytes()
    for values in ((0,0,0),(1,2,3),(0xdeadbeef,0x12345678,0x80000000)):
        for incoming_mask in (0,1):
            results=[]
            for original,entry in ((True,0x422aac),(False,0x10000)):
                cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                cpu.mem_map(0x10000,0x1000);cpu.mem_map(0x410000,0x25000);cpu.mem_map(0x20000000,0x4000)
                cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
                cpu.reg_write(a.UC_ARM_REG_SP,0x20003000);cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
                cpu.reg_write(a.UC_ARM_REG_R0,0x20000100);cpu.reg_write(a.UC_ARM_REG_R1,0x20000200)
                cpu.reg_write(a.UC_ARM_REG_PRIMASK,incoming_mask)
                reads=[];done=[]
                def memory(machine,access,address,size,value,unused):
                    if address==0x20000100:
                        index=len(reads);assert index<3
                        machine.mem_write(address,struct.pack('<I',values[index]))
                        reads.append((index,machine.reg_read(a.UC_ARM_REG_PRIMASK)))
                def hook(machine,pc,size,unused):
                    if pc==0x20002000:done.append(True);machine.emu_stop()
                cpu.hook_add(UC_HOOK_MEM_READ,memory);cpu.hook_add(UC_HOOK_CODE,hook)
                cpu.emu_start(entry|1,0x20002002,count=100)
                assert done
                words=struct.unpack('<3I',cpu.mem_read(0x20000200,12))
                results.append((words,tuple(reads),cpu.reg_read(a.UC_ARM_REG_PRIMASK),cpu.reg_read(a.UC_ARM_REG_SP)))
            assert results[0]==results[1],(values,incoming_mask,results)
            assert results[0][0]==values
            assert results[0][2]==incoming_mask
    print('PASS native/source triple volatile snapshot six cases')
