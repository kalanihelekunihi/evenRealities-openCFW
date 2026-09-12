#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 railc leaf.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_railc.c against the
stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of rail/table configurations, plus an independent
Python oracle.

Leaf: the PMU rail-sequencing operation at runtime 0x10000B90, package
0xBE0, 266 bytes of code: one `pmu_fill_desc` call into a stack
descriptor (the real linked bodies run on both sides: stock fill for
stock, compiled source fill for source), entry-word gating, a
selector/status poll body with two seven-store MMIO sequences, and the
shared pop-and-check spinner (no `rts`; the function never returns).
Check#1 observes the live arg2 on the skip arm (which jumps to the
check without popping) and the popped caller r5 everywhere else, so
the caller r5 is an explicit battery input alongside the three argument
registers; later checks always expect 1 with r2 decayed to 0/1.
Compared: the complete unfiltered access trace (kind, address, width,
and value of every read and write, including pop traffic), the final
descriptor word values via the captured fill-call argument, and the
final RAM.

Behavioral equivalence only: the C synthesizes the 0x04000000 stride
with movi/tlsli where stock uses movih, folds the two stock store tails
into one selected tail, and uses branch shapes of its own. Both frames
are exactly 24 bytes with the descriptor at the base, so the pop
traffic (addresses and values, including the pushed caller registers)
is compared exactly: no stack window is excluded. The checked word on
d4-store paths is the desc[4] address itself (stock reloads it), so the
check observes a per-domain-constant address bit there. Admission rests
on decoded-trace equivalence.

The stock re-poll edge (branch back into the poll body when the check
mismatches) is intentionally not reproduced: past the pops the body
would re-read the caller frame as descriptor words, which needs the
caller (0xDDC orchestrator) frame context owned by a later tranche.
Every battery case therefore runs stock through its re-poll decision
(one pop when caller r5 mismatches the bit, two when it matches) and
compares the complete unfiltered access trace, descriptor values, and
final RAM against the source run through the same pops; the source
then keeps popping where stock re-enters the body. That divergence
past the comparison window is recorded, not silently equated.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha
from verify_gx8002_uart_stage1_pmufill import (
    oracle as fill_oracle, TABLE_BASE as FILL_TABLE_BASE,
    TABLE_ENTRIES, ENTRY_STRIDE, MAX_ID, PMU_SPLIT,
    PMU_BASE, MCU_BASE, PMUFILL_FLAGS)

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_railc.c'
FILL_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-RAILC-NOTICE.txt'
RAILC_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize',
               '-fno-jump-tables']

MASK = 0xffffffff
ENTRY = 0x10000b90
FILL = 0x10000780
SPINNER = 0x10000c5e
BBE = 0x10000bbe
SP0 = 0x20002800
WINDOW_LO = SP0 - 64
WINDOW_HI = SP0 + 512
STEP_CAP = 6000
SPIN_PASSES = 6

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_railc', 0x10000b90, 0xbe0, 266,
     'railc', 'compiled_c'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_railc 0x10000b90 : { *(.text.open_cfw_gx8002_uart_stage1_railc) }
  .text.open_cfw_gx8002_uart_stage1_pmu_fill_desc 0x10000780 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_fill_desc) }
}
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
LOAD_INDEX = re.compile(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)')

PUSH_REGS = ('r4', 'r5', 'r15')


def signed(value):
    value &= MASK
    return value - 0x100000000 if value & 0x80000000 else value


def expand_regs(operand):
    regs = []
    for part in [p.strip() for p in operand.split(',')]:
        match = re.fullmatch(r'r(\d+)-r(\d+)', part)
        if match:
            regs.extend('r%d' % i for i in range(int(match.group(1)), int(match.group(2)) + 1))
        else:
            regs.append(part)
    return regs


class Repoll(Exception):
    """Stock re-entered the poll body past the spinner checks."""

    def __init__(self, registers, desc_base, model, pops_done):
        super().__init__('repoll')
        self.registers = dict(registers)
        self.desc_base = desc_base
        self.model = model
        self.pops_done = pops_done


