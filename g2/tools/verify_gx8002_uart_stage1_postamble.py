#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 postamble leaf.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_postamble.S against
the stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of entry-register/MMIO-cell/table/entry configurations,
plus an independent Python oracle.

Leaf: the rail postamble at runtime 0x10001D9C, package 0x1DEC, 60
bytes (56 of code plus the 4-byte literal pool word): set control bits
0 and 8 at [base+0x3A0] (base from the pointer cell 0x20002274), poll
status bit 0 at [base+0x2C0], clear the control bits, publish id 25
with selector 0, and noreturn-call the reviewed first PMU dispatcher
(0x10000D98) with r0=25, r1=0. The real linked dispatcher and fill
bodies run on both sides: stock pair for stock, compiled source pair
for source. Compared: the complete unfiltered access trace (kind,
address, width, and value of every read and write, including the
push/poll/dispatcher traffic), the final RAM, and the live registers
at the handoff into retained 0x10000EA0.

Behavioral equivalence only: the assembly keeps the stock register
plan, control flow, and encoding (the section assembles byte-identical
to the stock envelope, asserted below). Admission rests on
decoded-trace equivalence. The leaf takes no register inputs (r0/r1
are set explicitly; r6 passes through to the dispatcher), so the
battery sweeps entry r0/r1 garbage to prove they are not inputs, plus
the full dispatcher-id-25 slice (entry bytes, select cells, caller
selector, walk depth, fill-table modes) and the postamble MMIO cells.
The execution starts with sp 4 bytes high so the dispatcher's frame
lands exactly where the standalone dispatcher battery maps it; the
extra push word is compared exactly like every other access.

The single-pass poll shape is pinned; a clear poll bit spins both
sides on the same three byte-identical instructions, so no multi-pass
case is needed. Fill-failure exits of the dispatcher observe the fill
body's scratch leftovers (see the pmudispatch verifier) and stay out
of the battery; id 25 always matches both fills in the direct mode, so
every battery case reaches the handoff. Hardware timing remains
unqualified.
"""
import json
import re
import struct
import subprocess
import sys
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha
from verify_gx8002_uart_stage1_pmufill import PMUFILL_FLAGS
from verify_gx8002_uart_stage1_pmufill import (
    TABLE_BASE as FILL_TABLE_BASE, TABLE_ENTRIES, ENTRY_STRIDE, MAX_ID,
    PMU_SPLIT, PMU_BASE, MCU_BASE, PMU_SELECT, MCU_SELECT, FAIL,
    oracle as fill_oracle)
from verify_gx8002_uart_stage1_pmudisp import (
    PMUDISP_FLAGS, S_SOURCE as DISP_SOURCE, FILL_SOURCE,
    Model, HandedOff, seed, signed, expand_regs, split_sections,
    check_tables, config_ram,
    JT1, JT1_IDS, JT1_MAP, JT1_PASS, JT1_TARGET_FILL,
    JT2, JT2_IDS, JT2_CHECK, JT2_TARGET_BIT, JT1_EXPECT, JT2_EXPECT,
    SP0, DESC, WINDOW_LO, WINDOW_HI, SCRATCH, MASK, FILL, STEP_CAP)

ROOT = Path(__file__).resolve().parents[1]
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_postamble.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-POSTAMBLE-NOTICE.txt'
POST_FLAGS = ['-Os', *FLAGS[1:]]

ENTRY = 0x10001d9c
DISP = 0x10000d98
HANDOFF = 0x10000ea0
PKG = 0x1dec
SIZE = 60
PTR = 0x20002274
BASES = (0x20005000, 0x20006000)
POLL_OFF = 0x2c0
PUB_OFF = 0x398
CTRL_OFF = 0x3a0
SP0_POST = SP0 + 4

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_postamble', 0x10001d9c, 0x1dec, 60,
     'postamble', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_postamble 0x10001d9c : { *(.text.open_cfw_gx8002_uart_stage1_postamble) }
  .text.open_cfw_gx8002_uart_stage1_pmu_dispatch 0x10000d98 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_dispatch) }
  .text.open_cfw_gx8002_uart_stage1_pmu_fill_desc 0x10000780 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_fill_desc) }
}
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
LOAD_INDEX = re.compile(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)')
CALLS = (FILL, DISP)


def execute(code, start, args, model, handoff=HANDOFF, plog=None,
            sp0=SP0_POST):
    """Run decoded code with r0/r1/r6=args against the model.

    Same interpreter as the pmudispatch verifier (copied so this leaf
    owns its copy), plus two differences: the initial stack pointer is
    a parameter (the postamble runs 4 bytes high so the dispatcher's
    frame lands on the mapped standalone layout), and `bsr` admits the
    reviewed dispatcher in addition to the fill. Raises HandedOff at
    the retained-dispatcher boundary and ValueError on unmapped access
    or trap words. When plog is a list, appends the pc per step.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK,
                     r6=args[2] & MASK, r14=sp0)
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
                # the stock body itself (see the pmudispatch audit doc).
                # Two-operand forms are standard.
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
            if int(parts[0], 0) not in CALLS:
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


