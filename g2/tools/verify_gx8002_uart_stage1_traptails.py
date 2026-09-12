#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 traptails leaves.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_traptails.S against
the stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of register/MMIO configurations, plus an independent
Python oracle.

Leaves: the rail-configure trap tail at runtime 0x1000046C (package
0x4BC, 56 bytes) and the block-clear trap tail at runtime 0x100004A4
(package 0x4F4, 44 bytes). Both are H-class pop-then-bkpt flows whose
first dispatcher call already leaves the envelope: every terminal path
of the called PMU dispatchers pops its frame and falls into the
retained second-dispatcher loop (no `rts`), so neither leaf returns.
Compared: byte identity of both full envelopes (the transliteration
assembles exactly to stock, so the unreachable post-call tails are
covered by identity), plus the full unfiltered access trace (kind,
address, width, and value of every read and write), the final RAM, and
the live registers from entry to the first dispatcher call on both
sides and against the oracle.

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow with zero deviations (byte-identical). The
dispatcher cascade past the chaining branch is never executed here;
it is qualified by the reviewed pmudispatch/pmusecond batteries, and
both sides stop at the chaining branch (uartcfg-leaf precedent).
Hardware timing remains unqualified.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_traptails.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-TRAPTAILS-NOTICE.txt'
TRAPTAILS_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY1 = 0x1000046c
PKG1 = 0x4bc
SIZE1 = 56
ENTRY2 = 0x100004a4
PKG2 = 0x4f4
SIZE2 = 44
CHAIN = 0x10000d98
EA0 = 0x10000ea0
SP0 = 0x20002800
CNT = 0xa0400000
BLK_A = 0xa0500000
BLK_B = 0xa0600000
STEP_CAP = 20000

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_railcfg', ENTRY1, PKG1, SIZE1,
     'railcfg', 'compiled_assembly'),
    ('open_cfw_gx8002_uart_stage1_blkclr', ENTRY2, PKG2, SIZE2,
     'blkclr', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_railcfg 0x1000046c : { *(.text.open_cfw_gx8002_uart_stage1_railcfg) }
  .text.open_cfw_gx8002_uart_stage1_blkclr 0x100004a4 : { *(.text.open_cfw_gx8002_uart_stage1_blkclr) }
}
open_cfw_gx8002_uart_boot_stage1_d98_entry = 0x10000d98;
open_cfw_gx8002_uart_boot_stage1_ea0_entry = 0x10000ea0;
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')


class ChainedOff(Exception):
    """Reached the chaining branch into the retained dispatcher."""

    def __init__(self, registers, model):
        super().__init__('chained off')
        self.registers = dict(registers)
        self.model = model


class Model:
    """Flat word RAM; unmapped addresses trap."""

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


def in_frame(address, entry):
    if entry == ENTRY1:
        return (SP0 - 12) <= address < SP0
    return (SP0 - 8) <= address < SP0


