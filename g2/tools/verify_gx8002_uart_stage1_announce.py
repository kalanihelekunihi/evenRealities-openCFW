#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 announce leaf.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_announce.S against
the stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of register/MMIO configurations, plus an independent
Python oracle.

Leaf: the UART announce at runtime 0x1000065C (package 0x6AC, 124
bytes). It reads the UART block base from the base cell, raises the
rail-control word at [base+0xA8], then chains into the retained
rail-program entry (0x10001BF8) with the entry arguments plus a
rail-select id (4 unless the base already matches the first UART, in
which case 6). The rail-program entry runs straight-line push/movs
into the reviewed first PMU dispatcher (0x10000D98, noreturn per the
pmudisp audit), so the first chaining call already leaves this
envelope. Compared: byte identity of the full envelope (the
transliteration assembles exactly to stock, so the unreachable
post-call tail -- the polled "ready" transmit loop, the reviewed
rail-postamble call, and the pop-return -- is covered by identity),
plus the full unfiltered access trace (kind, address, width, and
value of every read and write), the final RAM, and the live
registers from entry to the chaining call on both sides and against
the oracle.

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow with zero deviations (byte-identical). The
rail-program/dispatcher cascade past the chaining branch is never
executed here; it is qualified by the reviewed pmudispatch battery
(the 0x1BF8 prefix is straight-line push/movs into 0x10000D98),
and both sides stop at the chaining branch
(uartcfg/traptails-leaf precedent). Hardware timing remains
unqualified.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_announce.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-ANNOUNCE-NOTICE.txt'
ANNOUNCE_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY = 0x1000065c
PKG = 0x6ac
SIZE = 124
POOL = 0x100006d4
NEXT = 0x100006d8
RAIL_PROG = 0x10001bf8
POSTAMBLE = 0x10001d9c
D98 = 0x10000d98
SP0 = 0x20002800
BASE_CELL = 0x20002014
UART_A = 0xa0100000
UART_B = 0xa0200000
STEP_CAP = 20000

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_announce', ENTRY, PKG,
     SIZE, 'announce', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_announce 0x1000065c : { *(.text.open_cfw_gx8002_uart_stage1_announce) }
}
open_cfw_gx8002_uart_boot_stage1_1bf8_entry = 0x10001bf8;
open_cfw_gx8002_uart_boot_stage1_1d9c_entry = 0x10001d9c;
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')

# The chaining call admitted for this entry. The rail-program body
# past the chain is qualified by the reviewed pmudispatch battery
# (straight-line prefix into 0x10000D98) and is never stepped into
# here; the reviewed postamble call is qualified by its own battery.
CHAINS = {
    ENTRY: (RAIL_PROG,),
}

# Full in-address-order call sequence, pinning the documented
# post-chain (dead, never executed) postamble call as well.
CALLS = {
    ENTRY: [RAIL_PROG, POSTAMBLE],
}


class ChainedOff(Exception):
    """Reached the chaining call out of the envelope."""

    def __init__(self, registers, model, target):
        super().__init__('chained off')
        self.registers = dict(registers)
        self.model = model
        self.target = target


class Model:
    """Flat word RAM; unmapped access traps."""

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


def expand_regs(operand):
    regs = []
    for part in [p.strip() for p in operand.split(',')]:
        match = re.fullmatch(r'r(\d+)-r(\d+)', part)
        if match:
            regs.extend('r%d' % i for i in range(int(match.group(1)), int(match.group(2)) + 1))
        else:
            regs.append(part)
    return regs


