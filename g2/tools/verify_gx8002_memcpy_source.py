#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Restricted target execution check for the source RAM-copy candidate.

Compares ordinary RAM results with decoded stock paths; not timing or placement.
"""
import json
import re
import subprocess
import struct
from pathlib import Path
from verify_gx8002_analog_source import FLAGS, sha
from build_transparent_image import Elf32

ROOT = Path(__file__).resolve().parents[1]
COPY_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize']


def execute(code, memory, destination, source, count, start=0, accesses=None):
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=destination, r1=source, r2=count)
    pc = start
    saved = []
    condition = False
    trace = []
    for _ in range(count * 10 + 20):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')]
        following = pc + width
        if op in ('bez', 'bnezad', 'bnez'):
            register = parts[0]
            if op == 'bnezad':
                registers[register] = (registers[register] - 1) & 0xffffffff
            take = registers[register] == 0 if op == 'bez' else registers[register] != 0
            if take:
                following = int(parts[1], 0)
        elif op == 'push':
            if operand != 'r4':
                raise ValueError('unsupported stack save')
            saved.append(registers['r4'])
        elif op == 'pop':
            if operand != 'r4' or len(saved) != 1:
                raise ValueError('unsupported stack restore')
            registers['r4'] = saved.pop()
            return registers['r0'], trace
        elif op in ('cmplti', 'cmphsi'):
            condition = registers[parts[0]] < int(parts[1], 0)
            if op == 'cmphsi':
                condition = not condition
        elif op == 'cmphs':
            condition = registers[parts[0]] >= registers[parts[1]]
        elif op == 'movi':
            registers[parts[0]] = int(parts[1], 0)
        elif op == 'zextb':
            registers[parts[0]] = registers[parts[1]] & 255
        elif op == 'lsri':
            registers[parts[0]] = registers[parts[1]] >> int(parts[2], 0)
        elif op in ('addu', 'subu'):
            left = registers[parts[0] if len(parts) == 2 else parts[1]]
            right = registers[parts[-1]]
            registers[parts[0]] = (left + (right if op == 'addu' else -right)) & 0xffffffff
        elif op in ('bt', 'bf', 'br'):
            if op == 'br' or (condition if op == 'bt' else not condition):
                following = int(parts[0], 0)
        elif op == 'or':
            registers[parts[0]] = registers[parts[1]] | registers[parts[2]]
        elif op in ('andi', 'andni'):
            mask = int(parts[2], 0)
            registers[parts[0]] = registers[parts[1]] & (mask if op == 'andi' else ~mask)
        elif op == 'mov':
            registers[parts[0]] = registers[parts[1]]
        elif op in ('addi', 'subi'):
            target = parts[0]
            base = target if len(parts) == 2 else parts[1]
            delta = int(parts[-1], 0) * (1 if op == 'addi' else -1)
            registers[target] = (registers[base] + delta) & 0xffffffff
        elif op in ('ld.b', 'stbi.b', 'st.b', 'ld.w', 'st.w', 'ldbi.b', 'ldbi.w', 'stbi.w'):
            match = re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)', operand)
            if not match:
                raise ValueError('unsupported memory operand: ' + operand)
            value, base, offset = match.groups()
            address = registers[base] + int(offset or '0', 0)
            access_size = 4 if op.endswith('.w') else 1
            if accesses is not None:
                accesses.append(('read' if op.startswith(('ld.', 'ldbi.')) else 'write', address, access_size))
            if access_size == 4 and address % 4:
                raise ValueError('unaligned word access')
            if op.startswith(('ld.', 'ldbi.')):
                if not source <= address or address + access_size > source + count:
                    raise ValueError('read outside source')
                registers[value] = sum(memory[address+i] << (8*i) for i in range(access_size))
                if op.startswith('ldbi.'):
                    registers[base] = (registers[base] + access_size) & 0xffffffff
                trace.extend(('read', address+i) for i in range(access_size))
            else:
                if not destination <= address or address + access_size > destination + count:
                    raise ValueError('write outside destination')
                for i in range(access_size):
                    memory[address+i] = (registers[value] >> (8*i)) & 255
                if op.startswith('stbi.'):
                    registers[base] = (registers[base] + access_size) & 0xffffffff
                trace.extend(('write', address+i) for i in range(access_size))
        elif op == 'rts':
            return registers['r0'], trace
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def decode(disassembly):
    code = {}
    for line in disassembly.splitlines():
        match = re.match(r'\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([\w.]+)\s*(.*?)\s*$', line)
        if match:
            address, encoding, op, operand = match.groups()
            code[int(address, 16)] = (op, operand.split('//')[0].strip(), len(encoding) // 2)
    return code


def verify(prefix=None, sdk=None, output=None):
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_memcpy.c'
    output = output or ROOT / 'build/gx8002-memcpy-source'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    obj = output / 'copy.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *COPY_FLAGS,
                    '-c', str(source), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.open_cfw_gx8002_memcpy')
    if section['size'] > 126 or 0x1774c % section['align']:
        raise ValueError('candidate does not fit original placement')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    if elf.relocations(section['index']):
        raise ValueError('unexpected relocation')
    disassembly = subprocess.check_output([str(prefix / 'csky-unknown-elf-objdump'), '-dr', str(obj)], text=True)
    code = decode(disassembly)
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
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
    stock_code = decode(subprocess.check_output([str(prefix / 'csky-unknown-elf-objdump'),
                        '-D', '--start-address=0x1774c', '--stop-address=0x177ca',
                        str(wrapper)], text=True))
    cases = 0
    for sa in range(4):
        for da in range(4):
            for size in range(258):
                src, dst = 0x1000 + sa, 0x3000 + da
                memory = {src+i: (i*73+19) % 256 for i in range(size)}
                original = memory.copy()
                stock_memory = memory.copy()
                accesses, stock_accesses = [], []
                result, trace = execute(code, memory, dst, src, size, accesses=accesses)
                if result != dst or any(memory[dst+i] != original[src+i] for i in range(size)):
                    raise ValueError('copy mismatch')
                if any(memory[a] != v for a, v in original.items()):
                    raise ValueError('source changed')
                stock_result, stock_trace = execute(stock_code, stock_memory, dst, src, size, 0x1774c, accesses=stock_accesses)
                if stock_result != result or stock_memory != memory:
                    raise ValueError('stock/source result mismatch')
                if accesses != stock_accesses:
                    raise ValueError('stock/source access width or order mismatch')
                for access in ('read', 'write'):
                    if sorted(a for kind, a in stock_trace if kind == access) != sorted(a for kind, a in trace if kind == access):
                        raise ValueError('stock/source accessed-byte mismatch')
                cases += 1
    report = {'source_sha256': sha(source.read_bytes()), 'compiled_sha256': sha(elf.contents(section)),
              'compiled_bytes': section['size'], 'compile_flags': COPY_FLAGS, 'target_cases': cases,
              'source_admitted': True, 'admission_scope': 'experimental hybrid codec; ordinary non-overlapping RAM',
              'stock_equivalence_proven': False,
              'symbol': 'open_cfw_gx8002_memcpy',
              'stock_occurrences': [{'symbol': 'open_cfw_gx8002_memcpy', 'package_offset': 0x1774c,
                                     'bytes': 126, 'sha256': sha(stock[0x1774c:0x177ca]),
                                     'region': 'image_a_sram_text'}],
              'stock_ram_result_comparison_cases': cases, 'exact_memory_access_trace_cases': cases, 'stock_body_sha256': sha(stock[0x1774c:0x177ca]),
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Memory access traces match tested cases; same-entry placement fits; hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
