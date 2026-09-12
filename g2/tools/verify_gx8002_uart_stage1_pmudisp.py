#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 pmudispatch leaf.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_pmudispatch.S against
the stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of id/selector/table/entry configurations, plus an
independent Python oracle.

Leaf: the first PMU rail dispatcher at runtime 0x10000D98, package
0xDE8, 264 bytes of code: a jump-table fill-id map, a first
`pmu_fill_desc` call into a 24-byte stack descriptor with
descriptor-bit gating, a second `pmu_fill_desc` call with the original
id, a jump-table status-bit map with a check arm, and pop-and-fall-
through handoff into the retained second dispatcher at 0x10000EA0 (no
`rts`; the function never returns). The real linked fill bodies run on
both sides: stock fill for stock, compiled source fill for source.
Compared: the complete unfiltered access trace (kind, address, width,
and value of every read and write, including push/pop/desc/jump-table
traffic), the final RAM, and the live registers at the handoff point.

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow (one documented peephole: an addi-fold of the
entry-byte -1 gate; the retained table bases are materialized with
movih/ori because the assembler places literal pools only at the
section end, and the one unreachable padding halfword after the first
indirect jump is omitted to hold the envelope). Admission rests on
decoded-trace equivalence. Both frames are exactly 24 bytes with the
descriptor at the base and the caller window is fully mapped, so all
traffic is compared exactly: no stack window is excluded.

Fill-failure exits of the SECOND fill observe the fill body's
scratch leftovers (stock leaves r3 = 25/0 by fail kind; the compiled
source fill leaves its own), so those paths run with
implementation-defined registers and are excluded from the battery
(the assembly keeps the same branches without an outcome claim
there); every battery case matches the second fill. The first fill
may hit or miss freely. Out-of-range ids also fail the second fill
and are excluded for the same reason; their guard edges land on the
same passthrough/check targets the in-range battery executes, and the
jump-table contents are pinned against the stock dump. The
never-zero status-bit arm (1u<<k is never 0) is kept for shape but is
unreachable. Register shifts by a register count use the low 5 bits;
both sides share the executor so agreement holds by construction.
Hardware timing remains unqualified.
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
    PMU_BASE, MCU_BASE, PMU_SELECT, MCU_SELECT, PMUFILL_FLAGS,
    FAIL as FILL_FAIL, oracle as fill_oracle)

