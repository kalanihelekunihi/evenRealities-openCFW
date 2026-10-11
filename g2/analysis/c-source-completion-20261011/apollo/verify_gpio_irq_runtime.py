#!/usr/bin/env python3
"""Bounded Boot GPIO IRQ status/clear/service original/source comparison."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/initializer_callbacks/gpio_irq_runtime.c'
entries = {'status': (0x41df48, 'opencfw_boot_gpio_irq_status'),
           'clear': (0x41dfc6, 'opencfw_boot_gpio_irq_clear'),
           'service': (0x41e09a, 'opencfw_boot_gpio_irq_service')}
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, elfpath = directory / 'gpio.o', directory / 'gpio.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb',
                    '-O2', '-ffreestanding', '-fno-builtin', '-c', str(source),
                    '-o', str(obj)], check=True)
    assert not subprocess.check_output(['arm-none-eabi-nm', '-u', str(obj)]).strip()
    subprocess.run(['arm-none-eabi-ld', '-e', 'opencfw_boot_gpio_irq_status',
                    '-Ttext=0x500000', '-o', str(elfpath), str(obj)], check=True)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    cases = 0
    for kind in entries:
        for irq in (0, 55, 56, 57, 62, 63, 124, 125, 126, 131, 132):
            for enabled in (0, 1):
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
                    cpu.mem_map(0x40010000, 0x10000)
                    for address in range(0x40010530, 0x40010600, 4):
                        cpu.mem_write(address, struct.pack('<I', (address ^ 0x93a7f50c) & 0xffffffff))
                    cpu.mem_write(0x20001000, struct.pack('<I', 0xdeadbeef))
                    cpu.mem_write(0x20023600, struct.pack('<I', 0))
                    calls = []
                    if kind == 'service' and irq in (56, 125):
                        callback_addr = 0x20023600 if irq == 56 else 0x20023980
                        arg_addr = 0x20023d00 if irq == 56 else 0x20024080
                        cpu.mem_write(callback_addr, struct.pack('<I', 0x500e01))
                        cpu.mem_write(arg_addr, struct.pack('<I', 0x12345678))
                    def on_code(emu, address, size, _):
                        if address == 0x500e00:
                            calls.append(emu.reg_read(UC_ARM_REG_R0))
                            emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))
                    cpu.hook_add(UC_HOOK_CODE, on_code)
                    cpu.reg_write(UC_ARM_REG_R0, irq)
                    cpu.reg_write(UC_ARM_REG_R1, enabled if kind == 'status' else (1 if kind == 'service' else 0x45))
                    cpu.reg_write(UC_ARM_REG_R2, 0x20001000)
                    cpu.reg_write(UC_ARM_REG_SP, 0x2002f000)
                    cpu.reg_write(UC_ARM_REG_LR, 0x50f001)
                    entry = entries[kind][0] if native else symbols[entries[kind][1]] & ~1
                    try:
                        cpu.emu_start(entry | 1, 0x50f000, count=5000)
                    except Exception as exc:
                        raise AssertionError((kind, irq, enabled, native,
                                              hex(cpu.reg_read(UC_ARM_REG_PC)))) from exc
                    pair.append((cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_SP),
                                 bytes(cpu.mem_read(0x20001000, 4)),
                                 bytes(cpu.mem_read(0x40010530, 0xd0)), calls))
                assert pair[0] == pair[1], (kind, irq, enabled, pair)
                cases += 1
    print('PASS_BOOT_GPIO_IRQ_RUNTIME', cases)
