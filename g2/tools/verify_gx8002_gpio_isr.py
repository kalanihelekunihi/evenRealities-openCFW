#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded GPIO snapshot/callback/acknowledgement equivalence checks."""
import json
import re
import shutil
import struct
import subprocess
from itertools import product
from build_gx8002_gpio_isr_candidate import ROOT, IMAGE, build, sha
from model_gx8002_gpio_isr import Case, Model, expected, MASK
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

OFFSET = 0xf46c
ADDRESS = 0x10205ee0


def execute(code, pc, case):
    m = Model(case)
    r = {f'r{i}': (case.seed ^ i * 0x1020304) & MASK for i in range(32)}
    r['r14'] = 0x2002f7fc
    initial = r.copy()
    saved = None
    condition = False
    for _ in range(800):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        nxt = pc + width
        if op == 'push':
            if args != 'r4-r9, r15' or saved is not None:
                raise ValueError('GPIO frame')
            saved = {f'r{i}': r[f'r{i}'] for i in (*range(4, 10), 15)}
            r['r14'] -= 28
        elif op in ('movi', 'lrw'):
            r[p[0]] = int(p[1], 0) & MASK
        elif op == 'mov':
            r[p[0]] = r[p[1]]
        elif op == 'rotli':
            value, shift = r[p[1]], int(p[2], 0)
            r[p[0]] = ((value << shift) | (value >> (32 - shift))) & MASK
        elif op in ('lsl', 'and'):
            a = r[p[1]] if len(p) == 3 else r[p[0]]
            b = r[p[-1]]
            if op == 'lsl' and b >= 32:
                raise ValueError('GPIO shift outside qualified pin range')
            r[p[0]] = (a << b if op == 'lsl' else a & b) & MASK
        elif op == 'addi':
            r[p[0]] = (r[p[0]] + int(p[1], 0)) & MASK
        elif op in ('ld.w', 'st.w'):
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not match:
                raise ValueError('GPIO memory operand')
            reg, base, off = match.groups()
            address = (r[base] + int(off, 0)) & MASK
            if op == 'ld.w':
                r[reg] = m.read(address)
            else:
                m.write(address, r[reg])
        elif op == 'bez':
            if r[p[0]] == 0:
                nxt = int(p[1], 0)
        elif op == 'cmpnei':
            condition = r[p[0]] != int(p[1], 0)
        elif op == 'bt':
            if condition:
                nxt = int(args, 0)
        elif op == 'jsr':
            if saved is None or r['r14'] != initial['r14'] - 28:
                raise ValueError('GPIO callback frame')
            result = m.callback(r[args], r['r0'], r['r1'])
            for i in (0, 1, 2, 3, 12, 13, 15, *range(18, 32)):
                r[f'r{i}'] = (case.seed ^ m.calls * 0x1234567 ^ i) & MASK
            r['r0'] = result
        elif op == 'pop':
            if saved is None or args != 'r4-r9, r15' or r['r14'] != initial['r14'] - 28:
                raise ValueError('GPIO return frame')
            r.update(saved)
            r['r14'] += 28
            if any(r[f'r{i}'] != initial[f'r{i}'] for i in (*range(4, 12), 14, 15, 16, 17)):
                raise ValueError('GPIO ABI')
            return m.trace, m.words, r['r0']
        else:
            raise ValueError('GPIO unknown instruction ' + op)
        pc = nxt
    raise ValueError('GPIO execution bound')


def programs():
    out = ROOT / 'build/gx8002-board'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    path = out / 'gpio-isr-stock.elf'
    subprocess.run([pre + 'objcopy', '-I', 'binary', '-O', 'elf32-csky-little', '-B', 'csky', str(IMAGE), str(path)], check=True)
    data = bytearray(path.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    path.write_bytes(data)
    old = decode(subprocess.check_output([pre + 'objdump', '-D', '--start-address=0xf46c', '--stop-address=0xf4b0', str(path)], text=True))
    new = decode((out / 'gpio-isr-candidate.disassembly.txt').read_text())
    return old, new


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    evidence = build()
    old, new = programs()
    patterns = (0, MASK, 0x55555555, 0xaaaaaaaa, *[1 << i for i in range(32)])
    cases = 0
    for pending, callbacks, seed, mutation in product(patterns, (0, MASK, 0x55555555, 0xaaaaaaaa), (0, MASK, 0x12345678), (False, True)):
        case = Case(pending, callbacks, seed, mutation)
        wanted = expected(case)
        if execute(old, OFFSET, case) != wanted or execute(new, ADDRESS, case) != wanted:
            raise ValueError('GPIO trace/state mismatch')
        cases += 1
    if not evidence['fits']:
        raise ValueError('GPIO envelope')
    row = {key: evidence[key] for key in ('symbol', 'section_name', 'compiled_bytes', 'compiled_sha256')}
    row['stock_occurrences'] = [{'symbol': evidence['symbol'], 'package_offset': OFFSET, 'bytes': 68, 'sha256': evidence['stock_sha256'], 'region': 'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'build/gx8002-board/gpio-isr-candidate.elf', output / 'gpio-isr.elf')
    return {'functions': [row], 'evidence': evidence, 'cases': cases,
            'model_sha256': sha((ROOT / 'tools/model_gx8002_gpio_isr.py').read_bytes()),
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Ordered pending snapshot, live callback fields, callbacks and MMIO writes, callback clobbers and 28-byte frame. Pending write-one-clear modeled, not silicon proof; callback bodies external.']}


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-gpio-isr-verification.json').write_text(json.dumps(verify(), indent=2) + '\n')