def execute(code, start, args, model, entry, entry_sp=SP0):
    """Run decoded code with r0/r1/r4/r5=args against the model.

    args is (r0, r1, r4, r5); every other register starts from a
    fixed seed and r14 starts at entry_sp. Raises ChainedOff at the
    chaining call and ValueError on unmapped access, trap words, or
    any foreign transfer. Post-call instructions are present in the
    code map but never reached: both sides chain off first, and the
    envelope is admitted by byte identity.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r4=args[2] & MASK, r5=args[3] & MASK, r14=entry_sp)
    condition = False
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
        elif op == 'lrw':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'addi':
            base = parts[0] if len(parts) == 2 else parts[1]
            registers[parts[0]] = (registers[base] + int(parts[-1], 0)) & MASK
        elif op == 'andi':
            registers[parts[0]] = (registers[parts[1]] & int(parts[2], 0)) & MASK
        elif op == 'cmpne':
            condition = registers[parts[0]] != registers[parts[1]]
        elif op == 'cmpnei':
            condition = registers[parts[0]] != int(parts[1], 0)
        elif op == 'inct':
            if condition:
                registers[parts[0]] = (registers[parts[1]] + int(parts[2], 0)) & MASK
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
        elif op == 'bez':
            if registers[parts[0]] == 0:
                following = int(parts[1], 0)
        elif op == 'bnez':
            if registers[parts[0]] != 0:
                following = int(parts[1], 0)
        elif op == 'bf':
            if not condition:
                following = int(parts[0], 0)
        elif op == 'br':
            following = int(parts[0], 0)
        elif op == 'bsr':
            target = int(parts[0], 0)
            if target not in CHAINS[entry]:
                raise ValueError('unexpected call to ' + operand)
            registers['r15'] = following
            raise ChainedOff(registers, model, target)
        elif op == 'bkpt':
            raise ValueError('trapped at %#x' % pc)
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def seed(reg):
    index = int(reg[1:])
    if reg == 'r14':
        return SP0
    return (0x98760000 + index * 0x111111) & MASK


# The leaf keeps the stock register plan, so every live register
# matches exactly at the chain on both sides (the pushed words carry
# the seeds identically; the chain-target rail program saves
# registers before any read).
LIVE_REGS = ('r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
             'r12', 'r14', 'r15')


def oracle(entry, r0seed, r1seed, r4seed, r5seed, ram):
    """Independent model: (outcome, chain target, regs, trace, ram).

    Stated from the decoded structure, not from decoded
    instructions. Announce: push r4/r15, read the base cell, write
    [base+0xA8]=1, select the rail id (4 unless the base already
    matches the first UART, in which case 6), then chain into
    0x1BF8 with (entry r0, base, entry r1, select).
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
            'r6': seed('r6'), 'r7': seed('r7'),
            'r12': seed('r12'), 'r14': SP0, 'r15': seed('r15')}
    if entry != ENTRY:
        raise ValueError('oracle unknown entry ' + hex(entry))
    write(SP0 - 4, regs['r4'])
    write(SP0 - 8, regs['r15'])
    regs['r14'] = SP0 - 8
    regs['r4'] = BASE_CELL
    regs['r3'] = UART_A
    base = read(BASE_CELL)
    regs['r12'] = base
    write(base + 0xa8, 1)
    regs['r2'] = 4
    regs['r3'] = 6
    if base != UART_A:
        regs['r3'] = regs['r2']
    regs['r2'] = regs['r1']
    regs['r1'] = base
    regs['r15'] = 0x10000680
    return {'outcome': 'chain', 'target': RAIL_PROG, 'regs': regs,
            'trace': trace, 'ram': ram}


SEED_PATTERNS = (
    (0x00000000, 0x00000000, 0x00000000, 0x00000000),
    (0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d),
    (0x12345678, 0x00000001, 0xa5a5a5a5, 0x5a5a5a5a),
    (0xffffffff, 0x00000000, 0x11111111, 0x22222222),
    (0x00c0ffee, 0xffffffff, 0x87654321, 0x0badf00d),
)

CELL_INITS = (0x00000000, 0x00000001, 0xffffffff)


def config_ram(base, a8_init):
    """Map the base cell, the rail-control word, and the stack."""
    ram = {BASE_CELL: base & MASK, base + 0xa8: a8_init & MASK}
    for address in range(SP0 - 16, SP0 + 16, 4):
        ram[address] = 0x51edc0de
    return ram


def battery_cases():
    # (r0, r1, r4, r5) seeds x base x rail-control init. Bases cover
    # the select-6 arm (UART_A) and the select-4 arm (UART_B); seeds
    # cover zero, repeated-word, mixed, all-ones, and sparse-bit
    # entry arguments.
    cases = []
    for regseed in SEED_PATTERNS:
        for base in (UART_A, UART_B):
            for init in CELL_INITS:
                cases.append(('announce', regseed, base, init))
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


def check_shape(source_code, entry, size):
    """Fail closed on prologue/transfer drift.

    The inline literal pool decodes as instructions, so decoded
    coverage must reach exactly entry+size. This envelope carries no
    trap word: the pool directly follows the pop-return. The
    pop-into-r15 return is dead (the chain never returns) and is
    covered by byte identity, not execution.
    """
    addresses = sorted(source_code)
    first = source_code[addresses[0]]
    if first[0] != 'push':
        raise ValueError('entry push changed: ' + repr(first))
    covered = max(addresses) + source_code[max(addresses)][2] - entry
    if covered != size:
        raise ValueError('section size changed: %d vs %d' % (covered, size))
    for op in ('rts', 'jmp', 'jmpi', 'jsr', 'bkpt'):
        hits = [pc for pc in addresses if source_code[pc][0] == op]
        if hits:
            raise ValueError('leaf keeps %s at %s'
                             % (op, [hex(pc) for pc in hits]))
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op == 'lrw':
            continue
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
    calls = [int(source_code[pc][1], 0) for pc in addresses
             if source_code[pc][0] == 'bsr']
    if calls != CALLS[entry]:
        raise ValueError('call sequence changed: %r'
                         % ([hex(c) for c in calls],))


