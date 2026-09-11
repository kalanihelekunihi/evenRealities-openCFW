#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-execution comparison for the GX8002 stage-2 libc leaf candidates.

Both the stock boot-stage-2 bytes and the compiled candidate are decoded and
symbolically executed by the same restricted interpreter; each result is also
checked against an independently computed Python oracle. strcmp only needs to
match on sign/zero (the documented C contract), not the stock's exact -1/0/1
encoding. This is a leaf-instruction interpreter, not a C-SKY system emulator
or hardware qualification.
"""
import json
import random
import re
import subprocess
import struct
from pathlib import Path

from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_gx8002_stage2_libc_candidate import build, STOCK_OCCURRENCES
from verify_gx8002_memcpy_source import decode

ROOT = Path(__file__).resolve().parents[1]
MASK = 0xffffffff


def _sign(n):
    n &= MASK
    if n & 0x80000000:
        n -= 1 << 32
    return (n > 0) - (n < 0)


def execute(code, entry, registers, memory, limit=20000):
    r = dict(registers)
    pc = entry
    condition = False
    for _ in range(limit):
        op, args, width = code[pc]
        parts = [p.strip() for p in args.split(',')] if args else []
        nxt = pc + width
        if op == 'mov':
            r[parts[0]] = r[parts[1]]
        elif op == 'movi':
            r[parts[0]] = int(parts[1], 0) & MASK
        elif op in ('addi', 'subi'):
            if len(parts) == 2:
                a, b = r[parts[0]], int(parts[1], 0)
            else:
                a, b = r[parts[1]], int(parts[2], 0)
            r[parts[0]] = (a + b if op == 'addi' else a - b) & MASK
        elif op in ('addu', 'subu'):
            if len(parts) == 2:
                a, b = r[parts[0]], r[parts[1]]
            else:
                a, b = r[parts[1]], r[parts[2]]
            r[parts[0]] = (a + b if op == 'addu' else a - b) & MASK
        elif op == 'zextb':
            r[parts[0]] = r[parts[1]] & 0xff
        elif op == 'lrw':
            r[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'andi':
            r[parts[0]] = r[parts[1]] & int(parts[2], 0) if len(parts) == 3 else r[parts[0]] & int(parts[1], 0)
        elif op == 'and':
            if len(parts) == 2:
                r[parts[0]] &= r[parts[1]]
            else:
                r[parts[0]] = r[parts[1]] & r[parts[2]]
        elif op == 'andn':
            r[parts[0]] = r[parts[1]] & ~r[parts[2]] & MASK
        elif op == 'or':
            if len(parts) == 2:
                r[parts[0]] |= r[parts[1]]
            else:
                r[parts[0]] = r[parts[1]] | r[parts[2]]
        elif op == 'cmpne':
            condition = r[parts[0]] != r[parts[1]]
        elif op == 'cmphs':
            condition = r[parts[0]] >= r[parts[1]]
        elif op in ('bt', 'bf'):
            if condition == (op == 'bt'):
                nxt = int(args, 0)
        elif op == 'br':
            nxt = int(args, 0)
        elif op in ('bez', 'bnez'):
            if (r[parts[0]] == 0) == (op == 'bez'):
                nxt = int(parts[1], 0)
        elif op == 'bnezad':
            r[parts[0]] = (r[parts[0]] - 1) & MASK
            if r[parts[0]] != 0:
                nxt = int(parts[1], 0)
        elif op in ('inct', 'incf'):
            if condition == (op == 'inct'):
                r[parts[0]] = (r[parts[1]] + int(parts[2], 0)) & MASK
        elif op in ('ld.b', 'ld.w'):
            m = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args)
            if not m:
                raise ValueError('stage2 libc load operand ' + args)
            reg, base, offset = m.groups()
            address = (r[base] + int(offset, 0)) & MASK
            if op == 'ld.b':
                r[reg] = memory.get(address, 0)
            else:
                r[reg] = int.from_bytes(bytes(memory.get(address + i, 0) for i in range(4)), 'little')
        elif op == 'ldbi.b':
            m = re.fullmatch(r'(r\d+), \((r\d+)\)', args)
            if not m:
                raise ValueError('stage2 libc post-increment load operand ' + args)
            reg, base = m.groups()
            address = r[base] & MASK
            r[reg] = memory.get(address, 0)
            r[base] = (r[base] + 1) & MASK
        elif op == 'rts':
            return r['r0']
        else:
            raise ValueError('unhandled stage2 libc instruction ' + op)
        pc = nxt
    raise ValueError('stage2 libc execution bound exceeded')


def load_buffer(memory, base, data):
    for i, byte in enumerate(data):
        memory[(base + i) & MASK] = byte


def stock_program(prefix):
    out = ROOT / 'build/gx8002-stage2-libc'
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'stage2-libc-stock.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-objcopy'), '-I', 'binary',
                     '-O', 'elf32-csky-little', '-B', 'csky', str(IMAGE), str(path)], check=True)
    data = bytearray(path.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    path.write_bytes(data)
    code = {}
    for symbol, occurrence in STOCK_OCCURRENCES.items():
        start, end = occurrence['package_offset'], occurrence['package_offset'] + occurrence['bytes']
        text = subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             f'--start-address={start:#x}', f'--stop-address={end:#x}', str(path)], text=True)
        code.update(decode(text))
    return code


def decode_sections(text):
    """Split a whole-object disassembly into one decode()-style dict per
    .text.<symbol> section; every section restarts its own instructions at
    relative address 0, so per-function dicts (not one merged dict) are
    required or same-address entries from different functions collide."""
    sections = {}
    current = None
    for line in text.splitlines():
        heading = re.match(r'Disassembly of section \.text\.(\w+):$', line)
        if heading:
            current = heading[1]
            sections[current] = []
            continue
        if current is None:
            continue
        match = re.match(r'\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([\w.]+)\s*(.*?)\s*$', line)
        if match:
            address, encoding, op, operand = match.groups()
            sections[current].append((int(address, 16), op, operand.split('//')[0].strip(), len(encoding) // 2))
    return {name: {address: (op, args, width) for address, op, args, width in rows}
            for name, rows in sections.items()}


def candidate_program(evidence):
    text = (ROOT / 'build/gx8002-stage2-libc' / (evidence['functions'][0]['symbol'] + '.disassembly.txt')).read_text()
    return decode_sections(text)


def base_registers():
    return {f'r{i}': 0x91230000 + i for i in range(32)}


def run_strcmp(code, entry, a_bytes, a_base, b_bytes, b_base):
    memory = {}
    load_buffer(memory, a_base, a_bytes)
    load_buffer(memory, b_base, b_bytes)
    r = base_registers()
    r['r0'], r['r1'] = a_base, b_base
    return execute(code, entry, r, memory)


def run_strchr(code, entry, s_bytes, base, target):
    memory = {}
    load_buffer(memory, base, s_bytes)
    r = base_registers()
    r['r0'], r['r1'] = base, target
    return execute(code, entry, r, memory)


def run_strlen(code, entry, s_bytes, base):
    memory = {}
    load_buffer(memory, base, s_bytes)
    r = base_registers()
    r['r0'] = base
    return execute(code, entry, r, memory)


def run_strnlen(code, entry, s_bytes, base, maxlen):
    memory = {}
    load_buffer(memory, base, s_bytes)
    r = base_registers()
    r['r0'], r['r1'] = base, maxlen
    return execute(code, entry, r, memory)


def expected_strcmp(a, b):
    ia = a.find(b'\0')
    ib = b.find(b'\0')
    la = a[:ia] if ia >= 0 else a
    lb = b[:ib] if ib >= 0 else b
    for x, y in zip(la, lb):
        if x != y:
            return (x > y) - (x < y)
    return (len(la) > len(lb)) - (len(la) < len(lb))


def expected_strchr(s, target, base):
    i = s.find(b'\0')
    scope = s[:i + 1] if i >= 0 else s + b'\0'
    for offset, byte in enumerate(scope):
        if byte == (target & 0xff):
            return (base + offset) & MASK
        if byte == 0:
            return 0
    raise ValueError('strchr oracle scan overran buffer')


def expected_strlen(s):
    i = s.find(b'\0')
    if i < 0:
        raise ValueError('strlen oracle requires a terminator')
    return i


def expected_strnlen(s, maxlen):
    i = s.find(b'\0')
    if i < 0 or i > maxlen:
        return maxlen
    return i


def verify(prefix=None, sdk=None, output=None):
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    evidence = build(prefix=prefix)
    stock = stock_program(prefix)
    candidate = candidate_program(evidence)
    entries = {row['symbol']: (STOCK_OCCURRENCES[row['symbol']]['package_offset'], 0)
               for row in evidence['functions']}

    rng = random.Random(0xcd005)
    alphabets = [bytes(range(1, 6)), b'ab', bytes([1, 255, 2, 254]), b'x']

    def random_string(min_len=0, max_len=12):
        length = rng.randint(min_len, max_len)
        alphabet = rng.choice(alphabets)
        return bytes(rng.choice(alphabet) for _ in range(length)) + b'\0'

    cases = {'strcmp': 0, 'strchr': 0, 'strlen': 0, 'strnlen': 0}

    strcmp_pairs = [(b'\0', b'\0'), (b'a\0', b'a\0'), (b'a\0', b'b\0'), (b'ab\0', b'a\0'),
                     (b'a\0', b'ab\0'), (bytes([1, 2, 3, 0]), bytes([1, 2, 3, 0])),
                     (bytes([0xff, 0]), bytes([0x01, 0])), (bytes([0x01, 0]), bytes([0xff, 0]))]
    for _ in range(200):
        strcmp_pairs.append((random_string(), random_string()))
    for a, b in strcmp_pairs:
        for a_base, b_base in ((0x20010000, 0x20020000), (0x20010001, 0x20020003)):
            want = expected_strcmp(a, b)
            stock_r = run_strcmp(stock, entries['open_cfw_gx8002_stage2_strcmp'][0], a, a_base, b, b_base)
            cand_r = run_strcmp(candidate['open_cfw_gx8002_stage2_strcmp'], 0, a, a_base, b, b_base)
            if _sign(stock_r) != want or _sign(cand_r) != want:
                raise ValueError(('stage2 strcmp mismatch', a, b, stock_r, cand_r, want))
            cases['strcmp'] += 1

    strchr_strings = [b'\0', b'a\0', bytes([1, 2, 3, 0]), bytes([0, 0]), bytes([5, 5, 5, 0])]
    for _ in range(200):
        strchr_strings.append(random_string())
    targets = [0, 1, 2, 3, 5, 255, 256, -1]
    for s in strchr_strings:
        for target in targets:
            for base in (0x20030000, 0x20030001, 0x20030002, 0x20030003):
                want = expected_strchr(s, target, base)
                stock_r = run_strchr(stock, entries['open_cfw_gx8002_stage2_strchr'][0], s, base, target)
                cand_r = run_strchr(candidate['open_cfw_gx8002_stage2_strchr'], 0, s, base, target)
                if (stock_r & MASK) != want or (cand_r & MASK) != want:
                    raise ValueError(('stage2 strchr mismatch', s, target, base, stock_r, cand_r, want))
                cases['strchr'] += 1

    strlen_strings = [b'\0', b'a\0', bytes(range(1, 33)) + b'\0']
    for _ in range(200):
        strlen_strings.append(random_string(0, 20))
    for s in strlen_strings:
        for base in (0x20040000, 0x20040001, 0x20040002, 0x20040003):
            want = expected_strlen(s)
            stock_r = run_strlen(stock, entries['open_cfw_gx8002_stage2_strlen'][0], s, base)
            cand_r = run_strlen(candidate['open_cfw_gx8002_stage2_strlen'], 0, s, base)
            if stock_r != want or cand_r != want:
                raise ValueError(('stage2 strlen mismatch', s, base, stock_r, cand_r, want))
            cases['strlen'] += 1

    strnlen_strings = [b'\0', b'a\0', bytes(range(1, 9)) + b'\0']
    for _ in range(150):
        strnlen_strings.append(random_string(0, 16))
    for s in strnlen_strings:
        for maxlen in (0, 1, 2, 3, 4, 7, 8, len(s), len(s) + 5, 255):
            for base in (0x20050000, 0x20050001, 0x20050002, 0x20050003):
                want = expected_strnlen(s, maxlen)
                stock_r = run_strnlen(stock, entries['open_cfw_gx8002_stage2_strnlen'][0], s, base, maxlen)
                cand_r = run_strnlen(candidate['open_cfw_gx8002_stage2_strnlen'], 0, s, base, maxlen)
                if stock_r != want or cand_r != want:
                    raise ValueError(('stage2 strnlen mismatch', s, maxlen, base, stock_r, cand_r, want))
                cases['strnlen'] += 1

    if sha(IMAGE.read_bytes()) != IMAGE_SHA:
        raise ValueError('codec package changed underneath the stage2 libc comparison')

    if output:
        output.mkdir(parents=True, exist_ok=True)
        (output / 'stage2_libc.o').write_bytes(Path(evidence['object']).read_bytes())

    return {'functions': evidence['functions'], 'cases': cases, 'total_cases': sum(cases.values()),
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Decoded leaf-instruction execution against synthetic buffers at several base '
                       'alignments; boundary, embedded-0xff/0x00, and random strings up to 20 bytes. '
                       'strcmp is checked for sign/zero agreement with the documented C contract, not '
                       'the stock -1/0/1 encoding. No hardware, MMIO, or timing qualification, and no '
                       'claim about any other occurrence of these symbols in the codec image.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-stage2-libc-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Stage2 libc cases:', report['total_cases'])
