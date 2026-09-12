#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for UART boot stage-1 PMU trim-bit leaves.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_pmubits.c (bit0 write,
bit0/bit1 reads) and the reviewed assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_pmusbit.S (bit1 write)
against the stock stage-1 bodies by executing decoded C-SKY instructions for
both across a battery of register states and inputs, plus an independent
Python oracle. The PMU register at 0xA0010030 is modeled as stateful MMIO:
reads return the current value, writes update it.

Behavioral equivalence only: register allocation and instruction choice may
differ. Compared: the final register value, the exact MMIO access trace, and
callee-saved register preservation for all four leaves, plus r0 (result) for
the two get leaves. The void set leaves leave different scratch in r0 (stock
folds its OR there; the source keeps the argument), so r0 is caller-clobbered
scratch for setters and is not compared.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmubits.c'
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmusbit.S'
PMUBITS_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize']

REG = 0xA0010030
MASK = 0xffffffff

# (symbol, package offset, stock envelope bytes, access kind, ownership kind).
# Runtime entries: set_bit0 0x10000374, set_bit1 0x1000038c,
# get_bit0 0x100003a4, get_bit1 0x100003b0; see the audit.
SPECS = [
    ('open_cfw_gx8002_uart_stage1_pmu_set_bit0', 0x3c4, 24, 'set0', 'compiled_c'),
    ('open_cfw_gx8002_uart_stage1_pmu_set_bit1', 0x3dc, 24, 'set1', 'compiled_assembly'),
    ('open_cfw_gx8002_uart_stage1_pmu_get_bit0', 0x3f4, 12, 'get0', 'compiled_c'),
    ('open_cfw_gx8002_uart_stage1_pmu_get_bit1', 0x400, 12, 'get1', 'compiled_c'),
]

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')


def signed(value):
    return value if value < 0x80000000 else value - 0x100000000


def execute(code, start, arg, reg_init):
    """Run decoded code with r0=arg; return (r0, final_reg, trace, preserved)."""
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=arg)
    saved = dict(registers)
    state = reg_init & MASK
    pc, trace = start, []
    for _ in range(200):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        if op == 'movih':
            registers[parts[0]] = (int(parts[1], 0) << 16) & MASK
        elif op == 'lsli':
            if len(parts) == 3:
                registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & MASK
            else:
                registers[parts[0]] = (registers[parts[0]] << registers[parts[1]]) & MASK
        elif op == 'ld.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            if address != REG:
                raise ValueError('unexpected read at ' + hex(address))
            registers[match.group(1)] = state
            trace.append(('read', address, state))
        elif op == 'st.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            if address != REG:
                raise ValueError('unexpected write at ' + hex(address))
            state = registers[match.group(1)] & MASK
            trace.append(('write', address, state))
        elif op == 'andi':
            if len(parts) == 3:
                registers[parts[0]] = registers[parts[1]] & int(parts[2], 0)
            else:
                base = parts[0] if len(parts) == 2 else parts[1]
                registers[parts[0]] = registers[base] & int(parts[-1], 0)
        elif op == 'andni':
            registers[parts[0]] = registers[parts[1]] & (MASK ^ int(parts[2], 0))
        elif op == 'or':
            if len(parts) == 2:
                registers[parts[0]] = registers[parts[0]] | registers[parts[1]]
            else:
                registers[parts[0]] = registers[parts[1]] | registers[parts[2]]
        elif op == 'bclri':
            registers[parts[0]] &= MASK ^ (1 << int(parts[1], 0))
        elif op == 'zext':
            registers[parts[0]] = (registers[parts[1]] >> int(parts[3], 0)) & (
                (1 << (int(parts[2], 0) - int(parts[3], 0) + 1)) - 1)
        elif op == 'mov':
            registers[parts[0]] = registers[parts[1]]
        elif op == 'rts':
            preserved = all(registers[r] == saved[r]
                            for r in ('r4', 'r5', 'r6', 'r7', 'r14', 'r15'))
            return registers['r0'], state, trace, preserved
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def oracle(kind, arg, reg_init):
    """Independent model: (final register, r0 result, access trace)."""
    reg = reg_init & MASK
    trace = []
    if kind == 'set0':
        trace.append(('read', REG, reg))
        reg &= MASK ^ 1
        trace.append(('write', REG, reg))
        trace.append(('read', REG, reg))
        reg |= arg & 1
        trace.append(('write', REG, reg))
        return reg, arg & MASK, trace
    if kind == 'set1':
        trace.append(('read', REG, reg))
        reg &= MASK ^ 2
        trace.append(('write', REG, reg))
        trace.append(('read', REG, reg))
        reg |= (arg << 1) & 2
        trace.append(('write', REG, reg))
        return reg & MASK, arg & MASK, trace
    if kind == 'get0':
        trace.append(('read', REG, reg))
        return reg, reg & 1, trace
    if kind == 'get1':
        trace.append(('read', REG, reg))
        return reg, (reg >> 1) & 1, trace
    raise ValueError('unknown leaf kind: ' + kind)