def run_side(code, start, args, ram, entry, label):
    """Execute one side; return (chain target, registers, trace, ram).

    Both sides raise ChainedOff at the chaining call. Any unexpected
    fault is a hard failure: every reachable address is mapped and
    post-call paths are never executed.
    """
    model = Model(ram)
    try:
        execute(code, start, args, model, entry)
    except ChainedOff as done:
        return done.target, done.registers, done.model.trace, done.model.ram
    raise ValueError(label + ': side returned instead of chaining off')


def check_stock(stock):
    """Fail closed when the stock envelope drifts from the decode."""
    return {entry: sha(stock[pkg:pkg + size])
            for _, entry, pkg, size, _, _ in SPECS}


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-announce'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    announce_obj = output / 'announce_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *ANNOUNCE_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(announce_obj)], check=True)
    script = output / 'announce.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'announce.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(announce_obj), '-o', str(elf_path)], check=True)
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
    (output / 'announce.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
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
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        check_shape(source_code, entry, size)
        # Stock body only (the rail-program/dispatcher cascade stays
        # retained or reviewed elsewhere and is never executed: both
        # sides stop at the chaining branch).
        stock_code = decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=%#x' % entry,
             '--stop-address=%#x' % (entry + size), str(adjusted)], text=True))
        for case in battery_cases():
            _, regseed, base, init = case
            args = regseed
            ram = config_ram(base, init)
            want = oracle(entry, *args, ram)
            if want['outcome'] != 'chain':
                raise ValueError('battery missed the chain on %r' % (case,))
            stock_target, stock_regs, stock_trace, stock_final = run_side(
                stock_code, entry, args, ram, entry, 'stock')
            source_target, source_regs, source_trace, source_final = run_side(
                source_code, entry, args, ram, entry, 'source')
            for label, got_target, got_regs, got_trace, got_final in (
                    ('stock', stock_target, stock_regs, stock_trace, stock_final),
                    ('source', source_target, source_regs, source_trace, source_final)):
                if got_target != want['target']:
                    raise ValueError('%s chained to %#x, oracle has %#x on %r'
                                     % (label, got_target, want['target'], case))
                if got_trace != want['trace']:
                    for i, (a, b) in enumerate(zip(want['trace'], got_trace)):
                        if a != b:
                            raise ValueError(
                                '%s trace/oracle mismatch at step %d: %r vs %r on %r'
                                % (label, i, a, b, case))
                    raise ValueError('%s trace/oracle length mismatch %d vs %d on %r'
                                     % (label, len(want['trace']), len(got_trace), case))
                if got_final != want['ram']:
                    raise ValueError('%s final-RAM mismatch on %r' % (label, case))
                for reg in LIVE_REGS:
                    if got_regs[reg] != want['regs'][reg]:
                        raise ValueError('%s %s mismatch (%#x vs %#x) on %r'
                                         % (label, reg, got_regs[reg],
                                            want['regs'][reg], case))
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    report = {'s_source_sha256': sha(S_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'assemble_flags': ANNOUNCE_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no SDK register map used; the '
                                    '0x20002014 cell, the 0xA0100000 base, '
                                    'and every offset, id, and constant is a '
                                    'numeric immediate observed in the '
                                    'decoded stock flow (traptails-leaf '
                                    'precedent)',
              'upstream_files': [],
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'announce leaf only',
              'stock_equivalence_proven': False,
              'stock_envelope_shas': {hex(k): v for k, v in envelope_shas.items()},
              'handoff': {'announce_chain': hex(RAIL_PROG),
                          'post_chain_call': hex(POSTAMBLE),
                          'compared_registers': list(LIVE_REGS)},
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'The chaining callee (retained rail program into '
                         'the reviewed first PMU dispatcher) and the '
                         'post-chain postamble call are never executed '
                         'here; both sides stop at the chaining branch. '
                         'They are qualified by the reviewed pmudispatch '
                         'and postamble batteries. The cases cover finite '
                         'register seeds and rail-control inits with no '
                         'external concurrent updates. The base cell is '
                         'fixed per case. Hardware timing remains '
                         'unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-announce-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-announce-verification.json').read_text()),
        indent=2))
