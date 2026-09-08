#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""GPIO setter ordered MMIO and decoded leaf-ABI qualification."""
import json
import re
import shutil
import struct
import subprocess
from itertools import product
from build_gx8002_gpio_output_candidate import ROOT, IMAGE, build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK = 0xffffffff


def expected(kind, port, value, words):
    words = words.copy()
    trace = []
    bit = 1 << (port & 31)
    operations = ([(8, False), (0, True)] if value == 1 else
                  [(0, False), (8, True)] if value == 0 else
                  [(8, False), (0, False)] if value == 2 else [])
    if kind == 'level':
        operations = [(4, value != 0)]
    for offset, set_bit in operations:
        address = 0xa0001000 + offset
        previous = words[address]
        trace.append(('read', address, previous))
        result = (previous | bit) if set_bit else previous & ~bit
        words[address] = result & MASK
        trace.append(('write', address, result & MASK))
    return trace, words, 0


def execute(code, pc, port, value, words, seed):
    words = words.copy()
    trace = []
    r = {f'r{i}': (seed ^ i * 0x1020304) & MASK for i in range(32)}
    r['r0'], r['r1'] = port, value
    initial = r.copy()
    condition = False
    for _ in range(80):
        op, args, width = code[pc]
        p = [s.strip() for s in args.split(',')]
        nxt = pc + width
        if op in ('movi', 'lrw'):
            r[p[0]] = int(p[1], 0) & MASK
        elif op == 'subi':
            r[p[0]] = (r[p[0]] - int(p[1], 0)) & MASK
        elif op in ('andi', 'and', 'andn', 'or', 'nor', 'lsl', 'rotl', 'rotli'):
            a = r[p[1]] if len(p) == 3 else r[p[0]]
            b = r[p[-1]] if p[-1] in r else int(p[-1], 0)
            if op in ('and', 'andi'): result = a & b
            elif op == 'andn': result = a & ~b
            elif op == 'or': result = a | b
            elif op == 'nor': result = ~(a | b)
            elif op == 'lsl':
                if b >= 32: raise ValueError('GPIO shift range')
                result = a << b
            else:
                b &= 31
                result = (a << b) | (a >> ((32 - b) & 31))
            r[p[0]] = result & MASK
        elif op in ('ld.w', 'st.w'):
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not match: raise ValueError('GPIO memory operand')
            reg, base, offset = match.groups()
            address = (r[base] + int(offset, 0)) & MASK
            if address not in words: raise ValueError('GPIO MMIO bounds')
            if op == 'ld.w':
                r[reg] = words[address]
                trace.append(('read', address, r[reg]))
            else:
                words[address] = r[reg]
                trace.append(('write', address, r[reg]))
        elif op == 'cmpnei': condition = r[p[0]] != int(p[1], 0)
        elif op in ('bt', 'br'):
            if op == 'br' or condition: nxt = int(args, 0)
        elif op in ('bez', 'bnez'):
            if (r[p[0]] == 0) == (op == 'bez'): nxt = int(p[1], 0)
        elif op == 'rts':
            if any(r[f'r{i}'] != initial[f'r{i}'] for i in (*range(4, 12), 14, 15, 16, 17)):
                raise ValueError('GPIO leaf ABI')
            return trace, words, r['r0']
        else: raise ValueError('GPIO unknown instruction ' + op)
        pc = nxt
    raise ValueError('GPIO execution bound')


def programs():
    out = ROOT / 'build/gx8002-board'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    path = out / 'gpio-output-stock.elf'
    subprocess.run([pre+'objcopy', '-I', 'binary', '-O', 'elf32-csky-little', '-B', 'csky', str(IMAGE), str(path)], check=True)
    data = bytearray(path.read_bytes()); struct.pack_into('<I', data, 36, 0x21006009); path.write_bytes(data)
    old = decode(subprocess.check_output([pre+'objdump', '-D', '--start-address=0xf4b0', '--stop-address=0xf540', str(path)], text=True))
    return old, decode((out / 'gpio-output-candidate.disassembly.txt').read_text())


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    evidence = build()
    old, new = programs()
    cases = 0
    ports = (*range(64), 0x7fffffff, 0x80000000, MASK)
    values = (0, 1, 2, 3, 0x80000000, MASK)
    patterns = (0, MASK, 0xaaaaaaaa, 0x55555555, 0x12345678)
    for kind, offset in (('direction', 0xf4b0), ('level', 0xf514)):
        for port, value, pattern, seed in product(ports, values, patterns, (0, MASK)):
            words = {0xa0001000: pattern, 0xa0001004: pattern ^ 0x87654321, 0xa0001008: pattern ^ MASK}
            wanted = expected(kind, port, value, words)
            if execute(old, offset, port, value, words, seed) != wanted or execute(new, offset+0x101f6a74, port, value, words, seed) != wanted:
                raise ValueError('GPIO output trace mismatch')
            cases += 1
    functions = []
    for entry in evidence['functions']:
        if not entry['fits']: raise ValueError('GPIO output envelope')
        row = {k: entry[k] for k in ('symbol', 'section_name', 'compiled_bytes', 'compiled_sha256')}
        row['stock_occurrences'] = [{'symbol': entry['symbol'], 'package_offset': entry['package_offset'], 'bytes': entry['stock_envelope_bytes'], 'sha256': entry['stock_sha256'], 'region': 'image_a_xip_text'}]
        functions.append(row)
    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/gpio-output-candidate.elf', output/'gpio-output.elf')
    return {'functions': functions, 'evidence': evidence, 'cases': cases, 'source_admitted': True,
            'hardware_qualified': False, 'limits': ['Ordered separate volatile transactions, masked ports, valid/invalid enum patterns and leaf ABI. No concurrency atomicity or silicon electrical qualification.']}


if __name__ == '__main__':
    (ROOT/'docs/research/gx8002-gpio-output-verification.json').write_text(json.dumps(verify(), indent=2)+'\n')
