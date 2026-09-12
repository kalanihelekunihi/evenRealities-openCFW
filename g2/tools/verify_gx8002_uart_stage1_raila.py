#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 raila leaf.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_raila.S against the
stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of rail/table configurations, plus an independent
Python oracle.

Leaf: the PMU rail-sequencing operation at runtime 0x10000860, package
0x8B0, 464 bytes of code (460 + one shared 4-byte literal-pool word
holding 0x20002018, which is the fill entry-table base, not an
immediate): entry id/arg1 gating, one `pmu_fill_desc` call into a
24-byte stack descriptor (the real linked bodies run on both sides:
stock fill for stock, compiled source fill for source), entry-byte
gating, an m-cell bit test, an id bit-table gate, a descriptor-table
combined test, id-gated merge/store arms, a divisor retry dispatcher,
a bit-mask retry check, and the shared fail tail that cycles the
shift and re-enters the body (no `rts`; the function never returns).

Compared: the complete unfiltered access trace (kind, address, width,
and value of every read and write, including push/pop/drift traffic),
the final RAM, and all registers at the stop point. The retry and
fail paths drift the frame up the caller stack (36 bytes per
pop-and-retry); the battery maps a tall caller window with pattern
words so every drifted access stays defined.

Stop rule (identical on stock, source, and oracle sides): the run
ends after FAIL_VISITS visits to the fail re-entry (0x10000978), after
FILL_CALLS fill calls (bound for first-pass fill-retry chains), or at
the first unmapped access. The stop kind must agree on all three
sides. Unmapped accesses are legitimate outcomes here, not battery
errors: the merge/store arms overwrite the entry-pointer register
with mask/table bytes, so later fail-loop iterations read wild but
deterministic addresses (same pc and address required on all sides).

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow (it assembles byte-identically when linked at
its runtime entry, which corroborates the transcription but is not
the admission claim). Entry id > 25, fill failure, and entry byte 6
== 0xFF reach the fail tail with unset address registers and trap on
the re-entry read; those arms observe implementation-defined state
and are excluded from the battery (the assembly keeps the same
branches without an outcome claim there).
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha
from verify_gx8002_uart_stage1_pmufill import (
    TABLE_BASE as FILL_TABLE_BASE,
    TABLE_ENTRIES, ENTRY_STRIDE, MAX_ID, PMU_SPLIT,
    PMU_BASE, MCU_BASE, PMUFILL_FLAGS)

ROOT = Path(__file__).resolve().parents[1]
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_raila.S'
FILL_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-RAILA-NOTICE.txt'
RAILA_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY = 0x10000860
FILL = 0x10000780
FAILRE = 0x10000978
DISP = 0x10000922
SP0 = 0x20002800
STACK_LO = SP0 - 64
STACK_HI = SP0 + 16384
T_MARGIN = 64
STEP_SAFETY = 200000
FAIL_VISITS = 260
FILL_CALLS = 60

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_raila', 0x10000860, 0x8b0, 464,
     'raila', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_raila 0x10000860 : { *(.text.open_cfw_gx8002_uart_stage1_raila) }
  .text.open_cfw_gx8002_uart_stage1_pmu_fill_desc 0x10000780 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_fill_desc) }
}
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
LOAD_INDEX = re.compile(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)')

PUSH_REGS = ('r4', 'r5', 'r15')

# Oracle block -> set of stock pcs that can fault there (used to
# cross-check trap points; a trap inside the fill range is allowed
# for the 'fill' block on either side, since stock and source run
# different fill bodies at the same base).
FILL_LO, FILL_HI = 0x10000780, 0x10000834
BLOCK_PCS = {
    'entry': set(),
    'fill': 'fill-range',
    'gate': {0x10000882, 0x10000888, 0x10000894},
    'bitest': {0x1000089a},
    'idtable': set(),
    'descpoll': {0x100008ba, 0x100008c0, 0x100008cc, 0x100008dc},
    'idgate': {0x100008f6},
    'merge': {0x10000902, 0x10000914, 0x10000918, 0x1000091c},
    'popdisp': {0x10000920},
    'disp': set(),
    'asr': set(),
    'poll2': {0x10000932, 0x10000934, 0x10000936},
    'foldrot': {0x1000094a, 0x10000958, 0x1000095e},
    'check': set(),
    'fail': {0x10000976},
    'failre': set(),
    'store78': {0x10000982, 0x10000996, 0x1000099a, 0x1000099e,
                0x100009a0, 0x100009a4, 0x100009a8, 0x100009ac,
                0x100009bc, 0x100009cc, 0x100009d0, 0x100009e6,
                0x100009ea},
    'stored5': {0x10000a02, 0x10000a04},
    'storearg': {0x10000a0c, 0x10000a14, 0x10000a18, 0x10000a26},
}


def trap_pc_ok(block, pc):
    """Whether pc is a faultable instruction of the oracle block."""
    pcs = BLOCK_PCS.get(block)
    if pcs == 'fill-range':
        return FILL_LO <= pc < FILL_HI
    return pcs is not None and pc in pcs


def signed(value):
    value &= MASK
    return value - 0x100000000 if value & 0x80000000 else value


def trunc_div(a, b):
    """C-SKY divs semantics: truncated signed division."""
    if b == 0:
        raise ValueError('division by zero')
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q & MASK


def expand_regs(operand):
    regs = []
    for part in [p.strip() for p in operand.split(',')]:
        match = re.fullmatch(r'r(\d+)-r(\d+)', part)
        if match:
            regs.extend('r%d' % i for i in range(int(match.group(1)), int(match.group(2)) + 1))
        else:
            regs.append(part)
    return regs


class MemFault(ValueError):
    """Unmapped access (a legitimate stop kind for this leaf)."""

    def __init__(self, address, is_write):
        super().__init__('unmapped %s at %s'
                         % ('write' if is_write else 'read', hex(address)))
        self.address = address & MASK
        self.is_write = is_write


