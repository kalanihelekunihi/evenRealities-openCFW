#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for UART boot stage-1 ID/bit leaves.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_idbit.c against the
stock stage-1 bodies by executing decoded C-SKY instructions for both
across a battery of inputs, plus an independent Python oracle.

Leaves: the stage-1-local ID word getter (runtime 0x100002BC, single word
load from 0x20002008) and the PMU clock-source single-bit modifier
(runtime 0x10000840, read-modify-write of PMU_CFG_SOURCE_SEL0 at
0xA001008C from a two-word descriptor: word[0] is the bit index, byte[4]
is the bit value). Compared: the exact access trace (kind, address,
width, and value of every read and write), r0, descriptor preservation,
the final register value, and callee-saved register preservation.

Behavioral equivalence only: the getter C synthesizes the cell address
with movi/bseti where the stock uses a literal pool, and scratch
registers may differ. Admission rests on decoded-trace equivalence.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_idbit.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-IDBIT-NOTICE.txt'
IDBIT_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize']

MASK = 0xffffffff
ID_CELL = 0x20002008
PMU_SOURCE_SEL0 = 0xa001008c

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_get_stored_id', 0x100002bc, 0x30c, 12,
     'get_id', 'compiled_c'),
    ('open_cfw_gx8002_uart_stage1_pmu_bit_modify', 0x10000840, 0x890, 30,
     'bit_modify', 'compiled_c'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_get_stored_id 0x100002bc : { *(.text.open_cfw_gx8002_uart_stage1_get_stored_id) }
  .text.open_cfw_gx8002_uart_stage1_pmu_bit_modify 0x10000840 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_bit_modify) }
}
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
CALLEE_SAVED = ('r4', 'r5', 'r6', 'r7', 'r14', 'r15')


class IdBitModel:
    """Scripted stage-1 memory: ID cell, descriptor words, PMU register."""

    def __init__(self, ram):
        self.ram = dict(ram)
        self.trace = []

    def read_word(self, address):
        if address not in self.ram:
            raise ValueError('unexpected read at ' + hex(address))
        value = self.ram[address] & MASK
        self.trace.append(('read', address, 4, value))
        return value

    def read_byte(self, address):
        word = self.read_word(address & ~0x3)
        value = (word >> ((address & 0x3) * 8)) & 0xff
        self.trace.pop()
        self.trace.append(('read', address, 1, value))
        return value

    def write_word(self, address, value):
        if address not in self.ram:
            raise ValueError('unexpected write at ' + hex(address))
        value &= MASK
        self.ram[address] = value
        self.trace.append(('write', address, 4, value))


def execute(code, start, arg, model):
    """Run decoded code with r0=arg against the memory model.

    Returns (r0, trace, callee-saved preserved).
    """
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=arg & MASK)
    saved = dict(registers)
    pc = start
    for _ in range(400):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        if op == 'movi':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'movih':
            registers[parts[0]] = (int(parts[1], 0) << 16) & MASK
        elif op == 'bseti':
            registers[parts[0]] = (registers[parts[0]] | (1 << int(parts[1], 0))) & MASK
        elif op == 'lrw':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'subi':
            registers[parts[0]] = (registers[parts[0]] - int(parts[1], 0)) & MASK
        elif op == 'ld.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            registers[match.group(1)] = model.read_word(address)
        elif op == 'ld.b':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            registers[match.group(1)] = model.read_byte(address)
        elif op == 'rotl':
            count = registers[parts[1]] & 31
            value = registers[parts[0]]
            registers[parts[0]] = ((value << count) | (value >> ((32 - count) & 31))) & MASK
        elif op == 'and':
            registers[parts[0]] = registers[parts[0]] & registers[parts[1]]
        elif op == 'lsl':
            registers[parts[0]] = (registers[parts[0]] << (registers[parts[1]] & 31)) & MASK
        elif op == 'or':
            registers[parts[0]] = registers[parts[0]] | registers[parts[1]]
        elif op == 'st.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            model.write_word(address, registers[match.group(1)])
        elif op == 'rts':
            preserved = all(registers[r] == saved[r] for r in CALLEE_SAVED)
            return (registers['r0'], list(model.trace), preserved)
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def oracle(kind, arg, ram):
    """Independent model: (r0, final ram snapshot, trace)."""
    ram = dict(ram)
    trace = []
    if kind == 'get_id':
        value = ram[ID_CELL] & MASK
        trace.append(('read', ID_CELL, 4, value))
        return value, ram, trace
    bit = ram[arg] & MASK
    value = (ram[(arg + 4) & ~0x3] >> (((arg + 4) & 0x3) * 8)) & 0xff
    trace.append(('read', arg, 4, bit))
    trace.append(('read', PMU_SOURCE_SEL0, 4, ram[PMU_SOURCE_SEL0] & MASK))
    trace.append(('read', arg + 4, 1, value))
    # Single-bit clear-then-set idiom, stated independently of the stock
    # rotate instruction: shift counts use the observed low-5-bit
    # convention (pinned by stock/source agreement on every case).
    shift = bit & 31
    want = ((ram[PMU_SOURCE_SEL0] & (~(1 << shift) & MASK)) | ((value << shift) & MASK)) & MASK
    ram[PMU_SOURCE_SEL0] = want
    trace.append(('write', PMU_SOURCE_SEL0, 4, want))
    return arg & MASK, ram, trace


