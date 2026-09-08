#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted port-wrapper comparison with a caller-clobbering transmit model."""
import json
import subprocess
from compare_gx8002_uart_transmit import verify as verify_transmit
from link_gx8002_uart_console import ROOT
from verify_gx8002_memcpy_source import decode


def register_list(operand):
    result = []
    for part in operand.split(', '):
        if '-' in part:
            a, b = part.split('-')
            result.extend(f'r{i}' for i in range(int(a[1:]), int(b[1:]) + 1))
        else:
            result.append(part)
    return result


def execute(code, start, target, port, character):
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=port & 0xffffffff, r1=character & 0xffffffff)
    initial = registers.copy()
    pc, condition, saved, calls = start, False, None, []
    for _ in range(100):
        op, args, width = code[pc]
        parts = [p.strip() for p in args.split(',')]
        following = pc + width
        if op == 'push':
            if saved is not None:
                raise ValueError('nested save unsupported')
            saved = {r: registers[r] for r in register_list(args)}
        elif op == 'pop':
            if saved is None or set(register_list(args)) != set(saved):
                raise ValueError('unbalanced save')
            registers.update(saved)
            if any(registers[f'r{i}'] != initial[f'r{i}'] for i in range(4, 12)):
                raise ValueError('callee-saved register changed')
            return calls
        elif op == 'cmpnei':
            condition = registers[parts[0]] != int(parts[1], 0)
        elif op == 'bt':
            if condition:
                following = int(parts[0], 0)
        elif op in ('lrw', 'movi'):
            registers[parts[0]] = int(parts[1], 0)
        elif op in ('mov', 'zextb'):
            registers[parts[0]] = registers[parts[1]] & (255 if op == 'zextb' else 0xffffffff)
        elif op in ('lsli', 'addu'):
            left = registers[parts[0] if len(parts) == 2 else parts[1]]
            right = int(parts[-1], 0) if op == 'lsli' else registers[parts[-1]]
            registers[parts[0]] = ((left << right) if op == 'lsli' else left + right) & 0xffffffff
        elif op == 'bsr':
            if int(parts[0], 0) != target:
                raise ValueError('unexpected transmit target')
            calls.append((registers['r0'], registers['r1']))
            # Depend only on ABI-preserved registers across the call.
            for i in (0, 1, 2, 3, 12, 13, 15):
                registers[f'r{i}'] = 0xdead0000 + i
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def verify(prefix=None, sdk=None, output=None):
    transmit = verify_transmit(prefix, sdk, output)
    output = output or ROOT / 'build/gx8002-uart-console'
    objdump = (prefix or ROOT / 'build/csky-macos/install/bin') / 'csky-unknown-elf-objdump'
    stock = decode(subprocess.check_output([str(objdump), '-D', '--start-address=0xcb40',
                   '--stop-address=0xcb64', str(output / 'stock.elf')], text=True))
    candidate = decode(subprocess.check_output([str(objdump), '-d',
                       '--section=.text.open_cfw_gx8002_uart_putc',
                       str(output / 'console.elf')], text=True))
    cases = 0
    for port in (0, 1, 2, 3, -1, 0x1ffffff, 0x2000000, 0x7fffffff):
        for character in (*range(-256, 512), -2147483648, 2147483647):
            descriptor = (0x20026a94 + ((port & 0xffffffff) << 7)) & 0xffffffff
            expected = ([(descriptor, 13)] if character == 10 else []) + [(descriptor, character & 255)]
            a = execute(stock, 0xcb40, 0xc7d8, port, character)
            b = execute(candidate, 0x102035b4, 0x1020324c, port, character)
            if a != b or a != expected:
                raise ValueError('stock/source port-wrapper mismatch')
            cases += 1
    report = {'transmit': transmit, 'port_wrapper_cases': cases,
              'exact_transmit_call_comparison': True, 'source_admitted': False,
              'hardware_qualified': False,
              'limits': ['Restricted instruction model; transmit calls modeled using the ABI.',
                         'Out-of-range ports test address arithmetic only, not valid hardware access.',
                         'Firmware ownership integration remains pending.']}
    (ROOT / 'docs/research/gx8002-uart-putc-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
