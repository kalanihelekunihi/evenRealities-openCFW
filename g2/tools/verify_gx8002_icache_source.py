#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare the recovered external-cache controller's bounded MMIO traces."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_icache_enable.c'


def instructions(objdump, path):
    text = subprocess.check_output([str(objdump), '-dr', '-j', '.text.gx_icache_enable', str(path)], text=True)
    result = {}
    for line in text.splitlines():
        m = re.match(r'\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([\w.]+)\s*(.*?)\s*$', line)
        if m:
            result[int(m[1], 16)] = (len(m[2]) // 2, m[3], m[4].split('//')[0].strip())
    return result


def execute(code, control, statuses, limit=256):
    registers = {f'r{i}': 0x12345678+i for i in range(4)}
    pc, condition, reads, trace = 0, False, 0, []
    for _ in range(limit):
        length, op, operand = code[pc]
        next_pc = pc + length
        p = [s.strip() for s in operand.split(',')]
        if op == 'movi':
            registers[p[0]] = int(p[1], 0)
        elif op == 'lsli':
            registers[p[0]] = (registers[p[1]] << int(p[2], 0)) & 0xffffffff
        elif op in ('ori', 'andi'):
            value = registers[p[1]]
            registers[p[0]] = value | int(p[2], 0) if op == 'ori' else value & int(p[2], 0)
        elif op in ('ld.w', 'st.w'):
            m = re.fullmatch(r'(r[0-3]), \((r[0-3]), (0x[0-9a-f]+)\)', operand)
            if not m:
                raise ValueError('unsupported memory operand')
            reg, base, offset = m.groups()
            address = registers[base] + int(offset, 0)
            if address not in (0xb0000000, 0xb0000004):
                raise ValueError('unexpected cache register')
            if op == 'st.w':
                trace.append(('write32', address, registers[reg]))
            else:
                if address == 0xb0000000:
                    registers[reg] = control
                else:
                    if reads >= len(statuses):
                        return 'polling', trace
                    registers[reg] = statuses[reads]
                    reads += 1
                trace.append(('read32', address, registers[reg]))
        elif op == 'cmpnei':
            condition = registers[p[0]] != int(p[1], 0)
        elif op == 'bt':
            if condition:
                next_pc = int(p[0], 0)
        elif op == 'rts':
            return 'returned', trace
        else:
            raise ValueError(f'unsupported instruction: {op}')
        pc = next_pc
    raise ValueError('execution bound exceeded')


def verify(prefix, sdk, output):
    candidates = analyze(sdk)
    matches = [m for m in candidates['matches'] if m['symbol'] == 'gx_icache_enable']
    if not matches:
        raise ValueError('missing authenticated cache function')
    output.mkdir(parents=True, exist_ok=True)
    obj = output / 'runtime_gx8002_icache_enable.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *FLAGS, '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.gx_icache_enable')
    if any(section['size'] != m['bytes'] for m in matches) or elf.relocations(section['index']):
        raise ValueError('function size or relocation boundary changed')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unexpected external symbol')
    objdump = prefix / 'csky-unknown-elf-objdump'
    original = instructions(objdump, sdk / 'drivers_lib/cache/gx_icache.o')
    compiled = instructions(objdump, obj)
    cases = 0
    statuses = [[2], [0, 1, 3, 2], [0]*12, [0xffffffff, 0x80000002]]
    statuses += [[s, 2] for s in range(16)]
    for control in (0, 1, 2, 0xff, 0x80000000, 0xdeadbeef, 0xffffffff):
        for sequence in statuses:
            before, after = execute(original, control, sequence), execute(compiled, control, sequence)
            if before != after:
                raise ValueError('different MMIO trace or polling behavior')
            expected_prefix = [('write32', 0xb0000000, 0), ('read32', 0xb0000000, control),
                               ('write32', 0xb0000000, control | 1)]
            if after[1][:3] != expected_prefix:
                raise ValueError('controller enable sequence changed')
            cases += 1
    report = {'source_sha256': sha(SOURCE.read_bytes()), 'compile_flags': FLAGS,
              'compiled_bytes': section['size'], 'compiled_sha256': sha(elf.contents(section)),
              'stock_occurrences': matches, 'matching_trace_cases': cases,
              'firmware_bytes_emitted': 0, 'production_source_admitted': False,
              'hardware_qualified': False,
              'limits': ['Restricted bounded interpreter; no hardware model.',
                         'Original unbounded wait is preserved, not repaired.',
                         'Whole-image integration remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/csky-macos/install/bin')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-icache-source')
    args = parser.parse_args()
    print(json.dumps(verify(args.prefix.resolve(), args.sdk.resolve(), args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