def s8(value):
    value &= 0xff
    return value - 0x100 if value & 0x80 else value


def oracle_prefix(regs_in, ram):
    """Model the postamble prefix; return (regs, trace, ram, base).

    Stated from the decoded structure: push the return address, load
    the base pointer, set the control bits, single-pass poll, clear
    the control bits, publish id 25 with selector 0. Entry r0/r1 are
    overwritten before any use; r6 passes through untouched.
    """
    ram = dict(ram)
    trace = []
    r0_in, r1_in, r6 = regs_in

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

    write(SP0_POST - 4, seed('r15'))
    sp = SP0_POST - 4
    base = read(PTR)
    ctrl = read(base + CTRL_OFF)
    write(base + CTRL_OFF, ctrl | 0x101)
    poll = read(base + POLL_OFF)
    if (poll & 1) == 0:
        raise ValueError('battery hit a multi-pass poll')
    ctrl = read(base + CTRL_OFF)
    ctrl = (ctrl & ~(1 << 0)) & MASK
    ctrl = (ctrl & ~(1 << 8)) & MASK
    write(base + CTRL_OFF, ctrl)
    write(base + PUB_OFF, 0)
    regs = {'r0': 25, 'r1': 0, 'r2': base, 'r3': ctrl, 'r6': r6 & MASK,
            'r14': sp, 'r15': seed('r15')}
    return regs, trace, ram, base


def oracle(regs_in, ram, table_words):
    """Independent model: (outcome, regs, trace, ram).

    The postamble prefix above, then the dispatcher body for id 25
    with selector 0 (the leaf publishes r1=0; the caller r6 passes
    through). The dispatcher model below is the admitted pmudispatch
    oracle restated for the composed entry: identical except the
    pushed return address is the postamble's call site (R15_ENTRY)
    rather than the standalone seed, because the leaf reaches the
    dispatcher through a real `bsr`. Both fills reuse the reviewed
    fill oracle.
    """
    regs, trace, ram, _base = oracle_prefix(regs_in, ram)
    want = disp_oracle_composed(25, 0, regs['r6'], ram, table_words)
    if want['outcome'] != 'handoff':
        raise ValueError('dispatcher missed the handoff')
    trace.extend(want['trace'])
    return {'outcome': 'handoff', 'regs': want['regs'], 'trace': trace,
            'ram': want['ram']}


# The postamble's `bsr` lands in the dispatcher with r15 holding this
# return address (ENTRY + 54 = 0x10001DD2), not the standalone seed.
R15_ENTRY = ENTRY + 54


