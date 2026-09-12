#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for UART boot stage-1 div/mod/noop leaves.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_divmod.c against the
stock stage-1 bodies by executing decoded C-SKY instructions for both across
a battery of dividends/divisors, plus an independent arithmetic oracle.
Behavioral equivalence only: register allocation and instruction choice may
differ; only r0 (result), callee-saved registers, stack use (none), and
memory traffic (none) are compared. The condition flag and scratch
registers r1-r3 are caller-clobbered scratch across the internal bsr
boundary and are explicitly not compared.
"""
import json
import random
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_divmod.c'
DIVMOD_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize']

# (symbol, package offset, stock envelope bytes, is_mod).
# The stock-analysis wrapper maps file offsets to identical VMAs, so decoded
# stock execution uses package offsets; runtime entries (udiv 0x1000013c,
# umod 0x10000180, stub 0x10000138) are documented in the audit and C header.
SPECS = [
    ('open_cfw_gx8002_uart_stage1_udiv', 0x18c, 66, False),
    ('open_cfw_gx8002_uart_stage1_umod', 0x1d0, 58, True),
]
STUB = ('open_cfw_gx8002_uart_stage1_clear_bss', 0x188, 4)
MASK = 0xffffffff


def signed(value):
    return value if value < 0x80000000 else value - 0x100000000


def execute(code, start, num, den):
    """Run decoded code with r0=num, r1=den; return (r0, preserved, accesses)."""
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=num, r1=den)
    saved = dict(registers)
    pc, condition, accesses = start, False, []
    for _ in range(500):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        if op == 'cmphs':
            condition = registers[parts[0]] >= registers[parts[1]]
        elif op == 'bt':
            if condition:
                following = int(parts[0], 0)
        elif op == 'bf':
            if not condition:
                following = int(parts[0], 0)
        elif op == 'blz':
            if signed(registers[parts[0]]) < 0:
                following = int(parts[1], 0)
        elif op == 'bez':
            if registers[parts[0]] == 0:
                following = int(parts[1], 0)
        elif op == 'bnez':
            if registers[parts[0]] != 0:
                following = int(parts[1], 0)
        elif op == 'br':
            following = int(parts[0], 0)
        elif op == 'movi':
            registers[parts[0]] = int(parts[1], 0)
        elif op == 'mov':
            registers[parts[0]] = registers[parts[1]]
        elif op in ('addu', 'subu'):
            left = registers[parts[0] if len(parts) == 2 else parts[1]]
            right = registers[parts[-1]]
            registers[parts[0]] = (left + (right if op == 'addu' else -right)) & MASK
        elif op in ('addi', 'subi'):
            base = parts[0] if len(parts) == 2 else parts[1]
            delta = int(parts[-1], 0) * (1 if op == 'addi' else -1)
            registers[parts[0]] = (registers[base] + delta) & MASK
        elif op == 'or':
            if len(parts) == 2:
                registers[parts[0]] = registers[parts[0]] | registers[parts[1]]
            else:
                registers[parts[0]] = registers[parts[1]] | registers[parts[2]]
        elif op == 'lsri':
            registers[parts[0]] = registers[parts[1]] >> int(parts[2], 0)
        elif op == 'inct':
            if condition:
                registers[parts[0]] = (registers[parts[1]] + int(parts[2], 0)) & MASK
        elif op == 'rts':
            preserved = all(registers[r] == saved[r]
                            for r in ('r4', 'r5', 'r6', 'r7', 'r14', 'r15'))
            return registers['r0'], preserved, accesses
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def oracle(num, den, is_mod):
    if den == 0:
        if is_mod:
            return num
        return 1 if num == 0 else 0
    if is_mod:
        return num % den
    return num // den


def battery_cases():
    edges = [0, 1, 2, 3, 0x7ffffffe, 0x7fffffff, 0x80000000, 0x80000001,
             0xfffffffe, 0xffffffff]
    cases = set()
    for num in range(65):
        for den in range(65):
            cases.add((num, den))
    for num in edges:
        for den in edges:
            cases.add((num, den))
    powers = []
    for shift in range(32):
        for value in (2 ** shift - 1, 2 ** shift, 2 ** shift + 1):
            powers.append(value & MASK)
    anchors = [0, 1, 2, 3, 5, 7, 16, 100, 1000, 0xffffffff, 0x80000000, 0x7fffffff]
    for power in powers:
        for anchor in anchors:
            cases.add((power, anchor))
            cases.add((anchor, power))
    rng = random.Random(0xc001)
    for _ in range(2048):
        cases.add((rng.randrange(2 ** 32), rng.randrange(2 ** 32)))
    for num in (0, 1, 2, 0x80000000, 0xffffffff):
        cases.add((num, 0))
    return sorted(cases)


def split_sections(disassembly):
    sections, current = {}, None
    for line in disassembly.splitlines():
        header = re.match(r'Disassembly of section (\S+):', line)
        if header:
            current = header.group(1)
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {name: decode('\n'.join(lines)) for name, lines in sections.items()}


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-divmod'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    obj = output / 'divmod.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *DIVMOD_FLAGS,
                    '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    # Analysis-only ELF wrapper: no stock bytes enter the compiled source object.
    wrapper = output / 'stock-analysis.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-objcopy'), '-I', 'binary',
                    '-O', 'elf32-csky-little', '-B', 'csky', str(IMAGE), str(wrapper)], check=True)
    data = bytearray(wrapper.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    wrapper.write_bytes(data)
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(obj)], text=True)
    sources = split_sections(disassembly)
    functions = []
    cases = 0
    for symbol, offset, size, _ in SPECS:
        entry = offset
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) > size or offset % section['align']:
            raise ValueError('candidate does not fit original placement')
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation')
        stock_code = decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=%#x' % entry, '--stop-address=%#x' % (entry + size),
             str(wrapper)], text=True))
        source_code = sources[section_name]
        is_mod = symbol.endswith('_umod')
        for num, den in battery_cases():
            expected = oracle(num, den, is_mod)
            stock_result, stock_ok, stock_accesses = execute(stock_code, entry, num, den)
            source_result, source_ok, source_accesses = execute(source_code, 0, num, den)
            if stock_result != expected or source_result != expected:
                raise ValueError('result/oracle mismatch at %#x %#x' % (num, den))
            if stock_result != source_result or not stock_ok or not source_ok:
                raise ValueError('stock/source result mismatch at %#x %#x' % (num, den))
            if stock_accesses or source_accesses:
                raise ValueError('unexpected memory traffic')
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    symbol, offset, size = STUB
    entry = offset
    section_name = '.text.' + symbol
    section = next(s for s in elf.sections if s['name'] == section_name)
    payload = elf.contents(section)
    if len(payload) > size or offset % section['align']:
        raise ValueError('stub does not fit original placement')
    if elf.relocations(section['index']):
        raise ValueError('unexpected relocation')
    stock_code = decode(subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-D',
         '--start-address=%#x' % entry, '--stop-address=%#x' % (entry + size),
         str(wrapper)], text=True))
    source_code = sources[section_name]
    for num, den in ((0, 0), (1, 2), (0xffffffff, 0x80000000), (0x12345678, 0x9abcdef0)):
        stock_result, stock_ok, stock_accesses = execute(stock_code, entry, num, den)
        source_result, source_ok, source_accesses = execute(source_code, 0, num, den)
        if (stock_result, stock_ok, stock_accesses) != (num, True, []):
            raise ValueError('stock stub is not a bare return')
        if (source_result, source_ok, source_accesses) != (num, True, []):
            raise ValueError('source stub is not a bare return')
        cases += 1
    functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                      'compiled_sha256': sha(payload),
                      'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                             'bytes': size,
                                             'sha256': sha(stock[offset:offset + size]),
                                             'region': 'uart_boot_stage1'}]})
    report = {'source_sha256': sha(SOURCE.read_bytes()), 'compile_flags': DIVMOD_FLAGS,
              'sdk_commit': '8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5',
              'algorithm_reference': 'arch/soc/grus/spl/spl.c uint32_divmodsi4 '
                                     '(clean-room reimplementation; no SDK text reproduced)',
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 leaves only',
              'stock_equivalence_proven': False,
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Return-value equivalence over finite battery plus independent oracle; '
                         'scratch registers and condition flag are caller-clobbered and not compared.',
                         'Same-entry placement fits; hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
