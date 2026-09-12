#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 PMU fill leaf.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c against the
stock stage-1 body by executing decoded C-SKY instructions for both across
a battery of inputs, plus an independent Python oracle.

Leaf: the PMU descriptor-fill routine (runtime 0x10000780, package 0x7D0,
180 bytes of code): bounds/null checks, a 26-entry peripheral-table
lookup at 0x20002018 (16-byte entries, direct hit at entry id, entry-0
fallback, linear scan of entries 1..25), then a six-word clock
descriptor fill selecting the PMU config domain (ids < 10) or the MCU
config domain (ids 10..25). Compared: the exact access trace (kind,
address, width, and value of every read and write), r0, final
descriptor/table RAM, and callee-saved register preservation.

Behavioral equivalence only: the C synthesizes the table base and the
domain bases with movi/bseti/movih/ori where the stock uses a 12-byte
literal pool (runtime 0x10000834, left as retained stock), folds the two
stock config tails into one selected tail, and drops the stock's dead
null check on the computed entry address. The r1 (descriptor pointer)
register value on return is caller scratch and is not compared.
Admission rests on decoded-trace equivalence.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-PMUFILL-NOTICE.txt'
PMUFILL_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize']

MASK = 0xffffffff
TABLE_BASE = 0x20002018
TABLE_ENTRIES = 26
ENTRY_STRIDE = 16
MAX_ID = 25
PMU_SPLIT = 10
PMU_BASE = 0xa0010000
MCU_BASE = 0xa0300000
PMU_SELECT = 0x8c
MCU_SELECT = 0x88
FAIL = 0xffffffff

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_pmu_fill_desc', 0x10000780, 0x7d0, 180,
     'fill_desc', 'compiled_c'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_pmu_fill_desc 0x10000780 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_fill_desc) }
}
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
LOAD_INDEX = re.compile(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)')
CALLEE_SAVED = ('r4', 'r5', 'r6', 'r7', 'r14', 'r15')


class FillModel:
    """Flat word RAM: peripheral table plus descriptor cells."""

    def __init__(self, ram):
        self.ram = dict(ram)
        self.trace = []

    def read_word(self, address):
        if address not in self.ram:
            raise ValueError('unexpected read at ' + hex(address))
        value = self.ram[address] & MASK
        self.trace.append(('read', address, 4, value))
        return value

    def write_word(self, address, value):
        if address not in self.ram:
            raise ValueError('unexpected write at ' + hex(address))
        value &= MASK
        self.ram[address] = value
        self.trace.append(('write', address, 4, value))