def battery_cases(kind):
    regs = [0x00000000, 0x00000001, 0x00000002, 0x00000003,
            0xfffffffc, 0xfffffffd, 0xfffffffe, 0xffffffff,
            0x80000000, 0x7fffffff, 0xa5a5a5a5, 0x5a5a5a5a,
            0xa0010030, 0x12345678]
    if kind.startswith('set'):
        args = [0x00000000, 0x00000001, 0x00000002, 0x00000003,
                0x00000004, 0x7fffffff, 0x80000000, 0xfffffffe,
                0xffffffff, 0xa5a5a5a5]
        return [(a, r) for r in regs for a in args]
    return [(0, r) for r in regs]


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
    output = output or ROOT / 'build/gx8002-uart-stage1-pmubits'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    c_obj = output / 'pmubits_c.o'
    s_obj = output / 'pmusbit_s.o'
    obj = output / 'pmubits.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUBITS_FLAGS,
                    '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
    subprocess.run([str(prefix / 'csky-unknown-elf-as'), '-mcpu=ck804ef',
                    '-mhard-float', str(S_SOURCE), '-o', str(s_obj)], check=True)
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-r',
                    str(c_obj), str(s_obj), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    # Analysis-only ELF wrapper: no stock bytes enter the compiled source objects.
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
    for symbol, offset, size, kind, ownership in SPECS:
        entry = offset
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) > size or offset % section['align']:
            raise ValueError('candidate does not fit original placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        stock_code = decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=%#x' % entry, '--stop-address=%#x' % (entry + size),
             str(wrapper)], text=True))
        source_code = sources[section_name]
        for arg, reg_init in battery_cases(kind):
            want_reg, want_r0, want_trace = oracle(kind, arg, reg_init)
            stock_r0, stock_reg, stock_trace, stock_ok = execute(
                stock_code, entry, arg, reg_init)
            source_r0, source_reg, source_trace, source_ok = execute(
                source_code, 0, arg, reg_init)
            # The set leaves return void: stock folds its OR into r0 while the
            # source keeps the argument there, so r0 is caller-clobbered
            # scratch for setters and only the register value plus the access
            # trace are compared. The get leaves return their result in r0.
            if kind.startswith('set'):
                if (stock_reg, stock_trace) != (want_reg, want_trace):
                    raise ValueError('stock/oracle mismatch for %s at %#x %#x'
                                     % (symbol, arg, reg_init))
                if (source_reg, source_trace) != (want_reg, want_trace):
                    raise ValueError('source/oracle mismatch for %s at %#x %#x'
                                     % (symbol, arg, reg_init))
            else:
                if (stock_r0, stock_reg, stock_trace) != (want_r0, want_reg, want_trace):
                    raise ValueError('stock/oracle mismatch for %s at %#x %#x'
                                     % (symbol, arg, reg_init))
                if (source_r0, source_reg, source_trace) != (want_r0, want_reg, want_trace):
                    raise ValueError('source/oracle mismatch for %s at %#x %#x'
                                     % (symbol, arg, reg_init))
            if not stock_ok or not source_ok:
                raise ValueError('callee-saved violation for ' + symbol)
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    report = {'c_source_sha256': sha(C_SOURCE.read_bytes()),
              's_source_sha256': sha(S_SOURCE.read_bytes()),
              'compile_flags': PMUBITS_FLAGS,
              'assemble_flags': ['-mcpu=ck804ef', '-mhard-float'],
              'sdk_commit': '8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5',
              'register_reference': 'arch/soc/grus/include/base_addr.h '
                                    'PMU_CFG_POWER_ON_RESET_REG1 (clean-room use of '
                                    'address and bit positions; no SDK text reproduced)',
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 PMU leaves only',
              'stock_equivalence_proven': False,
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'MMIO trace equivalence over a finite battery plus an independent '
                         'oracle; the PMU register is modeled as stateful with no external '
                         'concurrent updates. Hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
