#!/usr/bin/env python3
"""Bounded native/source UART interrupt status leaf at 0x42372a."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/initializer_callbacks/uart_irq_status.c'
with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    obj, elfpath = temp / 'status.o', temp / 'status.elf'
    subprocess.run(['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                    '-mthumb', '-O2', '-ffreestanding', '-fno-builtin', '-c',
                    str(source), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x00500000', str(obj),
                    '-o', str(elfpath)], check=True, stderr=subprocess.DEVNULL)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        entry = next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
                     if s.name == 'opencfw_boot_uart_interrupt_status') & ~1
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    for label, context, magic, module, enabled in [
        ('null', 0, 0, 0, 0),
        ('bad-magic', 0x20002000, 0, 0, 0),
        ('raw-module0', 0x20002000, 0x01ea9e06, 0, 0),
        ('enabled-module0', 0x20002000, 0x01ea9e06, 0, 1),
        ('raw-module1', 0x20002000, 0x01ea9e06, 1, 0),
        ('enabled-module1', 0x20002000, 0x01ea9e06, 1, 1),
    ]:
        pair = []
        for native in (True, False):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            u.mem_map(0, 0x1000)
            u.mem_map(0x00410000, 0x40000)
            u.mem_write(0x00410000, stock)
            u.mem_map(0x00500000, 0x10000)
            if not native:
                for address, payload in segments:
                    u.mem_write(address, payload)
            u.mem_map(0x20000000, 0x30000)
            u.mem_map(0x40039000, 0x3000)
            if context:
                u.mem_write(context, struct.pack('<I', magic))
                u.mem_write(context + 0x28, struct.pack('<I', module))
            u.mem_write(0x4003903c, struct.pack('<I', 0x12345678))
            u.mem_write(0x40039040, struct.pack('<I', 0x87654321))
            u.mem_write(0x4003a03c, struct.pack('<I', 0xabcdef01))
            u.mem_write(0x4003a040, struct.pack('<I', 0x10fedcba))
            u.mem_write(0x20003000, struct.pack('<I', 0xdeadbeef))
            u.reg_write(UC_ARM_REG_R0, context)
            u.reg_write(UC_ARM_REG_R1, 0x20003000)
            u.reg_write(UC_ARM_REG_R2, enabled)
            u.reg_write(UC_ARM_REG_SP, 0x2002f000)
            u.reg_write(UC_ARM_REG_LR, 0x0050f001)
            try:
                u.emu_start((0x0042372a if native else entry) | 1, 0x0050f000, count=1000)
            except Exception as exc:
                raise AssertionError((label, native, hex(u.reg_read(UC_ARM_REG_PC)))) from exc
            pair.append((u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_SP),
                         bytes(u.mem_read(0x20003000, 4))))
        assert pair[0] == pair[1], (label, pair)
    print('PASS_BOOT_UART_IRQ_STATUS', 6)