def execute(code, start, arg0, arg1, model):
    """Run decoded code with r0=arg0, r1=arg1 against the memory model.

    Returns (r0, trace, callee-saved preserved).
    """
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=arg0 & MASK, r1=arg1 & MASK)
    saved = dict(registers)
    condition = False
    pc = start
    for _ in range(2000):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        if op == 'movi':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'movih':
            registers[parts[0]] = (int(parts[1], 0) << 16) & MASK
        elif op == 'mov':
            registers[parts[0]] = registers[parts[1]]
        elif op == 'bseti':
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] | (1 << int(parts[1], 0))) & MASK
            else:
                registers[parts[0]] = (registers[parts[1]] | (1 << int(parts[2], 0))) & MASK
        elif op == 'lrw':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'addi':
            base = parts[0] if len(parts) == 2 else parts[1]
            registers[parts[0]] = (registers[base] + int(parts[-1], 0)) & MASK
        elif op == 'subi':
            base = parts[0] if len(parts) == 2 else parts[1]
            registers[parts[0]] = (registers[base] - int(parts[-1], 0)) & MASK
        elif op == 'addu':
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] + registers[parts[1]]) & MASK
            else:
                registers[parts[0]] = (registers[parts[1]] + registers[parts[2]]) & MASK
        elif op == 'or':
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] | registers[parts[1]]) & MASK
            else:
                registers[parts[0]] = (registers[parts[1]] | registers[parts[2]]) & MASK
        elif op == 'ori':
            registers[parts[0]] = (registers[parts[1]] | int(parts[2], 0)) & MASK
        elif op in ('tlsli', 'lsli'):
            registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & MASK
        elif op in ('inct', 'incf'):
            take = condition if op == 'inct' else not condition
            if take:
                registers[parts[0]] = (registers[parts[1]] + int(parts[2], 0)) & MASK
        elif op == 'cmphs':
            condition = registers[parts[0]] >= registers[parts[1]]
        elif op == 'cmphsi':
            condition = registers[parts[0]] >= int(parts[1], 0)
        elif op == 'cmpne':
            condition = registers[parts[0]] != registers[parts[1]]
        elif op == 'cmpnei':
            condition = registers[parts[0]] != int(parts[1], 0)
        elif op == 'ld.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            registers[match.group(1)] = model.read_word(address)
        elif op == 'ldr.w':
            match = LOAD_INDEX.fullmatch(operand)
            address = (registers[match.group(2)]
                       + ((registers[match.group(3)] << int(match.group(4), 0)) & MASK)) & MASK
            registers[match.group(1)] = model.read_word(address)
        elif op == 'st.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            model.write_word(address, registers[match.group(1)])
        elif op == 'bez':
            if registers[parts[0]] == 0:
                following = int(parts[1], 0)
        elif op == 'bnez':
            if registers[parts[0]] != 0:
                following = int(parts[1], 0)
        elif op == 'bnezad':
            registers[parts[0]] = (registers[parts[0]] - 1) & MASK
            if registers[parts[0]] != 0:
                following = int(parts[1], 0)
        elif op == 'bt':
            if condition:
                following = int(parts[0], 0)
        elif op == 'bf':
            if not condition:
                following = int(parts[0], 0)
        elif op == 'br':
            following = int(parts[0], 0)
        elif op == 'rts':
            preserved = all(registers[r] == saved[r] for r in CALLEE_SAVED)
            return (registers['r0'], list(model.trace), preserved)
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def oracle(ident, desc, table_words):
    """Independent model: (r0, final ram, trace).

    Stated from the decoded structure, not from decoded instructions:
    bounds/null gate, leading zero store, direct/entry-0/scan match
    order over 16-byte entries, then the domain-selected six-word fill.
    """
    ram = dict(table_words)
    trace = []
    if desc is not None:
        for index in range(6):
            ram[desc + 4 * index] = ram.get(desc + 4 * index, 0x5a5a5a5a) & MASK
    if ident > MAX_ID or desc is None:
        return FAIL, ram, trace
    ram[desc] = 0
    trace.append(('write', desc, 4, 0))

    def read_entry(slot):
        address = TABLE_BASE + slot * ENTRY_STRIDE
        value = ram[address] & MASK
        trace.append(('read', address, 4, value))
        return value

    if read_entry(ident) == (ident & MASK):
        slot = ident
    elif read_entry(0) == (ident & MASK):
        slot = 0
    else:
        slot = None
        for candidate in range(1, TABLE_ENTRIES):
            if read_entry(candidate) == (ident & MASK):
                slot = candidate
                break
        if slot is None:
            return FAIL, ram, trace
    ram[desc] = (TABLE_BASE + slot * ENTRY_STRIDE) & MASK
    trace.append(('write', desc, 4, ram[desc]))
    if ident < PMU_SPLIT:
        base, select = PMU_BASE, PMU_SELECT
    else:
        base, select = MCU_BASE, MCU_SELECT
    words = [base, base | select, base | 0x18, base | 0x1c, base | 0x20]
    for index, value in enumerate(words, start=1):
        ram[desc + 4 * index] = value & MASK
        trace.append(('write', desc + 4 * index, 4, value & MASK))
    return 0, ram, trace


