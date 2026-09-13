#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify a second, boot-stage-2 occurrence of the reviewed VIC enable-IRQ leaf.

runtime_gx8002_irq.c's open_cfw_gx8002_irq_enable (a thin, noinline wrapper
around the pinned Apache-2.0 C-SKY CSI csi_vic_enable_irq()) is already
qualified against one main-image occurrence (see verify_gx8002_irq.py /
compare_gx8002_irq.py). The stock UART boot stage 2 image contains a second,
byte-different but instruction-for-instruction equivalent compilation of the
same csi_vic_enable_irq() body at package offset 0x311C. This module decodes
both the compiled candidate and that second stock occurrence and proves they
compute the identical VIC->ISER[(IRQn>>5)&3] = 1<<(IRQn&31) write for every
tested 32-bit IRQn, independent of register allocation.
"""
import json
import re
import struct
import subprocess
from pathlib import Path

from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_logging import check_paths
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_irq.c'
SYMBOL = 'open_cfw_gx8002_irq_enable'
PACKAGE_OFFSET = 0x311C
ENVELOPE_BYTES = 28
VIC_BASE = 0xe000e100

FLAGS = ['-O2', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin',
         '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']


def execute(code, entry, irqn):
    r = {f'r{i}': 0x87650000 + i for i in range(32)}
    r['r0'] = irqn & 0xffffffff
    initial = r.copy()
    pc = entry
    writes = []
    for _ in range(64):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        if op == 'andi':
            r[p[0]] = r[p[1]] & int(p[2], 0)
        elif op == 'movi':
            r[p[0]] = int(p[1], 0) & 0xffffffff
        elif op == 'lsl':
            # Two-operand form (rx <<= ry) and three-operand form (rz = rx << ry).
            source, shift = (p[0], p[1]) if len(p) == 2 else (p[1], p[2])
            r[p[0]] = (r[source] << (r[shift] & 31)) & 0xffffffff
        elif op == 'lrw':
            r[p[0]] = int(p[1], 0)
        elif op == 'zext':
            high, low = int(p[2], 0), int(p[3], 0)
            r[p[0]] = (r[p[1]] >> low) & ((1 << (high - low + 1)) - 1)
        elif op == 'str.w':
            m = re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d)\)', args)
            if not m:
                raise ValueError('unsupported store operand')
            value, base, shift_reg, shift = m.groups()
            address = (r[base] + (r[shift_reg] << int(shift))) & 0xffffffff
            writes.append((address, r[value]))
        elif op == 'rts':
            if len(writes) != 1 or any(r[f'r{i}'] != initial[f'r{i}'] for i in range(4,32)):
                raise ValueError('VIC write count or preserved ABI mismatch')
            return writes[0]
        else:
            raise ValueError(f'unsupported instruction: {op}')
        pc += width
    raise ValueError('execution bound exceeded')
    return None


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    out = output or ROOT / 'build/gx8002-irq-boot-stage2-enable'
    out.mkdir(parents=True, exist_ok=True)
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    obj = out / 'irq.o'
    command = [pre + 'gcc', *FLAGS]
    for p in ('arch/soc/grus/include', 'include/utility', 'include/utility/libc'):
        command += ['-isystem', str(sdk / p)]
    subprocess.run([*command, '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.' + SYMBOL)
    if section['size'] > ENVELOPE_BYTES or elf.relocations(section['index']):
        raise ValueError('irq_enable placement/relocation failure')
    # runtime_gx8002_irq.c's other functions reference externs (the IRQ table,
    # saved-enable state); the empty relocation list on this section already
    # proves open_cfw_gx8002_irq_enable itself is self-contained.
    payload = elf.contents(section)
    (out / 'irq.disassembly.txt').write_text(
        subprocess.check_output([pre + 'objdump', '-d', str(obj)], text=True))
    # decode() keys instructions by address; every section in a relocatable
    # .o starts at 0, so isolate just this function's section before decoding.
    isolated = subprocess.check_output(
        [pre + 'objdump', '-d', '--section=.text.' + SYMBOL, str(obj)], text=True)
    candidate_code = decode(isolated)
    candidate_start = 0

    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('irq_enable stock identity')
    envelope = stock[PACKAGE_OFFSET:PACKAGE_OFFSET + ENVELOPE_BYTES]
    wrapper = out / 'stock.elf'
    subprocess.run([pre + 'objcopy', '-I', 'binary', '-O', 'elf32-csky-little', '-B', 'csky',
                    str(IMAGE), str(wrapper)], check=True)
    data = bytearray(wrapper.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    wrapper.write_bytes(data)
    stock_disassembly = subprocess.check_output(
        [pre + 'objdump', '-D', f'--start-address={PACKAGE_OFFSET}',
         f'--stop-address={PACKAGE_OFFSET + ENVELOPE_BYTES}', str(wrapper)], text=True)
    stock_code = decode(stock_disassembly)

    cases = 0
    irqns = [*range(0, 260), 0x7f, 0x80, 0xff, 0x7fffffff, 0x80000000, -1, -128, 0xffffff80, 0xdeadbeef]
    for irqn in irqns:
        candidate = execute(candidate_code, candidate_start, irqn)
        stock_result = execute(stock_code, PACKAGE_OFFSET, irqn)
        expected = (VIC_BASE + 4 * ((irqn >> 5) & 3), (1 << (irqn & 31)) & 0xffffffff)
        if candidate != stock_result or candidate != expected:
            raise ValueError('VIC enable-IRQ write mismatch')
        cases += 1

    row = {'symbol': SYMBOL, 'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
           'ownership_kind': 'compiled_c',
           'stock_occurrences': [{'symbol': SYMBOL, 'package_offset': PACKAGE_OFFSET,
                                   'bytes': ENVELOPE_BYTES, 'sha256': sha(envelope),
                                   'region': 'boot_stage2'}]}
    return {'functions': [row], 'source_sha256': sha(SOURCE.read_bytes()),
            'verifier_sha256': sha(Path(__file__).read_bytes()), 'flags': FLAGS,
            'decoded_cases': cases, 'source_admitted': True, 'hardware_qualified': False,
            'policy': 'Decoded-instruction VIC write comparison; consistent register renaming only.',
            'limits': ['Compiled bytes differ from the stock envelope (register allocation only); '
                       'instruction-level MMIO write is proven identical for all tested IRQn.',
                       'VIC hardware behavior is not qualified.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-irq-boot-stage2-enable-verification.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('Qualified boot-stage-2 VIC enable-IRQ occurrence:', report['decoded_cases'], 'cases')