class Spinning(Exception):
    """Completed SPIN_PASSES spinner visits without re-polling."""

    def __init__(self, registers, desc_base, model):
        super().__init__('spinning')
        self.registers = dict(registers)
        self.desc_base = desc_base
        self.model = model


class Model:
    """Flat word RAM with byte access; unmapped addresses trap."""

    def __init__(self, ram):
        self.ram = dict(ram)
        self.trace = []

    def in_window(self, address):
        return WINDOW_LO <= address < WINDOW_HI

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

    def read_byte(self, address, sign):
        base = address & ~3
        if base not in self.ram:
            raise ValueError('unexpected read at ' + hex(address))
        raw = (self.ram[base] >> ((address & 3) * 8)) & 0xff
        self.trace.append(('read', address, 1, raw))
        if sign and raw & 0x80:
            return raw - 0x100
        return raw


def execute(code, start, args, model, spin_lo, spin_hi, repoll_pc,
            spin_passes=SPIN_PASSES, plog=None):
    """Run decoded code with r0/r1/r2=args against the model.

    args is (r0, r1, r2, caller_r5): r5 is overwritten by the entry
    sequence (it carries arg2 into the body) but the pushed copy is
    what the spinner check observes, so the caller frame value is an
    explicit input. Raises Spinning after SPIN_PASSES spinner visits,
    Repoll when a repoll_pc visit follows a spinner visit, and
    ValueError on unmapped access. When plog is a list, appends (pc,
    op) per step.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r2=args[2] & MASK, r5=args[3] & MASK, r14=SP0)
    condition = False
    desc_base = None
    seen_spin = False
    visits = 0
    pc = start
    for step in range(STEP_CAP):
        # BBE is the normal first-pass body entry; only a BBE visit
        # after the first spinner visit is a re-poll.
        if not seen_spin and spin_lo <= pc < spin_hi:
            seen_spin = True
        if seen_spin and pc == repoll_pc:
            raise Repoll(registers, desc_base, model, visits)
        if seen_spin and pc == spin_lo:
            visits += 1
            if visits > spin_passes:
                raise Spinning(registers, desc_base, model)
        op, operand, width = code[pc]
        if plog is not None:
            plog.append(pc)
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
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
        elif op == 'nor':
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
        elif op in ('tlsli', 'lsli'):
            registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & MASK
        elif op == 'lsl':
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] << (registers[parts[1]] & 31)) & MASK
            else:
                registers[parts[0]] = (registers[parts[1]] << (registers[parts[2]] & 31)) & MASK
        elif op == 'lsr':
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] >> (registers[parts[1]] & 31)) & MASK
            else:
                registers[parts[0]] = (registers[parts[1]] >> (registers[parts[2]] & 31)) & MASK
        elif op in ('tlsr', 'lsri'):
            registers[parts[0]] = (registers[parts[1]] >> int(parts[2], 0)) & MASK
        elif op == 'zext':
            registers[parts[0]] = (registers[parts[1]] >> int(parts[3], 0)) & (
                (1 << (int(parts[2], 0) - int(parts[3], 0) + 1)) - 1)
        elif op == 'zextb':
            registers[parts[0]] = registers[parts[1]] & 0xff
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
            if desc_base is None:
                desc_base = registers['r1']
            registers['r15'] = following
            following = int(parts[0], 0)
        elif op == 'rts':
            following = registers['r15']
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def outside_window(trace):
    """Drop stack-window traffic (compiler scratch slot assignment)."""
    return [entry for entry in trace if not WINDOW_LO <= entry[1] < WINDOW_HI]


def oracle(ident, arg1, arg2, caller_r5, ram):
    """Independent model: (outcome, path, desc, trace, ram).

    Stated from the decoded structure, not from decoded instructions:
    fill gate/match/domain order, entry gating, selector poll, the two
    store tails, and the first spinner check. Fill failure and
    null-entry exits observe fill exit-register leftovers, which are
    implementation-defined, so the oracle reports those as
    'leftover-dependent' without an outcome prediction.
    """
    ram = dict(ram)
    trace = []
    # Stock prologue pushes 12 bytes then frees 24 more: the fill
    # buffer starts 36 bytes below the entry stack pointer.
    desc = SP0 - 36

    def read(address, width=4):
        if width == 4:
            if address not in ram:
                raise ValueError('oracle missing cell at ' + hex(address))
            value = ram[address] & MASK
        else:
            if (address & ~3) not in ram:
                raise ValueError('oracle missing cell at ' + hex(address))
            value = (ram[address & ~3] >> ((address & 3) * 8)) & 0xff
        trace.append(('read', address, width, value))
        return value

    def write(address, value):
        if address not in ram:
            raise ValueError('oracle missing cell at ' + hex(address))
        value &= MASK
        ram[address] = value
        trace.append(('write', address, 4, value))

    for index in range(6):
        ram[desc + 4 * index] = ram.get(desc + 4 * index, 0x5a5a5a5a) & MASK
    # Entry push (saves the entry r4, the caller r5, the entry lr).
    write(SP0 - 4, seed('r4'))
    write(SP0 - 8, caller_r5)
    write(SP0 - 12, seed('r15'))
    if ident > MAX_ID:
        return {'outcome': 'leftover-dependent', 'path': 'fill-fail', 'pops': None}
    write(desc, 0)

    def read_entry(slot):
        return read(FILL_TABLE_BASE + slot * ENTRY_STRIDE)

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
            return {'outcome': 'leftover-dependent', 'path': 'fill-fail', 'pops': None}
    entry = (FILL_TABLE_BASE + slot * ENTRY_STRIDE) & MASK
    write(desc, entry)
    base, select = (PMU_BASE, 0x8c) if ident < PMU_SPLIT else (MCU_BASE, 0x88)
    for index, value in enumerate(
            [base, base | select, base | 0x18, base | 0x1c, base | 0x20], start=1):
        write(desc + 4 * index, value)
    fill_desc = [entry, base, base | select, base | 0x18, base | 0x1c, base | 0x20]

    # Stock reloads the entry pointer from its stack buffer (BA2).
    if read(desc) != entry:
        raise ValueError('descriptor round-trip changed the entry address')
    w3 = read(entry + 12)
    if w3 == 0:
        return {'outcome': 'leftover-dependent', 'path': 'null-entry',
                'desc': fill_desc, 'trace': trace, 'ram': ram, 'pops': None}
    b0 = read(w3, 1)
    if b0 == 0:
        return {'outcome': 'leftover-dependent', 'path': 'null-byte',
                'desc': fill_desc, 'trace': trace, 'ram': ram, 'pops': None}
    sel = (read(desc + 4) + b0) & MASK
    v = read(sel)
    if arg1 == (v & 0x1ffffff):
        r2check = v
        path = 'skip'
    else:
        b4 = read(entry + 4, 1)
        b4 = b4 - 0x100 if b4 & 0x80 else b4
        cond = 1 if arg2 == 0 else 0
        mcell = read(desc + 8)
        b6 = read(entry + 6, 1)
        b6 = b6 - 0x100 if b6 & 0x80 else b6
        if b4 < 0:
            r0bit = 0
        else:
            d3 = read(read(desc + 12))
            r0bit = ((d3 >> b4) & 1)
            if r0bit:
                write(read(desc + 20), (1 << b4) & MASK)
        m = read(mcell)
        r1bit = ((m >> (b6 & 31)) & 1)
        r2c = ((cond << 27) | arg1) & MASK
        r2b = (r2c | 0x06000000) & MASK
        merged = (r2c | 0x04000000) & MASK
        if r1bit:
            one = (1 << (b6 & 31)) & MASK
            write(mcell, read(mcell) & (~one & MASK))
            for value in (0x04000000, 0, 0x04000000, merged, r2b, r2b, merged):
                write(sel, value)
            m2 = read(mcell)
            write(mcell, (one | (m2 & (~one & MASK))) & MASK)
        else:
            for value in (0x04000000, 0, 0x04000000, merged, r2b, r2b, merged):
                write(sel, value)
        if r0bit:
            d4addr = read(desc + 16)
            write(d4addr, (1 << b4) & MASK)
            # The d4 reload repoints the checked word at the desc[4]
            # address itself (stock C52); the check then observes an
            # address bit, constant per domain.
            r2check = d4addr
        else:
            # bseti sets bits 25/26 only, so the check sees r2c's bit 27.
            r2check = r2c
        path = 'body-set' if r1bit else 'body-clear'
    bit = ((r2check ^ 0x08000000) >> 27) & 1
    # Pop/check sequence. Check#1 observes the live arg2 on the skip
    # (which jumps to the check without popping) and the popped caller
    # r5 everywhere else. Past check#1, r2 has decayed to 0/1, so every
    # later check expects exactly 1; check#2 observes the popped caller
    # r5, check#3+ observes caller-stack pattern (never 0/1 here), so
    # the run always re-polls by the third check at the latest.
    def pop_reads(number):
        base = SP0 - 12 + 36 * (number - 1)
        for address in (base, base + 4, base + 8):
            read(address)

    pops = 0
    if path != 'skip':
        pop_reads(1)
        pops = 1
    first_r5 = arg2 if path == 'skip' else caller_r5
    if (first_r5 & MASK) != bit:
        return {'outcome': 'repoll', 'path': path, 'desc': fill_desc,
                'trace': trace, 'ram': ram, 'pops': pops}
    # Check#1 matched: the next pop follows on every path.
    pop_reads(pops + 1)
    pops += 1
    if path == 'skip':
        # Check#2 observes the popped caller r5 and still expects 1.
        if (caller_r5 & MASK) != 1:
            return {'outcome': 'repoll', 'path': path, 'desc': fill_desc,
                    'trace': trace, 'ram': ram, 'pops': pops}
        # Check#2 matched as well: one more pop, then the pattern
        # check re-polls.
        pop_reads(pops + 1)
        pops += 1
    # Body check#2 (and skip check#3) observes caller-stack pattern,
    # which is never 0/1 here: always re-polls.
    return {'outcome': 'repoll', 'path': path, 'desc': fill_desc,
            'trace': trace, 'ram': ram, 'pops': pops}


B0BASE = 0x20003000


def config_ram(table_mode, ident, b4, b6, b0, sel_init, m_init, d3_init):
    """Build the initial RAM for one battery case.

    table_mode in ('direct', 'entry0', 'scan'). Returns (ram, slot).
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
    for i in range(TABLE_ENTRIES):
        base = FILL_TABLE_BASE + i * ENTRY_STRIDE
        ram[base] = words[i] & MASK
        ram[base + 4] = 0x5a5a5a5a
        ram[base + 8] = 0xa5a5a5a5
        ram[base + 12] = 0x5a5a5a5a
    entry = FILL_TABLE_BASE + slot * ENTRY_STRIDE
    b0addr = (B0BASE + (b0 & 0xff) * 4) & MASK
    ram[entry + 4] = ((b4 & 0xff) | (0x5a << 8) | ((b6 & 0xff) << 16) | (0xa5 << 24)) & MASK
    ram[entry + 12] = b0addr
    ram[b0addr] = ((b0 & 0xff) | (0x5a << 8) | (0xa5 << 16) | (0x5a << 24)) & MASK
    domain = PMU_BASE if ident < PMU_SPLIT else MCU_BASE
    for addr in (domain + (b0 & 0xff), domain | 0x88, domain | 0x8c,
                 domain | 0x18, domain | 0x1c, domain | 0x20):
        ram[addr] = 0xa5a5a500 + (addr & 0xff)
    ram[domain + (b0 & 0xff)] = sel_init & MASK
    mcell = domain | (0x8c if ident < PMU_SPLIT else 0x88)
    ram[mcell] = m_init & MASK
    ram[domain | 0x18] = d3_init & MASK
    for address in range(WINDOW_LO, WINDOW_HI, 4):
        ram[address] = (0x5a000000 + (address - WINDOW_LO)) & MASK
    return ram, slot


