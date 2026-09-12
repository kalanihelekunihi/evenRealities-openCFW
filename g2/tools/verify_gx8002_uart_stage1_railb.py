#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 railb leaf.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_railb.S against the
stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of rail/table configurations, plus an independent
Python oracle.

Leaf: the PMU rail-sequencing operation at runtime 0x10000A30, package
0xA80, 350 bytes of code: one `pmu_fill_desc` call into a stack
descriptor (the real linked bodies run on both sides: stock fill for
stock, compiled source fill for source), entry-word gating, a
selector/status poll body with MMIO store sequences, and the shared
pop-and-update loop (no `rts`; the function never returns). Compared:
the complete unfiltered access trace (kind, address, width, and value
of every read and write, including push/pop traffic), the final
descriptor word values via the captured fill-call argument, all
registers at the stop point, and the final RAM.

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow (it assembles byte-identically when linked at
its runtime entry, which corroborates the transcription but is not the
admission claim). Both frames are exactly 24 bytes with the descriptor
at the base, so the pop traffic is compared exactly: no stack window
is excluded. Admission rests on decoded-trace equivalence.

The loop never exits, so every battery case runs both sides through
the body plus exactly LOOP_PASSES loop passes and compares the full
traces. The popped caller registers are never observed by the loop
(no branch reads them after a pop), so the caller frame only needs to
be mapped: every caller word holds a scratch address, which also keeps
the per-pass latch stores mapped. Fill failure, null entry words, and
the selector-match arm run with implementation-defined registers and
are excluded from the battery (the assembly keeps the same branches
without an outcome claim there); the general-form bit-length poll and
nonzero entry shift/mask are unreachable through the fill contract
(the fill matches entry word 0 against the full id, forcing entry
bytes 1..3 to zero) and are covered by transcription identity plus the
oracle structure, not by executed cases.
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
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_railb.S'
FILL_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-RAILB-NOTICE.txt'
RAILB_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY = 0x10000a30
FILL = 0x10000780
LOOP_TOP = 0x10000b4e
SP0 = 0x20002800
SCRATCH = 0x20002900
WINDOW_LO = SP0 - 64
WINDOW_HI = SP0 + 512
STEP_CAP = 4000
LOOP_PASSES = 4

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_railb', 0x10000a30, 0xa80, 350,
     'railb', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_railb 0x10000a30 : { *(.text.open_cfw_gx8002_uart_stage1_railb) }
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


class Looped(Exception):
    """Completed LOOP_PASSES loop-top visits (the routine never returns)."""

    def __init__(self, registers, desc_base, model):
        super().__init__('looped')
        self.registers = dict(registers)
        self.desc_base = desc_base
        self.model = model


class Model:
    """Flat word RAM with byte/halfword access; unmapped addresses trap."""

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

    def read_half(self, address):
        base = address & ~3
        if base not in self.ram or base + 2 > base and (address & 3) == 3:
            raise ValueError('unexpected read at ' + hex(address))
        if (address & 3) == 3:
            raise ValueError('halfword read spans words at ' + hex(address))
        if base not in self.ram:
            raise ValueError('unexpected read at ' + hex(address))
        raw = (self.ram[base] >> ((address & 3) * 8)) & 0xffff
        self.trace.append(('read', address, 2, raw))
        return raw

    def read_byte(self, address, sign):
        base = address & ~3
        if base not in self.ram:
            raise ValueError('unexpected read at ' + hex(address))
        raw = (self.ram[base] >> ((address & 3) * 8)) & 0xff
        self.trace.append(('read', address, 1, raw))
        if sign and raw & 0x80:
            return raw - 0x100
        return raw