class Stopped(Exception):
    """The routine reached a stop condition (it never returns)."""

    def __init__(self, kind, registers, fill_bases, model, trap_pc=None,
                 trap_addr=None):
        super().__init__(kind)
        self.kind = kind
        self.registers = dict(registers)
        self.fill_bases = list(fill_bases)
        self.model = model
        self.trap_pc = trap_pc
        self.trap_addr = trap_addr


class Model:
    """Flat word RAM with byte/halfword access; unmapped addresses trap."""

    def __init__(self, ram):
        self.ram = dict(ram)
        self.trace = []

    def read_word(self, address):
        address &= MASK
        if address not in self.ram:
            raise MemFault(address, False)
        value = self.ram[address] & MASK
        self.trace.append(('read', address, 4, value))
        return value

    def write_word(self, address, value):
        address &= MASK
        if address not in self.ram:
            raise MemFault(address, True)
        value &= MASK
        self.ram[address] = value
        self.trace.append(('write', address, 4, value))

    def read_half(self, address):
        address &= MASK
        base = address & ~3
        if base not in self.ram:
            raise MemFault(address, False)
        if (address & 3) == 3:
            raise MemFault(address, False)
        raw = (self.ram[base] >> ((address & 3) * 8)) & 0xffff
        self.trace.append(('read', address, 2, raw))
        return raw

    def read_byte(self, address, sign):
        address &= MASK
        base = address & ~3
        if base not in self.ram:
            raise MemFault(address, False)
        raw = (self.ram[base] >> ((address & 3) * 8)) & 0xff
        self.trace.append(('read', address, 1, raw))
        if sign and raw & 0x80:
            return raw - 0x100
        return raw


