#!/usr/bin/env python3
"""Bounded native/source GPIO vector read sequence and signed IRQ check."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP)

ROOT = Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/initializer_callbacks/external_irq_wrappers.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert hashlib.sha256(BLOB.read_bytes()).hexdigest() == LOCKED

with tempfile.TemporaryDirectory(prefix='boot-gpio-vectors-') as directory:
    out = Path(directory)
    obj, stubs, elfpath = out / 'wrappers.o', out / 'stubs.o', out / 'wrappers.elf'
    cc = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb']
    subprocess.run(cc + ['-O2', '-ffreestanding', '-fno-builtin',
                         '-ffunction-sections', '-c', str(SOURCE), '-o', str(obj)], check=True)
    names = [line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(obj)], text=True).splitlines()]
    assembly = out / 'stubs.S'
    assembly.write_text('.syntax unified\n.thumb\n.text\n' + ''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n'
        for name in names if name != 'opencfw_boot_gpio_irqnums') +
        '.data\n.global opencfw_boot_gpio_irqnums\nopencfw_boot_gpio_irqnums:\n'
        '.short 56,57,58,59\n')
    subprocess.run(cc + ['-c', str(assembly), '-o', str(stubs)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x500000', '-o', str(elfpath),
                    str(obj), str(stubs)], check=True, stderr=subprocess.DEVNULL)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments()
                    if p['p_type'] == 'PT_LOAD']
    rows = []
    native_trace = {}
    for row, native in ((0, 0x4303de), (1, 0x430404), (2, 0x43042a)):
        for first, second, third in ((56 + row, -1, 57 + row),
                                     (0, 32767, -32768)):
            result = []
            for stock in (True, False):
                cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                cpu.mem_map(0x410000, 0x40000)
                cpu.mem_write(0x410000, BLOB.read_bytes())
                cpu.mem_map(0x500000, 0x10000)
                if not stock:
                    for address, data in segments:
                        cpu.mem_write(address, data)
                cpu.mem_map(0x20000000, 0x40000)
                table = (0x43409c if stock else symbols['opencfw_boot_gpio_irqnums']) + 2 * row
                cpu.mem_write(table, struct.pack('<h', first))
                child = {
                    (0x41df48 if stock else symbols['opencfw_boot_gpio_irq_status'] & ~1): 'status',
                    (0x41dfc6 if stock else symbols['opencfw_boot_gpio_irq_clear'] & ~1): 'clear',
                    (0x41e09a if stock else symbols['opencfw_boot_gpio_irq_service'] & ~1): 'service',
                }
                calls = []
                done = [False]
                def code(emu, address, size, _):
                    if address == 0x50f000:
                        done[0] = True
                        emu.emu_stop()
                        return
                    if stock and native <= address < native + 38:
                        native_trace.setdefault(hex(address),
                                                bytes(emu.mem_read(address, size)).hex())
                    kind = child.get(address)
                    if kind:
                        irq = emu.reg_read(UC_ARM_REG_R0)
                        arg = emu.reg_read(UC_ARM_REG_R1)
                        calls.append([kind, irq, arg if kind != 'status' else 0])
                        if kind == 'status':
                            emu.mem_write(emu.reg_read(UC_ARM_REG_R2), struct.pack('<I', 0x11223344))
                            emu.mem_write(table, struct.pack('<h', second))
                        elif kind == 'clear':
                            emu.mem_write(table, struct.pack('<h', third))
                        emu.reg_write(UC_ARM_REG_R0, 0)
                        emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))
                cpu.hook_add(UC_HOOK_CODE, code)
                cpu.reg_write(UC_ARM_REG_SP, 0x2003f000)
                cpu.reg_write(UC_ARM_REG_LR, 0x50f001)
                symbol = f'opencfw_boot_gpio_irq{row}'
                cpu.emu_start((native if stock else symbols[symbol] & ~1) | 1,
                              0x50f002, count=1000)
                assert done[0], (row, stock)
                result.append(calls)
            expected = [['status', first & 0xffffffff, 0],
                        ['clear', second & 0xffffffff, 0x11223344],
                        ['service', third & 0xffffffff, 0x11223344]]
            assert result[0] == result[1] == expected, (row, first, second, third, result)
            rows.append({'row': row, 'irq_values': [first, second, third],
                         'calls': expected})
    report = {'status': 'PASS_BOUNDED_GPIO_VECTOR_READS', 'cases': rows,
              'original_sha256': LOCKED,
              'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'source_elf_sha256': hashlib.sha256(elfpath.read_bytes()).hexdigest(),
              'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'original_trace': native_trace,
              'limits': ['Child status/clear/service bodies are intercepted; wrapper ordering, three signed IRQ table reads, stack status propagation and argument ABI compare.',
                         'Modified IRQ table values are synthetic fault fixtures; source-owned product table is 56,57,58,59. No physical IRQ/device proof.']}
    path = Path(__file__).with_name('external-gpio-irq-wrapper-oracle.json')
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'cases': len(rows),
                      'source_sha256': report['source_sha256']}))