def execute(code, start, args, model, loop_top, loop_passes=LOOP_PASSES,
            plog=None):
    """Run decoded code with r0/r1/r2=args against the model.

    args is (r0, r1, r2): r5 is overwritten by the entry sequence
    before any use and the popped caller registers are never observed,
    so no caller state is an input. Raises Looped after loop_passes
    visits to loop_top, ValueError on unmapped access. When plog is a
    list, appends the pc per step.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r2=args[2] & MASK, r14=SP0)
    condition = False
    desc_base = None
    visits = 0
    pc = start
    for step in range(STEP_CAP):
        if pc == loop_top:
            visits += 1
            if visits > loop_passes:
                raise Looped(registers, desc_base, model)
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


def oracle(ident, arg1, arg2, ram):
    """Independent model: (path, desc, trace, ram, regs).

    Stated from the decoded structure, not from decoded instructions:
    fill gate/match/domain order, entry gating, selector poll, the
    bit-length shortcut, the desc[3] arm, the id-gated rotl tail, the
    selector store sequence, the first fold/check/latch, then exactly
    LOOP_PASSES loop passes over a modeled caller stack. Fill failure,
    null entry words, and the selector-match arm observe
    implementation-defined registers, so the oracle reports those as
    'leftover-dependent' without an outcome prediction; the battery
    never executes them.
    """
    ram = dict(ram)
    trace = []
    # Stock prologue pushes 12 bytes then frees 24 more: the fill
    # buffer starts 36 bytes below the entry stack pointer.
    desc = SP0 - 36
    # Loop-carried model registers.
    regs = {}

    def read(address, width=4):
        if width == 4:
            if address not in ram:
                raise ValueError('oracle missing cell at ' + hex(address))
            value = ram[address] & MASK
        elif width == 2:
            base = address & ~3
            if base not in ram or (address & 3) == 3:
                raise ValueError('oracle missing cell at ' + hex(address))
            value = (ram[base] >> ((address & 3) * 8)) & 0xffff
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
    # Entry push (saves the entry r4, the entry r5, the entry lr).
    write(SP0 - 4, seed('r4'))
    write(SP0 - 8, seed('r5'))
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

    # Stock reloads the entry pointer from its stack buffer.
    if read(desc) != entry:
        raise ValueError('descriptor round-trip changed the entry address')
    w3 = read(entry + 8)
    if w3 == 0:
        return {'outcome': 'leftover-dependent', 'path': 'null-entry',
                'desc': fill_desc, 'trace': trace, 'ram': ram}
    b0 = read(w3, 1)
    if b0 == 0:
        return {'outcome': 'leftover-dependent', 'path': 'null-byte',
                'desc': fill_desc, 'trace': trace, 'ram': ram}
    # The shift/mask come from the descriptor's own byte cell
    # (w3+1/w3+2), so they are free battery variables: the bit-length
    # poll and nonzero-shift paths are all reachable.
    r18 = read(w3 + 1, 1)
    r13 = read(w3 + 2, 2)
    sel = (read(desc + 4) + b0) & MASK
    v = read(sel)
    r19 = arg1 & 0xffff
    gated = (v >> (r18 & 31)) & r13
    if gated != 0:
        gated += 1
    if r19 == gated:
        return {'outcome': 'leftover-dependent', 'path': 'skip',
                'desc': fill_desc, 'trace': trace, 'ram': ram}
    # Bit-length poll over the entry mask (stock 0xA78); r13 == 0
    # takes the shortcut.
    if r13 == 0:
        bitlen = 0
    else:
        bitlen = 0
        shifted = r13
        while shifted != 0:
            bitlen += 1
            shifted = r13 >> (bitlen & 31)
    b4 = read(entry + 4, 1)
    b4 = b4 - 0x100 if b4 & 0x80 else b4
    r25 = (r18 + bitlen + 1) & MASK
    b6 = read(entry + 6, 1)
    b6 = b6 - 0x100 if b6 & 0x80 else b6
    mcell = read(desc + 8)
    if b4 < 0:
        r0bit = 0
    else:
        d3 = read(read(desc + 12))
        r0bit = ((d3 >> (b4 & 31)) & 1)
        if r0bit:
            write(read(desc + 20), (1 << (b4 & 31)) & MASK)
    m = read(mcell)
    r1bit = ((m >> (b6 & 31)) & 1)
    # Stock gate pair (cmpnei r4,6 / bf; movi 9 / cmphs / bf) arms
    # the rotl tail and the fold-first entry iff id == 6 or id > 9
    # (unsigned): cmphs sets the condition to (9 >= id), so bf takes
    # the arm only when id >= 10.
    gated_id = (ident == 6 or ident >= 10)
    if r1bit and gated_id:
        acc = 0
        acc = (acc - 2) & MASK
        stage = read(mcell)
        count = b6 & 31
        acc = (((acc << count) | (acc >> ((32 - count) & 31))) & MASK)
        acc &= stage
        write(mcell, acc)
    # Selector clear/set sequence; desc[1] is read a second time.
    ap = (read(desc + 4) + b0) & MASK
    if ap != sel:
        raise ValueError('selector recomputation drifted')
    cur = read(ap)
    one = (1 << (r25 & 31)) & MASK
    cur &= (~one & MASK)
    write(ap, cur)
    cur = read(ap)
    one |= cur
    one &= MASK
    write(ap, one)
    cur = read(ap)
    mask = (r13 << (r18 & 31)) & MASK
    one = (cur & (~mask & MASK)) & MASK
    write(ap, one)
    narrow = 0
    if r19 != 0:
        narrow = ((r19 - 1) << (r18 & 31)) & MASK
    cur = read(ap)
    narrow |= cur
    narrow &= MASK
    write(ap, narrow)
    cur = read(ap)
    bit = (1 << ((r18 + bitlen) & 31)) & MASK
    one = (cur & (~bit & MASK)) & MASK
    write(ap, one)
    one = read(ap)
    bit |= one
    bit &= MASK
    write(ap, bit)
    # First fold (id-gated paths only), first check, first latch.
    # Latch/fold hold the raw sign-extended entry bytes, exactly as
    # the stock ld.bs leaves them; shifts use their low 5 bits.
    r20 = r0bit
    r21 = (b4 & MASK)
    r22 = (b6 & MASK)
    r23 = mcell
    if r1bit and gated_id:
        bit1 = (1 << (r22 & 31)) & MASK
        seen = read(r23)
        keep = (seen & (~bit1 & MASK)) & MASK
        r22 = (bit1 | keep) & MASK
        write(r23, r22)
    if r20:
        d4addr = read(desc + 16)
        r21 = (1 << (r21 & 31)) & MASK
        write(d4addr, r21)
    # Exactly LOOP_PASSES loop passes: pop, fold, check, maybe latch.
    sp = SP0 - 36
    for _ in range(LOOP_PASSES):
        sp = (sp + 24) & MASK
        for address in (sp, sp + 4, sp + 8):
            read(address)
        sp = (sp + 12) & MASK
        bit1 = (1 << (r22 & 31)) & MASK
        seen = read(r23)
        keep = (seen & (~bit1 & MASK)) & MASK
        r22 = (bit1 | keep) & MASK
        write(r23, r22)
        if r20:
            # Post-pop sp points 12 bytes past the freed frame base;
            # stock reads the latch address word at (r14, 0x10), i.e.
            # sp + 16. The pop above already consumed three model
            # reads; the address read itself is one more stack read.
            latch_addr = (sp + 16) & MASK
            addr_value = read(latch_addr)
            r21 = (1 << (r21 & 31)) & MASK
            write(addr_value, r21)
    regs = {'r20': r20, 'r21': r21, 'r22': r22, 'r23': r23}
    return {'outcome': 'looped', 'path': 'body', 'desc': fill_desc,
            'trace': trace, 'ram': ram, 'regs': regs}


B0BASE = 0x20003000


def config_ram(table_mode, ident, b4, b6, b0, r18, r13, sel_init,
               m_init, d3_init):
    """Build the initial RAM for one battery case.

    table_mode in ('direct', 'entry0', 'scan'). Returns (ram, slot).
    The b0 descriptor cell carries the poll shift (byte 1) and mask
    (bytes 2..3), exactly as the stock body reads them.
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
    ram[entry + 8] = b0addr
    ram[entry + 12] = 0x5a5a5a5a
    ram[b0addr] = ((b0 & 0xff) | ((r18 & 0xff) << 8) | ((r13 & 0xffff) << 16)) & MASK
    domain = PMU_BASE if ident < PMU_SPLIT else MCU_BASE
    for addr in (domain + (b0 & 0xff), domain | 0x88, domain | 0x8c,
                 domain | 0x18, domain | 0x1c, domain | 0x20):
        ram[addr] = 0xa5a5a500 + (addr & 0xff)
    # The selector address is desc[1] + b0 with desc[1] = domain base.
    select = 0x8c if ident < PMU_SPLIT else 0x88
    ram[domain + (b0 & 0xff)] = sel_init & MASK
    mcell = domain | select
    ram[mcell] = m_init & MASK
    ram[domain | 0x18] = d3_init & MASK
    ram[domain | 0x1c] = 0xa5a5a51c
    ram[domain | 0x20] = 0xa5a5a520
    ram[SCRATCH] = 0x51edc0de
    for address in range(WINDOW_LO, WINDOW_HI, 4):
        if address not in ram:
            ram[address] = (0x5a000000 + (address - WINDOW_LO)) & MASK
    # The loop never observes popped caller registers, but the
    # per-pass latch stores through caller-stack words: every caller
    # word holds the scratch address so those stores stay mapped.
    for address in range(SP0 - 12, WINDOW_HI, 4):
        ram[address] = SCRATCH
    return ram, slot