def execute(code, start, args, model, plog=None):
    """Run decoded code with r0/r1/r2=args against the model.

    args is (r0, r1, r2). r5 is the entry id on paths that never pop
    (entry-direct dispatcher) and the popped entry-seed or caller
    pattern afterwards; every popped word is mapped, so no caller
    state is an input beyond the mapped RAM. Always raises Stopped
    with kind 'fail-cycle' (FAIL_VISITS fail re-entries), 'fill-cap'
    (FILL_CALLS fill calls, bounding first-pass fill-retry chains),
    or 'trap' (first unmapped access, with pc and address); the step
    safety net must never trigger. When plog is a list, appends the
    pc per step.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r2=args[2] & MASK, r14=SP0)
    condition = False
    fill_bases = []
    visits = 0
    fills = 0
    pc = start
    for _step in range(STEP_SAFETY):
        if pc == FAILRE:
            visits += 1
            if visits > FAIL_VISITS:
                raise Stopped('fail-cycle', registers, fill_bases, model)
        try:
            op, operand, width = code[pc]
        except KeyError:
            raise Stopped('trap', registers, fill_bases, model,
                          trap_pc=pc, trap_addr=pc)
        if plog is not None:
            plog.append(pc)
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        try:
            if op == 'movi':
                registers[parts[0]] = int(parts[1], 0) & MASK
            elif op == 'movih':
                registers[parts[0]] = (int(parts[1], 0) << 16) & MASK
            elif op == 'mov':
                registers[parts[0]] = registers[parts[1]]
            elif op == 'mvcv':
                registers[parts[0]] = int(not condition) & MASK
            elif op == 'push':
                for reg in expand_regs(operand):
                    registers['r14'] = (registers['r14'] - 4) & MASK
                    model.write_word(registers['r14'], registers[reg])
            elif op == 'pop':
                for reg in reversed(expand_regs(operand)):
                    registers[reg] = model.read_word(registers['r14'])
                    registers['r14'] = (registers['r14'] + 4) & MASK
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
            elif op == 'subu':
                registers[parts[0]] = (registers[parts[1]] - registers[parts[2]]) & MASK
            elif op == 'or':
                if len(parts) == 2:
                    registers[parts[0]] = (registers[parts[0]] | registers[parts[1]]) & MASK
                else:
                    registers[parts[0]] = (registers[parts[1]] | registers[parts[2]]) & MASK
            elif op == 'ori':
                registers[parts[0]] = (registers[parts[1]] | int(parts[2], 0)) & MASK
            elif op == 'and':
                if len(parts) == 2:
                    registers[parts[0]] = (registers[parts[0]] & registers[parts[1]]) & MASK
                else:
                    registers[parts[0]] = (registers[parts[1]] & registers[parts[2]]) & MASK
            elif op == 'andi':
                if len(parts) == 3:
                    registers[parts[0]] = (registers[parts[1]] & int(parts[2], 0)) & MASK
                else:
                    registers[parts[0]] = (registers[parts[0]] & int(parts[1], 0)) & MASK
            elif op == 'andn':
                if len(parts) == 2:
                    registers[parts[0]] = (registers[parts[0]] & ~registers[parts[1]]) & MASK
                else:
                    registers[parts[0]] = (registers[parts[1]] & ~registers[parts[2]]) & MASK
            elif op == 'nor':
                if len(parts) == 2:
                    registers[parts[0]] = (~registers[parts[1]]) & MASK
                else:
                    registers[parts[0]] = (~(registers[parts[1]] | registers[parts[2]])) & MASK
            elif op == 'xor':
                if len(parts) == 2:
                    registers[parts[0]] = (registers[parts[0]] ^ registers[parts[1]]) & MASK
                else:
                    registers[parts[0]] = (registers[parts[1]] ^ registers[parts[2]]) & MASK
            elif op == 'bseti':
                if len(parts) == 2:
                    registers[parts[0]] = (registers[parts[0]] | (1 << int(parts[1], 0))) & MASK
                else:
                    registers[parts[0]] = (registers[parts[1]] | (1 << int(parts[2], 0))) & MASK
            elif op in ('lsl', 'tlsl'):
                # gas spells the stock tlsr/tlsl encodings lsl/lsr;
                # objdump prints both back as tlsr/tlsl, so both
                # spellings arrive here with identical semantics.
                if len(parts) == 2:
                    registers[parts[0]] = (registers[parts[0]] << (registers[parts[1]] & 31)) & MASK
                else:
                    registers[parts[0]] = (registers[parts[1]] << (registers[parts[2]] & 31)) & MASK
            elif op in ('lsr', 'tlsr'):
                if len(parts) == 2:
                    registers[parts[0]] = (registers[parts[0]] >> (registers[parts[1]] & 31)) & MASK
                else:
                    try:
                        count = int(parts[2], 0)
                    except ValueError:
                        count = registers[parts[2]] & 31
                    registers[parts[0]] = (registers[parts[1]] >> count) & MASK
            elif op in ('tlsli', 'lsli'):
                registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & MASK
            elif op == 'lsri':
                registers[parts[0]] = (registers[parts[1]] >> int(parts[2], 0)) & MASK
            elif op == 'asri':
                registers[parts[0]] = (signed(registers[parts[1]]) >> int(parts[2], 0)) & MASK
            elif op == 'divs':
                registers[parts[0]] = trunc_div(signed(registers[parts[1]]),
                                               signed(registers[parts[2]]))
            elif op == 'rotl':
                if len(parts) == 2:
                    count = registers[parts[1]] & 31
                    value = registers[parts[0]]
                else:
                    count = registers[parts[2]] & 31
                    value = registers[parts[1]]
                registers[parts[0]] = ((value << count) | (value >> ((32 - count) & 31))) & MASK
            elif op == 'zext':
                registers[parts[0]] = (registers[parts[1]] >> int(parts[3], 0)) & (
                    (1 << (int(parts[2], 0) - int(parts[3], 0) + 1)) - 1)
            elif op == 'zextb':
                registers[parts[0]] = registers[parts[1]] & 0xff
            elif op == 'zexth':
                registers[parts[0]] = registers[parts[1]] & 0xffff
            elif op == 'sextb':
                raw = registers[parts[1]] & 0xff
                registers[parts[0]] = (raw - 0x100) & MASK if raw & 0x80 else raw
            elif op in ('inct', 'incf'):
                take = condition if op == 'inct' else not condition
                if take:
                    registers[parts[0]] = (registers[parts[1]] + int(parts[2], 0)) & MASK
            elif op == 'cmphs':
                condition = registers[parts[0]] >= registers[parts[1]]
            elif op == 'cmphsi':
                condition = registers[parts[0]] >= int(parts[1], 0)
            elif op == 'cmplti':
                condition = signed(registers[parts[0]]) < int(parts[1], 0)
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
            elif op == 'lrw':
                registers[parts[0]] = int(parts[1], 0) & MASK
            elif op == 'ld.b':
                match = LOAD_STORE.fullmatch(operand)
                address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
                registers[match.group(1)] = model.read_byte(address, False)
            elif op in ('ld.bs',):
                match = LOAD_STORE.fullmatch(operand)
                address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
                registers[match.group(1)] = model.read_byte(address, True) & MASK
            elif op == 'ld.h':
                match = LOAD_STORE.fullmatch(operand)
                address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
                registers[match.group(1)] = model.read_half(address)
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
            elif op == 'blz':
                if signed(registers[parts[0]]) < 0:
                    following = int(parts[1], 0)
            elif op == 'bt':
                if condition:
                    following = int(parts[0], 0)
            elif op == 'bf':
                if not condition:
                    following = int(parts[0], 0)
            elif op == 'br':
                following = int(parts[0], 0)
            elif op == 'bsr':
                if int(parts[0], 0) != FILL:
                    raise ValueError('unexpected call to ' + operand)
                fills += 1
                if fills > FILL_CALLS:
                    raise Stopped('fill-cap', registers, fill_bases, model)
                fill_bases.append(registers['r1'])
                registers['r15'] = following
                following = int(parts[0], 0)
            elif op == 'rts':
                following = registers['r15']
            else:
                raise ValueError('unsupported instruction: ' + op)
        except MemFault as fault:
            raise Stopped('trap', registers, fill_bases, model,
                          trap_pc=pc, trap_addr=fault.address)
        pc = following
    raise ValueError('execution bound exceeded')


def seed(reg):
    index = int(reg[1:])
    if reg == 'r14':
        return SP0
    return (0x98760000 + index * 0x111111) & MASK


def oracle(ident, arg1, arg2, ram):
    """Independent model: (outcome, block/path, trace, ram, regs).

    Stated from the decoded structure as label-block emulation, not
    from decoded instructions: entry gating, fill entry scan, m-cell
    bit test, id bit-table gate, descriptor-table combined test,
    merge/store arms, divisor dispatcher, bit-mask check, fail tail
    with shift cycling, and the entry-table polls. Every register the
    stock body touches (r0-r5, r12, r13, r18, r19, sp, r15) is tracked
    exactly, so fail-cycle and fill-cap stops compare full register
    files. Outcomes: 'fail-cycle', 'fill-cap', or 'trap' (with block
    and address); 'leftover-dependent' for the id-range, fill-fail,
    and entry-6-0xFF arms, which the battery never executes.
    """
    model = Model(dict(ram))
    regs = {f'r{i}': seed(f'r{i}') for i in range(32)}
    regs.update(r0=ident & MASK, r1=arg1 & MASK, r2=arg2 & MASK, r14=SP0)
    sp = SP0
    block = 'entry'
    fillcalls = 0
    failvisits = 0
    body_ran = False
    regs['r12'] = seed('r12')
    regs['r13'] = seed('r13')
    out = {'trace': model.trace, 'ram': model.ram, 'regs': regs}

    def set_sp(value):
        nonlocal sp
        sp = value & MASK
        regs['r14'] = sp

    def pop3():
        r15 = model.read_word(sp)
        r5 = model.read_word(sp + 4)
        r4 = model.read_word(sp + 8)
        set_sp(sp + 12)
        return r4, r5, r15

    def fill_at(desc, fid):
        """The proven fill traffic shape (cf. the fill pilot): fast
        id-range guard with no traffic, then zero desc[0], scan the
        entry table, store the descriptor words. The fill id is the
        current r5: the entry id on direct/first fills, a popped
        caller seed or pattern word (fast-fail) on retries, since
        the entry push saves the caller registers before r5 takes
        the id."""
        if fid > MAX_ID:
            return None
        model.write_word(desc, 0)

        def read_entry(slot):
            return model.read_word(FILL_TABLE_BASE + slot * ENTRY_STRIDE)

        if read_entry(fid) == (fid & MASK):
            slot = fid
        elif read_entry(0) == (fid & MASK):
            slot = 0
        else:
            slot = None
            for candidate in range(1, TABLE_ENTRIES):
                if read_entry(candidate) == (fid & MASK):
                    slot = candidate
                    break
            if slot is None:
                return None
        entry = (FILL_TABLE_BASE + slot * ENTRY_STRIDE) & MASK
        model.write_word(desc, entry)
        base, select = (PMU_BASE, 0x8c) if fid < PMU_SPLIT else (MCU_BASE, 0x88)
        for index, value in enumerate(
                [base, base | select, base | 0x18, base | 0x1c, base | 0x20], start=1):
            model.write_word(desc + 4 * index, value)
        return entry

    try:
        while True:
            if block == 'entry':
                model.write_word(sp - 4, regs['r4'])
                model.write_word(sp - 8, regs['r5'])
                model.write_word(sp - 12, regs['r15'])
                set_sp(sp - 36)
                regs['r5'] = ident & MASK
                regs['r4'] = arg1 & MASK
                if ident > MAX_ID:
                    return {'outcome': 'leftover-dependent', 'path': 'id-range',
                            **out}
                if arg1 == 2:
                    block = 'check'
                elif arg1 >= 3:
                    block = 'disp'
                else:
                    block = 'fill'
            elif block == 'fill':
                fillcalls += 1
                if fillcalls > FILL_CALLS:
                    return {'outcome': 'fill-cap', 'path': 'fill-chain',
                            'fills': fillcalls, **out}
                entry = fill_at(sp, regs['r5'])
                if entry is None:
                    if body_ran:
                        # Retry fill with a drifted caller id: the real
                        # fill fast-fails, bnez takes the fail tail with
                        # the previous body registers still live.
                        block = 'fail'
                        continue
                    return {'outcome': 'leftover-dependent', 'path': 'fill-fail',
                            **out}
                regs['r0'] = 0
                regs['r15'] = 0x1000087e
                block = 'gate'
            elif block == 'gate':
                regs['r13'] = model.read_word(sp)
                raw = model.read_byte(regs['r13'] + 6, True)
                if raw == -1:
                    return {'outcome': 'leftover-dependent',
                            'path': 'entry6-ff', **out}
                regs['r1'] = raw & MASK
                regs['r12'] = model.read_word(sp + 8)
                body_ran = True
                if regs['r4'] == 2:
                    block = 'failre'
                else:
                    block = 'bitest'
            elif block == 'bitest':
                regs['r2'] = model.read_word(regs['r12'])
                regs['r2'] = ((regs['r2'] >> (regs['r1'] & 31)) & 1)
                if regs['r2'] == regs['r4']:
                    block = 'popdisp'
                else:
                    block = 'idtable'
            elif block == 'idtable':
                if regs['r5'] >= 23:
                    block = 'poll2'
                elif (((0x490000 >> (regs['r5'] & 31)) & 1) == 0):
                    block = 'poll2'
                else:
                    block = 'descpoll'
            elif block == 'descpoll':
                d3addr = model.read_word(sp + 12)
                regs['r18'] = model.read_word(d3addr)
                t1 = (FILL_TABLE_BASE
                      + ((((regs['r5'] + 1) & MASK) << 4) & MASK)) & MASK
                s1 = model.read_byte(t1 + 5, True)
                t2 = (FILL_TABLE_BASE
                      + ((((regs['r5'] + 2) & MASK) << 4) & MASK)) & MASK
                s2 = model.read_byte(t2 + 5, True)
                regs['r2'] = ((regs['r18'] >> (s1 & 31)) & MASK)
                regs['r18'] = ((regs['r18'] >> (s2 & 31)) & MASK)
                regs['r2'] = ((regs['r2'] & regs['r18']) & MASK)
                regs['r2'] = (((~regs['r2']) & MASK) & 1)
                if regs['r2'] == 0:
                    block = 'foldrot'
                else:
                    block = 'idgate'
            elif block == 'idgate':
                regs['r2'] = model.read_byte(regs['r13'] + 4, True) & MASK
                if ((regs['r5'] - 7) & MASK) >= 2:
                    if regs['r4'] == 1:
                        block = 'storearg'
                    else:
                        block = 'merge'
                else:
                    block = 'store78'
            elif block == 'merge':
                regs['r18'] = model.read_word(regs['r12'])
                regs['r13'] = ((1 << (regs['r1'] & 31)) & MASK)
                regs['r13'] = (regs['r18'] & (~regs['r13'] & MASK)) & MASK
                regs['r1'] = ((regs['r4'] << (regs['r1'] & 31)) & MASK)
                regs['r1'] = (regs['r1'] | regs['r13']) & MASK
                model.write_word(regs['r12'], regs['r1'])
                regs['r1'] = model.read_word(sp + 16)
                regs['r3'] = ((1 << (regs['r2'] & 31)) & MASK)
                model.write_word(regs['r1'], regs['r3'])
                block = 'popdisp'
            elif block == 'popdisp':
                set_sp(sp + 24)
                r4, r5, _r15 = pop3()
                regs['r4'] = r4
                regs['r5'] = r5
                block = 'disp'
            elif block == 'disp':
                if regs['r0'] == 7:
                    block = 'asr'
                elif regs['r0'] != 8:
                    block = 'fail'
                else:
                    regs['r4'] = trunc_div(signed(regs['r1']), 6)
                    block = 'fill'
            elif block == 'asr':
                regs['r4'] = (signed(regs['r1']) >> 2) & MASK
                block = 'fill'
            elif block == 'poll2':
                d3addr = model.read_word(sp + 12)
                regs['r2'] = model.read_word(d3addr)
                s3 = model.read_byte(regs['r13'] + 5, True)
                regs['r2'] = ((regs['r2'] >> (s3 & 31)) & MASK)
                regs['r2'] = (((~regs['r2']) & MASK) & 1)
                if regs['r2'] != 0:
                    block = 'idgate'
                else:
                    block = 'foldrot'
            elif block == 'foldrot':
                regs['r3'] = ((0 - 2) & MASK)
                regs['r2'] = model.read_word(regs['r12'])
                count = regs['r1'] & 31
                regs['r3'] = (((regs['r3'] << count)
                               | (regs['r3'] >> ((32 - count) & 31))) & MASK)
                regs['r3'] = (regs['r3'] & regs['r2']) & MASK
                regs['r1'] = ((regs['r4'] << (regs['r1'] & 31)) & MASK)
                regs['r3'] = (regs['r3'] | regs['r1']) & MASK
                model.write_word(regs['r12'], regs['r3'])
                set_sp(sp + 24)
                r4, r5, _r15 = pop3()
                regs['r4'] = r4
                regs['r5'] = r5
                block = 'check'
            elif block == 'check':
                if regs['r0'] >= 10:
                    block = 'fail'
                elif (((1 << (regs['r0'] & 31)) & 583) != 0):
                    block = 'fill'
                else:
                    block = 'fail'
            elif block == 'fail':
                regs['r0'] = (0 - 1) & MASK
                set_sp(sp + 24)
                r4, r5, _r15 = pop3()
                regs['r4'] = r4
                regs['r5'] = r5
                block = 'failre'
            elif block == 'failre':
                failvisits += 1
                if failvisits > FAIL_VISITS:
                    return {'outcome': 'fail-cycle', 'path': 'fail-loop',
                            'visits': failvisits, **out}
                regs['r1'] = (regs['r1'] + 1) & MASK
                low = regs['r1'] & 0xff
                regs['r1'] = (low - 0x100) & MASK if low & 0x80 else low
                regs['r4'] = 1
                block = 'bitest'
            elif block == 'store78':
                regs['r18'] = model.read_word(regs['r12'])
                regs['r13'] = ((1 << (regs['r1'] & 31)) & MASK)
                regs['r13'] = (regs['r18'] & (~regs['r13'] & MASK)) & MASK
                regs['r1'] = ((regs['r4'] << (regs['r1'] & 31)) & MASK)
                regs['r4'] = (regs['r1'] | regs['r13']) & MASK
                model.write_word(regs['r12'], regs['r4'])
                regs['r1'] = model.read_word(sp + 16)
                regs['r3'] = ((1 << (regs['r2'] & 31)) & MASK)
                model.write_word(regs['r1'], regs['r3'])
                d3addr = model.read_word(sp + 12)
                regs['r18'] = model.read_word(d3addr)
                regs['r12'] = model.read_word(regs['r12'])
                s = model.read_byte(FILL_TABLE_BASE + 0x26, True)
                regs['r2'] = ((regs['r12'] >> (s & 31)) & 1)
                if regs['r2'] == 0:
                    block = 'popdisp'
                    continue
                s = model.read_byte(FILL_TABLE_BASE + 0x25, True)
                regs['r2'] = ((regs['r18'] >> (s & 31)) & 1)
                if regs['r2'] == 0:
                    block = 'popdisp'
                    continue
                regs['r13'] = model.read_byte(FILL_TABLE_BASE + 0x86, True)
                s = model.read_byte(FILL_TABLE_BASE + 0x85, True)
                regs['r13'] = ((regs['r12'] >> (regs['r13'] & 31)) & MASK)
                regs['r2'] = ((regs['r18'] >> (s & 31)) & MASK)
                regs['r13'] = (regs['r13'] | regs['r2']) & MASK
                regs['r13'] = regs['r13'] & 1
                if regs['r13'] == 0:
                    block = 'stored5'
                    continue
                s = model.read_byte(FILL_TABLE_BASE + 0x76, True)
                s2 = model.read_byte(FILL_TABLE_BASE + 0x75, True)
                regs['r2'] = ((regs['r12'] >> (s & 31)) & MASK)
                regs['r18'] = ((regs['r18'] >> (s2 & 31)) & MASK)
                regs['r2'] = (regs['r2'] | regs['r18']) & MASK
                regs['r2'] = regs['r2'] & 1
                regs['r1'] = s2 & MASK
                if regs['r2'] != 0:
                    block = 'popdisp'
                else:
                    block = 'stored5'
            elif block == 'stored5':
                d5addr = model.read_word(sp + 20)
                model.write_word(d5addr, regs['r3'])
                block = 'popdisp'
            elif block == 'storearg':
                d5addr = model.read_word(sp + 20)
                regs['r3'] = ((regs['r4'] << (regs['r2'] & 31)) & MASK)
                model.write_word(d5addr, regs['r3'])
                regs['r3'] = model.read_word(regs['r12'])
                regs['r1'] = ((regs['r4'] << (regs['r1'] & 31)) & MASK)
                regs['r4'] = (regs['r3'] & (~regs['r1'] & MASK)) & MASK
                regs['r1'] = (regs['r1'] | regs['r4']) & MASK
                model.write_word(regs['r12'], regs['r1'])
                block = 'popdisp'
            else:
                raise ValueError('unknown oracle block ' + block)
    except MemFault as fault:
        return {'outcome': 'trap', 'block': block, 'addr': fault.address,
                **out}


B0BASE = 0x20003000


def config_ram(table_mode, ident, b4, b5, b6, neigh, fixed, m_init,
               d3_init):
    """Build the initial RAM for one battery case.

    table_mode in ('direct', 'entry0', 'scan'). neigh is
    ((n1b5, n1b6), (n2b5, n2b6)) for entries ident+1/ident+2;
    fixed is ((f2b5, f2b6), (f7b5, f7b6), (f8b5, f8b6)) for entries
    2/7/8, which the table-poll arms read as bytes 5/6. Other
    entries carry pattern bytes. Returns (ram, slot).
    """
    words = {}
    if table_mode == 'direct':
        for i in range(TABLE_ENTRIES):
            words[i] = i
        slot = ident
    elif table_mode == 'entry0':
        for i in range(TABLE_ENTRIES):
            words[i] = 0x70000000 + i
        words[0] = ident
        slot = 0
    else:
        for i in range(TABLE_ENTRIES):
            words[i] = 0x70000000 + i
        slot = 13 if ident != 13 else 14
        words[slot] = ident
    ram = {}
    entry = FILL_TABLE_BASE + slot * ENTRY_STRIDE
    for i in range(TABLE_ENTRIES):
        base = FILL_TABLE_BASE + i * ENTRY_STRIDE
        ram[base] = words[i] & MASK
        if base == entry:
            ram[base + 4] = ((b4 & 0xff) | ((b5 & 0xff) << 8)
                             | ((b6 & 0xff) << 16) | (0xa5 << 24)) & MASK
        else:
            ram[base + 4] = ((i & 0xff) | (((i * 3 + 1) & 0xff) << 8)
                             | (((i * 5 + 2) & 0xff) << 16) | (0xa5 << 24)) & MASK
        ram[base + 8] = (B0BASE + 16) & MASK
        ram[base + 12] = 0x5a5a5a5a
    ram[B0BASE + 16] = (4 | (0 << 8) | (0 << 16)) & MASK
    # Neighbor entries ident+1/ident+2 (bytes 5/6 read by descpoll).
    for offset, (nb5, nb6) in enumerate(neigh, start=1):
        nbase = FILL_TABLE_BASE + (ident + offset) * ENTRY_STRIDE
        word = ram.get(nbase + 4, 0x5a5a5a5a)
        ram[nbase + 4] = ((word & 0xff) | ((nb5 & 0xff) << 8)
                          | ((nb6 & 0xff) << 16) | (0xa5 << 24)) & MASK
    # Fixed entries 2/7/8 (bytes 5/6 read by the tpoll arms). These
    # win over the owned entry bytes when ident is 2, 7, or 8; the
    # battery sides stay consistent since the table is what it is.
    for fslot, (fb5, fb6) in zip((2, 7, 8), fixed):
        fbase = FILL_TABLE_BASE + fslot * ENTRY_STRIDE
        word = ram.get(fbase + 4, 0x5a5a5a5a)
        ram[fbase + 4] = ((word & 0xff) | ((fb5 & 0xff) << 8)
                          | ((fb6 & 0xff) << 16) | (0xa5 << 24)) & MASK
    domain = PMU_BASE if ident < PMU_SPLIT else MCU_BASE
    for base in (PMU_BASE, MCU_BASE):
        for addr in range(base, base + 0x100, 4):
            ram[addr] = (0xa5a5a500 + (addr & 0xff)) & MASK
    mcell = domain | (0x8c if ident < PMU_SPLIT else 0x88)
    ram[mcell] = m_init & MASK
    ram[domain | 0x18] = d3_init & MASK
    for address in range(STACK_LO, STACK_HI, 4):
        if address not in ram:
            ram[address] = (0x5a000000 + (address - STACK_LO)) & MASK
    for address in range(FILL_TABLE_BASE + TABLE_ENTRIES * ENTRY_STRIDE,
                         FILL_TABLE_BASE + TABLE_ENTRIES * ENTRY_STRIDE + T_MARGIN,
                         4):
        if address not in ram:
            ram[address] = (0x5a000000 + (address - FILL_TABLE_BASE)) & MASK
    return ram, slot


def pass_shift(value):
    """A shift selecting a zero bit of value (for deep-table crafting)."""
    if value == 0:
        return 0
    return ((value.bit_length()) & 31)


def deep_tables(m_init, d3_init):
    """Neighbor/fixed table bytes that pass every poll stage.

    Targets the idgate (descpoll combined test nonzero) and the
    stored5 latch (all tpoll stages clear). Requires single-bit (or
    zero) m/d3 words, i.e. the md=set battery shape.
    """
    nbit = pass_shift(m_init) if m_init != 0 else 0
    m_byte = (m_init.bit_length() - 1) & 31 if m_init != 0 else 0
    d_byte = pass_shift(d3_init)
    neigh = ((0, m_byte), (0, (m_byte + 1) & 31))
    # f7b6 carries m_byte (not nbit): when ident == 7 the fixed bytes
    # clobber the owned entry, and the bit test needs m_bit == b6 to
    # reach the store arm. f7 never gates the stored5 path (stage 4
    # only runs when stage 3 is nonzero), so this costs no coverage.
    fixed = ((0, m_byte), (d_byte, m_byte), (d_byte, nbit))
    return neigh, fixed


SHALLOW_NEIGH = ((0, 0), (0, 0))
SHALLOW_FIXED = ((0, 0), (0, 0), (0, 0))


def battery_cases():
    # Case: (table_mode, ident, arg2, arg1, b4, b5, b6, neigh, fixed,
    #        m_init, d3_init). arg2 is dead on every path and is swept
    #        on a subset to prove it. Entry byte 6 == 0xFF never
    #        appears (leftover arm); idents stay in 0..25 (id-range
    #        arm is leftover).
    cases = []
    bsets = {'A': (3, 0x5a, 7), 'B': (31, 0x7f, 0x80)}
    # P1: direct fill (arg1 in {0,1}); arg1 0 takes merge, 1 takes
    # the storearg arm; idents cover the bit-table in/out sets,
    # the {7,8} store arm, and the 23+ poll boundary.
    p1_idents = (1, 2, 6, 7, 8, 9, 16, 19, 22, 23, 25)
    for table_mode in ('direct', 'scan'):
        for ident in p1_idents:
            for arg1 in (0, 1):
                for bkey in ('A', 'B'):
                    b4, b5, b6 = bsets[bkey]
                    for md in ('set', 'clear'):
                        if md == 'set':
                            m_init = (1 << (b6 & 31)) & MASK
                            d3_init = ((1 << (b4 & 31)) & MASK
                                       if b4 >= 0 else 0xaaaaaaaa)
                        else:
                            m_init = 0xa5a5a500 & (~(1 << (b6 & 31)) & MASK)
                            d3_init = 0
                        cases.append((table_mode, ident, 0, arg1, b4, b5,
                                      b6, SHALLOW_NEIGH, SHALLOW_FIXED,
                                      m_init, d3_init))
    # P1 deep: table bytes crafted to pass the descpoll combined
    # test and the full tpoll chain (stored5 latch).
    for ident in (2, 7, 8, 16):
        for arg1 in (0, 1):
            b4, b5, b6 = bsets['A']
            m_init = (1 << (b6 & 31)) & MASK
            d3_init = (1 << (b4 & 31)) & MASK
            neigh, fixed = deep_tables(m_init, d3_init)
            cases.append(('direct', ident, 0, arg1, b4, b5, b6, neigh,
                          fixed, m_init, d3_init))
    # P2: bit-mask check (arg1 == 2); idents cover mask bits
    # {0,1,2,6,9} (retry) and the >= 10 fail plus others.
    for table_mode in ('direct', 'scan'):
        for ident in (0, 1, 2, 6, 9, 10, 11, 25):
            b4, b5, b6 = bsets['A']
            m_init = (1 << (b6 & 31)) & MASK
            d3_init = (1 << (b4 & 31)) & MASK
            cases.append((table_mode, ident, 0, 2, b4, b5, b6,
                          SHALLOW_NEIGH, SHALLOW_FIXED, m_init, d3_init))
    for ident in (2, 6):
        b4, b5, b6 = bsets['A']
        m_init = (1 << (b6 & 31)) & MASK
        d3_init = (1 << (b4 & 31)) & MASK
        neigh, fixed = deep_tables(m_init, d3_init)
        cases.append(('direct', ident, 0, 2, b4, b5, b6, neigh, fixed,
                      m_init, d3_init))
    # P3: divisor dispatcher (arg1 >= 3, no first fill); id 7
    # shifts, 8 divides, others fail at once.
    for table_mode in ('direct', 'scan'):
        for ident in (0, 7, 8, 9, 25):
            for arg1 in (3, 12):
                b4, b5, b6 = bsets['A']
                m_init = (1 << (b6 & 31)) & MASK
                d3_init = (1 << (b4 & 31)) & MASK
                cases.append((table_mode, ident, 0, arg1, b4, b5, b6,
                              SHALLOW_NEIGH, SHALLOW_FIXED, m_init, d3_init))
    for ident in (7, 8):
        b4, b5, b6 = bsets['A']
        m_init = (1 << (b6 & 31)) & MASK
        d3_init = (1 << (b4 & 31)) & MASK
        neigh, fixed = deep_tables(m_init, d3_init)
        cases.append(('direct', ident, 0, 12, b4, b5, b6, neigh, fixed,
                      m_init, d3_init))
    # entry0 table spot checks.
    for ident in (2, 16):
        b4, b5, b6 = bsets['A']
        m_init = (1 << (b6 & 31)) & MASK
        d3_init = (1 << (b4 & 31)) & MASK
        cases.append(('entry0', ident, 0, 0, b4, b5, b6, SHALLOW_NEIGH,
                      SHALLOW_FIXED, m_init, d3_init))
    # arg2 is dead: same setup with three arg2 values must agree.
    b4, b5, b6 = bsets['A']
    m_init = (1 << (b6 & 31)) & MASK
    d3_init = (1 << (b4 & 31)) & MASK
    for arg2 in (1, 0xa5a5a5a5):
        cases.append(('direct', 2, arg2, 0, b4, b5, b6, SHALLOW_NEIGH,
                      SHALLOW_FIXED, m_init, d3_init))
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
    """Fail closed on prologue/transfer drift."""
    addresses = sorted(source_code)
    if source_code[addresses[0]] != ('push', 'r4-r5, r15', 2):
        raise ValueError('prologue push changed: ' + repr(source_code[addresses[0]]))
    if source_code[addresses[1]][0] != 'subi' or 'r14' not in source_code[addresses[1]][1]:
        raise ValueError('frame subi changed: ' + repr(source_code[addresses[1]]))
    covered = max(addresses) + source_code[max(addresses)][2] - entry
    if covered != size:
        raise ValueError('section size changed: %d vs %d' % (covered, size))
    pops = [pc for pc in addresses if source_code[pc][0] == 'pop']
    if len(pops) != 3 or any(source_code[pc][1] != 'r4-r5, r15' for pc in pops):
        raise ValueError('expected exactly three pops of r4-r5, r15')
    frames = [pc for pc in addresses
              if source_code[pc][0] in ('subi', 'addi')
              and source_code[pc][1].split(',')[0].strip() == 'r14']
    if len(frames) != 4:
        raise ValueError('frame-pointer sites changed: %r' % frames)
    calls = [pc for pc in addresses if source_code[pc][0] == 'bsr']
    if len(calls) != 1 or int(source_code[calls[0]][1], 0) != FILL:
        raise ValueError('expected one fill call to %#x' % FILL)
    lrws = [pc for pc in addresses if source_code[pc][0] == 'lrw']
    if len(lrws) != 2 or any(source_code[pc][1] != 'r1, 0x20002018'
                             and source_code[pc][1] != 'r19, 0x20002018'
                             for pc in lrws):
        raise ValueError('literal-pool loads changed: %r' % lrws)
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
        if op in ('rts', 'bkpt', 'jmp', 'jmpi', 'jsr'):
            raise ValueError('unexpected transfer %s at %#x' % (op, pc))
    return FAILRE


def run_side(code, start, args, ram, label):
    """Execute one side; return (kind, registers, traces, ram, extra).

    Both sides always raise Stopped. Any unexpected fault is a hard
    failure: every reachable address is mapped and leftover paths are
    never executed.
    """
    model = Model(ram)
    try:
        execute(code, start, args, model, None)
    except Stopped as done:
        return (done.kind, done.registers, list(done.model.trace),
                dict(done.model.ram), (done.trap_pc, done.trap_addr,
                                       list(done.fill_bases)))
    raise ValueError(label + ': side returned instead of stopping')


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-raila'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    raila_obj = output / 'raila_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *RAILA_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(raila_obj)], check=True)
    fill_obj = output / 'fill_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                    '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
    script = output / 'raila.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'raila.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(raila_obj), str(fill_obj), '-o', str(elf_path)], check=True)
    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    # Analysis-only slice wrapper: the stage-1 span is rewrapped with the
    # CK804EF ELF flags and shifted to its runtime base so decoded branch
    # targets are absolute (see gx8002-uart-boot-stage1-cd001-analysis.md).
    # No stock bytes enter the assembled source objects.
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
    # Stock body plus the stock fill it calls (the literal pool needs
    # no decoding: objdump resolves lrw to the loaded value).
    stock_code = {}
    for lo, hi in (('0x10000860', '0x10000a30'), ('0x10000780', '0x10000834')):
        stock_code.update(decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=' + lo, '--stop-address=' + hi,
             str(adjusted)], text=True)))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'raila.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
    functions = []
    cases = 0
    kinds = {}
    for symbol, entry, offset, size, kind, ownership in SPECS:
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) != size or offset % section['align']:
            raise ValueError('candidate does not exactly fill its placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        check_shape(source_code, entry, len(payload))
        # The linked fill body executes on the source side too.
        source_all = {}
        for section_code in sources.values():
            source_all.update(section_code)
        for case in battery_cases():
            (table_mode, ident, arg2, arg1, b4, b5, b6, neigh, fixed,
             m_init, d3_init) = case
            ram, _slot = config_ram(table_mode, ident, b4, b5, b6, neigh,
                                    fixed, m_init, d3_init)
            want = oracle(ident, arg1, arg2, ram)
            if want['outcome'] == 'leftover-dependent':
                raise ValueError('battery hit a leftover path on %r' % (case,))
            stock_kind, stock_regs, stock_trace, stock_final, stock_xtra = run_side(
                stock_code, entry, (ident, arg1, arg2), ram, 'stock')
            if want['outcome'] != stock_kind:
                raise ValueError(
                    'stock kind/oracle mismatch: %s vs %s on %r'
                    % (stock_kind, want['outcome'], case))
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
            if stock_kind != 'trap':
                for reg in ['r%d' % i for i in range(32)] + ['r14']:
                    if want['regs'][reg] != stock_regs[reg]:
                        raise ValueError('oracle reg %s mismatch on %r' % (reg, case))
            else:
                if (want['block'] is None
                        or not trap_pc_ok(want['block'], stock_xtra[0])
                        or want['addr'] != stock_xtra[1]):
                    raise ValueError(
                        'stock trap/oracle mismatch: pc %#x addr %#x vs block %s addr %#x on %r'
                        % (stock_xtra[0], stock_xtra[1], want['block'],
                           want['addr'], case))
            src_kind, src_regs, src_trace, src_final, src_xtra = run_side(
                source_all, entry, (ident, arg1, arg2), ram,
                'source')
            if src_kind != stock_kind:
                raise ValueError(
                    'source kind/stock mismatch: %s vs %s on %r'
                    % (src_kind, stock_kind, case))
            if src_trace != stock_trace:
                for i, (a, b) in enumerate(zip(src_trace, stock_trace)):
                    if a != b:
                        raise ValueError(
                            'source trace/stock mismatch at step %d: %r vs %r on %r'
                            % (i, a, b, case))
                raise ValueError('source trace/stock length mismatch %d vs %d on %r'
                                 % (len(src_trace), len(stock_trace), case))
            if src_final != stock_final:
                raise ValueError('source ram/stock mismatch on %r' % (case,))
            if stock_kind != 'trap':
                for reg in ['r%d' % i for i in range(32)] + ['r14']:
                    if src_regs[reg] != stock_regs[reg]:
                        raise ValueError('%s differs stock/source on %r'
                                         % (reg, case))
            else:
                if src_xtra[0] != stock_xtra[0] or src_xtra[1] != stock_xtra[1]:
                    raise ValueError('source trap/stock mismatch on %r' % (case,))
            kinds[stock_kind] = kinds.get(stock_kind, 0) + 1
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    if cases < 200:
        raise ValueError('battery admitted too few cases: %d' % cases)
    report = {'c_source_sha256': sha(S_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': RAILA_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no upstream register map is used: every '
                                    'address is a fill-provided descriptor '
                                    'value and every constant is a stock '
                                    'immediate; clean-room body from decoded '
                                    'stock flow, no SDK text reproduced',
              'functions': functions, 'target_cases': cases,
              'stop_kinds': kinds,
              'fail_visits': FAIL_VISITS,
              'fill_calls': FILL_CALLS,
              'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'rail-sequencing operation A only (body plus '
                                 'bounded fail-loop/fill-chain window, exact '
                                 'unfiltered traces)',
              'stock_equivalence_proven': False,
              'leftover_paths': 'id-range, fill-fail, and entry-6-0xFF arms '
                                'reach the fail tail with unset address '
                                'registers and are excluded from the battery; '
                                'the assembly keeps the same branches without '
                                'an outcome claim there.',
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Register shifts by a register count use the low 5 '
                         'bits; both sides share the executor so agreement '
                         'holds by construction, hardware shift semantics for '
                         'negative counts remain unqualified.',
                         'Signed division truncates toward zero and the '
                         'divisor is always the nonzero constant 6 on '
                         'executed paths; both sides share the executor so '
                         'agreement holds by construction, hardware divide '
                         'semantics remain unqualified.',
                         'Trap stops compare pc, address, traces, and RAM '
                         'but not the full register file: register leftovers '
                         'at a wild access are implementation-defined.',
                         'Both frames drift up the caller stack on '
                         'retry/fail paths; every drifted word is mapped '
                         'with pattern values and compared exactly with no '
                         'window exclusion. Hardware timing remains '
                         'unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-raila-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-raila-verification.json').read_text()),
        indent=2))


