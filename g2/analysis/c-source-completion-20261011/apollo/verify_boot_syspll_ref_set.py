#!/usr/bin/env python3
"""Bounded original/source check for native SYSPLL bit-6 setter 0x41ac92."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[4]
stock = (root / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
source = root / 'g2/components/bootloader/clock_manager/clock_class_provider6.c'
with tempfile.TemporaryDirectory() as directory:
    out = Path(directory)
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
                    '-mfpu=fpv5-sp-d16', '-mfloat-abi=softfp', '-std=c11',
                    '-ffreestanding', '-fno-builtin', '-O2', '-ffunction-sections',
                    '-fdata-sections', '-c', str(source), '-o', str(out/'body.o')], check=True)
    subprocess.run(['arm-none-eabi-ld', '--gc-sections', '-Ttext=0x10000',
                    '-e', 'opencfw_boot_syspll_ref_set', str(out/'body.o'),
                    '-o', str(out/'body.elf')], check=True)
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', str(out/'body.elf'),
                    str(out/'body.bin')], check=True)
    with (out/'body.elf').open('rb') as file:
        entry = ELFFile(file).header['e_entry']
    body = (out/'body.bin').read_bytes()
    cases = [(mode, prior, value) for mode in (0, 1, 2, 255)
             for prior in (0, 1) for value in (0, 0xffffffff, 0x12345678)]
    for mode, prior, value in cases:
        outputs = []
        for original in (True, False):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            cpu.mem_map(0x10000, 0x1000)
            cpu.mem_map(0x410000, 0x30000)
            cpu.mem_map(0x20000000, 0x30000)
            cpu.mem_map(0x40008000, 0x1000)
            cpu.mem_write(0x10000, body)
            cpu.mem_write(0x410000, stock)
            cpu.mem_write(0x40008858, value.to_bytes(4, 'little'))
            cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
            cpu.reg_write(a.UC_ARM_REG_LR, 0x20008001)
            cpu.reg_write(a.UC_ARM_REG_R0, mode)
            cpu.reg_write(a.UC_ARM_REG_PRIMASK, prior)
            done = []
            def hook(machine, pc, size, unused):
                if pc == 0x20008000:
                    done.append(True)
                    machine.emu_stop()
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.emu_start((0x41ac92 if original else entry) | 1, 0x20008002, count=200)
            assert done, (original, mode, prior, value)
            outputs.append((int.from_bytes(cpu.mem_read(0x40008858, 4), 'little'),
                            cpu.reg_read(a.UC_ARM_REG_PRIMASK)))
        assert outputs[0] == outputs[1], (mode, prior, value, outputs)
    print('PASS native/source SYSPLL ref setter', len(cases), 'cases')