ROOT = Path(__file__).resolve().parents[1]
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmudispatch.S'
FILL_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-PMUDISP-NOTICE.txt'
PMUDISP_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY = 0x10000d98
FILL = 0x10000780
HANDOFF = 0x10000ea0
JT1 = 0x10001e60
JT1_IDS = tuple(range(7, 25))
JT2 = 0x10001ea8
JT2_IDS = tuple(range(6, 25))
SP0 = 0x20002800
DESC = SP0 - 40
SCRATCH = 0x20004000
WINDOW_LO = SP0 - 64
WINDOW_HI = SP0 + 4096
STEP_CAP = 20000

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_pmu_dispatch', 0x10000d98, 0xde8, 264,
     'pmudispatch', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_pmu_dispatch 0x10000d98 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_dispatch) }
  .text.open_cfw_gx8002_uart_stage1_pmu_fill_desc 0x10000780 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_fill_desc) }
}
'''

# First-table fill-id map (stock jump table at package 0x1EB0, dumped
# from the image; every other id passes through unchanged). Used for
# battery table logistics; the oracle itself reads the mapped tables
# and derives behavior from their contents (reverse maps below).
JT1_MAP = {7: 2, 8: 2, 17: 16, 18: 16, 20: 19, 21: 19, 23: 22, 24: 22}
# Reverse maps from jump-target address to behavior, mirroring what
# the dispatched stock arms do. The oracle reads each table entry
# (a real traced access, like the stock ldr.w) and derives the arm
# from the entry value; anything outside these sets fails closed.
JT1_PASS = 0x10000e54
JT1_TARGET_FILL = {0x10000db4: 2, 0x10000e30: 16, 0x10000e2c: 19,
                   0x10000e28: 22}
JT2_CHECK = 0x10000e8c
JT2_TARGET_BIT = {0x10000e58: 0x8000, 0x10000e82: 8, 0x10000e74: 0x2000,
                  0x10000e7e: 1 << 16, 0x10000e7a: 1 << 17,
                  0x10000e6c: 1 << 18, 0x10000e68: 1 << 19,
                  0x10000e70: 1 << 20, 0x10000e88: 1 << 21}
# Expected raw table contents (runtime entry targets) in id order.
JT1_EXPECT = [0x10000db4, 0x10000db4, 0x10000e54, 0x10000e54, 0x10000e54,
              0x10000e54, 0x10000e54, 0x10000e54, 0x10000e54, 0x10000e54,
              0x10000e30, 0x10000e30, 0x10000e54, 0x10000e2c, 0x10000e2c,
              0x10000e54, 0x10000e28, 0x10000e28]
JT2_EXPECT = [0x10000e58, 0x10000e8c, 0x10000e8c, 0x10000e8c, 0x10000e8c,
              0x10000e82, 0x10000e8c, 0x10000e74, 0x10000e58, 0x10000e8c,
              0x10000e8c, 0x10000e7e, 0x10000e7a, 0x10000e8c, 0x10000e6c,
              0x10000e68, 0x10000e8c, 0x10000e70, 0x10000e88]

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
LOAD_INDEX = re.compile(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)')


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


class HandedOff(Exception):
    """Reached the retained second dispatcher (the routine never returns)."""

    def __init__(self, registers, model):
        super().__init__('handed off')
        self.registers = dict(registers)
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
        if base not in self.ram:
            raise ValueError('unexpected read at ' + hex(address))
        if (address & 3) == 3:
            raise ValueError('halfword read spans words at ' + hex(address))
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


def execute(code, start, args, model, handoff=HANDOFF, plog=None):
    """Run decoded code with r0/r1/caller-r6=args against the model.

    args is (r0, r1, caller_r6): the body overwrites r4/r6 before any
    use, but the pop-and-walk handoff restores caller registers, so
    the caller r6 is an explicit input. All other registers start
    from fixed seeds. Raises HandedOff at the first visit to the
    handoff address and ValueError on unmapped access or trap words.
    When plog is a list, appends the pc per step.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r6=args[2] & MASK, r14=SP0)
    condition = False
    pc = start
    for _step in range(STEP_CAP):
        if pc == handoff:
            raise HandedOff(registers, model)
        if pc not in code:
            raise ValueError('unexpected pc ' + hex(pc))
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
        elif op == 'bclri':
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] & ~(1 << int(parts[1], 0))) & MASK
            else:
                raise ValueError('unsupported bclri form: ' + operand)
        elif op in ('tlsli', 'lsli'):
            registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & MASK
        elif op in ('lsl', 'tlsl'):
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] << (registers[parts[1]] & 31)) & MASK
            else:
                # Printed (rd, rx, ry) executes as ry OP rx: proven by
                # the stock body itself (the fill-id mask and the
                # extended bit test both demand the reversed order;
                # see the audit doc). Two-operand forms are standard.
                registers[parts[0]] = (registers[parts[2]] << (registers[parts[1]] & 31)) & MASK
        elif op in ('lsr', 'tlsr'):
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] >> (registers[parts[1]] & 31)) & MASK
            else:
                registers[parts[0]] = (registers[parts[2]] >> (registers[parts[1]] & 31)) & MASK
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
        elif op == 'jmp':
            following = registers[parts[0]]
        elif op == 'bsr':
            if int(parts[0], 0) != FILL:
                raise ValueError('unexpected call to ' + operand)
            registers['r15'] = following
            following = int(parts[0], 0)
        elif op == 'rts':
            following = registers['r15']
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


def s8(value):
    value &= 0xff
    return value - 0x100 if value & 0x80 else value


def oracle(ident, sel, caller_r6, ram, table_words):
    """Independent model: (outcome, regs, trace, ram).

    Stated from the decoded structure, not from decoded instructions:
    push, first-table fill-id map, first fill, the entry-byte gate
    with its mask/extended/plain tests, the second fill with the
    original id, the status-bit map or check arm, the selector-
    gated store, and the pop-and-walk handoff. Both fills reuse the
    reviewed fill oracle; everything else is modeled here. The
    caller-stack walk is modeled pass by pass against the same mapped
    window the executor uses.
    """
    ram = dict(ram)
    trace = []

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

    # Entry push saves the caller registers in executor order (the
    # body overwrites r4/r6 afterwards; the handoff pops restore
    # these same words, so the caller r6 is a real input).
    write(SP0 - 4, seed('r4'))
    write(SP0 - 8, seed('r5'))
    write(SP0 - 12, caller_r6)
    write(SP0 - 16, seed('r15'))
    for index in range(6):
        ram[DESC + 4 * index] = ram.get(DESC + 4 * index, 0x5a5a5a5a) & MASK
    regs = {'r0': 0, 'r2': 0, 'r3': 0, 'r4': ident & MASK, 'r5': seed('r5'),
            'r6': sel & MASK, 'r14': SP0, 'r15': seed('r15')}
    sp = SP0 - 40

    def do_fill(fid):
        rc, fill_ram, fill_trace = fill_oracle(fid, DESC, dict(table_words))
        for address, value in fill_ram.items():
            ram[address] = value & MASK
        trace.extend(fill_trace)
        regs['r0'] = rc & MASK
        return rc

    def store4(entry):
        b4 = s8(read(entry + 4, 1))
        write(read(DESC + 16), (1 << (b4 & 31)) & MASK)

    def walk(handoff_r3):
        # Pop-and-walk handoff: pop the frame, set bit 19, and either
        # store through the caller word and hand off (nonzero
        # selector) or store through the frame word and walk another
        # 40 bytes (zero selector). Caller words hold mapped
        # addresses; selector slots are battery inputs.
        nonlocal sp
        while True:
            sp = (sp + 24) & MASK
            regs['r15'] = read(sp)
            regs['r6'] = read(sp + 4)
            regs['r5'] = read(sp + 8)
            regs['r4'] = read(sp + 12)
            sp = (sp + 16) & MASK
            regs['r14'] = sp
            handoff_r3 = (handoff_r3 | (1 << 19)) & MASK
            regs['r3'] = handoff_r3
            if regs['r6'] != 0:
                regs['r2'] = read(sp + 0x14)
                write(regs['r2'], handoff_r3)
                sp = (sp + 24) & MASK
                regs['r15'] = read(sp)
                regs['r6'] = read(sp + 4)
                regs['r5'] = read(sp + 8)
                regs['r4'] = read(sp + 12)
                sp = (sp + 16) & MASK
                regs['r14'] = sp
                return
            regs['r2'] = read(sp + 0x10)
            write(regs['r2'], handoff_r3)

    sub = (ident - 7) & MASK
    if sub >= 18:
        fill = ident
    else:
        target = read(JT1 + 4 * sub)
        if target == JT1_PASS:
            fill = ident
        elif target in JT1_TARGET_FILL:
            fill = JT1_TARGET_FILL[target]
        else:
            raise ValueError('unexpected first-table target ' + hex(target))
    regs['r5'] = fill & MASK
    if do_fill(fill) == 0:
        entry = read(DESC)
        b6 = s8(read(entry + 6, 1))
        if b6 != -1:
            # Mask and extended tests use the reversed three-operand
            # shift order the stock body exhibits (see the executor
            # note and the audit doc): (fill<<1) and (b6+1)>>cell.
            if fill < 10 and (((fill << 1) & 579) != 0):
                other = read(read(DESC + 8))
                if ((((b6 + 1) & MASK) >> (other & 31)) & 1) != 0:
                    store4(entry)
                    return finish_fill2(ident, sel, ram, trace, regs, sp,
                                        table_words, read, write, walk)
                # Not taken: control joins the shift with the cell
                # still loaded (no re-read); test bit b6 of it.
                bit = (other >> (b6 & 31)) & 1
            else:
                cell = read(read(DESC + 8))
                bit = (cell >> (b6 & 31)) & 1
            if bit == 0 or sel == 0:
                store4(entry)
                return finish_fill2(ident, sel, ram, trace, regs, sp,
                                    table_words, read, write, walk)
            b4 = s8(read(entry + 4, 1))
            write(read(DESC + 20), (1 << (b4 & 31)) & MASK)
    return finish_fill2(ident, sel, ram, trace, regs, sp, table_words,
                        read, write, walk)


def finish_fill2(ident, sel, ram, trace, regs, sp, table_words, read,
                 write, walk):
    """Second fill with the original id, status map, store, handoff."""
    rc, fill_ram, fill_trace = fill_oracle(ident, DESC, dict(table_words))
    for address, value in fill_ram.items():
        ram[address] = value & MASK
    trace.extend(fill_trace)
    regs['r0'] = rc & MASK
    if rc != 0:
        raise ValueError('battery hit a second-fill failure')
    entry = read(DESC)
    b5 = s8(read(entry + 5, 1))
    regs['r3'] = (1 << (b5 & 31)) & MASK
    sub2 = (ident - 6) & MASK
    check = True
    if sub2 < 19:
        target = read(JT2 + 4 * sub2)
        if target == JT2_CHECK:
            check = True
        elif target in JT2_TARGET_BIT:
            check = False
            regs['r3'] = (regs['r3'] | JT2_TARGET_BIT[target]) & MASK
        else:
            raise ValueError('unexpected second-table target ' + hex(target))
    if check:
        regs['r4'] = (ident & ~(1 << 2)) & MASK
        if regs['r4'] == 1:
            walk(regs['r3'])
            return {'outcome': 'handoff', 'regs': regs, 'trace': trace,
                    'ram': ram}
        if regs['r3'] == 0:
            # Dead arm: 1u<<k is never 0 for k in 0..31. Kept for
            # shape parity with stock; never taken.
            walk(regs['r3'])
            return {'outcome': 'handoff', 'regs': regs, 'trace': trace,
                    'ram': ram}
    if sel != 0:
        regs['r2'] = read(DESC + 20)
        write(regs['r2'], regs['r3'])
        sp = (sp + 24) & MASK
        regs['r15'] = read(sp)
        regs['r6'] = read(sp + 4)
        regs['r5'] = read(sp + 8)
        regs['r4'] = read(sp + 12)
        sp = (sp + 16) & MASK
        regs['r14'] = sp
        return {'outcome': 'handoff', 'regs': regs, 'trace': trace,
                'ram': ram}
    regs['r2'] = read(DESC + 16)
    write(regs['r2'], regs['r3'])
    walk(regs['r3'])
    return {'outcome': 'handoff', 'regs': regs, 'trace': trace, 'ram': ram}


LIVE_REGS = ('r0', 'r2', 'r3', 'r4', 'r5', 'r6', 'r14', 'r15')


def jt1_fill(ident):
    return JT1_MAP.get(ident, ident)


def table_ram_for(mode, ident):
    """Entry-table first words for one battery case.

    Returns (words, fill1_slot, fill2_slot). Every case matches the
    second fill (original id); second-fill failures observe fill
    scratch leftovers and stay out of the battery. Modes: 'direct'
    (identity), 'entry0' (first fill via slot 0), 'scan' (first fill
    via slot 13/14), 'fill1miss' (first fill fails, second hits).
    Returns None when the mode cannot satisfy the constraints.
    """
    fill1 = jt1_fill(ident)
    if ident > MAX_ID:
        return None
    if mode == 'direct':
        words = list(range(TABLE_ENTRIES))
        return words, fill1, ident
    if mode == 'entry0':
        if fill1 == ident or fill1 > MAX_ID or ident == 0:
            return None
        words = [0x70000000 + i for i in range(TABLE_ENTRIES)]
        words[ident] = ident
        words[0] = fill1
        return words, 0, ident
    if mode == 'scan':
        if fill1 == ident or fill1 > MAX_ID:
            return None
        slot = 13 if fill1 != 13 and ident != 13 else 14
        if ident == slot:
            return None
        words = [0x70000000 + i for i in range(TABLE_ENTRIES)]
        words[ident] = ident
        words[slot] = fill1
        return words, slot, ident
    if mode == 'fill1miss':
        if fill1 == ident or fill1 > MAX_ID:
            return None
        words = list(range(TABLE_ENTRIES))
        words[fill1] = 0x70000000 + fill1
        return words, None, ident
    raise ValueError('unknown table mode ' + mode)


def config_ram(mode, ident, sel, b4, b5, b6, mcell, walk_depth):
    """Build the initial RAM for one battery case.

    Returns (ram, table_words, fill1_slot). Entry bytes and domain
    cells are seeded for both fills; the caller window holds mapped
    addresses with battery-controlled selector slots for the walk.
    """
    built = table_ram_for(mode, ident)
    if built is None:
        return None
    words, _fill1_slot, _fill2_slot = built
    ram = {}
    for slot in range(TABLE_ENTRIES):
        base = FILL_TABLE_BASE + slot * ENTRY_STRIDE
        ram[base] = words[slot] & MASK
        ram[base + 4] = 0x5a5a5a5a
        ram[base + 8] = 0xa5a5a5a5
        ram[base + 12] = 0x5a5a5a5a
    fill1 = jt1_fill(ident)
    for slot_id in {fill1, ident}:
        if slot_id is not None and slot_id <= MAX_ID:
            entry = FILL_TABLE_BASE + words.index(slot_id) * ENTRY_STRIDE \
                if slot_id in words else None
            if entry is not None:
                ram[entry + 4] = ((b4 & 0xff) | ((b5 & 0xff) << 8)
                                  | ((b6 & 0xff) << 16) | (0xa5 << 24)) & MASK
    for base, select in ((PMU_BASE, PMU_SELECT), (MCU_BASE, MCU_SELECT)):
        ram[base | select] = mcell & MASK
        ram[base | 0x18] = 0xa5a5a518
        ram[base | 0x1c] = 0xa5a5a51c
        ram[base | 0x20] = 0xa5a5a520
    ram[SCRATCH] = 0x51edc0de
    for address in range(WINDOW_LO, WINDOW_HI, 4):
        if address not in ram:
            ram[address] = SCRATCH
    # Walk selector slots: the first pop restores the entry selector
    # (SP0-12); deeper pops read r6 at SP0+28+40m. Zeros extend the
    # walk, nonzero (mapped-address default) exits it.
    slot_addr = SP0 + 28
    depth = 0
    while slot_addr < WINDOW_HI and depth < walk_depth:
        ram[slot_addr] = 0
        slot_addr += 40
        depth += 1
    table_words = {FILL_TABLE_BASE + slot * ENTRY_STRIDE: words[slot] & MASK
                   for slot in range(TABLE_ENTRIES)}
    return ram, table_words, _fill1_slot


def battery_cases():
    # Case: (mode, ident, sel, caller_r6, b4, b5, b6, mcell,
    # walk_depth). The mcell bit pair (b6, b6+1) is swept over
    # set/clear wherever the first fill runs and b6 != -1; entry
    # bytes cover -1/0/edges/sign; caller_r6 0 unlocks multi-pass
    # walks (walk_depth 3 zeroes the first three deep selector
    # slots for a 4-zero walk).
    cases = []
    byte_sets = [(-1, 0, 0), (0, 5, 3), (5, 21, 6), (27, 31, 27),
                 (31, -4, 31), (-128, 0, -8)]
    for mode in ('direct', 'entry0', 'scan', 'fill1miss'):
        for ident in list(range(26)):
            if table_ram_for(mode, ident) is None:
                continue
            for sel in (0, 1, 0x8000):
                for caller_r6 in (0x600d600d, 0):
                    for b6, b5, b4 in byte_sets:
                        # The first-fill gate reads the select cell
                        # only on a first-fill hit with b6 != -1.
                        if mode == 'fill1miss' or b6 == -1:
                            bit_pairs = ((0, 0),)
                        else:
                            bit_pairs = ((0, 0), (0, 1), (1, 0), (1, 1))
                        for set6, set61 in bit_pairs:
                            mcell = 0xa5a5a500
                            if set6:
                                mcell |= (1 << (b6 & 31)) & MASK
                            if set61:
                                mcell |= (1 << ((b6 + 1) & 31)) & MASK
                            for walk_depth in (0, 3):
                                if walk_depth and caller_r6 != 0:
                                    continue
                                cases.append((mode, ident, sel, caller_r6,
                                              b4, b5, b6, mcell,
                                              walk_depth))
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
    if source_code[addresses[0]] != ('push', 'r4-r6, r15', 2):
        raise ValueError('prologue push changed: ' + repr(source_code[addresses[0]]))
    if source_code[addresses[1]][0] != 'subi' or 'r14' not in source_code[addresses[1]][1]:
        raise ValueError('frame subi changed: ' + repr(source_code[addresses[1]]))
    covered = max(addresses) + source_code[max(addresses)][2] - entry
    if covered != size:
        raise ValueError('section size changed: %d vs %d' % (covered, size))
    pops = [pc for pc in addresses if source_code[pc][0] == 'pop']
    if len(pops) != 2 or any(source_code[pc][1] != 'r4-r6, r15' for pc in pops):
        raise ValueError('expected exactly two handoff pops of r4-r6, r15')
    calls = [pc for pc in addresses if source_code[pc][0] == 'bsr']
    if len(calls) != 2 or any(int(source_code[pc][1], 0) != FILL for pc in calls):
        raise ValueError('expected exactly two fill calls to %#x' % FILL)
    jmps = [pc for pc in addresses if source_code[pc][0] == 'jmp']
    if len(jmps) != 2 or any(not source_code[pc][1].startswith('r') for pc in jmps):
        raise ValueError('expected exactly two register-indirect table jumps')
    bkpts = [pc for pc in addresses if source_code[pc][0] == 'bkpt']
    if bkpts:
        raise ValueError('trap words are not admitted in this leaf')
    movihs = sorted(source_code[pc][1] for pc in addresses
                    if source_code[pc][0] == 'movih')
    oris = sorted(source_code[pc][1] for pc in addresses
                  if source_code[pc][0] == 'ori')
    if movihs != ['r1, 4096', 'r2, 4096']:
        raise ValueError('table-base movih pair changed: %r' % movihs)
    if sorted(oris) != ['r1, r1, 7848', 'r2, r2, 7776', 'r3, r3, 32768',
                         'r3, r3, 8', 'r3, r3, 8192']:
        raise ValueError('ori set changed: %r' % oris)
    # Guard edges: the range checks must land on the passthrough and
    # check-arm bodies (verified by following each guard branch to its
    # target body's first instruction).
    cmps = [pc for pc in addresses if source_code[pc][0] == 'cmphsi']
    if len(cmps) != 3:
        raise ValueError('expected exactly three compares (mask + guards)')
    for pc in cmps:
        # The first branch after the compare consumes its condition
        # (moves may sit between).
        brop = broperand = None
        cursor = pc + 2
        for _ in range(4):
            op, operand, width = source_code[cursor]
            if op in ('bt', 'bf'):
                brop, broperand = op, operand
                break
            cursor += width
        if brop != 'bt':
            raise ValueError('guard compare has no following bt at %#x' % pc)
        target = int(broperand, 0)
        first = source_code[target]
        if source_code[pc][1] == 'r5, 10':
            if first != ('ld.w', 'r3, (r14, 0x8)', 2):
                raise ValueError('mask test misses alternate body')
        elif source_code[pc][1] == 'r3, 18':
            if first != ('mov', 'r5, r4', 2):
                raise ValueError('first-table guard misses passthrough')
        elif source_code[pc][1] == 'r2, 19':
            if first != ('bclri', 'r4, 2', 2):
                raise ValueError('second-table guard misses check arm')
        else:
            raise ValueError('unexpected guard compare at %#x' % pc)
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
        if op in ('rts', 'jmpi', 'jsr', 'lrw', 'bnezad'):
            raise ValueError('unexpected transfer %s at %#x' % (op, pc))


def run_side(code, start, args, ram, label):
    """Execute one side; return (registers, trace, ram).

    Both sides raise HandedOff at the retained-dispatcher boundary.
    Any unexpected fault is a hard failure: every reachable address
    is mapped and leftover paths are never executed.
    """
    model = Model(ram)
    try:
        execute(code, start, args, model)
    except HandedOff as done:
        return done.registers, list(done.model.trace), dict(done.model.ram)
    raise ValueError(label + ': side returned instead of handing off')


def check_tables(stock):
    """Fail closed when the retained jump tables drift from the maps."""
    jt1 = [int.from_bytes(stock[0x1eb0 + 4 * i:0x1eb0 + 4 * i + 4], 'little')
           for i in range(len(JT1_IDS))]
    jt2 = [int.from_bytes(stock[0x1ef8 + 4 * i:0x1ef8 + 4 * i + 4], 'little')
           for i in range(len(JT2_IDS))]
    if jt1 != JT1_EXPECT:
        raise ValueError('first jump table drifted from the pinned map')
    if jt2 != JT2_EXPECT:
        raise ValueError('second jump table drifted from the pinned map')
    return jt1, jt2


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-pmudisp'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    disp_obj = output / 'pmudisp_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUDISP_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(disp_obj)], check=True)
    fill_obj = output / 'fill_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                    '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
    script = output / 'pmudisp.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'pmudisp.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(disp_obj), str(fill_obj), '-o', str(elf_path)], check=True)
    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    jt1, jt2 = check_tables(stock)
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
    for lo, hi in (('0x10000d98', '0x10000ea0'), ('0x10000780', '0x10000834')):
        stock_code.update(decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=' + lo, '--stop-address=' + hi,
             str(adjusted)], text=True)))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'pmudisp.disassembly.txt').write_text(disassembly)
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
        check_shape(source_code, entry, len(payload))
        # The linked fill body executes on the source side too.
        source_all = {}
        for section_code in sources.values():
            source_all.update(section_code)
        for case in battery_cases():
            (mode, ident, sel, caller_r6, b4, b5, b6, mcell,
             walk_depth) = case
            built = config_ram(mode, ident, sel, b4, b5, b6, mcell,
                               walk_depth)
            if built is None:
                raise ValueError('battery built an impossible case %r' % (case,))
            ram, table_words, _fill1_slot = built
            # Retained jump tables are analysis-oracle inputs: map the
            # dumped stock words for both executed sides.
            for base, ids in ((JT1, JT1_IDS), (JT2, JT2_IDS)):
                for index, want in zip(ids, jt1 if base == JT1 else jt2):
                    ram[base + 4 * (index - ids[0])] = want & MASK
            want = oracle(ident, sel, caller_r6, ram, table_words)
            if want['outcome'] != 'handoff':
                raise ValueError('battery missed the handoff on %r' % (case,))
            stock_regs, stock_trace, stock_final = run_side(
                stock_code, entry, (ident, sel, caller_r6), ram, 'stock')
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
                source_all, entry, (ident, sel, caller_r6), ram, 'source')
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
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    if cases < 200:
        raise ValueError('battery admitted too few cases: %d' % cases)
    report = {'c_source_sha256': sha(S_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': PMUDISP_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no upstream register map is used: every '
                                    'address is a fill-provided descriptor '
                                    'value or a retained table base and every '
                                    'constant is a stock immediate; '
                                    'clean-room body from decoded stock flow, '
                                    'no SDK text reproduced',
              'functions': functions, 'target_cases': cases,
              'handoff': hex(HANDOFF),
              'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot '
                                 'stage-1 first PMU dispatcher only (entry '
                                 'through handoff into retained 0x10000ea0, '
                                 'exact unfiltered traces)',
              'stock_equivalence_proven': False,
              'leftover_paths': 'second-fill failures observe fill scratch '
                                'leftovers and are excluded from the battery; '
                                'out-of-range ids fail the second fill for '
                                'the same reason. The assembly keeps the same '
                                'branches without an outcome claim there. The '
                                'zero status-bit arm is mathematically '
                                'unreachable (1u<<k never 0). Fill scratch '
                                'registers r1/r7-r13/r16+ are compared by '
                                'trace only, not at the handoff.',
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Register shifts by a register count use the low 5 '
                         'bits; both sides share the executor so agreement '
                         'holds by construction, hardware shift semantics for '
                         'negative counts remain unqualified.',
                         'Push/pop traffic is compared exactly with no '
                         'window exclusion; descriptor values and all other '
                         'accesses are compared exactly. The caller window '
                         'is fully mapped. Hardware timing remains '
                         'unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-pmudisp-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-pmudisp-verification.json').read_text()),
        indent=2))