def predict_pops(ident, arg1, arg2, caller_r5, r0bit, sel_init, is_body):
    """Re-poll pop count from the decoded structure (battery selection).

    Check#1 observes arg2 on skips and caller r5 elsewhere, against bit
    27 of a path-dependent word (selector word, desc[4] address, or
    (cond<<27)|arg1). Later checks always expect 1: body check#2 sees
    pattern (pops in {1,2}), while skip check#2 still sees caller r5
    (pops in {0,1,2}).
    """
    if arg1 == (sel_init & 0x1ffffff):
        word = sel_init & MASK
    elif r0bit:
        word = (PMU_BASE if ident < PMU_SPLIT else MCU_BASE) | 0x1c
    else:
        word = (((1 if arg2 == 0 else 0) << 27) | arg1) & MASK
    bit = (((word ^ 0x08000000) >> 27) & 1)
    if is_body:
        pops = 1 + (caller_r5 == bit)
    else:
        pops = (arg2 == bit) + (arg2 == bit and caller_r5 == 1)
    return pops


def battery_cases():
    # Case: (table_mode, ident, arg2, arg1, b4, b6, b0,
    #        sel_init, m_init, d3_init, tag). The driver sweeps caller_r5
    #        over {0, 1} for every case, covering one-, two-, and
    #        three-pop re-polls on bodies and zero-, one-, and two-pop
    #        re-polls on skips.
    cases = []
    for table_mode in ('direct', 'entry0', 'scan'):
        for ident in (2, 9, 10, 20):
            domain_b0 = [4, 0x10]
            for b0 in domain_b0:
                body_sel = 0x12345678
                # Body paths: d3/m bits x b4 sign.
                for b4, b6, d3bit, mbit in (
                        (3, 7, 1, 1), (3, 7, 1, 0), (3, 7, 0, 1), (3, 7, 0, 0),
                        (0, 1, 1, 1), (31, 30, 1, 1), (-5, 7, 0, 1), (-128, -3, 0, 0)):
                    m_init = (mbit << (b6 & 31)) & MASK
                    d3_init = (d3bit << b4) & MASK if b4 >= 0 else 0xaaaaaaaa
                    arg1 = ((body_sel + 1) & 0x1ffffff) | 0x08000000
                    if (arg1 & 0x1ffffff) == (body_sel & 0x1ffffff):
                        arg1 ^= 0x00000002
                    cases.append((table_mode, ident, 0, arg1, b4, b6, b0,
                                  body_sel, m_init, d3_init, 'body-a2z'))
                # Bodies with arg2=1 and bit27(arg1)==0.
                arg1 = ((body_sel + 1) & 0x1ffffff) & ~0x08000000
                if (arg1 & 0x1ffffff) == (body_sel & 0x1ffffff):
                    arg1 ^= 0x00000002
                for b4, b6, d3bit, mbit in ((3, 7, 1, 1), (-5, 7, 0, 1)):
                    m_init = (mbit << (b6 & 31)) & MASK
                    d3_init = (d3bit << b4) & MASK if b4 >= 0 else 0xaaaaaaaa
                    cases.append((table_mode, ident, 1, arg1, b4, b6, b0,
                                  body_sel, m_init, d3_init, 'body-a2o'))
                # Skip path: arg1 matches low25; sweep arg2.
                for sel_init in (0x1a2b3c4d, 0x0a2b3c4d):
                    for arg2 in (0, 1):
                        cases.append((table_mode, ident, arg2, sel_init & 0x1ffffff,
                                      3, 7, b0, sel_init, 1 << 7, 1 << 3, 'skip'))
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
    """Fail closed on prologue/transfer drift (pops balance the push)."""
    addresses = sorted(source_code)
    if source_code[addresses[0]] != ('push', 'r4-r5, r15', 2):
        raise ValueError('prologue push changed: ' + repr(source_code[addresses[0]]))
    if source_code[addresses[1]][0] != 'subi' or 'r14' not in source_code[addresses[1]][1]:
        raise ValueError('frame subi changed: ' + repr(source_code[addresses[1]]))
    pops = [pc for pc in addresses if source_code[pc][0] == 'pop']
    if not pops or any(source_code[pc][1] != 'r4-r5, r15' for pc in pops):
        raise ValueError('spinner pops must restore exactly r4-r5, r15')
    # The spinner is exactly addi/pop/br-to-self, pinned by address
    # wherever the toolchain places it.
    spins = [pc for pc in addresses
             if source_code[pc] == ('addi', 'r14, r14, 24', 2)
             and source_code.get(pc + 2) == ('pop', 'r4-r5, r15', 2)
             and source_code.get(pc + 4, (None, None, None))[0] == 'br'
             and int(source_code[pc + 4][1], 0) == pc]
    if len(spins) != 1:
        raise ValueError('spinner shape changed: %r' % spins)
    spin = spins[0]
    calls = [pc for pc in addresses if source_code[pc][0] == 'bsr']
    if len(calls) != 1 or int(source_code[calls[0]][1], 0) != FILL:
        raise ValueError('expected one fill call to %#x' % FILL)
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('subi', 'addi') and operand.split(',')[0].strip() == 'r14' and pc not in (
                addresses[1], spin):
            raise ValueError('unexpected stack-pointer frame at %#x' % pc)
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
            # Backward body edges (the stock C94 layout artifact) are
            # allowed; non-termination would trip the execution bound
            # loudly on every affected case instead of passing silently.
        if op in ('rts', 'bkpt', 'jmp', 'jmpi', 'jsr', 'lrw'):
            raise ValueError('unexpected transfer %s at %#x' % (op, pc))
    return spin