def execute(code, start, args, model, entry, chain=CHAIN, entry_sp=SP0):
    """Run decoded code with r0-r7=args against the model.

    args is (r0, r1, r4, r5, r6, r7); every other register starts from
    a fixed seed and r14 starts at entry_sp. Raises ChainedOff at the
    first dispatcher call and ValueError on unmapped access, trap
    words, or any foreign transfer. Post-call instructions
    (rotli/divs/tail stores/bkpt) are present in the code map but
    never reached: both sides chain off first, and the envelopes are
    admitted by byte identity.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r4=args[2] & MASK, r5=args[3] & MASK,
                     r6=args[4] & MASK, r7=args[5] & MASK, r14=entry_sp)
    pc = start
    for _step in range(STEP_CAP):
        if pc not in code:
            raise ValueError('unexpected pc ' + hex(pc))
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        if op == 'movi':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'movih':
            registers[parts[0]] = (int(parts[1], 0) << 16) & MASK
        elif op == 'mov':
            registers[parts[0]] = registers[parts[1]]
        elif op == 'push':
            for reg in expand_regs(operand):
                registers['r14'] = (registers['r14'] - 4) & MASK
                model.write_word(registers['r14'], registers[reg])
        elif op == 'pop':
            for reg in reversed(expand_regs(operand)):
                registers[reg] = model.read_word(registers['r14'])
                registers['r14'] = (registers['r14'] + 4) & MASK
        elif op == 'ld.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            registers[match.group(1)] = model.read_word(address)
        elif op == 'st.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            model.write_word(address, registers[match.group(1)])
        elif op == 'bsr':
            if int(parts[0], 0) != chain:
                raise ValueError('unexpected call to ' + operand)
            registers['r15'] = following
            raise ChainedOff(registers, model)
        elif op == 'bkpt':
            raise ValueError('trapped at %#x' % pc)
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def expand_regs(operand):
    regs = []
    for part in [p.strip() for p in operand.split(',')]:
        match = re.fullmatch(r'r(\d+)-r(\d+)', part)
        if match:
            regs.extend('r%d' % i for i in range(int(match.group(1)), int(match.group(2)) + 1))
        else:
            regs.append(part)
    return regs


def seed(reg):
    index = int(reg[1:])
    if reg == 'r14':
        return SP0
    return (0x98760000 + index * 0x111111) & MASK


# Both leaves keep their stock frames, so every register matches
# exactly at the chain on both sides (no implementation-defined
# registers: the pushed words carry the seeds identically, and the
# chain-target dispatchers save r4/r5 before any read).
LIVE_REGS = ('r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r14', 'r15')


def oracle(entry, r0seed, r1seed, r4seed, r5seed, r6seed, r7seed, ram):
    """Independent model: (outcome, regs, trace, ram).

    Stated from the decoded structure, not from decoded
    instructions. Railcfg: push r4-r5/r15, materialize 0xA0400000
    (no traffic), set (r0, r1) = (23, 1), chain into the first
    dispatcher. Blkclr: push r4/r15, clear 0x30/0x6C around
    discarded 0x40 status reads on the 0xA0500000 then 0xA0600000
    blocks, set (r0, r1) = (20, 0), chain into the first
    dispatcher. Entry r2/r3/r6/r7 pass through untouched on both
    leaves; r15 at the chain is the post-bsr address.
    """
    ram = dict(ram)
    trace = []

    def read(address):
        if address not in ram:
            raise ValueError('oracle missing cell at ' + hex(address))
        value = ram[address] & MASK
        trace.append(('read', address, 4, value))
        return value

    def write(address, value):
        if address not in ram:
            raise ValueError('oracle missing cell at ' + hex(address))
        value &= MASK
        ram[address] = value
        trace.append(('write', address, 4, value))

    regs = {'r0': r0seed & MASK, 'r1': r1seed & MASK,
            'r2': seed('r2'), 'r3': seed('r3'),
            'r4': r4seed & MASK, 'r5': r5seed & MASK,
            'r6': r6seed & MASK, 'r7': r7seed & MASK,
            'r14': SP0, 'r15': seed('r15')}
    if entry == ENTRY1:
        write(SP0 - 4, regs['r4'])
        write(SP0 - 8, regs['r5'])
        write(SP0 - 12, regs['r15'])
        regs['r14'] = SP0 - 12
        regs['r4'] = CNT
        regs['r1'] = 1
        regs['r0'] = 23
        regs['r15'] = 0x1000047a
    elif entry == ENTRY2:
        write(SP0 - 4, regs['r4'])
        write(SP0 - 8, regs['r15'])
        regs['r14'] = SP0 - 8
        regs['r3'] = BLK_A
        regs['r4'] = 0
        regs['r2'] = read(BLK_A + 0x40)
        write(BLK_A + 0x30, 0)
        write(BLK_A + 0x6c, 0)
        regs['r3'] = BLK_B
        regs['r1'] = 0
        regs['r2'] = read(BLK_B + 0x40)
        regs['r0'] = 20
        write(BLK_B + 0x30, 0)
        write(BLK_B + 0x6c, 0)
        regs['r15'] = 0x100004c4
    else:
        raise ValueError('oracle unknown entry ' + hex(entry))
    return {'outcome': 'chain', 'regs': regs, 'trace': trace,
            'ram': ram}


def config_ram(entry, status_a, status_b, clear_init):
    """Build the initial RAM for one battery case.

    Maps the two status-read cells, the four clear cells, and the
    stack window. Returns ram. The counter block needs no cell: the
    railcfg prefix performs no MMIO traffic before chaining off.
    """
    ram = {}
    ram[BLK_A + 0x40] = status_a & MASK
    ram[BLK_B + 0x40] = status_b & MASK
    for base in (BLK_A, BLK_B):
        for offset in (0x30, 0x6c):
            ram[base + offset] = clear_init & MASK
    for address in range(SP0 - 16, SP0 + 16, 4):
        ram[address] = 0x51edc0de
    return ram


def battery_cases():
    # Case: (entry, r0seed, r1seed, r4seed, r5seed, r6seed, r7seed,
    # status_a, status_b, clear_init). Register seeds prove the
    # pushed frame words (and only those) carry entry state on the
    # railcfg path; the blkclr path additionally proves the
    # discarded status reads and the unconditional clears.
    cases = []
    seeds = (
        (0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000),
        (0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d),
        (0xffffffff, 0x12345678, 0xa5a5a5a5, 0x5a5a5a5a, 0xdeadbeef, 0x01010101),
    )
    statuses = (0x00000000, 0x00000001, 0xffffffff, 0xa5a5a5a5)
    clears = (0x00000000, 0xffffffff, 0x12345678)
    for entry in (ENTRY1, ENTRY2):
        for regseed in seeds:
            for status_a in statuses:
                for status_b in statuses:
                    for clear_init in clears:
                        cases.append((entry, *regseed, status_a,
                                      status_b, clear_init))
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


def check_shape(source_code, entry, size, expect_calls):
    """Fail closed on prologue/transfer drift."""
    addresses = sorted(source_code)
    first = source_code[addresses[0]]
    if first[0] != 'push':
        raise ValueError('entry push changed: ' + repr(first))
    # `objdump -d` skips the zero trap word, so decoded code covers
    # size-2; the trap word itself is pinned on the section payload
    # (last word zero) plus byte identity against stock.
    covered = max(addresses) + source_code[max(addresses)][2] - entry
    if covered != size - 2:
        raise ValueError('section size changed: %d vs %d' % (covered, size))
    for op in ('rts', 'jmp', 'lrw', 'jmpi', 'jsr', 'bkpt'):
        hits = [pc for pc in addresses if source_code[pc][0] == op]
        if hits:
            raise ValueError('leaf keeps %s at %s'
                             % (op, [hex(pc) for pc in hits]))
    calls = [(pc, source_code[pc][1]) for pc in addresses
             if source_code[pc][0] == 'bsr']
    if [target for _, target in calls] != expect_calls:
        raise ValueError('call sequence changed: %r' % (calls,))
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)


def run_side(code, start, args, ram, entry, label):
    """Execute one side; return (registers, trace, ram).

    Both sides raise ChainedOff at the first dispatcher call. Any
    unexpected fault is a hard failure: every reachable address is
    mapped and post-call paths are never executed.
    """
    model = Model(ram)
    try:
        execute(code, start, args, model, entry)
    except ChainedOff as done:
        return done.registers, done.model.trace, done.model.ram
    raise ValueError(label + ': side returned instead of chaining off')


def check_stock(stock):
    """Fail closed when a stock envelope drifts from the decode."""
    return {entry: sha(stock[pkg:pkg + size])
            for _, entry, pkg, size, _, _ in SPECS}


CALLS = {
    ENTRY1: ['0x10000d98', '0x10000ea0'],
    ENTRY2: ['0x10000d98', '0x10000d98'],
}


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-traptails'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    traptails_obj = output / 'traptails_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *TRAPTAILS_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(traptails_obj)], check=True)
    script = output / 'traptails.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'traptails.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(traptails_obj), '-o', str(elf_path)], check=True)
    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    envelope_shas = check_stock(stock)
    # Analysis-only slice wrapper: the stage-1 span is rewrapped with
    # the CK804EF ELF flags and shifted to its runtime base so decoded
    # branch targets are absolute (see
    # gx8002-uart-boot-stage1-cd001-analysis.md). No stock bytes enter
    # the assembled source objects.
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
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'traptails.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
    source_all = {}
    for section_code in sources.values():
        source_all.update(section_code)
    functions = []
    cases = 0
    for symbol, entry, offset, size, kind, ownership in SPECS:
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) != size or offset % section['align']:
            raise ValueError('candidate does not exactly fill its placement: ' + symbol)
        if payload != stock[offset:offset + size]:
            raise ValueError('candidate is not byte-identical to stock: ' + symbol)
        if payload[-2:] != b'\x00\x00':
            raise ValueError('missing trap word: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        check_shape(source_code, entry, size, CALLS[entry])
        # Stock body only (the dispatcher cascade stays retained and
        # is never executed: both sides stop at the chaining branch).
        stock_code = decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=%#x' % entry,
             '--stop-address=%#x' % (entry + size), str(adjusted)], text=True))
        for case in battery_cases():
            case_entry, r0s, r1s, r4s, r5s, r6s, r7s = case[:7]
            status_a, status_b, clear_init = case[7:]
            if case_entry != entry:
                continue
            args = (r0s, r1s, r4s, r5s, r6s, r7s)
            ram = config_ram(entry, status_a, status_b, clear_init)
            want = oracle(entry, r0s, r1s, r4s, r5s, r6s, r7s, ram)
            if want['outcome'] != 'chain':
                raise ValueError('battery missed the chain on %r' % (case,))
            stock_regs, stock_trace, stock_final = run_side(
                stock_code, entry, args, ram, entry, 'stock')
            if want['trace'] != stock_trace:
                for i, (a, b) in enumerate(zip(want['trace'], stock_trace)):
                    if a != b:
                        raise ValueError(
                            'stock trace/oracle mismatch at step %d: %r vs %r on %r'
                            % (i, a, b, case))
                raise ValueError('stock trace/oracle length mismatch %d vs %d on %r'
                                 % (len(want['trace']), len(stock_trace), case))
            if want['ram'] != stock_final:
                for address in sorted(set(want['ram']) | set(stock_final)):
                    if want['ram'].get(address) != stock_final.get(address):
                        raise ValueError(
                            'stock ram/oracle mismatch at %#x on %r'
                            % (address, case))
            src_regs, src_trace, src_final = run_side(
                source_all, entry, args, ram, entry, 'source')
            if src_trace != stock_trace:
                for i, (a, b) in enumerate(zip(src_trace, stock_trace)):
                    if a != b:
                        raise ValueError(
                            'source trace/stock mismatch at step %d: %r vs %r on %r'
                            % (i, a, b, case))
                raise ValueError('source trace/stock length mismatch %d vs %d on %r'
                                 % (len(src_trace), len(stock_trace), case))
            if src_final != stock_final:
                for address in sorted(set(src_final) | set(stock_final)):
                    if src_final.get(address) != stock_final.get(address):
                        raise ValueError(
                            'source ram/stock mismatch at %#x on %r'
                            % (address, case))
            for reg in LIVE_REGS:
                if src_regs[reg] != stock_regs[reg]:
                    raise ValueError('%s differs stock/source on %r'
                                     % (reg, case))
            for reg in LIVE_REGS:
                if stock_regs[reg] != want['regs'][reg]:
                    raise ValueError('oracle reg %s mismatch on %r' % (reg, case))
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': envelope_shas[entry],
                                                 'region': 'uart_boot_stage1'}]})
    if cases < 200:
        raise ValueError('battery admitted too few cases: %d' % cases)
    report = {'c_source_sha256': sha(S_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': TRAPTAILS_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no upstream register map is used: the '
                                    '0xA0400000/0xA0500000/0xA0600000 bases, '
                                    'every offset, id, and constant is a numeric '
                                    'immediate observed in the decoded stock flow; '
                                    'clean-room body from decoded stock flow, '
                                    'no SDK text reproduced',
              'functions': functions, 'target_cases': cases,
              'handoff': hex(CHAIN),
              'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot '
                                 'stage-1 rail-configure and block-clear trap '
                                 'tails only (entry through the first '
                                 'dispatcher call into retained 0x10000d98; '
                                 'full unfiltered traces)',
              'stock_equivalence_proven': False,
              'leftover_paths': 'none: both leaves are straight-line to the '
                                'first dispatcher call (no branches), so the '
                                'battery covers every reachable path; the '
                                'post-call tails never execute on either side '
                                'and are admitted by byte identity of the full '
                                'envelopes. All registers match exactly at the '
                                'chain (frames kept, no implementation-defined '
                                'state).',
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'The dispatcher cascade past the chaining branch is '
                         'never executed here; it is qualified by the reviewed '
                         'pmudispatch/pmusecond batteries. Hardware timing '
                         'remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-traptails-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-traptails-verification.json').read_text()),
        indent=2))
