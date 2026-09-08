#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted stock/upstream integer formatting execution comparison."""
import json
import random
import re
import struct
import subprocess
from link_gx8002_tinyprintf_candidate import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from verify_gx8002_memcpy_source import decode


def signed(x):
    return x if x < 0x80000000 else x - 0x100000000


def execute(code, start, number, base, upper):
    r = {f'r{i}': 0x98760000 + i for i in range(32)}
    r.update(r0=number, r1=0x1000)
    memory = {0x1000+i: 0 for i in range(16)}
    memory.update({0x2000+i: 0xa5 for i in range(40)})
    memory[0x1007], memory[0x1008], memory[0x100d] = base, upper, 0x20
    pc, condition, writes = start, False, []
    for _ in range(2000):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        following = pc + width
        if op in ('ld.b', 'ld.w', 'st.b', 'stbi.b'):
            m = re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)', args)
            if not m: raise ValueError('unsupported operand')
            reg, pointer, offset = m.groups()
            address = r[pointer] + int(offset or '0', 0)
            size = 4 if op == 'ld.w' else 1
            if any(address+i not in memory for i in range(size)): raise ValueError('outside memory')
            if op.startswith('ld'):
                r[reg] = sum(memory[address+i] << (8*i) for i in range(size))
            else:
                if not 0x2000 <= address < 0x2028: raise ValueError('write outside output')
                memory[address] = r[reg] & 255
                writes.append((address, memory[address]))
                if op == 'stbi.b': r[pointer] += 1
        elif op == 'movi': r[p[0]] = int(p[1], 0)
        elif op in ('divu', 'mult', 'subu', 'addu', 'addi', 'lsli'):
            a = r[p[0] if len(p) == 2 else p[1]]
            b = int(p[-1], 0) if op in ('addi', 'lsli') else r[p[-1]]
            if op == 'divu':
                if b == 0: raise ValueError('division by zero')
                value = a // b
            elif op == 'mult': value = a * b
            elif op == 'subu': value = a - b
            elif op == 'lsli': value = a << b
            else: value = a + b
            r[p[0]] = value & 0xffffffff
        elif op == 'cmphs': condition = r[p[0]] >= r[p[1]]
        elif op == 'cmplti': condition = signed(r[p[0]]) < int(p[1], 0)
        elif op == 'cmpnei': condition = r[p[0]] != int(p[1], 0)
        elif op == 'inct':
            if condition: r[p[0]] = (r[p[1]] + int(p[2], 0)) & 0xffffffff
        elif op in ('bt', 'bf', 'br', 'bez', 'bnez', 'bhz'):
            take = {'bt': condition, 'bf': not condition, 'br': True}.get(op)
            if take is None:
                take = r[p[0]] == 0 if op == 'bez' else r[p[0]] != 0 if op == 'bnez' else signed(r[p[0]]) > 0
            if take: following = int(p[-1], 0)
        elif op == 'rts': return bytes(memory[0x2000+i] for i in range(40)), writes
        else: raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('instruction bound exceeded')


def verify():
    placement = link()
    output = ROOT / 'build/gx8002-tinyprintf'
    prefix = ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper = output / 'stock.elf'
    subprocess.run([str(prefix)+'objcopy', '-I', 'binary', '-O', 'elf32-csky-little', '-B', 'csky', str(IMAGE), str(wrapper)], check=True)
    data = bytearray(wrapper.read_bytes()); struct.pack_into('<I', data, 36, 0x21006009); wrapper.write_bytes(data)
    stock = decode(subprocess.check_output([str(prefix)+'objdump', '-D', '--start-address=0xfeac', '--stop-address=0xff24', str(wrapper)], text=True))
    source = decode(subprocess.check_output([str(prefix)+'objdump', '-d', '--section=.text.ui2a', str(output/'formatter.elf')], text=True))
    rng = random.Random(804)
    values = sorted(set(range(257)) | {0x7fffffff, 0x80000000, 0xffffffff} | {rng.randrange(2**32) for _ in range(256)})
    cases = 0
    for base, fmt in ((8, 'o'), (10, 'd'), (16, 'x')):
        for upper in (0, 1):
            for value in values:
                a = execute(stock, 0xfeac, value, base, upper)
                b = execute(source, 0x10206920, value, base, upper)
                expected = format(value, fmt)
                if upper: expected = expected.upper()
                encoded = expected.encode() + b'\0'
                oracle = (encoded + b'\xa5'*(40-len(encoded)), [(0x2000+i, x) for i, x in enumerate(encoded)])
                if a != b or a != oracle: raise ValueError('integer conversion mismatch')
                cases += 1
    report = {'placement': placement, 'cases': cases, 'exact_output_write_trace': True,
              'source_admitted': False, 'limits': ['Restricted model; ordinary parameter and output RAM only.',
              'Finite inputs for bases 8/10/16; no concurrent parameter changes or timing claim.']}
    (ROOT/'docs/research/gx8002-ui2a-comparison.json').write_text(json.dumps(report, indent=2)+'\n')
    print(cases)
    return report


if __name__ == '__main__': verify()