def seed(reg):
    index = int(reg[1:])
    if reg == 'r14':
        return SP0
    return (0x98760000 + index * 0x111111) & MASK


def run_side(code, start, args, ram, spin_lo, spin_hi, repoll_pc, label,
               spin_passes=SPIN_PASSES):
    """Execute one side; return (registers, desc, trace, ram, pops).

    The stock side raises Repoll (carrying its pop count); the source
    side raises Spinning after spin_passes loop visits. Any unexpected
    fault is a hard failure: every first-pass address is mapped, and
    re-poll garbage is classified as Repoll before it executes.
    """
    model = Model(ram)
    try:
        execute(code, start, args, model, spin_lo, spin_hi, repoll_pc,
                spin_passes, None)
    except Spinning as done:
        desc = [done.model.ram[done.desc_base + 4 * index] & MASK for index in range(6)]
        return done.registers, desc, list(done.model.trace), dict(done.model.ram), None
    raise ValueError(label + ': side returned instead of spinning')


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-railc'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    railc_obj = output / 'railc_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *RAILC_FLAGS,
                    '-c', str(C_SOURCE), '-o', str(railc_obj)], check=True)
    fill_obj = output / 'fill_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                    '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
    script = output / 'railc.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'railc.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(railc_obj), str(fill_obj), '-o', str(elf_path)], check=True)
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
    # Stock body plus the stock fill it calls (the 12-byte literal pool
    # needs no decoding: objdump resolves lrw to the loaded values).
    stock_code = {}
    for lo, hi in (('0x10000b90', '0x10000c9a'), ('0x10000780', '0x10000834')):
        stock_code.update(decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=' + lo, '--stop-address=' + hi,
             str(adjusted)], text=True)))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'railc.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
    functions = []
    cases = 0
    pops_hist = {}
    for symbol, entry, offset, size, kind, ownership in SPECS:
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) > size or offset % section['align']:
            raise ValueError('candidate does not fit original placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        spin = check_shape(source_code, entry, len(payload))
        # The linked fill body executes on the source side too.
        source_all = {}
        for section_code in sources.values():
            source_all.update(section_code)
        for case in battery_cases():
            (table_mode, ident, arg2, arg1, b4, b6, b0,
             sel_init, m_init, d3_init, tag) = case
            ram, _slot = config_ram(table_mode, ident, b4, b6, b0,
                                    sel_init, m_init, d3_init)
            is_body = (arg1 != (sel_init & 0x1ffffff))
            r0bit = bool(is_body and b4 >= 0 and ((d3_init >> b4) & 1))
            for caller_r5 in (0, 1):
                want = oracle(ident, arg1, arg2, caller_r5, ram)
                expect_pops = predict_pops(ident, arg1, arg2, caller_r5,
                                           r0bit, sel_init, is_body)
                try:
                    run_side(stock_code, entry, (ident, arg1, arg2, caller_r5),
                             ram, SPINNER, 0x10000c72, BBE, 'stock')
                    raise ValueError('stock failed to re-poll on %r c5=%d'
                                     % (case, caller_r5))
                except Repoll as rep:
                    pops = rep.pops_done
                    stock_trace = list(rep.model.trace)
                    stock_final = dict(rep.model.ram)
                    stock_desc = [rep.model.ram[rep.desc_base + 4 * index] & MASK
                                  for index in range(6)]
                    stock_regs = rep.registers
                if pops != expect_pops or pops != want['pops']:
                    raise ValueError('check model wrong: pops=%d expect=%d oracle=%r on %r c5=%d'
                                     % (pops, expect_pops, want['pops'], case, caller_r5))
                if want['trace'] != stock_trace:
                    raise ValueError('stock trace/oracle mismatch on %r c5=%d'
                                     % (case, caller_r5))
                if want['desc'] != stock_desc:
                    raise ValueError('stock desc/oracle mismatch on %r c5=%d'
                                     % (case, caller_r5))
                # The oracle models the push, the fill, the body, and
                # the pops, so final RAM must agree exactly.
                if want['ram'] != stock_final:
                    for address in sorted(set(want['ram']) | set(stock_final)):
                        if want['ram'].get(address) != stock_final.get(address):
                            raise ValueError(
                                'stock ram/oracle mismatch at %#x on %r c5=%d'
                                % (address, case, caller_r5))
                src_regs, src_desc, src_trace, src_final, _ = run_side(
                    source_all, entry, (ident, arg1, arg2, caller_r5), ram,
                    spin, spin + 6, -1, 'source', pops)
                if src_trace != stock_trace:
                    raise ValueError('source trace/stock mismatch on %r c5=%d'
                                     % (case, caller_r5))
                if src_desc != stock_desc:
                    raise ValueError('source desc/stock mismatch on %r c5=%d'
                                     % (case, caller_r5))
                if src_final != stock_final:
                    raise ValueError('source ram/stock mismatch on %r c5=%d'
                                     % (case, caller_r5))
                # After pops_done pops both sides hold the same popped
                # words (pushed registers, then caller-stack pattern);
                # r6 is untouched scratch on both sides.
                for reg in ('r4', 'r5', 'r6', 'r14', 'r15'):
                    if src_regs[reg] != stock_regs[reg]:
                        raise ValueError('%s differs stock/source on %r c5=%d'
                                         % (reg, case, caller_r5))
                cases += 1
                pops_hist[pops] = pops_hist.get(pops, 0) + 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    if cases < 50:
        raise ValueError('battery admitted too few cases: %d' % cases)
    report = {'c_source_sha256': sha(C_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': RAILC_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no upstream register map is used: every '
                                    'address is a fill-provided descriptor '
                                    'value and every constant is a stock '
                                    'immediate; clean-room body from decoded '
                                    'stock flow, no SDK text reproduced',
              'functions': functions, 'target_cases': cases,
              'repoll_pops': sorted([list(item) for item in pops_hist.items()]),
              'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'rail-sequencing leaf only (first pass '
                                 'through the re-poll decision, zero to two '
                                 'pops, exact unfiltered traces)',
              'stock_equivalence_proven': False,
              'spinner': {'address': hex(SPINNER),
                          'repoll_edge': 'not reproduced past the decision: '
                                         're-poll re-reads the caller frame '
                                         'as descriptor words (0xDDC '
                                         'orchestrator context, followup); '
                                         'the C keeps popping instead'},
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Register shifts by a register count use the low 5 '
                         'bits; both sides share the executor so agreement '
                         'holds by construction, hardware shift semantics for '
                         'negative counts remain unqualified.',
                         'Fill exit-register leftovers (fill-fail, null-entry '
                         'paths) are implementation-defined and excluded; '
                         'the C keeps the same branches without an outcome claim. '
                         'Both frames are exactly 24 bytes, so pop traffic '
                         'is compared exactly with no window exclusion; '
                         'descriptor values and all other accesses are '
                         'compared exactly. Hardware timing remains '
                         'unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-railc-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-railc-verification.json').read_text()),
        indent=2))
