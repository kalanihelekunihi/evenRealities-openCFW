#!/usr/bin/env python3
"""Bounded native/source UART IRQ dispatch and DMA register leaves."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/initializer_callbacks/uart_irq_dispatch.c'
with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    obj, stubobj, elfpath = temp/'irq.o', temp/'stub.o', temp/'irq.elf'
    cc = ['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb']
    subprocess.run(cc + ['-O2', '-ffreestanding', '-fno-builtin', '-c',
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
    addresses = {
        'opencfw_boot_uart_irq_dispatch': 0x42377c,
        'opencfw_boot_uart_dma_disable': 0x422d20,
        'opencfw_boot_uart_dma_rx_stop': 0x422d4c,
        'opencfw_boot_uart_dma_error': 0x422d7a,
        'opencfw_boot_uart_dma_recover': 0x422fde,
    }
    cases = [
        ('dispatch-null', 'opencfw_boot_uart_irq_dispatch', 0, 0, 0, 0),
        ('dispatch-bad-magic', 'opencfw_boot_uart_irq_dispatch', 0, 0, 0, 1),
        ('dispatch-idle', 'opencfw_boot_uart_irq_dispatch', 0, 0, 0, 2),
        ('dispatch-flag', 'opencfw_boot_uart_irq_dispatch', 1, 0, 0, 2),
        ('dispatch-dma-idle', 'opencfw_boot_uart_irq_dispatch', 0, 1, 0, 2),
        ('dispatch-dma-complete', 'opencfw_boot_uart_irq_dispatch', 0x800, 1, 0, 2),
        ('dispatch-dma-stop', 'opencfw_boot_uart_irq_dispatch', 0x1000, 1, 0, 2),
        ('dma-disable', 'opencfw_boot_uart_dma_disable', 0, 1, 0, 2),
        ('dma-rx-stop', 'opencfw_boot_uart_dma_rx_stop', 0, 1, 0, 2),
        ('dma-error-none', 'opencfw_boot_uart_dma_error', 0, 1, 0, 2),
        ('dma-error-bit6', 'opencfw_boot_uart_dma_error', 0x40, 1, 0, 2),
        ('dma-error-bit12', 'opencfw_boot_uart_dma_error', 0x1000, 1, 0, 2),
        ('dma-recover-idle', 'opencfw_boot_uart_dma_recover', 0, 0, 0, 2),
        ('dma-recover-active', 'opencfw_boot_uart_dma_recover', 0, 1, 0, 2),
        ('dma-recover-timer', 'opencfw_boot_uart_dma_recover', 0, 1, 0, 3),
        ('dma-recover-timer-clock', 'opencfw_boot_uart_dma_recover', 0, 1, 0, 4),
    ]
    for label, function, status, dma, callback, context_kind in cases:
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
            context = 0 if context_kind == 0 else 0x20002000
            if context:
                u.mem_write(context, struct.pack('<I', 0 if context_kind == 1 else 0x01ea9e06))
                u.mem_write(context + 0x28, struct.pack('<I', 0))
                u.mem_write(context + 0x11b, bytes([dma]))
                u.mem_write(context + 0xf0, struct.pack('<I', callback))
                u.mem_write(context + 0xe4, struct.pack('<I', 11))
                u.mem_write(context + 0xe8, struct.pack('<I', 0x20003000))
                if context_kind >= 3:
                    u.mem_write(context + 0x30, struct.pack('<I', 4000000))
            u.mem_write(0x40039004, struct.pack('<I', 0xffff))
            u.mem_write(0x40039030, struct.pack('<I', 0x5234 if context_kind == 4 else 0x1234))
            u.mem_write(0x4003903c, struct.pack('<I', 0))
            u.mem_write(0x40039050, struct.pack('<I', 3))
            if context_kind >= 3:
                u.mem_write(0x40039018, struct.pack('<I', 8))
            u.reg_write(UC_ARM_REG_R0, context if function != 'opencfw_boot_uart_dma_error' else 0)
            u.reg_write(UC_ARM_REG_R1, status)
            u.reg_write(UC_ARM_REG_SP, 0x2002f000)
            u.reg_write(UC_ARM_REG_LR, 0x0050f001)
            entry = addresses[function] if native else symbols[function] & ~1
            calls = []
            if function == 'opencfw_boot_uart_dma_recover':
                def lower_cut(cpu, address, size, _):
                    delay = 0x41d1c0 if native else symbols['opencfw_boot_delay_us_math'] & ~1
                    if address == delay:
                        calls.append(('delay', cpu.reg_read(UC_ARM_REG_R0)))
                        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
                    elif native and address in (0x423342, 0x422fa2):
                        cpu.reg_write(UC_ARM_REG_R0, 0)
                        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE, lower_cut)
            u.emu_start(entry | 1, 0x0050f000, count=2000)
            result = u.reg_read(UC_ARM_REG_R0) if function in (
                'opencfw_boot_uart_irq_dispatch', 'opencfw_boot_uart_dma_error') else None
            pair.append((result, u.reg_read(UC_ARM_REG_SP),
                         bytes(u.mem_read(0x20002000, 0x120)),
                         bytes(u.mem_read(0x20003000, 4)),
                         bytes(u.mem_read(0x40039000, 0x54)), calls))
        assert pair[0] == pair[1], (label, pair[0][0], pair[1][0])
    print('PASS_BOOT_UART_IRQ_DISPATCH', len(cases))
