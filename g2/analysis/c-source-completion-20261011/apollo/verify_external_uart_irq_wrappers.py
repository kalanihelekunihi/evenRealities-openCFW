#!/usr/bin/env python3
"""Bounded source/native UART vector wrapper branch and child-argument check."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/initializer_callbacks/external_irq_wrappers.c'
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, stubobj, elfpath = directory / 'wrappers.o', directory / 'stubs.o', directory / 'wrappers.elf'
    cc = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb']
    subprocess.run(cc + ['-O2', '-ffreestanding', '-fno-builtin', '-fno-inline-functions',
                         '-c', str(source), '-o', str(obj)], check=True)
    names = [line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(obj)], text=True).splitlines()]
    stub = directory / 'stubs.S'
    stub.write_text('.syntax unified\n.thumb\n.text\n' + ''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n' for name in names
        if name != 'opencfw_boot_gpio_irqnums') +
        '.data\n.global opencfw_boot_gpio_irqnums\nopencfw_boot_gpio_irqnums:\n'
        '.short 56,57,58,59\n')
    subprocess.run(cc + ['-c', str(stub), '-o', str(stubobj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x500000', '-o', str(elfpath),
                    str(obj), str(stubobj)], check=True, stderr=subprocess.DEVNULL)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    cases = 0
    for row, native_entry in ((1, 0x41f5d0), (2, 0x41f5e6), (3, 0x41f5fc)):
        for flag in (0, 1, 2):
            pair = []
            for native in (True, False):
                cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                cpu.mem_map(0x410000, 0x40000)
                cpu.mem_write(0x410000, stock)
                cpu.mem_map(0x500000, 0x10000)
                if not native:
                    for address, payload in segments:
                        cpu.mem_write(address, payload)
                cpu.mem_map(0x20000000, 0x30000)
                cpu.mem_write(0x20000454 + row * 0x1c + 0x18, bytes([flag]))
                calls = []
                child = 0x41f558 if native else symbols['opencfw_boot_uart_irq_row'] & ~1
                def cut(emu, address, size, _):
                    if address == child:
                        calls.append(emu.reg_read(UC_ARM_REG_R0))
                        emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))
                cpu.hook_add(UC_HOOK_CODE, cut)
                cpu.reg_write(UC_ARM_REG_SP, 0x2002f000)
                cpu.reg_write(UC_ARM_REG_LR, 0x50f001)
                name = f'opencfw_boot_uart_irq{row}'
                cpu.emu_start((native_entry if native else symbols[name] & ~1) | 1,
                              0x50f000, count=1000)
                pair.append((calls, cpu.reg_read(UC_ARM_REG_SP), cpu.reg_read(UC_ARM_REG_PC)))
            assert pair[0] == pair[1], (row, flag, pair)
            cases += 1
    print('PASS_BOOT_UART_VECTOR_WRAPPERS', cases)
