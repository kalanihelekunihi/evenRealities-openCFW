#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 handshake leaf.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_handshake.S against
the stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of register/stack configurations, plus an independent
Python oracle.

Leaf: the UART handshake at runtime 0x100006D8 (package 0x728, 168
bytes). It runs the rail-configure tail (0x1000046C) first, then two
PMU bit reads (0x100003A4/0x100003B0) gating the UART bring-up call
(0x100005C4), a TX-empty-polled "GET" transmit, an RX match against
'O' then the retained table at 0x10001E5C, and a delay call
(0x100003FC) on empty-budget retries, ending in a pop-trap tail. The
rail-configure tail is H-class (its first dispatcher call already
leaves its envelope and the dispatcher cascade never returns, per the
traptails/pmudisp/pmusecond audits), so the first chaining call
already leaves this envelope. Compared: byte identity of the full
envelope (the transliteration assembles exactly to stock, so the
unreachable post-call tail -- the PMU bit reads, bring-up calls,
"GET"/"OK" exchange, delay call, and pop-trap -- is covered by
identity), plus the full unfiltered access trace (kind, address,
width, and value of every read and write), the final RAM, and the
live registers from entry to the chaining call on both sides and
against the oracle.

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow with zero deviations (byte-identical). The
rail-configure/dispatcher cascade past the chaining branch is never
executed here; it is qualified by the reviewed traptails (288 cases),
pmudispatch (8,370 cases), and pmusecond (2,688 cases) batteries, and
both sides stop at the chaining branch (uartcfg/traptails-leaf
precedent). Hardware timing remains unqualified.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_handshake.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-HANDSHAKE-NOTICE.txt'
HANDSHAKE_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY = 0x100006d8
PKG = 0x728
SIZE = 168
POOL_START = 0x10000774
TRAP_PC = 0x10000772
NEXT = 0x10000780
RAILCFG = 0x1000046c
GET0 = 0x100003a4
GET1 = 0x100003b0
BRINGUP = 0x100005c4
MDELAY = 0x100003fc
SP0 = 0x20002800
STEP_CAP = 20000

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_handshake', ENTRY, PKG,
     SIZE, 'handshake', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_handshake 0x100006d8 : { *(.text.open_cfw_gx8002_uart_stage1_handshake) }
}
open_cfw_gx8002_uart_boot_stage1_46c_entry = 0x1000046c;
open_cfw_gx8002_uart_boot_stage1_3a4_entry = 0x100003a4;
open_cfw_gx8002_uart_boot_stage1_3b0_entry = 0x100003b0;
open_cfw_gx8002_uart_boot_stage1_5c4_entry = 0x100005c4;
open_cfw_gx8002_uart_boot_stage1_3fc_entry = 0x100003fc;
'''

# The chaining call admitted for this entry. The rail-configure tail
# past the chain is qualified by the reviewed traptails battery
# (straight-line prefix into 0x10000D98, noreturn cascade) and is
# never stepped into here.
CHAINS = {
    ENTRY: (RAILCFG,),
}

# Full in-address-order call sequence, pinning the documented
# post-chain (dead, never executed) PMU/bring-up/delay calls as well.
CALLS = {
    ENTRY: [RAILCFG, GET0, GET1, BRINGUP, BRINGUP, MDELAY],
}

# Literal pool words the assembler must emit at the section end,
# matching the stock pool at 0x10000774..0x1000077F.
POOLS = (0x20002010, 0x20002014, 0x10001e5c)


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
    """Run decoded code with r0/r1/r4-r9=args against the model.

    args is (r0, r1, r4, r5, r6, r7, r8, r9); every other register
    starts from a fixed seed and r14 starts at entry_sp. Raises
    ChainedOff at the chaining call and ValueError on unmapped
    access, trap words, or any foreign transfer. Post-call
    instructions are present in the code map but never reached: both
    sides chain off first, and the envelope is admitted by byte
    identity.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r4=args[2] & MASK, r5=args[3] & MASK,
                     r6=args[4] & MASK, r7=args[5] & MASK,
                     r8=args[6] & MASK, r9=args[7] & MASK,
                     r14=entry_sp)
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
        elif op == 'push':
            for reg in expand_regs(operand):
                registers['r14'] = (registers['r14'] - 4) & MASK
                model.write_word(registers['r14'], registers[reg])
        elif op == 'pop':
            for reg in reversed(expand_regs(operand)):
                registers[reg] = model.read_word(registers['r14'])
                registers['r14'] = (registers['r14'] + 4) & MASK
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
# the seeds identically; the chain-target rail-configure tail saves
# registers before any read).
LIVE_REGS = ('r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8',
             'r9', 'r12', 'r14', 'r15')

PUSH_ORDER = ('r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r15')


def oracle(entry, args, ram, entry_sp=SP0):
    """Independent model: (outcome, chain target, regs, trace, ram).

    Stated from the decoded structure, not from decoded
    instructions. Handshake: push r4-r9/r15, then chain into 0x46C
    with entry registers unchanged.
    """
    ram = dict(ram)
    trace = []

    def write(address, value):
        if address not in ram:
            raise ValueError('oracle missing cell at ' + hex(address))
        value &= MASK
        ram[address] = value
        trace.append(('write', address, 4, value))

    regs = {f'r{i}': seed(f'r{i}') for i in range(32)}
    regs.update(r0=args[0] & MASK, r1=args[1] & MASK,
                r4=args[2] & MASK, r5=args[3] & MASK,
                r6=args[4] & MASK, r7=args[5] & MASK,
                r8=args[6] & MASK, r9=args[7] & MASK,
                r14=entry_sp)
    if entry != ENTRY:
        raise ValueError('oracle unknown entry ' + hex(entry))
    for index, reg in enumerate(PUSH_ORDER):
        write(entry_sp - 4 * (index + 1), regs[reg])
    regs['r14'] = entry_sp - 4 * len(PUSH_ORDER)
    regs['r15'] = 0x100006de
    return {'outcome': 'chain', 'target': RAILCFG, 'regs': regs,
            'trace': trace, 'ram': ram}


SEED_PATTERNS = (
    (0x00000000, 0x00000000, 0x00000000, 0x00000000,
     0x00000000, 0x00000000, 0x00000000, 0x00000000),
    (0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d,
     0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d),
    (0x12345678, 0x00000001, 0xa5a5a5a5, 0x5a5a5a5a,
     0xdeadbeef, 0x00c0ffee, 0x87654321, 0x0badf00d),
    (0xffffffff, 0x00000000, 0x11111111, 0x22222222,
     0x33333333, 0x44444444, 0x55555555, 0x66666666),
    (0x00c0ffee, 0xffffffff, 0x87654321, 0x0badf00d,
     0x10203040, 0x50607080, 0x90a0b0c0, 0xd0e0f000),
)

SP_OFFSETS = (0, 32, 64)


def config_ram(entry_sp):
    """Map the stack window around the entry stack pointer."""
    ram = {}
    for address in range(entry_sp - 48, entry_sp + 16, 4):
        ram[address] = 0x51edc0de
    return ram


def battery_cases():
    # Seed patterns x stack-pointer offsets. The live prefix performs
    # zero MMIO traffic (seven frame pushes only), so cases vary the
    # pushed register seeds and the stack base.
    cases = []
    for regseed in SEED_PATTERNS:
        for offset in SP_OFFSETS:
            cases.append(('handshake', regseed, SP0 - offset))
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


def check_shape(source_code, entry, size, payload):
    """Fail closed on prologue/transfer/pool drift.

    The trap word decodes as `bkpt` (pinned to TRAP_PC) and the pool
    words past POOL_START decode as instructions, so decoded coverage
    reaches exactly entry+size. Decoded pool words are data, pinned
    by explicit word values plus byte identity, not control flow.
    """
    addresses = sorted(source_code)
    first = source_code[addresses[0]]
    if first[0] != 'push':
        raise ValueError('entry push changed: ' + repr(first))
    covered = max(addresses) + source_code[max(addresses)][2] - entry
    if covered != size:
        raise ValueError('section size changed: %d vs %d' % (covered, size))
    for pc in addresses:
        op = source_code[pc][0]
        if op in ('rts', 'jmp', 'jmpi', 'jsr'):
            raise ValueError('leaf keeps %s at %s' % (op, hex(pc)))
        if op == 'bkpt' and pc != TRAP_PC:
            raise ValueError('unexpected trap at %s' % hex(pc))
    if payload[TRAP_PC - entry:TRAP_PC - entry + 2] != b'\x00\x00':
        raise ValueError('trap word changed')
    pool_bytes = payload[POOL_START - entry:]
    if len(pool_bytes) != 12:
        raise ValueError('pool length changed: %d' % len(pool_bytes))
    words = struct.unpack('<III', pool_bytes)
    if words != POOLS:
        raise ValueError('pool contents changed: %r' % (words,))
    for pc in addresses:
        if pc >= POOL_START:
            continue
        op, operand, _ = source_code[pc]
        if op == 'lrw':
            continue
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
    calls = [int(source_code[pc][1], 0) for pc in addresses
             if source_code[pc][0] == 'bsr' and pc < POOL_START]
    if calls != CALLS[entry]:
        raise ValueError('call sequence changed: %r'
                         % ([hex(c) for c in calls],))


def run_side(code, start, args, ram, entry, label, entry_sp):
    """Execute one side; return (chain target, registers, trace, ram).

    Both sides raise ChainedOff at the chaining call. Any unexpected
    fault is a hard failure: every reachable address is mapped and
    post-call paths are never executed.
    """
    model = Model(ram)
    try:
        execute(code, start, args, model, entry, entry_sp)
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
    output = output or ROOT / 'build/gx8002-uart-stage1-handshake'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    handshake_obj = output / 'handshake_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *HANDSHAKE_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(handshake_obj)], check=True)
    script = output / 'handshake.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'handshake.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(handshake_obj), '-o', str(elf_path)], check=True)
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
    (output / 'handshake.disassembly.txt').write_text(disassembly)
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
        check_shape(source_code, entry, size, payload)
        # Stock body only (the rail-configure/dispatcher cascade stays
        # retained or reviewed elsewhere and is never executed: both
        # sides stop at the chaining branch).
        stock_code = decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=%#x' % entry,
             '--stop-address=%#x' % (entry + size), str(adjusted)], text=True))
        for case in battery_cases():
            _, regseed, entry_sp = case
            args = regseed
            ram = config_ram(entry_sp)
            want = oracle(entry, args, ram, entry_sp)
            if want['outcome'] != 'chain':
                raise ValueError('battery missed the chain on %r' % (case,))
            stock_target, stock_regs, stock_trace, stock_final = run_side(
                stock_code, entry, args, ram, entry, 'stock', entry_sp)
            source_target, source_regs, source_trace, source_final = run_side(
                source_code, entry, args, ram, entry, 'source', entry_sp)
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
              'assemble_flags': HANDSHAKE_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no SDK register map used; the '
                                    '0x20002010/0x20002014 cells, the '
                                    '0x10001E5C table address, and every '
                                    'offset and constant is a numeric '
                                    'immediate observed in the decoded '
                                    'stock flow (traptails-leaf precedent)',
              'upstream_files': [],
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'handshake leaf only',
              'stock_equivalence_proven': False,
              'stock_envelope_shas': {hex(k): v for k, v in envelope_shas.items()},
              'handoff': {'handshake_chain': hex(RAILCFG),
                          'post_chain_calls': [hex(c) for c in CALLS[ENTRY][1:]],
                          'compared_registers': list(LIVE_REGS)},
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'The chaining callee (reviewed rail-configure tail '
                         'into the reviewed PMU dispatchers) and the '
                         'post-chain PMU/bring-up/delay calls are never '
                         'executed here; both sides stop at the chaining '
                         'branch. They are qualified by the reviewed '
                         'traptails, pmudispatch, and pmusecond batteries. '
                         'The cases cover finite register seeds and stack '
                         'bases with no external concurrent updates. '
                         'Hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-handshake-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-handshake-verification.json').read_text()),
        indent=2))
