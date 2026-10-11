#!/usr/bin/env python3
"""Bounded native/source UART IRQ row composition at 0x41f558."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/initializer_callbacks/uart_irq_rx.c'
with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    obj, stubobj, elfpath = temp/'row.o', temp/'stub.o', temp/'row.elf'
    cc = ['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb']
    subprocess.run(cc + ['-O2', '-ffreestanding', '-fno-builtin',
                         '-fno-inline-functions', '-c',
                         str(source), '-o', str(obj)], check=True)
    undefined = subprocess.check_output(['arm-none-eabi-nm', '-u', str(obj)], text=True)
    names = [line.split()[-1] for line in undefined.splitlines() if line.strip()]
    stub = temp/'stub.S'
    stub.write_text('.syntax unified\n.thumb\n.text\n' + ''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n' for name in names))
    subprocess.run(cc + ['-c', str(stub), '-o', str(stubobj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x00500000', str(obj), str(stubobj),
                    '-o', str(elfpath)], check=True, stderr=subprocess.DEVNULL)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    native_cuts = {0x42372a: 'status', 0x423700: 'clear',
                   0x42377c: 'dispatch', 0x41f776: 'drain'}
    source_cuts = {
        symbols['opencfw_boot_uart_interrupt_status'] & ~1: 'status',
        symbols['opencfw_boot_uart_interrupt_clear'] & ~1: 'clear',
        symbols['opencfw_boot_uart_irq_dispatch'] & ~1: 'dispatch',
        symbols['opencfw_boot_uart_irq_rx_drain'] & ~1: 'drain',
    }
    for status in (0, 1, 0x10, 0x40, 0x50, 0x51):
        pair = []
        for native in (True, False):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            u.mem_map(0x00410000, 0x40000)
            u.mem_write(0x00410000, stock)
            u.mem_map(0x00500000, 0x10000)
            if not native:
                for address, payload in segments:
                    u.mem_write(address, payload)
            u.mem_map(0x20000000, 0x30000)
            row = 0x20000454 + 0x1c
            u.mem_write(row + 4, struct.pack('<I', 0x20002000))
            calls = []
            cuts = native_cuts if native else source_cuts
            def callback(cpu, address, size, _):
                if address not in cuts:
                    return
                kind = cuts[address]
                args = tuple(cpu.reg_read(reg) for reg in
                             (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
                calls.append((kind, args[0], None if kind == 'status' else args[1], args[2]))
                if kind == 'status':
                    cpu.mem_write(args[1], struct.pack('<I', status))
                cpu.reg_write(UC_ARM_REG_R0, 0)
                cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, callback)
            u.reg_write(UC_ARM_REG_R0, 1)
            u.reg_write(UC_ARM_REG_SP, 0x2002f000)
            u.reg_write(UC_ARM_REG_LR, 0x0050f001)
            entry = 0x41f558 if native else symbols['opencfw_boot_uart_irq_row'] & ~1
            try:
                u.emu_start(entry | 1, 0x0050f000, count=2000)
            except Exception as exc:
                raise AssertionError((hex(status), native,
                                      hex(u.reg_read(UC_ARM_REG_PC)), calls)) from exc
            pair.append((u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_SP),
                         bytes(u.mem_read(row + 0x19, 1)), calls))
        assert pair[0] == pair[1], (hex(status), pair)
    print('PASS_BOOT_UART_IRQ_ROW', 6)
