#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded startup clears with an independent exact write oracle."""
import json
import re
import struct
import subprocess
from build_gx8002_clear_bss_candidate import build, ROOT, IMAGE
from verify_gx8002_memcpy_source import decode

START, END = 0x20026d80, 0x2002ecec


def execute(code, entry, seed):
    regs = {f'r{i}': (seed+i*0x1020304)&0xffffffff for i in range(32)}
    regs['r14'] = 0x2002f7fc
    original = regs.copy()
    saved = None
    trace = []
    carry = None
    pc = entry
    for _ in range(50000):
        op, args, width = code[pc]
        operands = [s.strip() for s in args.split(',')]
        next_pc = pc+width
        if op in ('lrw', 'movi'):
            regs[operands[0]] = int(operands[1], 0)
        elif op == 'push':
            if args != 'r4-r6' or saved is not None:
                raise ValueError('unexpected save')
            saved = [regs[f'r{i}'] for i in range(4, 7)]
            regs['r14'] -= 12
        elif op == 'pop':
            if args != 'r4-r6' or saved is None:
                raise ValueError('unexpected restore')
            for i, value in enumerate(saved, 4):
                regs[f'r{i}'] = value
            saved = None
            regs['r14'] += 12
        elif op == 'xor':
            regs[operands[0]] ^= regs[operands[1]]
        elif op == 'addi':
            regs[operands[0]] = (regs[operands[0]]+int(operands[1], 0))&0xffffffff
        elif op == 'cmphs':
            carry = regs[operands[0]] >= regs[operands[1]]
        elif op in ('br', 'bt', 'bf'):
            if op != 'br' and carry is None:
                raise ValueError('branch without comparison')
            if op == 'br' or carry == (op == 'bt'):
                next_pc = int(args, 0)
        elif op in ('st.w', 'stbi.w'):
            match = re.fullmatch(r'(r\d+), \((r\d+)(?:, 0x0)?\)', args)
            if match is None:
                raise ValueError('unsupported store')
            value, base = match.groups()
            address = regs[base]
            if not START <= address < END or address % 4:
                raise ValueError('write outside BSS')
            trace.append([address, regs[value]])
            if op == 'stbi.w':
                regs[base] = (address+4)&0xffffffff
        elif op == 'rts':
            if saved is not None or any(regs[f'r{i}'] != original[f'r{i}'] for i in range(4, 32)):
                raise ValueError('preserved register mismatch')
            return trace
        else:
            raise ValueError('unsupported instruction '+op)
        pc = next_pc
    raise ValueError('execution bound exceeded')


def verify():
    evidence = build()
    output = ROOT/'build/gx8002-clear-bss'
    prefix = ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper = output/'stock.elf'
    subprocess.run([str(prefix)+'objcopy', '-I', 'binary', '-O', 'elf32-csky-little',
                    '-B', 'csky', str(IMAGE), str(wrapper)], check=True)
    data = bytearray(wrapper.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    wrapper.write_bytes(data)
    old = decode(subprocess.check_output([str(prefix)+'objdump', '-D',
        '--start-address=0x1553c', '--stop-address=0x15560', str(wrapper)], text=True))
    new = decode((output/'clear.disassembly.txt').read_text())
    expected = [[address, 0] for address in range(START, END, 4)]
    for seed in (0, 1, 0xffffffff, 0x55555555, 0xaaaaaaaa, 0x80000000):
        if execute(old, 0x1553c, seed) != expected or execute(new, 0x10023528, seed) != expected:
            raise ValueError('clear trace mismatch')
    report = {'build': evidence, 'cases': 6, 'writes_per_case': len(expected),
              'first_write': expected[0], 'last_write': expected[-1],
              'source_admitted': False,
              'limits': ['Fixed shipped BSS bounds only; memory is assumed writable RAM.',
                         'Stock private stack saves modeled separately from BSS writes; candidate needs no stack.',
                         'Does not qualify reset, system_init or other startup routines.']}
    (ROOT/'docs/research/gx8002-clear-bss-comparison.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    verify()
