#!/usr/bin/env python3
"""Bounded stock/source constraint handler ABI with a real callback hook."""
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

with tempfile.TemporaryDirectory() as folder:
    work = Path(folder)
    sources = [root / 'g2/components/bootloader/runtime_memory/iar_constraint_dispatch.c',
               root / 'g2/components/bootloader/runtime_memory/iar_constraint_dispatch_entry.S']
    objects = []
    for n, source in enumerate(sources):
        obj = work / f'unit{n}.o'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-O2', '-ffreestanding', '-fno-builtin',
                        '-c', str(source), '-o', str(obj)], check=True)
        objects.append(str(obj))
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x10000', '-e',
                    'opencfw_boot_constraint_dispatch',
                    '--defsym=opencfw_format_abort_contract=0x12001',
                    *objects, '-o', str(work / 'dispatch.elf')],
                   check=True, stderr=subprocess.DEVNULL)
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary',
                    str(work / 'dispatch.elf'), str(work / 'dispatch.bin')], check=True)
    code = (work / 'dispatch.bin').read_bytes()
    nm = subprocess.check_output(['arm-none-eabi-nm', str(work / 'dispatch.elf')], text=True)
    entry = int(next(line.split()[0] for line in nm.splitlines()
                     if line.endswith(' opencfw_boot_constraint_dispatch')), 16)

    def run(original, null_message):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x10000, 0x3000)
        cpu.mem_map(0x410000, 0x25000)
        cpu.mem_map(0x20000000, 0x40000)
        cpu.mem_write(0x10000, code)
        cpu.mem_write(0x410000, stock)
        cpu.mem_write(0x20027190, struct.pack('<I', 0x20002001))
        cpu.mem_write(0x20000100, b'fixture message\0')
        cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
        cpu.reg_write(a.UC_ARM_REG_LR, 0x20003001)
        cpu.reg_write(a.UC_ARM_REG_R7, 0x71a7cafe)
        cpu.reg_write(a.UC_ARM_REG_R0, 0 if null_message else 0x20000100)
        calls = []
        stopped = []
        def hook(machine, pc, size, unused):
            if pc == 0x20002000:
                p = machine.reg_read(a.UC_ARM_REG_R0)
                chars = []
                for offset in range(80):
                    c = machine.mem_read(p + offset, 1)[0]
                    if c == 0:
                        break
                    chars.append(c)
                calls.append((bytes(chars), machine.reg_read(a.UC_ARM_REG_R1),
                              machine.reg_read(a.UC_ARM_REG_R2)))
                machine.reg_write(a.UC_ARM_REG_PC, machine.reg_read(a.UC_ARM_REG_LR))
            elif pc == 0x20003000:
                stopped.append(True)
                machine.emu_stop()
        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x422590 if original else entry) | 1,
                      0x20003002, count=1000)
        assert stopped
        return calls, cpu.reg_read(a.UC_ARM_REG_R0), cpu.reg_read(a.UC_ARM_REG_R1), cpu.reg_read(a.UC_ARM_REG_SP)

    for null_message in (False, True):
        native = run(True, null_message)
        selected = run(False, null_message)
        assert native == selected, (null_message, native, selected)
        assert native[0][0][1:] == (0, 34)
        assert native[1:3] == (34, 0x71a7cafe)
    print('PASS native/source constraint dispatch explicit and default message')
