#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded transmit loops with scripted MMIO; no hardware claim."""
import json
import re
import struct
import subprocess

from analyze_gx8002_upstream_objects import IMAGE
from link_gx8002_uart_console import ROOT, build
from verify_gx8002_memcpy_source import decode


def execute(code, start, descriptor, base, value, statuses):
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=descriptor, r1=value)
    trace, index, pc = [], 0, start
    for _ in range(10000):
        op, args, width = code[pc]
        parts = [p.strip() for p in args.split(',')]
        following = pc + width
        if op in ('ld.w', 'st.w'):
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not match:
                raise ValueError('unsupported memory operand')
            reg, pointer, offset = match.groups()
            address = (registers[pointer] + int(offset, 0)) & 0xffffffff
            if op == 'st.w':
                if address != base:
                    raise ValueError('unexpected write address')
                trace.append(('write', address, 4, registers[reg]))
            else:
                if address == descriptor + 4:
                    loaded = base
                elif address == base + 20:
                    if index == len(statuses):
                        return 'waiting', trace
                    loaded = statuses[index]
                    index += 1
                else:
                    raise ValueError('unexpected read address')
                trace.append(('read', address, 4, loaded))
                registers[reg] = loaded
        elif op in ('addi', 'andi'):
            a = registers[parts[-2]]
            b = int(parts[-1], 0)
            registers[parts[0]] = ((a + b) if op == 'addi' else (a & b)) & 0xffffffff
        elif op == 'bez':
            if registers[parts[0]] == 0:
                following = int(parts[1], 0)
        elif op == 'rts':
            return 'returned', trace
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def verify(prefix=None, sdk=None, output=None):
    placement = build(prefix, output)  # Authenticates stock and rebuilds native source.
    output = output or ROOT / 'build/gx8002-uart-console'
    prefix = (prefix or ROOT / 'build/csky-macos/install/bin') / 'csky-unknown-elf-'
    wrapper = output / 'stock.elf'
    subprocess.run([str(prefix) + 'objcopy', '-I', 'binary', '-O', 'elf32-csky-little',
                    '-B', 'csky', str(IMAGE), str(wrapper)], check=True)
    data = bytearray(wrapper.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    wrapper.write_bytes(data)
    stock = decode(subprocess.check_output([str(prefix) + 'objdump', '-D',
                   '--start-address=0xc7d8', '--stop-address=0xc7ec', str(wrapper)], text=True))
    candidate = decode(subprocess.check_output([str(prefix) + 'objdump', '-d',
                       '--section=.text.open_cfw_gx8002_uart_transmit',
                       str(output / 'console.elf')], text=True))
    cases = 0
    for descriptor, base in ((0x20026a94, 0xa0000000), (0x20026b14, 0xa0100000)):
        for value in (0, 10, 13, 255, 266, 0x80000000, 0xffffffff):
            for delay in (0, 1, 2, 7, 31):
                for ready in (32, 33, 0xffffffff):
                    for waiting in (False, True):
                        statuses = [0xffffffdf] * delay + ([] if waiting else [ready])
                        a = execute(stock, 0xc7d8, descriptor, base, value, statuses)
                        b = execute(candidate, 0x1020324c, descriptor, base, value, statuses)
                        expected = [('read', descriptor + 4, 4, base)]
                        expected += [('read', base + 20, 4, s) for s in statuses]
                        if not waiting:
                            expected.append(('write', base, 4, value))
                        oracle = ('waiting' if waiting else 'returned', expected)
                        if a != b or a != oracle:
                            raise ValueError('transmit trace or oracle mismatch')
                        cases += 1
    report = {'placement': placement, 'cases': cases, 'exact_mmio_trace_comparison': True,
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Restricted instruction interpreter, scripted MMIO, no timing model.',
                         'Never-ready paths checked only for finite prefixes.',
                         'Port wrapper behavior is not covered by this comparison.']}
    (ROOT / 'docs/research/gx8002-uart-transmit-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
