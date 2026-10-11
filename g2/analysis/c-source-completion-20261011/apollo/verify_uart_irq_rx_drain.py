#!/usr/bin/env python3
"""Bounded native/source UART IRQ RX drain comparison (0x41f776)."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PRIMASK, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
sources = [ROOT / 'g2/components/bootloader/initializer_callbacks/uart_irq_rx.c',
           ROOT / 'g2/components/bootloader/initializer_callbacks/uart_rx.c']
with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    cc = ['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
          '-mthumb', '-O2', '-ffreestanding', '-fno-builtin']
    objects = []
    for index, source in enumerate(sources):
        obj = temp / f'unit{index}.o'
        subprocess.run(cc + ['-c', str(source), '-o', str(obj)], check=True)
        objects.append(obj)
    undefined = set()
    defined = set()
    for obj in objects:
        for line in subprocess.check_output(['arm-none-eabi-nm', '-g', str(obj)], text=True).splitlines():
            fields = line.split()
            if len(fields) == 2 and fields[0] == 'U':
                undefined.add(fields[1])
            elif len(fields) == 3 and fields[1] in ('T', 'W'):
                defined.add(fields[2])
    missing = sorted(undefined - defined)
    stub = temp / 'stub.S'
    stub.write_text('.syntax unified\n.thumb\n.text\n' + ''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n' for name in missing))
    stubobj = temp / 'stub.o'
    subprocess.run(cc + ['-c', str(stub), '-o', str(stubobj)], check=True)
    elfpath = temp / 'rx.elf'
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x00500000',
                    *[str(obj) for obj in objects], str(stubobj),
                    '-o', str(elfpath)], check=True)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    entry = symbols['opencfw_boot_uart_irq_rx_drain'] & ~1
    cases = [
        ('empty-continue', 0, 4, 0x10, 0, 2),
        ('empty-notify', 1, 4, 0x10, 0, 2),
        ('ready-continue', 0, 4, 0, 0x45, 2),
        ('ready-notify', 1, 4, 0, 0x45, 2),
        ('fifo-error', 0, 4, 0, 0x145, 2),
        ('zero-limit', 1, 0, 0, 0x45, 2),
    ]
    for label, notify, maximum, status, data, prior in cases:
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
            u.mem_map(0x40039000, 0x1000)
            u.mem_write(0x40039000, struct.pack('<I', data))
            u.mem_write(0x40039018, struct.pack('<I', status))
            row = 0x20000454
            context = 0x20002000
            state = 0x20003000
            dest = 0x20004000
            u.mem_write(row + 4, struct.pack('<I', context))
            u.mem_write(row + 0x10, struct.pack('<I', state))
            u.mem_write(context + 0x28, struct.pack('<I', 0))
            u.mem_write(state + 8, struct.pack('<I', prior))
            u.mem_write(state + 0xc, struct.pack('<I', dest))
            u.mem_write(dest, b'\xaa' * 16)
            u.reg_write(UC_ARM_REG_R0, 0)
            u.reg_write(UC_ARM_REG_R1, maximum)
            u.reg_write(UC_ARM_REG_R2, notify)
            u.reg_write(UC_ARM_REG_SP, 0x2002f000)
            u.reg_write(UC_ARM_REG_LR, 0x0050f001)
            u.emu_start((0x0041f776 if native else entry) | 1, 0x0050f000, count=3000)
            pair.append((u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_SP),
                         u.reg_read(UC_ARM_REG_PRIMASK),
                         bytes(u.mem_read(state + 8, 4)), bytes(u.mem_read(dest, 16))))
        assert pair[0] == pair[1], (label, pair)
    print('PASS_BOOT_UART_IRQ_RX_DRAIN', len(cases))
