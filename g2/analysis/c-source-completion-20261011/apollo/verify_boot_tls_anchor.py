#!/usr/bin/env python3
"""Bounded stock/source return ABI for the IAR TLS anchor leaf at 0x422874."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_SP, UC_ARM_REG_LR

root = Path(__file__).resolve().parents[4]
stock = (root / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'

with tempfile.TemporaryDirectory() as folder:
    work = Path(folder)
    source = root / 'g2/components/bootloader/runtime_memory/iar_thread_pointer_anchor.c'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-ffreestanding', '-c', str(source),
                    '-o', str(work / 'anchor.o')], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x10000', '-e',
                    'opencfw_boot_iar_thread_pointer_anchor', str(work / 'anchor.o'),
                    '-o', str(work / 'anchor.elf')], check=True)
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary',
                    str(work / 'anchor.elf'), str(work / 'anchor.bin')], check=True)
    source_code = (work / 'anchor.bin').read_bytes()
    results = []
    for original, entry in ((True, 0x422874), (False, 0x10000)):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x10000, 0x1000)
        cpu.mem_map(0x410000, 0x25000)
        cpu.mem_map(0x20000000, 0x2000)
        cpu.mem_write(0x10000, source_code)
        cpu.mem_write(0x410000, stock)
        stopped = []
        def hook(machine, pc, size, unused):
            if pc == 0x20001000:
                stopped.append(True)
                machine.emu_stop()
        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.reg_write(UC_ARM_REG_SP, 0x20001800)
        cpu.reg_write(UC_ARM_REG_LR, 0x20001001)
        cpu.emu_start(entry | 1, 0x20001002, count=16)
        assert stopped
        results.append(cpu.reg_read(UC_ARM_REG_R0))
    assert results == [0x20000518, 0x20000518], results
    print('PASS native/source TLS anchor return', [hex(x) for x in results])
