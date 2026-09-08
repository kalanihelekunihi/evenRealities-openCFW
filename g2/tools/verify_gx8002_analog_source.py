#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile recovered codec C on macOS and compare decoded MMIO traces.

This is a restricted leaf-instruction interpreter, not a C-SKY system emulator
or hardware qualification. Unsupported instructions fail closed. SDK objects
are authenticated comparison inputs only; they are never linked into outputs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import re
import struct
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, SDK_COMMIT
from build_transparent_image import Elf32

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_analog.c'
HEADER = SOURCE.with_suffix('.h')
FLAGS = ['-O2', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin',
         '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def disassemble(objdump, path):
    output = subprocess.check_output([str(objdump), '-dr', str(path)], text=True)
    functions, current = {}, None
    for line in output.splitlines():
        heading = re.match(r'Disassembly of section \.text\.(\w+):$', line)
        if heading:
            current = []
            functions[heading[1]] = current
        match = re.match(r'\s*[0-9a-f]+:\s+[0-9a-f]+\s+([\w.]+)\s*(.*?)\s*$', line)
        if match and current is not None:
            current.append((match[1], match[2].split('//')[0].strip()))
    return functions, output


def execute(instructions, value, previous):
    registers = {f'r{i}': (value if i == 0 else 0x87654321 + i) for i in range(4)}
    memory, trace = {}, []
    for opcode, operands in instructions:
        parts = [p.strip() for p in operands.split(',')]
        if opcode in ('lrw', 'movi'):
            registers[parts[0]] = int(parts[1], 0)
        elif opcode in ('ld.w', 'st.w'):
            match = re.fullmatch(r'(r[0-3]), \((r[0-3]), (0x[0-9a-f]+)\)', operands)
            if not match:
                raise ValueError(f'unsupported MMIO operand: {operands}')
            register, base, offset = match.groups()
            address = (registers[base] + int(offset, 0)) & 0xffffffff
            if address not in (0xa0005088, 0xa0005090, 0xa0005094):
                raise ValueError(f'out-of-scope register address: {address:#x}')
            if opcode == 'ld.w':
                registers[register] = memory.get(address, previous)
                trace.append(('read32', address, registers[register]))
            else:
                memory[address] = registers[register]
                trace.append(('write32', address, registers[register]))
        elif opcode == 'min.u32':
            registers[parts[0]] = min(registers[parts[1]], registers[parts[2]])
        elif opcode in ('andi', 'andni'):
            mask = int(parts[2], 0)
            registers[parts[0]] = registers[parts[1]] & (mask if opcode == 'andi' else ~mask)
        elif opcode == 'or':
            if len(parts) != 2:
                raise ValueError('unexpected OR operand count')
            registers[parts[0]] |= registers[parts[1]]
        elif opcode == 'lsli':
            registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & 0xffffffff
        elif opcode == 'zextb':
            registers[parts[0]] = registers[parts[1]] & 0xff
        elif opcode == 'rts':
            return registers['r0'], trace
        else:
            raise ValueError(f'unsupported executable instruction: {opcode} {operands}')
    raise ValueError('function did not return')


def verify(prefix, sdk, output):
    candidates = analyze(sdk)  # Authenticates stock, ledger, SDK revision and blobs.
    output.mkdir(parents=True, exist_ok=True)
    compiler, objdump = (prefix / f'csky-unknown-elf-{tool}' for tool in ('gcc', 'objdump'))
    target = subprocess.check_output([str(compiler), '-dumpmachine'], text=True).strip()
    if target != 'csky-unknown-elf':
        raise ValueError('unexpected target compiler')
    obj = output / 'runtime_gx8002_analog.o'
    subprocess.run([str(compiler), *FLAGS, '-c', str(SOURCE), '-o', str(obj)], check=True)
    data = obj.read_bytes()
    if struct.unpack_from('<H', data, 18)[0] != 252 or struct.unpack_from('<I', data, 36)[0] != 0x21006009:
        raise ValueError('compiled C-SKY machine or ABI flags changed')
    elf = Elf32(data, str(obj))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('recovered leaves gained undefined symbols')
    original, original_text = disassemble(objdump, sdk / 'drivers_lib/analog/adc.o')
    compiled, compiled_text = disassemble(objdump, obj)
    selected = [m for m in candidates['matches'] if m['object'] == 'drivers_lib/analog/adc.o']
    names = {m['symbol'] for m in selected}
    if set(compiled) != names or len(names) != 7:
        raise ValueError('recovered function inventory differs from reviewed seven leaves')
    rng = random.Random(0x8002)
    boundary = (0, 1, 2, 3, 31, 63, 64, 127, 255, 256, 0x7fffffff, 0x80000000, 0xffffffff)
    pairs = [(value, old) for value in boundary for old in boundary]
    pairs += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(4096)]
    results = []
    for name in sorted(names):
        section = next(s for s in elf.sections if s['name'] == '.text.' + name)
        if elf.relocations(section['index']):
            raise ValueError(f'{name} gained relocations')
        matches = [m for m in selected if m['symbol'] == name]
        if any(section['size'] != m['bytes'] for m in matches):
            raise ValueError(f'{name} no longer fits its complete stock section')
        for value, old in pairs:
            before = execute(original[name], value, old)
            after = execute(compiled[name], value, old)
            if before != after:
                raise ValueError(f'{name}: differing return/MMIO trace for {(value, old)}')
            if after[0] != 0 or [t[0] for t in after[1]] != ['read32', 'write32']:
                raise ValueError(f'{name}: unexpected MMIO access sequence')
        results.append({'symbol': name, 'compiled_bytes': section['size'],
                        'compiled_sha256': sha(elf.contents(section)),
                        'stock_occurrences': matches, 'matching_cases': len(pairs)})
    report = {'schema_version': 1, 'sdk_commit': SDK_COMMIT,
              'source_sha256': sha(SOURCE.read_bytes()), 'header_sha256': sha(HEADER.read_bytes()),
              'compiler_version': subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0],
              'target': target, 'elf_flags': '0x21006009', 'compile_flags': FLAGS,
              'functions': results, 'compiled_function_bytes': sum(r['compiled_bytes'] for r in results),
              'stock_occurrence_bytes': sum(m['bytes'] for m in selected),
              'differential_cases': len(pairs) * len(results),
              'firmware_bytes_emitted': 0, 'production_source_admitted': False,
              'hardware_qualified': False,
              'limits': ['Restricted instruction interpreter, not a complete C-SKY emulator.',
                         'Finite differential cases, not an all-input proof.',
                         'No whole-image startup, call-site, interrupt or hardware qualification.']}
    (output / 'stock-adc-disassembly.txt').write_text(original_text)
    (output / 'compiled-analog-disassembly.txt').write_text(compiled_text)
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/csky-macos/install/bin')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-analog-source')
    args = parser.parse_args()
    print(json.dumps(verify(args.prefix.resolve(), args.sdk.resolve(), args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
