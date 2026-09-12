#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 beacon leaves.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_beacon.S against
the stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of register/MMIO configurations, plus an independent
Python oracle.

Leaves: the baud beacon at runtime 0x100004D0 (package 0x520, 180
bytes) and the UART bring-up at runtime 0x100005C4 (package 0x614, 92
bytes). Both are H-class flows that never return: the beacon programs
the UART block words, polls the receiver status bit, then chains into
the retained second PMU dispatcher entry (0x10000EA0) with a clock id;
the bring-up selects the UART base cell and either chains into the
beacon with (115200, 0) or runs PMU fills through the first dispatcher
(0x10000D98) and then chains into the beacon. Every terminal path of
the called dispatchers pops its frame and falls into the retained
second-dispatcher loop (no `rts`, per the pmudisp/pmusecond audits),
so the first chaining call already leaves each envelope. Compared:
byte identity of both full envelopes (the transliteration assembles
exactly to stock, so the unreachable post-call tails are covered by
identity), plus the full unfiltered access trace (kind, address,
width, and value of every read and write), the final RAM, and the live
registers from entry to the chaining call on both sides and against
the oracle.

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow with zero deviations (byte-identical). The
dispatcher cascade past the chaining branch is never executed here;
it is qualified by the reviewed pmudispatch/pmusecond/divmod
batteries, and both sides stop at the chaining branch
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
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_beacon.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-BEACON-NOTICE.txt'
BEACON_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY_BEACON = 0x100004d0
PKG_BEACON = 0x520
SIZE_BEACON = 180
TRAP_BEACON = 0x1000057e
POOL_BEACON = 0x10000580
ENTRY_BRINGUP = 0x100005c4
PKG_BRINGUP = 0x614
SIZE_BRINGUP = 92
TRAP_BRINGUP = 0x10000616
D98 = 0x10000d98
EA0 = 0x10000ea0
DIV = 0x1000013c
MOD = 0x10000180
SP0 = 0x20002800
BASE_CELL = 0x20002014
FLAG_CELL = 0x20002008
UART_A = 0xa0100000
UART_B = 0xa0200000
STEP_CAP = 20000

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_beacon', ENTRY_BEACON, PKG_BEACON,
     SIZE_BEACON, 'beacon', 'compiled_assembly'),
    ('open_cfw_gx8002_uart_stage1_bringup', ENTRY_BRINGUP, PKG_BRINGUP,
     SIZE_BRINGUP, 'bringup', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_beacon 0x100004d0 : { *(.text.open_cfw_gx8002_uart_stage1_beacon) }
  .text.open_cfw_gx8002_uart_stage1_bringup 0x100005c4 : { *(.text.open_cfw_gx8002_uart_stage1_bringup) }
}
open_cfw_gx8002_uart_boot_stage1_d98_entry = 0x10000d98;
open_cfw_gx8002_uart_boot_stage1_ea0_entry = 0x10000ea0;
open_cfw_gx8002_uart_boot_stage1_div_entry = 0x1000013c;
open_cfw_gx8002_uart_boot_stage1_mod_entry = 0x10000180;
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')

# Chaining calls admitted per entry. The div/mod bodies past the
# beacon chain are qualified by the reviewed divmod tranche and are
# never stepped into here; the bring-up's beacon call targets the
# reviewed section linked in the same ELF.
CHAINS = {
    ENTRY_BEACON: (EA0,),
    ENTRY_BRINGUP: (D98, ENTRY_BEACON),
}

# Full in-address-order call sequence per entry, pinning the
# documented post-chain (dead, never executed) calls as well.
CALLS = {
    ENTRY_BEACON: [EA0, DIV, MOD, DIV, DIV, EA0],
    ENTRY_BRINGUP: [D98, D98, D98, ENTRY_BEACON, ENTRY_BEACON],
}


class ChainedOff(Exception):
    """Reached a chaining call out of the envelope."""

    def __init__(self, registers, model, target):
        super().__init__('chained off')
        self.registers = dict(registers)
        self.model = model
        self.target = target