def skip_gate(r18, r13, sel_init):
    """The selector-match value the skip arm compares against."""
    gated = ((sel_init >> (r18 & 31)) & r13) & MASK
    if gated != 0:
        gated = (gated + 1) & MASK
    return gated


def battery_cases():
    # Case: (table_mode, ident, arg2, arg1, b4, b6, b0, r18, r13,
    #        sel_init, m_init, d3_init). arg1's low 16 bits avoid the
    #        selector-match value (that arm is leftover-dependent);
    #        one merge-skip body (low16 == 0 with nonzero gate) is kept
    #        per shape. arg2 is dead on every path and is swept to
    #        prove it.
    cases = []
    for table_mode in ('direct', 'entry0', 'scan'):
        for ident in (2, 6, 9, 20):
            for b0 in (4, 0x10):
                for r18, r13 in ((0, 0), (1, 1), (7, 0x1f), (3, 0xffff),
                                 (29, 0x8001)):
                    for b4, b6, d3bit, mbit in (
                            (3, 7, 1, 1), (3, 7, 1, 0), (3, 7, 0, 1), (3, 7, 0, 0),
                            (0, 1, 1, 1), (31, 30, 1, 1), (-5, 7, 0, 1), (-128, -3, 0, 0)):
                        m_init = (mbit << (b6 & 31)) & MASK
                        d3_init = (d3bit << b4) & MASK if b4 >= 0 else 0xaaaaaaaa
                        for sel_init in (0x0, 0xffffffff):
                            gated = skip_gate(r18, r13, sel_init)
                            lows = []
                            if gated != 0:
                                lows.append(0x0000)
                            for candidate in (0x0001, 0xbeef):
                                if candidate != gated:
                                    lows.append(candidate)
                            for low16 in lows[:2]:
                                arg1 = (0xcafe0000 | low16) & MASK
                                for arg2 in (0, 1):
                                    cases.append((table_mode, ident, arg2, arg1, b4, b6,
                                                  b0, r18, r13, sel_init, m_init, d3_init))
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
    if len(pops) != 1 or any(source_code[pc][1] != 'r4-r5, r15' for pc in pops):
        raise ValueError('expected exactly one loop pop of r4-r5, r15')
    # The loop top is exactly addi/pop, pinned by address wherever the
    # assembler places it.
    tops = [pc for pc in addresses
            if source_code[pc] == ('addi', 'r14, r14, 24', 2)
            and source_code.get(pc + 2) == ('pop', 'r4-r5, r15', 2)]
    if len(tops) != 1:
        raise ValueError('loop-top shape changed: %r' % tops)
    loop_top = tops[0]
    calls = [pc for pc in addresses if source_code[pc][0] == 'bsr']
    if len(calls) != 1 or int(source_code[calls[0]][1], 0) != FILL:
        raise ValueError('expected one fill call to %#x' % FILL)
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
        if op in ('rts', 'bkpt', 'jmp', 'jmpi', 'jsr', 'lrw'):
            raise ValueError('unexpected transfer %s at %#x' % (op, pc))
    return loop_top