def table_ram(words):
    """Full table word map (first word of each 16-byte entry set)."""
    ram = {}
    for slot in range(TABLE_ENTRIES):
        ram[TABLE_BASE + slot * ENTRY_STRIDE] = words[slot] & MASK
    return ram


def battery_cases():
    identity = list(range(TABLE_ENTRIES))
    zeros = [0] * TABLE_ENTRIES
    ones = [0xffffffff] * TABLE_ENTRIES
    entry0 = [0x12345678] + [0x9abcdef0] * (TABLE_ENTRIES - 1)
    tables = [identity, zeros, ones, entry0]
    for hit in (1, 9, 10, 24, 25):
        words = [0xdead0000 + slot for slot in range(TABLE_ENTRIES)]
        words[hit] = hit
        tables.append(words)
    for slot in range(TABLE_ENTRIES):
        words = [0x11111111] * TABLE_ENTRIES
        words[slot] = slot
        tables.append(words)
    dup = list(range(TABLE_ENTRIES))
    dup[0] = 7
    tables.append(dup)
    zero_hit = [0x42424242] * TABLE_ENTRIES
    zero_hit[17] = 0
    tables.append(zero_hit)
    tables.append([(slot * 0x01010101) & MASK for slot in range(TABLE_ENTRIES)])
    ids = list(range(27)) + [31, 255, 256, 0x80000000, 0xffffffff]
    descs = [0x20001000, 0x200024b0]
    cases = []
    for words in tables:
        for ident in ids:
            for desc in descs:
                cases.append((ident, desc, table_ram(words)))
    for ident in (0, 7, 10, 25, 26, 0xffffffff):
        cases.append((ident, None, table_ram(identity)))
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
    output = output or ROOT / 'build/gx8002-uart-stage1-pmufill'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    c_obj = output / 'pmufill_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                    '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
    script = output / 'pmufill.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'pmufill.elf'
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
         '--start-address=0x10000780', '--stop-address=0x10000834',
         str(adjusted)], text=True))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'pmufill.disassembly.txt').write_text(disassembly)
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
        for ident, desc, words in battery_cases():
            want_r0, want_ram, want_trace = oracle(ident, desc, words)
            for code, start, label in ((stock_code, entry, 'stock'),
                                       (source_code, entry, 'source')):
                model = FillModel(dict(words))
                if desc is not None:
                    for index in range(6):
                        model.ram[desc + 4 * index] = 0x5a5a5a5a
                got_r0, got_trace, preserved = execute(code, start, ident,
                                                       desc or 0, model)
                if got_r0 != want_r0 or model.ram != want_ram or got_trace != want_trace:
                    raise ValueError('%s/oracle mismatch for %s (id=%#x desc=%s)'
                                     % (label, symbol, ident,
                                        hex(desc) if desc else 'NULL'))
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
              'compile_flags': PMUFILL_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'arch/soc/grus/include/base_addr.h '
                                    '(GX_REG_BASE_MCU_CONFIG = 0xA0300000 with '
                                    'MCU_CFG_SOURCE_SEL +0x88 and the '
                                    'MEPG_CLK_INHIBIT_NORM/1SET/1CLR triple; '
                                    'GX_REG_BASE_PMU_CONFIG = 0xA0010000 with '
                                    'PMU_CFG_SOURCE_SEL0 +0x8C and the same '
                                    'triple); clean-room body from decoded '
                                    'stock flow, no SDK text reproduced',
              'upstream_files': upstream_files(sdk),
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'PMU descriptor-fill leaf only',
              'stock_equivalence_proven': False,
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'MMIO trace equivalence over a finite battery plus an independent '
                         'oracle; the peripheral table is modeled RAM, not hardware state. '
                         'The stock 12-byte literal pool stays retained stock. '
                         'Hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-pmufill-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-pmufill-verification.json').read_text()),
        indent=2))