def battery_cases(kind):
    if kind == 'get_id':
        seeds = [0x00000000, 0x00000001, 0x0000000f, 0x00000010,
                 0xdeadbeef, 0xffffffff, 0x12345678, 0x00000009,
                 0xa5a5a5a5, 0x5a5a5a5a, 0x80000000, 0x00000007]
        return [(0x11111111 * (i + 1) & MASK, {ID_CELL: seed})
                for i, seed in enumerate(seeds)]
    bits = list(range(32)) + [32, 33, 63]
    values = [0x00, 0x01, 0xff]
    curs = [0x00000000, 0xffffffff, 0xa5a5a5a5]
    descs = [0x200024b0, 0x20001000]
    cases = []
    for base in descs:
        for bit in bits:
            for value in values:
                for cur in curs:
                    ram = {base: bit & MASK,
                           (base + 4) & ~0x3: 0xa5a500 | (value & 0xff),
                           PMU_SOURCE_SEL0: cur & MASK}
                    cases.append((base, ram))
    return cases


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


def upstream_files(sdk):
    from analyze_gx8002_upstream_objects import SDK_COMMIT, authenticated_blob
    deps = []
    for relative in ('arch/soc/grus/include/base_addr.h', 'LICENSE'):
        blob = subprocess.check_output(
            ['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + relative],
            text=True).strip()
        deps.append({'path': relative, 'git_blob': blob,
                     'sha256': sha(authenticated_blob(sdk / relative, blob))})
    return deps


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-idbit'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    c_obj = output / 'idbit_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *IDBIT_FLAGS,
                    '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
    script = output / 'idbit.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'idbit.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(c_obj), '-o', str(elf_path)], check=True)
    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    # Analysis-only slice wrapper: the stage-1 span is rewrapped with the
    # CK804EF ELF flags and shifted to its runtime base so decoded branch
    # targets are absolute (see gx8002-uart-boot-stage1-cd001-analysis.md).
    # No stock bytes enter the compiled source objects.
    wrapper = output / 'stock-analysis.elf'
    (output / 'stage1-slice.bin').write_bytes(stock[0x50:0x2050])
    subprocess.run([str(prefix / 'csky-unknown-elf-objcopy'), '-I', 'binary',
                    '-O', 'elf32-csky-little', '-B', 'csky',
                    '--set-section-flags', '.data=alloc,code,load',
                    str(output / 'stage1-slice.bin'), str(wrapper)], check=True)
    data = bytearray(wrapper.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    wrapper.write_bytes(data)
    adjusted = output / 'stock-analysis-vma.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-objcopy'),
                    '--adjust-vma=0x10000000', str(wrapper), str(adjusted)],
                   check=True)
    stock_code = decode(subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-D',
         '--start-address=0x100002bc', '--stop-address=0x100002c8',
         str(adjusted)], text=True))
    stock_code.update(decode(subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-D',
         '--start-address=0x10000840', '--stop-address=0x10000860',
         str(adjusted)], text=True)))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'idbit.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
    functions = []
    cases = 0
    for symbol, entry, offset, size, kind, ownership in SPECS:
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) > size or offset % section['align']:
            raise ValueError('candidate does not fit original placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        for arg, ram in battery_cases(kind):
            want_r0, want_ram, want_trace = oracle(kind, arg, ram)
            for code, start, label in ((stock_code, entry, 'stock'),
                                       (source_code, entry, 'source')):
                model = IdBitModel(ram)
                got_r0, got_trace, preserved = execute(code, start, arg, model)
                if got_r0 != want_r0 or model.ram != want_ram or got_trace != want_trace:
                    raise ValueError('%s/oracle mismatch for %s at %#x'
                                     % (label, symbol, arg))
                if not preserved:
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
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': IDBIT_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'arch/soc/grus/include/base_addr.h '
                                    '(PMU_CFG_SOURCE_SEL0 = GX_REG_BASE_PMU_CONFIG '
                                    '+ 0x8C = 0xA001008C, the clock-source-select '
                                    'register read by the SDK clock_board.c); '
                                    'clean-room bodies from decoded stock flow, '
                                    'no SDK text reproduced',
              'upstream_files': upstream_files(sdk),
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'ID-cell and clock-source leaves only',
              'stock_equivalence_proven': False,
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'MMIO trace equivalence over a finite battery plus an independent '
                         'oracle; shift counts of 32 or more follow the observed low-5-bit '
                         'convention pinned by stock/source agreement. Descriptor and '
                         'register state outside the modeled cells is unmodeled. '
                         'Hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-idbit-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-idbit-verification.json').read_text()),
        indent=2))