def disp_oracle_composed(ident, sel, caller_r6, ram, table_words):
    """Dispatcher body for the composed entry (cf. disp_oracle).

    Restates the admitted pmudispatch oracle for a dispatcher reached
    by `bsr` from the postamble: the entry push saves r15=R15_ENTRY.
    All addresses match the standalone layout because the composed
    execution starts 4 bytes high (SP0_POST). Everything else is the
    reviewed dispatcher behavior: first-table fill-id map, first
    fill, the entry-byte gate, the second fill with the original id,
    the status-bit map, and the pop-and-walk handoff.
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
    # these same words, so the caller r6 is a real input). The pushed
    # r15 is the postamble's return address: the leaf calls here.
    write(SP0 - 4, seed('r4'))
    write(SP0 - 8, seed('r5'))
    write(SP0 - 12, caller_r6)
    write(SP0 - 16, R15_ENTRY)
    for index in range(6):
        ram[DESC + 4 * index] = ram.get(DESC + 4 * index, 0x5a5a5a5a) & MASK
    regs = {'r0': 0, 'r2': 0, 'r3': 0, 'r4': ident & MASK, 'r5': seed('r5'),
            'r6': sel & MASK, 'r14': SP0, 'r15': R15_ENTRY}
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
                    return finish_fill2_composed(ident, sel, ram, trace,
                                                 regs, sp, table_words,
                                                 read, write, walk)
                # Not taken: control joins the shift with the cell
                # still loaded (no re-read); test bit b6 of it.
                bit = (other >> (b6 & 31)) & 1
            else:
                cell = read(read(DESC + 8))
                bit = (cell >> (b6 & 31)) & 1
            if bit == 0 or sel == 0:
                store4(entry)
                return finish_fill2_composed(ident, sel, ram, trace,
                                             regs, sp, table_words,
                                             read, write, walk)
            b4 = s8(read(entry + 4, 1))
            write(read(DESC + 20), (1 << (b4 & 31)) & MASK)
    return finish_fill2_composed(ident, sel, ram, trace, regs, sp,
                                 table_words, read, write, walk)


def finish_fill2_composed(ident, sel, ram, trace, regs, sp, table_words,
                          read, write, walk):
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

ENTRY_REGS = ((0, 0), (0xdeadbeef, 0xdeadbeef))
CALLER_R6 = (0x600d600d, 0)
CTRL0S = (0x0, 0x101, 0xffffffff)
POLLS = (0x1, 0x80000001, 0xffffffff)
BYTE_SETS = [(-1, 0, 0), (0, 5, 3), (5, 21, 6), (27, 31, 27),
             (31, -4, 31), (-128, 0, -8)]


def config_case(entry_regs, caller_r6, b4, b5, b6, mcell, walk_depth,
                base, ctrl0, poll):
    """Build the initial RAM for one battery case.

    The dispatcher-id-25 slice comes from the admitted pmudispatch
    battery (direct mode: id 25 passes the first table through and
    matches both fills); the postamble pointer cell and base cells are
    added. Returns (ram, table_words) or None when the mode cannot
    satisfy the constraints.
    """
    built = config_ram('direct', 25, 0, b4, b5, b6, mcell, walk_depth)
    if built is None:
        return None
    ram, table_words, _fill_slot = built
    ram[PTR] = base & MASK
    ram[base + POLL_OFF] = poll & MASK
    ram[base + PUB_OFF] = 0x5a5a5a5a
    ram[base + CTRL_OFF] = ctrl0 & MASK
    return ram, table_words


def battery_cases():
    # Case: (entry_regs, caller_r6, b4, b5, b6, mcell, walk_depth,
    # base, ctrl0, poll). The mcell bit pair (b6, b6+1) is swept over
    # set/clear wherever the first fill runs and b6 != -1; entry bytes
    # cover -1/0/edges/sign; caller_r6 0 unlocks multi-pass walks
    # (walk_depth 3 zeroes the first three deep selector slots for a
    # 4-zero walk); the postamble cells sweep the control-word start,
    # the poll don't-care bits, and two base addresses.
    cases = []
    for entry_regs in ENTRY_REGS:
        for caller_r6 in CALLER_R6:
            for b6, b5, b4 in BYTE_SETS:
                if b6 == -1:
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
                        for base in BASES:
                            for ctrl0 in CTRL0S:
                                for poll in POLLS:
                                    cases.append((entry_regs, caller_r6,
                                                  b4, b5, b6, mcell,
                                                  walk_depth, base,
                                                  ctrl0, poll))
    return cases


def check_shape(source_code, entry, size, stock):
    """Fail closed on prologue/transfer/pool drift."""
    addresses = sorted(source_code)
    if source_code[addresses[0]] != ('push', 'r15', 2):
        raise ValueError('prologue push changed: ' + repr(source_code[addresses[0]]))
    if source_code[addresses[1]][0] != 'lrw':
        raise ValueError('base-pointer lrw changed: ' + repr(source_code[addresses[1]]))
    covered = max(addresses) + source_code[max(addresses)][2] - entry
    if covered != size:
        raise ValueError('section size changed: %d vs %d' % (covered, size))
    pops = [pc for pc in addresses if source_code[pc][0] == 'pop']
    if len(pops) != 1 or source_code[pops[0]][1] != 'r15':
        raise ValueError('expected exactly one epilogue pop of r15')
    calls = [pc for pc in addresses if source_code[pc][0] == 'bsr']
    if len(calls) != 1 or int(source_code[calls[0]][1], 0) != DISP:
        raise ValueError('expected exactly one dispatcher call to %#x' % DISP)
    lrw_ops = [pc for pc in addresses if source_code[pc][0] == 'lrw']
    if len(lrw_ops) != 1 or source_code[lrw_ops[0]][1] != 'r3, 0x20002274':
        raise ValueError('expected exactly one numeric base-pointer lrw')
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('bt', 'bf', 'br', 'bez', 'bnez', 'blz'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
        if op in ('rts', 'jmp', 'jmpi', 'jsr', 'bkpt', 'bnezad'):
            raise ValueError('unexpected transfer %s at %#x' % (op, pc))
    # The transliteration keeps the stock encoding exactly (no
    # peepholes were needed): byte identity against the envelope is
    # pinned on the linked payload in verify().


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


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-postamble'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    post_obj = output / 'postamble_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *POST_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(post_obj)], check=True)
    disp_obj = output / 'pmudispatch_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUDISP_FLAGS,
                    '-c', str(DISP_SOURCE), '-o', str(disp_obj)], check=True)
    fill_obj = output / 'fill_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                    '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
    script = output / 'postamble.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'postamble.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(post_obj), str(disp_obj), str(fill_obj),
                    '-o', str(elf_path)], check=True)
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
    # Stock body plus the stock dispatcher and fill it calls.
    stock_code = {}
    for lo, hi in (('0x10001d9c', '0x10001dd8'), ('0x10000d98', '0x10000ea0'),
                   ('0x10000780', '0x10000834')):
        stock_code.update(decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=' + lo, '--stop-address=' + hi,
             str(adjusted)], text=True)))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'postamble.disassembly.txt').write_text(disassembly)
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
        check_shape(source_code, entry, len(payload), stock[offset:offset + size])
        if sha(payload) != sha(stock[offset:offset + size]):
            raise ValueError('linked payload is not byte-identical to the stock envelope')
        # The linked dispatcher and fill bodies execute on the source
        # side too.
        source_all = {}
        for section_code in sources.values():
            source_all.update(section_code)
        for case in battery_cases():
            (entry_regs, caller_r6, b4, b5, b6, mcell, walk_depth,
             base, ctrl0, poll) = case
            built = config_case(entry_regs, caller_r6, b4, b5, b6,
                                mcell, walk_depth, base, ctrl0, poll)
            if built is None:
                raise ValueError('battery built an impossible case %r' % (case,))
            ram, table_words = built
            # Retained jump tables are analysis-oracle inputs: map the
            # dumped stock words for both executed sides.
            for base_addr, ids in ((JT1, JT1_IDS), (JT2, JT2_IDS)):
                for index, want_word in zip(ids, jt1 if base_addr == JT1 else jt2):
                    ram[base_addr + 4 * (index - ids[0])] = want_word & MASK
            want = oracle((entry_regs[0], entry_regs[1], caller_r6),
                          ram, table_words)
            if want['outcome'] != 'handoff':
                raise ValueError('battery missed the handoff on %r' % (case,))
            stock_regs, stock_trace, stock_final = run_side(
                stock_code, entry, (entry_regs[0], entry_regs[1], caller_r6),
                ram, 'stock')
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
                source_all, entry, (entry_regs[0], entry_regs[1], caller_r6),
                ram, 'source')
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
              'compile_flags': POST_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'no upstream register map is used: every '
                                    'address is a pointer-cell value or a '
                                    'retained table base and every constant '
                                    'is a stock immediate; clean-room body '
                                    'from decoded stock flow, no SDK text '
                                    'reproduced',
              'functions': functions, 'target_cases': cases,
              'handoff': hex(HANDOFF),
              'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot '
                                 'stage-1 rail postamble only (entry '
                                 'through handoff into retained 0x10000ea0, '
                                 'exact unfiltered traces, byte-identical '
                                 'payload)',
              'stock_equivalence_proven': False,
              'leftover_paths': 'multi-pass polls spin both sides on the '
                                'same three byte-identical instructions and '
                                'are excluded from the battery; '
                                'dispatcher fill failures observe fill '
                                'scratch leftovers and are excluded (id 25 '
                                'matches both fills in every battery case). '
                                'The assembly keeps the same branches without '
                                'an outcome claim there. The dead rts past '
                                'the envelope stays retained and is never '
                                'executed: the dispatcher does not return.',
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
    (ROOT / 'docs/research/gx8002-uart-stage1-postamble-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-postamble-verification.json').read_text()),
        indent=2))