class Model:
    """Flat word RAM plus scripted poll reads; unmapped access traps."""

    def __init__(self, ram, poll_scripts=()):
        self.ram = dict(ram)
        self.poll_scripts = {address: list(script)
                             for address, script in poll_scripts}
        self.trace = []

    def read_word(self, address):
        if address in self.poll_scripts:
            script = self.poll_scripts[address]
            value = script[0] if len(script) == 1 else script.pop(0)
            value &= MASK
            self.trace.append(('read', address, 4, value))
            return value
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
    """Run decoded code with r0/r1/r4-r7=args against the model.

    args is (r0, r1, r4, r5, r6, r7); every other register starts from
    a fixed seed and r14 starts at entry_sp. Raises ChainedOff at a
    chaining call and ValueError on unmapped access, trap words, or
    any foreign transfer. Post-call instructions are present in the
    code map but never reached: both sides chain off first, and the
    envelopes are admitted by byte identity.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r4=args[2] & MASK, r5=args[3] & MASK,
                     r6=args[4] & MASK, r7=args[5] & MASK, r14=entry_sp)
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
        elif op == 'bseti':
            registers[parts[0]] = (registers[parts[0]] | (1 << int(parts[1], 0))) & MASK
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


# Both leaves keep the stock register plan, so every live register
# matches exactly at the chain on both sides (the pushed words carry
# the seeds identically; the chain-target dispatchers save registers
# before any read).
LIVE_REGS = ('r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
             'r12', 'r14', 'r15')


def oracle(entry, r0seed, r1seed, r4seed, r5seed, r6seed, r7seed,
           ram, poll_script=()):
    """Independent model: (outcome, chain target, regs, trace, ram).

    Stated from the decoded structure, not from decoded
    instructions. Beacon: push r4-r7/r15, read the base cell, write
    [base+0x4]=0 and [base+0x10]=3; when r1 is nonzero, poll
    [base+124] bit 0 until clear, write [base+12]=3 and [base+8]=79,
    then pop; chain into 0xEA0 with r0=17 when the base is already
    the first UART, else r0=18. Bring-up: push r4-r5/r15, read the
    flag cell; when nonzero, chain into the beacon with
    (115200, 0); otherwise select the base cell from the flag word
    (0xA0100000 unless it reads exactly 1) and chain into 0xD98
    with (16, 1).
    """
    ram = dict(ram)
    trace = []
    poll = list(poll_script)

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

    def poll_bit0(address):
        while True:
            value = poll[0] if len(poll) == 1 else poll.pop(0)
            value &= MASK
            trace.append(('read', address, 4, value))
            if not value & 1:
                return

    regs = {'r0': r0seed & MASK, 'r1': r1seed & MASK,
            'r2': seed('r2'), 'r3': seed('r3'),
            'r4': r4seed & MASK, 'r5': r5seed & MASK,
            'r6': r6seed & MASK, 'r7': r7seed & MASK,
            'r12': seed('r12'), 'r14': SP0, 'r15': seed('r15')}
    if entry == ENTRY_BEACON:
        write(SP0 - 4, regs['r4'])
        write(SP0 - 8, regs['r5'])
        write(SP0 - 12, regs['r6'])
        write(SP0 - 16, regs['r7'])
        write(SP0 - 20, regs['r15'])
        regs['r14'] = SP0 - 20
        regs['r6'] = BASE_CELL
        base = read(BASE_CELL)
        regs['r12'] = base
        regs['r4'] = regs['r0']
        write(base + 0x4, 0)
        write(base + 0x10, 3)
        if regs['r1'] != 0:
            regs['r2'] = (base + 124) & MASK
            regs['r1'] = (base + 12) & MASK
            poll_bit0(base + 124)
            write(base + 12, 3)
            write(base + 8, 79)
            regs['r15'] = read(SP0 - 20)
            regs['r7'] = read(SP0 - 16)
            regs['r6'] = read(SP0 - 12)
            regs['r5'] = read(SP0 - 8)
            regs['r4'] = read(SP0 - 4)
            regs['r14'] = SP0
        regs['r3'] = UART_A
        if base == UART_A:
            regs['r0'] = 17
            regs['r15'] = 0x1000057a
        else:
            regs['r0'] = 18
            regs['r15'] = 0x10000516
        return {'outcome': 'chain', 'target': EA0, 'regs': regs,
                'trace': trace, 'ram': ram}
    if entry == ENTRY_BRINGUP:
        write(SP0 - 4, regs['r4'])
        write(SP0 - 8, regs['r5'])
        write(SP0 - 12, regs['r15'])
        regs['r14'] = SP0 - 12
        regs['r3'] = FLAG_CELL
        regs['r5'] = regs['r0']
        flag = read(FLAG_CELL)
        regs['r2'] = flag
        regs['r4'] = regs['r1']
        if flag != 0:
            regs['r1'] = 0
            regs['r0'] = 115200
            regs['r15'] = 0x10000614
            return {'outcome': 'chain', 'target': ENTRY_BEACON,
                    'regs': regs, 'trace': trace, 'ram': ram}
        select = read(FLAG_CELL + 4)
        regs['r3'] = UART_A if select != 1 else UART_B
        regs['r2'] = BASE_CELL
        regs['r1'] = 1
        regs['r0'] = 16
        write(BASE_CELL, regs['r3'])
        regs['r15'] = 0x100005ee
        return {'outcome': 'chain', 'target': D98, 'regs': regs,
                'trace': trace, 'ram': ram}
    raise ValueError('oracle unknown entry ' + hex(entry))


SEED_PATTERNS = (
    (0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000),
    (0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d, 0x600d600d),
    (0x12345678, 0x00000001, 0xa5a5a5a5, 0x5a5a5a5a, 0xdeadbeef, 0x01010101),
    (0xffffffff, 0x00000000, 0x11111111, 0x22222222, 0x33333333, 0x44444444),
    (0x00c0ffee, 0xffffffff, 0x87654321, 0x0badf00d, 0xfeedface, 0x77aa55cc),
)

# Every script ends with bit 0 clear (hold-last); otherwise the
# polled loop would never exit on either side.
POLL_SCRIPTS = (
    [0x00000000],
    [0x00000001, 0x00000000],
    [0x00000001, 0x00000001, 0x00000001, 0x00000000],
    [0xffffffff, 0x00000001, 0x00000000],
    [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000040],
)

CELL_INITS = (0x00000000, 0xffffffff)


def config_beacon_ram(base, cell_init):
    """Map the base cell, the four beacon control words, and the stack."""
    ram = {BASE_CELL: base & MASK}
    for offset in (0x4, 0x10, 0x0c, 0x08):
        ram[base + offset] = cell_init & MASK
    for address in range(SP0 - 24, SP0 + 16, 4):
        ram[address] = 0x51edc0de
    return ram


def config_bringup_ram(flag, select):
    """Map the flag/select cells, the base cell, and the stack."""
    ram = {FLAG_CELL: flag & MASK, FLAG_CELL + 4: select & MASK,
           BASE_CELL: 0x51edc0de}
    for address in range(SP0 - 16, SP0 + 16, 4):
        ram[address] = 0x51edc0de
    return ram


def battery_cases():
    # Beacon: (r0, r1, r4, r5, r6, r7) seeds x base x poll script x
    # cell init. Seed patterns cover r1 == 0 (rows 0 and 3) and
    # r1 != 0 (rows 1, 2, and 4); bases cover the 0xEA0 id-17 arm
    # (UART_A) and the id-18 arm (UART_B).
    # Bring-up: (r0, r1, r4, r5) seeds x flag x select. Flags cover
    # the beacon-chain path (nonzero) and the dispatcher-chain path
    # (zero); selects cover UART_A (0, 2, 0xffffffff) and UART_B (1).
    cases = []
    for regseed in SEED_PATTERNS:
        for base in (UART_A, UART_B):
            for script in POLL_SCRIPTS:
                for init in CELL_INITS:
                    cases.append(('beacon', regseed, base, script, init))
    for regseed in SEED_PATTERNS[:4]:
        for flag in (0x00000000, 0x00000001, 0xdeadbeef):
            for select in (0x00000000, 0x00000001, 0x00000002, 0xffffffff):
                cases.append(('bringup', regseed, flag, select))
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


def check_shape(source_code, entry, size, trap):
    """Fail closed on prologue/transfer drift.

    The inline literal pools decode as instructions, so decoded
    coverage must reach exactly entry+size. The single zero trap word
    decodes as `bkpt` (the pools past it keep disassembly going) and
    must sit exactly at the known trap address; its bytes are
    additionally pinned by payload check plus byte identity in
    verify(). It is never executed on either side.
    """
    addresses = sorted(source_code)
    first = source_code[addresses[0]]
    if first[0] != 'push':
        raise ValueError('entry push changed: ' + repr(first))
    covered = max(addresses) + source_code[max(addresses)][2] - entry
    if covered != size:
        raise ValueError('section size changed: %d vs %d' % (covered, size))
    for op in ('rts', 'jmp', 'jmpi', 'jsr'):
        hits = [pc for pc in addresses if source_code[pc][0] == op]
        if hits:
            raise ValueError('leaf keeps %s at %s'
                             % (op, [hex(pc) for pc in hits]))
    bkpts = [pc for pc in addresses if source_code[pc][0] == 'bkpt']
    if bkpts != [trap]:
        raise ValueError('trap word moved: %s' % [hex(pc) for pc in bkpts])
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


def run_side(code, start, args, ram, poll, entry, label):
    """Execute one side; return (chain target, registers, trace, ram).

    Both sides raise ChainedOff at a chaining call. Any unexpected
    fault is a hard failure: every reachable address is mapped and
    post-call paths are never executed.
    """
    model = Model(ram, poll)
    try:
        execute(code, start, args, model, entry)
    except ChainedOff as done:
        return done.target, done.registers, done.model.trace, done.model.ram
    raise ValueError(label + ': side returned instead of chaining off')


def check_stock(stock):
    """Fail closed when a stock envelope drifts from the decode."""
    return {entry: sha(stock[pkg:pkg + size])
            for _, entry, pkg, size, _, _ in SPECS}


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-beacon'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    beacon_obj = output / 'beacon_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *BEACON_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(beacon_obj)], check=True)
    script = output / 'beacon.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'beacon.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(beacon_obj), '-o', str(elf_path)], check=True)
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
    (output / 'beacon.disassembly.txt').write_text(disassembly)
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
        trap_off = (TRAP_BEACON if entry == ENTRY_BEACON
                    else TRAP_BRINGUP) - entry
        if payload[trap_off:trap_off + 2] != b'\x00\x00':
            raise ValueError('missing trap word: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        check_shape(source_code, entry, size,
                    TRAP_BEACON if entry == ENTRY_BEACON else TRAP_BRINGUP)
        # Stock body only (the dispatcher/beacon cascade stays retained
        # or reviewed elsewhere and is never executed: both sides stop
        # at the chaining branch).
        stock_code = decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=%#x' % entry,
             '--stop-address=%#x' % (entry + size), str(adjusted)], text=True))
        for case in battery_cases():
            if case[0] != kind:
                continue
            if kind == 'beacon':
                _, regseed, base, script, init = case
                args = regseed
                ram = config_beacon_ram(base, init)
                poll = [((base + 124) & MASK, list(script))]
            else:
                _, regseed, flag, select = case
                args = (regseed[0], regseed[1], regseed[2],
                        regseed[3], seed('r6'), seed('r7'))
                ram = config_bringup_ram(flag, select)
                poll = []
            if kind == 'beacon':
                want = oracle(entry, *args, ram, poll_script=script)
            else:
                want = oracle(entry, *args, ram)
            if want['outcome'] != 'chain':
                raise ValueError('battery missed the chain on %r' % (case,))
            stock_target, stock_regs, stock_trace, stock_final = run_side(
                stock_code, entry, args, ram, poll, entry, 'stock')
            source_target, source_regs, source_trace, source_final = run_side(
                source_code, entry, args, ram, poll, entry, 'source')
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
              'assemble_flags': BEACON_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no SDK register map used; the '
                                    '0x20002008/0x20002014 cells, the '
                                    '0xA0100000/0xA0200000 bases, and every '
                                    'offset, id, and constant is a numeric '
                                    'immediate observed in the decoded stock '
                                    'flow (traptails-leaf precedent)',
              'upstream_files': [],
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'baud-beacon and bring-up leaves only',
              'stock_equivalence_proven': False,
              'stock_envelope_shas': {hex(k): v for k, v in envelope_shas.items()},
              'handoff': {'beacon_chain': hex(EA0),
                          'bringup_chains': [hex(D98), hex(ENTRY_BEACON)],
                          'compared_registers': list(LIVE_REGS)},
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'The chaining callees (PMU dispatchers, div/mod, the '
                         'beacon itself for the bring-up path) are never '
                         'executed here; both sides stop at the chaining '
                         'branch. They are qualified by the reviewed '
                         'pmudispatch/pmusecond/divmod batteries. Poll loops '
                         'are verified only over finite scripts with '
                         'hold-last and no external concurrent updates. The '
                         'base/flag cells are fixed per case. Hardware '
                         'timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-beacon-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-beacon-verification.json').read_text()),
        indent=2))