def seed(reg):
    index = int(reg[1:])
    if reg == 'r14':
        return SP0
    return (0x98760000 + index * 0x111111) & MASK


def run_side(code, start, args, ram, loop_top, label,
             loop_passes=LOOP_PASSES):
    """Execute one side; return (registers, desc, trace, ram).

    Both sides raise Looped after loop_passes loop-top visits. Any
    unexpected fault is a hard failure: every reachable address is
    mapped and leftover paths are never executed.
    """
    model = Model(ram)
    try:
        execute(code, start, args, model, loop_top, loop_passes, None)
    except Looped as done:
        desc = [done.model.ram[done.desc_base + 4 * index] & MASK for index in range(6)]
        return done.registers, desc, list(done.model.trace), dict(done.model.ram)
    raise ValueError(label + ': side returned instead of looping')


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-railb'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    railb_obj = output / 'railb_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *RAILB_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(railb_obj)], check=True)
    fill_obj = output / 'fill_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                    '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
    script = output / 'railb.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'railb.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(railb_obj), str(fill_obj), '-o', str(elf_path)], check=True)
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
    # Stock body plus the stock fill it calls.
    stock_code = {}
    for lo, hi in (('0x10000a30', '0x10000b8e'), ('0x10000780', '0x10000834')):
        stock_code.update(decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=' + lo, '--stop-address=' + hi,
             str(adjusted)], text=True)))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'railb.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
    functions = []
    cases = 0
    for symbol, entry, offset, size, kind, ownership in SPECS:
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) != size or offset % section['align']:
            raise ValueError('candidate does not exactly fill its placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        loop_top = check_shape(source_code, entry, len(payload))
        # The linked fill body executes on the source side too.
        source_all = {}
        for section_code in sources.values():
            source_all.update(section_code)
        for case in battery_cases():
            (table_mode, ident, arg2, arg1, b4, b6, b0, r18, r13,
             sel_init, m_init, d3_init) = case
            ram, _slot = config_ram(table_mode, ident, b4, b6, b0, r18, r13,
                                    sel_init, m_init, d3_init)
            want = oracle(ident, arg1, arg2, ram)
            if want['outcome'] != 'looped':
                raise ValueError('battery hit a leftover path on %r' % (case,))
            stock_regs, stock_desc, stock_trace, stock_final = run_side(
                stock_code, entry, (ident, arg1, arg2), ram,
                LOOP_TOP, 'stock')
            if want['trace'] != stock_trace:
                for i, (a, b) in enumerate(zip(want['trace'], stock_trace)):
                    if a != b:
                        raise ValueError(
                            'stock trace/oracle mismatch at step %d: %r vs %r on %r'
                            % (i, a, b, case))
                raise ValueError('stock trace/oracle length mismatch %d vs %d on %r'
                                 % (len(want['trace']), len(stock_trace), case))
            if want['desc'] != stock_desc:
                raise ValueError('stock desc/oracle mismatch on %r' % (case,))
            if want['ram'] != stock_final:
                for address in sorted(set(want['ram']) | set(stock_final)):
                    if want['ram'].get(address) != stock_final.get(address):
                        raise ValueError(
                            'stock ram/oracle mismatch at %#x on %r'
                            % (address, case))
            src_regs, src_desc, src_trace, src_final = run_side(
                source_all, entry, (ident, arg1, arg2), ram,
                loop_top, 'source')
            if src_trace != stock_trace:
                for i, (a, b) in enumerate(zip(src_trace, stock_trace)):
                    if a != b:
                        raise ValueError(
                            'source trace/stock mismatch at step %d: %r vs %r on %r'
                            % (i, a, b, case))
                raise ValueError('source trace/stock length mismatch %d vs %d on %r'
                                 % (len(src_trace), len(stock_trace), case))
            if src_desc != stock_desc:
                raise ValueError('source desc/stock mismatch on %r' % (case,))
            if src_final != stock_final:
                raise ValueError('source ram/stock mismatch on %r' % (case,))
            for reg in ['r%d' % i for i in range(32)] + ['r14']:
                if src_regs[reg] != stock_regs[reg]:
                    raise ValueError('%s differs stock/source on %r'
                                     % (reg, case))
            for reg, value in want['regs'].items():
                if stock_regs[reg] != value:
                    raise ValueError('oracle reg %s mismatch on %r' % (reg, case))
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
              'compile_flags': RAILB_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no upstream register map is used: every '
                                    'address is a fill-provided descriptor '
                                    'value and every constant is a stock '
                                    'immediate; clean-room body from decoded '
                                    'stock flow, no SDK text reproduced',
              'functions': functions, 'target_cases': cases,
              'loop_passes': LOOP_PASSES,
              'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'rail-sequencing operation B only (body plus '
                                 'exactly four loop passes, exact unfiltered '
                                 'traces)',
              'stock_equivalence_proven': False,
              'leftover_paths': 'fill-fail, null-entry, and selector-match '
                                'arms run with implementation-defined '
                                'registers and are excluded from the battery; '
                                'the assembly keeps the same branches without '
                                'an outcome claim there. General-form '
                                'bit-length/shift code is unreachable through '
                                'the fill contract (entry bytes 1..3 forced '
                                'zero) and verified by transcription identity '
                                'only.',
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Register shifts by a register count use the low 5 '
                         'bits; both sides share the executor so agreement '
                         'holds by construction, hardware shift semantics for '
                         'negative counts remain unqualified.',
                         'The ld.h halfword load is modeled zero-extending; '
                         'only zero values occur on fill-reachable paths so '
                         'sign semantics are unprobed and unqualified.',
                         'Both frames are exactly 24 bytes, so pop traffic '
                         'is compared exactly with no window exclusion; '
                         'descriptor values and all other accesses are '
                         'compared exactly. Hardware timing remains '
                         'unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-railb-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-railb-verification.json').read_text()),
        indent=2))

