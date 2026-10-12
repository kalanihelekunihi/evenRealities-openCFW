#!/usr/bin/env python3
"""Bounded native/source oracle for Apollo510 MSPI INTEN disable at 0x426484."""
from pathlib import Path
import hashlib
import struct
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

root = Path(__file__).resolve().parents[4]
stock = (root / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'

with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / 'disable.o'
    elf = Path(directory) / 'disable.elf'
    binary = Path(directory) / 'disable.bin'
    source = root / 'g2/components/bootloader/source_candidate_20261010/mspi_interrupt_disable.c'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb', '-O2', '-ffreestanding', '-fno-builtin', '-c', str(source), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x10000', '-e', 'am_hal_mspi_interrupt_disable', str(obj), '-o', str(elf)], check=True)
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', str(elf), str(binary)], check=True)
    code = binary.read_bytes()
    cases = 0
    for valid, module, mask in ((False,0,0), (False,1,0xffff), (True,0,0), (True,0,0x55aa55aa), (True,1,0xffffffff), (True,2,0x80000001)):
        for null in (False,True):
            results = []
            for original,entry in ((True,0x426484),(False,0x10000)):
                cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                cpu.mem_map(0x10000,0x1000)
                cpu.mem_map(0x410000,0x30000)
                cpu.mem_map(0x20000000,0x30000)
                cpu.mem_map(0x40060000,0x3000)
                cpu.mem_write(0x10000,code)
                cpu.mem_write(0x410000,stock)
                cpu.mem_write(0x20010000,struct.pack('<II',0x01bebebe if valid else 0x100, module))
                cpu.mem_write(0x40060000+module*0x1000+0x200,struct.pack('<I',0xa55aa55a))
                cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000)
                cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
                cpu.reg_write(a.UC_ARM_REG_R0,0 if null else 0x20010000)
                cpu.reg_write(a.UC_ARM_REG_R1,mask)
                done=[]
                def hook(machine,pc,size,unused):
                    if pc==0x20002000:done.append(True);machine.emu_stop()
                cpu.hook_add(UC_HOOK_CODE,hook)
                cpu.emu_start(entry|1,0x20002002,count=100)
                assert done,(original,valid,module,mask,null)
                results.append((cpu.reg_read(a.UC_ARM_REG_R0), bytes(cpu.mem_read(0x40060000+module*0x1000+0x200,4))))
            assert results[0]==results[1],(valid,module,mask,null,results)
            cases += 1
    print('PASS native/source MSPI interrupt disable', cases, 'cases')
