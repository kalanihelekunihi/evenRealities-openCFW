#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile the reviewed LDO analog-voltage assembly and require exact stock equivalence.

Companion to verify_gx8002_analog_source.py (the drivers_lib/analog/adc.o
leaves) for the drivers_lib/analog/ldo.o leaf that occupies part of the
boot-stage-2 IRAM span this tranche targets. As with gx_dcache_disable, the
pinned toolchain's C lowering of the stock mask/OR algorithm does not
reproduce the stock byte sequence, so the reviewed algorithm is pinned as
inline assembly instead of C; this script authenticates it against the
pinned SDK's ldo.o byte for byte and differentially checks its behavior
against that same authenticated stock object.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, sha, SDK_COMMIT
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_analog_ldo.c'
ADDRESS = 0xa0005054
MASK = 0xffffffff


def disassemble(objdump, path, section):
    output = subprocess.check_output([str(objdump), '-d', str(path)], text=True)
    lines, current = [], None
    for line in output.splitlines():
        if line.startswith(f'Disassembly of section {section}:'):
            current = lines
            continue
        if current is not None and re.match(r'Disassembly of section ', line):
            break
        match = re.match(r'\s*[0-9a-f]+:\s+[0-9a-f]+\s+([\w.]+)\s*(.*?)\s*$', line)
        if match and current is not None:
            current.append((match[1], match[2].split('//')[0].strip()))
    return lines


def execute(instructions, voltage, previous):
    registers = {'r0': voltage & MASK, 'r1': 0x11111111, 'r2': 0x22222222, 'r3': 0x33333333}
    memory = {ADDRESS: previous & MASK}
    trace = []
    condition = False
    for opcode, operands in instructions:
        parts = [p.strip() for p in operands.split(',')]
        if opcode == 'movi':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif opcode == 'subi':
            registers[parts[0]] = (registers[parts[0]] - int(parts[1], 0)) & MASK
        elif opcode == 'cmpne':
            condition = registers[parts[0]] != registers[parts[1]]
        elif opcode == 'bf':
            if not condition:
                return registers['r0'], trace
        elif opcode == 'lrw':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif opcode == 'ld.w':
            reg, base, offset = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', operands).groups()
            address = (registers[base] + int(offset, 0)) & MASK
            if address != ADDRESS:
                raise ValueError(f'unexpected LDO read address {address:#x}')
            registers[reg] = memory[address]
            trace.append(('read32', address, registers[reg]))
        elif opcode == 'st.w':
            reg, base, offset = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', operands).groups()
            address = (registers[base] + int(offset, 0)) & MASK
            if address != ADDRESS:
                raise ValueError(f'unexpected LDO write address {address:#x}')
            memory[address] = registers[reg]
            trace.append(('write32', address, registers[reg]))
        elif opcode == 'andi':
            registers[parts[0]] = registers[parts[1]] & int(parts[2], 0)
        elif opcode == 'or':
            registers[parts[0]] |= registers[parts[1]]
        elif opcode == 'zextb':
            registers[parts[0]] = registers[parts[1]] & 0xff
        elif opcode == 'rts':
            return registers['r0'], trace
        else:
            raise ValueError(f'unsupported LDO instruction: {opcode} {operands}')
    raise ValueError('LDO function did not return')


def verify(prefix, sdk, output):
    candidates = analyze(sdk)
    output.mkdir(parents=True, exist_ok=True)
    compiler, objdump = (prefix / f'csky-unknown-elf-{tool}' for tool in ('gcc', 'objdump'))
    obj = output / 'runtime_gx8002_analog_ldo.o'
    subprocess.run([str(compiler), *FLAGS, '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.gx_analog_set_ldo_ana_voltage')
    payload = elf.contents(section)
    matches = [m for m in candidates['matches'] if m['symbol'] == 'gx_analog_set_ldo_ana_voltage']
    if not matches or any(m['bytes'] != len(payload) or m['sha256'] != sha(payload) for m in matches):
        raise ValueError('reviewed LDO assembly no longer exactly matches authenticated stock')
    if elf.relocations(section['index']) or any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('reviewed LDO assembly gained external references')
    executable = [s for s in elf.sections if s['flags'] & 4 and s['size']]
    if executable != [section]:
        raise ValueError('unexpected additional executable sections')

    stock_object = sdk / 'drivers_lib/analog/ldo.o'
    stock = disassemble(objdump, stock_object, '.text.gx_analog_set_ldo_ana_voltage')
    compiled = disassemble(objdump, obj, '.text.gx_analog_set_ldo_ana_voltage')
    boundary = (0, 1, 15, 16, 0x0f, 0xf0, 0xff, 0x100, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff)
    cases = 0
    for voltage in boundary:
        for previous in boundary:
            before = execute(stock, voltage, previous)
            after = execute(compiled, voltage, previous)
            if before != after:
                raise ValueError(f'LDO trace mismatch for voltage={voltage:#x} previous={previous:#x}')
            cases += 1

    report = {'symbol': 'gx_analog_set_ldo_ana_voltage', 'section_name': '.text.gx_analog_set_ldo_ana_voltage',
              'ownership_kind': 'compiled_assembly',
              'sdk_commit': SDK_COMMIT, 'source_sha256': sha(SOURCE.read_bytes()),
              'compile_flags': FLAGS,
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'stock_occurrences': matches, 'differential_cases': cases,
              'firmware_bytes_emitted': 0, 'production_source_admitted': False,
              'hardware_qualified': False,
              'limits': ['Restricted leaf interpreter, not a complete C-SKY emulator.',
                         'Boundary-value differential cases, not an all-input proof.',
                         'No whole-image startup, call-site or hardware qualification.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/csky-macos/install/bin')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-analog-ldo-source')
    args = parser.parse_args()
    print(json.dumps(verify(args.prefix.resolve(), args.sdk.resolve(), args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
