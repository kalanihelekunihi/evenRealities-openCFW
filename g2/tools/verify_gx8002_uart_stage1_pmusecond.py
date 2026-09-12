#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 pmusecond leaf.

Compares the reviewed clean-room assembly in
components/shared/gx8002/runtime_gx8002_uart_stage1_pmusecond.S against
the stock stage-1 body by executing decoded C-SKY instructions for both
across a battery of id/descriptor/table/MMIO configurations, plus an
independent Python oracle.

Leaf: the second PMU rail dispatcher body at runtime 0x10000EB8,
package 0xF08, 476 bytes of code: the restore-and-retry-19 block, one
`pmu_fill_desc` call into a 24-byte stack descriptor, descriptor
byte/bit gating, a UART-clock divisor computation from the
0xA0005000-block registers, an entry-word multiplier path, and
fill-retry loops that never return (no `rts`; H-class, like the
reviewed rail leaves). The 24-byte entry head (frame setup, id-range
guard, retained jump-table dispatch) stays retained stock and executes
identically on both sides. The real linked fill bodies run on both
sides: stock fill for stock, compiled source fill for source.
Compared: the complete unfiltered access trace (kind, address, width,
and value of every read and write, including push/pop/desc/table
traffic), the final RAM, and the live registers when the fourth fill
call is reached (every path loops back to the fill; MAX_FILLS bounds
the H-class loop).

Behavioral equivalence only: the assembly keeps the stock register
plan and control flow with two documented deviations at the body entry
(a trace-neutral `nop` position pad for the stock dead `movi r0, 0`,
and the fill-failure branch retargeted past it to the restore block;
both battery-proven). Admission rests on decoded-trace equivalence.
Both frames are exactly 24 bytes with the descriptor at the base and
the caller window is fully mapped, so all traffic is compared exactly:
no stack window is excluded. `lrw` performs no modeled access, so pool
placement is trace-invisible.

Fill-failure exits observe the fill body's scratch leftovers (stock
leaves its own registers; the compiled source fill leaves its own),
so chains whose last executed fill misses run with
implementation-defined registers: those cases compare the exact trace
and RAM but only the fill-independent registers (the oracle flags
them). Every other case compares the full live set. Out-of-range ids
take the retained guard bypass; the dispatch reads slot id-7, so
id 25 reads the last in-bounds slot (the retry-10 arm), with the table
bounds pinned against the stock dump. Register shifts by a register
count use the low 5 bits; three-operand register shifts never occur in
this body but the executor keeps the reversed-order reading proven by
the first dispatcher for shared-code parity. The `mul.u32` low word is
modeled (the high half is never read); every `divu` site is provably
nonzero on reachable paths and the executor fail-closes on a zero
divisor. Hardware timing remains unqualified.
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
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmusecond.S'
FILL_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_pmufill.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-PMUSECOND-NOTICE.txt'
PMUSECOND_FLAGS = ['-Os', *FLAGS[1:]]

MASK = 0xffffffff
ENTRY = 0x10000ea0
BODY = 0x10000eb8
FILL = 0x10000780
JT = 0x10001ef4
JT_IDS = tuple(range(7, 26))
SP0 = 0x20002800
SCRATCH = 0x20004000
SCRATCH2 = 0x20005000
SCRATCH3 = 0x20006000
WINDOW_LO = SP0 - 64
WINDOW_HI = SP0 + 4096
STEP_CAP = 30000
MAX_FILLS = 3
MMIO_UART = 0xa0005000
MMIO_CELL = 0xa001008c

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_pmu_second_body', 0x10000eb8, 0xf08, 476,
     'pmusecond', 'compiled_assembly'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_pmu_second_body 0x10000eb8 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_second_body) }
  .text.open_cfw_gx8002_uart_stage1_pmu_fill_desc 0x10000780 : { *(.text.open_cfw_gx8002_uart_stage1_pmu_fill_desc) }
}
'''

# Retained jump-table targets by id (dumped from the stock image;
# pinned by check_tables below; slot id-7). 0xEB8 restores the frame and retries
# with 19; 0xEBE sets 19; 0xEC0 fills with the entry id unchanged;
# 0xF7C/0xF80/0xF84 retry with 16/22/10.
JT_TARGET = {7: 0x10000eb8, 8: 0x10000eb8, 9: 0x10000ec0,
             10: 0x10000ec0, 11: 0x10000ec0, 12: 0x10000ec0,
             13: 0x10000ec0, 14: 0x10000ec0, 15: 0x10000ec0,
             16: 0x10000ec0, 17: 0x10000f7c, 18: 0x10000f7c,
             19: 0x10000ec0, 20: 0x10000ebe, 21: 0x10000ebe,
             22: 0x10000ec0, 23: 0x10000f80, 24: 0x10000f80,
             25: 0x10000f84}
JT_EXPECT = [0x10000eb8, 0x10000eb8, 0x10000ec0, 0x10000ec0,
             0x10000ec0, 0x10000ec0, 0x10000ec0, 0x10000ec0,
             0x10000ec0, 0x10000ec0, 0x10000f7c, 0x10000f7c,
             0x10000ec0, 0x10000ebe, 0x10000ebe, 0x10000ec0,
             0x10000f80, 0x10000f80, 0x10000f84]

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


class StoppedAtFill(Exception):
    """Reached the (MAX_FILLS+1)-th fill call (the routine never returns)."""

    def __init__(self, registers, model, fills):
        super().__init__('stopped at fill')
        self.registers = dict(registers)
        self.model = model
        self.fills = fills


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


def execute(code, start, args, model):
    """Run decoded code with r0/r1=args against the model.

    args is (r0, r1); every other register starts from a fixed seed
    and r14 starts at SP0. Stops at the (MAX_FILLS+1)-th call of the
    fill routine and raises StoppedAtFill. Raises ValueError on
    unmapped access or trap words.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=args[0] & MASK, r1=args[1] & MASK, r14=SP0)
    condition = False
    fills = 0
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
        elif op == 'mult':
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] * registers[parts[1]]) & MASK
            else:
                registers[parts[0]] = (registers[parts[1]] * registers[parts[2]]) & MASK
        elif op == 'mul.u32':
            # Low 32 bits to the named destination; the body never
            # reads the high half (see the audit doc).
            registers[parts[0]] = (registers[parts[1]] * registers[parts[2]]) & MASK
        elif op == 'divu':
            if registers[parts[2]] == 0:
                raise ValueError('division by zero at %#x' % pc)
            registers[parts[0]] = (registers[parts[1]] // registers[parts[2]]) & MASK
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
                # the first dispatcher's stock body (see its audit
                # doc). No three-register shift occurs in this body.
                registers[parts[0]] = (registers[parts[2]] << (registers[parts[1]] & 31)) & MASK
        elif op in ('lsr', 'tlsr'):
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] >> (registers[parts[1]] & 31)) & MASK
            else:
                registers[parts[0]] = (registers[parts[2]] >> (registers[parts[1]] & 31)) & MASK
        elif op in ('tlsri', 'lsri'):
            registers[parts[0]] = (registers[parts[1]] >> int(parts[2], 0)) & MASK
        elif op in ('rotl', 'rotli'):
            if len(parts) == 2:
                count = int(parts[1], 0) & 31
                value = registers[parts[0]]
            elif parts[2].startswith('r'):
                count = registers[parts[2]] & 31
                value = registers[parts[1]]
            else:
                count = int(parts[2], 0) & 31
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
            fills += 1
            if fills > MAX_FILLS:
                raise StoppedAtFill(registers, model, fills - 1)
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


def rotl(value, count):
    count &= 31
    return ((value << count) | (value >> ((32 - count) & 31))) & MASK


def oracle(ident, r1seed, ram, table_words):
    """Independent model: (outcome, regs, trace, ram, full_regs).

    Stated from the decoded structure, not from decoded instructions:
    retained-head push/guard/table dispatch, the fill loop with
    caller-stack drift, the entry-byte gate, the fill-id class split,
    the extended/cell bit tests, the divisor sink, the descriptor-walk
    tail with its retry arms, the bit-set UART-clock computation with
    range clamps, and the entry-word multiplier path. Both fills reuse
    the reviewed fill oracle; everything else is modeled here. Stops
    at the (MAX_FILLS+1)-th fill call like the executor. full_regs is
    False when the last executed fill missed (fill scratch
    implementation-defined: trace and RAM still compare, registers
    compare on the fill-independent subset).
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

    def read_half(address):
        base = address & ~3
        if base not in ram:
            raise ValueError('oracle missing cell at ' + hex(address))
        if (address & 3) == 3:
            raise ValueError('halfword read spans words')
        value = (ram[base] >> ((address & 3) * 8)) & 0xffff
        trace.append(('read', address, 2, value))
        return value

    def write(address, value):
        if address not in ram:
            raise ValueError('oracle missing cell at ' + hex(address))
        value &= MASK
        ram[address] = value
        trace.append(('write', address, 4, value))

    regs = {f'r{i}': seed(f'r{i}') for i in range(32)}
    regs.update(r0=ident & MASK, r1=r1seed & MASK, r14=SP0)
    sp = SP0
    fills = 0
    all_hit = True

    def do_fill(fid, desc):
        # Merge only the traced writes: the fill oracle silently
        # pre-fills the six descriptor words with 0x5A garbage (its
        # own battery maps them so), which must not leak into this
        # battery's stack-mapped descriptor. The fill never reads
        # the descriptor (writes only), so the garbage is unread.
        nonlocal fills, all_hit
        rc, _fill_ram, fill_trace = fill_oracle(fid, desc,
                                                dict(table_words))
        for kind, address, _width, value in fill_trace:
            if kind == 'write':
                ram[address] = value & MASK
        trace.extend(fill_trace)
        regs['r0'] = rc & MASK
        fills += 1
        if rc != 0:
            all_hit = False
        return rc

    def restore():
        # Stock 0xEBA (reviewed .Lrestore19): pop the 24-byte frame
        # plus the push pair; consumes caller-stack words on repeat
        # passes. r4 is always overwritten next; r15 is caller
        # garbage (mapped, same on both sides). Pop order matches
        # the executor (r15 first, then r4).
        nonlocal sp
        sp = (sp + 24) & MASK
        regs['r15'] = read(sp)
        regs['r4'] = read(sp + 4)
        sp = (sp + 8) & MASK
        regs['r14'] = sp

    def stop():
        regs['r14'] = sp
        return {'outcome': 'stopped', 'regs': regs, 'trace': trace,
                'ram': ram, 'full_regs': all_hit, 'fills': fills}

    def extended_path(b6):
        # Stock 0xEEA: bit (b6+1) of the word at [desc+8].
        regs['r13'] = (b6 + 1) & MASK
        regs['r12'] = read(0xa0010080 + 0xc)
        regs['r0'] = read(sp + 8)
        if regs['r13'] == 0:
            return bittest(regs['r0'], b6)
        word = read(regs['r0'])
        if (((word >> (regs['r13'] & 31)) & MASK) & 1) == 0:
            return bittest(regs['r0'], b6)
        regs['r0'] = 32000
        return 'walk'

    def cell_path(entry, b6):
        # Stock 0xF10: entry and b6 already loaded by the gate.
        regs['r0'] = read(sp + 8)
        regs['r12'] = read(0xa0010080 + 0xc)
        return bittest(regs['r0'], b6)

    def bittest(r0, b6):
        # Stock 0xF1C: bit b6 of the entry word at [r0].
        if (((read(r0) >> (b6 & 31)) & MASK) & 1) != 0:
            return bitset_path(r0, b6)
        return sink_path()

    def sink_path():
        # Stock 0xF28: the inct result feeds r0 only when the cell is
        # nonzero, else r0 keeps the descriptor word; the r4 chain
        # then provably always restores except for r4 in
        # {0,1,3,4,5,7,8}, which fall through to the walk tail with
        # the computed divisor (see the audit doc).
        if regs['r12'] != 0:
            regs['r0'] = rotl(64000, 4)
        if not (9 >= regs['r4']):
            return 'restore19'
        if regs['r4'] != 9:
            regs['r4'] = (regs['r4'] & ~(1 << 2)) & MASK
            if regs['r4'] == 2:
                return 'restore19'
            return 'walk'
        return 'restore19'

    def walk_tail(entry, reload):
        # Stock 0xF56/0xF5A: table-driven divisor, ends in divu plus
        # the shared restore/retry-16 terminator. reload selects the
        # 0xF56 entry (reloads r12 from the descriptor); the mul-path
        # joins (0x101E/0x102E/0x1040 to 0xF5A) keep the r12 the
        # multiplier entry loaded.
        if reload:
            regs['r12'] = read(sp + 4)
        r2 = read(entry + 8)
        if r2 == 0:
            return 'restore19'
        b0 = read(r2, 1)
        r3 = (b0 + regs['r12']) & MASK
        b1 = read(r2 + 1, 1)
        regs['r1'] = entry
        r3 = read(r3)
        r3 = (r3 >> (b1 & 31)) & MASK
        r2 = read_half(r2 + 2)
        r3 &= r2
        if r3 == 0:
            return 'restore19'
        r3 = (r3 + 1) & MASK
        if r3 == 0:
            raise ValueError('walk divisor is zero')
        regs['r0'] = (regs['r0'] // r3) & MASK
        return 'retry16'

    def restore_like_walk():
        # Stock 0xF78: the walk tail's own restore (addi, pop) before
        # the shared retry-16 terminator.
        nonlocal sp
        sp = (sp + 24) & MASK
        regs['r15'] = read(sp)
        regs['r4'] = read(sp + 4)
        sp = (sp + 8) & MASK
        regs['r14'] = sp

    def bitset_path(r0, b6):
        # Stock 0xF88.
        word = read(r0)
        regs['r0'] = word
        if ((word >> (b6 & 31)) & MASK) & 1 == 0:
            return 'walk'
        r12 = regs['r12'] & 1
        regs['r12'] = r12
        if r12 == 0:
            return 'mul'
        return 'clock'

    def clock_path(entry):
        # Stock 0xF9C: UART-clock divisor computation. The or/addi
        # pair always executes; the div_cfg arms select the
        # multiplier source.
        r2base = MMIO_UART
        r13init = 7936
        r0 = read(r2base + 0x1c) & 63
        r12 = (r0 + 1) & MASK
        regs['r12'] = r12
        r0 = read(r2base + 0x20)
        r3 = read(r2base + 0x24)
        r3 = ((r3 << 8) & MASK) & r13init
        r13 = read(r2base + 0x28)
        regs['r13'] = r13
        r2 = read(r2base + 0x30)
        cfg = (r2 >> 4) & 3
        regs['r0'] = r0
        regs['r3'] = r3
        r0 = (r0 | r3) & MASK
        r3 = (r0 + 1) & MASK
        regs['r0'] = r0
        regs['r3'] = r3
        if cfg == 2:
            # Stock 0x106A arm.
            regs['r2'] = rotl(42000, 11)
            return clock_join(entry)
        if cfg == 3:
            # Stock 0x1064 arm.
            regs['r2'] = (1500 << 16) & MASK
            return clock_join(entry)
        # cfg 0/1: stock 0xFCA arm with the inct conditional move
        # (taken unless cfg == 1).
        r0 = rotl(60000, 10)
        r2 = (1125 << 16) & MASK
        if cfg != 1:
            r2 = (r0 + 0) & MASK
        regs['r2'] = r2
        return clock_join(entry)

    def clock_join(entry):
        # Stock 0xFDC. r3 is always or+1 here: the or/addi pair runs
        # before the div_cfg branches on every path.
        r2 = regs['r2']
        r12 = regs['r12']
        r3 = regs['r3']
        r13 = regs['r13']
        if r3 == 0:
            raise ValueError('clock divisor is zero')
        r2 = (r2 * r12) & MASK
        r0 = (~15999) & MASK
        r2 = (r2 // r3) & MASK
        r18 = (r2 + r0) & MASK
        regs['r2'] = r2
        regs['r18'] = r18
        r0 = 31999
        if r0 >= r18:
            regs['r0'] = 32000
            return range0div(entry)
        r0 = 0xfff83000
        r18 = (r2 + r0) & MASK
        regs['r18'] = r18
        r0 = 0x000f9fff
        if r0 >= r18:
            regs['r0'] = rotl(64000, 4)
            return range0div(entry)
        r0 = 0xfffda800
        r2 = (r2 + r0) & MASK
        regs['r2'] = r2
        r0 = 0x002c87ff
        if r0 >= r2:
            regs['r0'] = rotl(64000, 5)
            return range0div(entry)
        regs['r0'] = 0
        regs['r0'] = (regs['r0'] - 1) & MASK
        return 'restore19'

    def range0div(entry):
        # Stock 0x1046 (joined from 0x1042/0x105E/0x107C with r0 and
        # r3 preset by the caller).
        r12 = regs['r12']
        r3 = regs['r3']
        r13 = regs['r13']
        if r12 == 0:
            raise ValueError('range divisor is zero')
        r0 = (regs['r0'] // r12) & MASK
        r0 = (r0 * r3) & MASK
        r3 = r13 & 7
        r3 = (r3 + 1) & MASK
        r3 = (r3 + r3) & MASK
        if r3 == 0:
            raise ValueError('range divisor is zero')
        r0 = (r0 // r3) & MASK
        regs['r0'] = r0
        regs['r3'] = r3
        return mul_entry_at(entry)

    def mul_path(entry):
        # Stock 0x1014.
        regs['r0'] = (375 << 16) & MASK
        return mul_entry_at(entry)

    def mul_entry_at(entry):
        # Stock 0x1018. All three exits join the walk at 0xF5A
        # (r12 already loaded here), reported as walkjoin.
        r3 = read(entry + 12)
        r12 = read(sp + 4)
        regs['r12'] = r12
        if r3 == 0:
            regs['r1'] = entry
            return 'walkjoin'
        b0 = read(r3, 1)
        r3 = (b0 + r12) & MASK
        r2 = read(r3)
        r3 = 2048 & r2
        if r3 != 0:
            regs['r1'] = entry
            return 'walkjoin'
        r2 &= 0xffffff
        r2 = (r2 * regs['r0']) & MASK
        r0 = ((r3 << 7) | (r2 >> 25)) & MASK
        regs['r0'] = r0
        regs['r2'] = r2
        regs['r1'] = entry
        return 'walkjoin'

    # Entry push + frame (stock 0xEA0, retained).
    write(sp - 4, regs['r4'])
    write(sp - 8, regs['r15'])
    sp = (sp - 32) & MASK
    regs['r14'] = sp
    # Range guard (stock 0xEA4): sub = id-7 unsigned.
    sub = (ident - 7) & MASK
    regs['r4'] = ident & MASK
    if sub >= 19:
        fid = ident
    else:
        # Table dispatch (stock 0xEAC lrw the table base, 0xEAE ldr.w
        # the slot, 0xEB2 jmp to it): slot sub (id-7), so id 25 reads
        # the last in-bounds slot.
        target = read(JT + 4 * sub)
        if target != JT_TARGET[ident]:
            raise ValueError('jump table drifted at id %d' % ident)
        if target == 0x10000eb8:
            # Table arm for 7,8: dead move, restore, retry with 19.
            restore()
            regs['r4'] = 19
            fid = 19
        elif target == 0x10000ebe:
            regs['r4'] = 19
            fid = 19
        elif target == 0x10000ec0:
            fid = regs['r4']
        elif target == 0x10000f7c:
            regs['r4'] = 16
            fid = 16
        elif target == 0x10000f80:
            regs['r4'] = 22
            fid = 22
        elif target == 0x10000f84:
            regs['r4'] = 10
            fid = 10
        else:
            raise ValueError('unexpected table target ' + hex(target))

    while True:
        # Fill entry (stock 0xEC0).
        regs['r1'] = sp
        regs['r0'] = regs['r4']
        if fills >= MAX_FILLS:
            return stop()
        rc = do_fill(regs['r0'], sp)
        if rc != 0:
            restore()
            regs['r4'] = 19
            continue
        entry = read(sp)
        b6 = s8(read(entry + 6, 1))
        if b6 == -1:
            restore()
            regs['r4'] = 19
            continue
        if regs['r4'] >= 10:
            outcome = cell_path(entry, b6)
        elif ((1 << regs['r4']) & 579) == 0:
            outcome = cell_path(entry, b6)
        else:
            outcome = extended_path(b6)
        # 'walk' enters at 0xF56 (reloads r12); 'walkjoin' enters at
        # 0xF5A (keeps the multiplier entry's r12).
        while outcome in ('walk', 'walkjoin', 'clock', 'mul'):
            if outcome == 'walk':
                outcome = walk_tail(entry, True)
            elif outcome == 'walkjoin':
                outcome = walk_tail(entry, False)
            elif outcome == 'clock':
                outcome = clock_path(entry)
            elif outcome == 'mul':
                outcome = mul_path(entry)
        if outcome == 'restore19':
            restore()
            regs['r4'] = 19
            continue
        if outcome == 'retry16':
            restore_like_walk()
            regs['r4'] = 16
            continue
        raise ValueError('unexpected outcome ' + str(outcome))
FULL_REGS = ('r0', 'r1', 'r4', 'r5', 'r6', 'r7', 'r14', 'r15')
# Live set compared on every case. r2/r3/r12/r13/r18 hold fill scratch
# on some paths (the fill clobbers them and the body does not always
# redefine them before the stop point); they are verified through the
# exact trace and RAM instead, and any divergence that steers control
# flow or stores would surface there. r5/r6/r7 are seeds the fill
# provably preserves and the body never touches.
SAFE_REGS = FULL_REGS

UART_TUPLES = [
    (0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000010),
    (0xffffffff, 0x12345678, 0x0000001f, 0x00000007, 0x00000020),
    (0x00000000, 0x80000000, 0x00000000, 0xffffffff, 0x00000030),
    (0xffffffff, 0x00000001, 0x0000001f, 0x00000007, 0x00000000),
]
CELL12_VALUES = (0x00000000, 0x00000001, 0x00000004, 0x00000005)
PATTERN = {}
for _b in range(256):
    PATTERN[_b] = 0x800 if _b & 1 else 0x1


def first_fill_id(ident):
    sub = (ident - 7) & MASK
    if sub >= 19:
        return ident
    return {0: 19, 1: 19, 10: 16, 11: 16, 13: 19, 14: 19,
            16: 22, 17: 22, 18: 10}.get(sub, ident)


def battery_cases():
    """(ident, r1seed, mode, b6, w2kind, w3kind, deep, b0, cellbit,
    cell12, uart) cases. mode selects the fill-table shape: direct
    (identity), miss1 (first-fill slot broken, retries intact), or
    missloop (a retry slot broken: the loop never settles and the
    stop-point registers compare on the fill-independent subset).
    w2kind/w3kind select the entry+8/+12 words (0 or a mapped
    scratch); deep selects the scratch byte/half patterns; cellbit
    selects the extended-test cell bit; cell12 and uart seed
    the MMIO cells."""
    cases = []
    ids = [0, 1, 2, 6, 7, 8, 9, 10, 12, 15, 16, 18, 19, 22, 24,
           25, 26, 27, 31]
    deep_sets = [(0, 0, 0), (0, 0, 0xffff), (1, 0, 0xffff)]
    r1seeds = (0x600d600d, 0x00000000)
    for index, ident in enumerate(ids):
        fid = first_fill_id(ident)
        modes = ['direct']
        if fid <= MAX_ID and fid not in (10, 16, 19, 22):
            modes.append('miss1')
        if ident in (7, 16):
            modes.append('missloop')
        for mode in modes:
            for b6 in (-1, 0, 5, 31):
                for w2kind in (0, 1):
                    for w3kind in (0, 1):
                        deeps = deep_sets if w2kind else [(0, 0, 0)]
                        b0s = (0, 1) if w3kind else (0,)
                        for deep in deeps:
                            for b0 in b0s:
                                for cellbit in (0, 1):
                                    cell12 = CELL12_VALUES[(index + b6) % 4]
                                    uart = UART_TUPLES[(index + w2kind + w3kind) % 4]
                                    r1seed = r1seeds[(index + cellbit) % 2]
                                    cases.append((ident, r1seed, mode, b6,
                                                  w2kind, w3kind, deep, b0,
                                                  cellbit, cell12, uart))
    if len(cases) < 500:
        raise ValueError('battery too small: %d' % len(cases))
    if len(cases) > 4000:
        raise ValueError('battery too large: %d' % len(cases))
    return cases


def config_ram(ident, mode, b6, w2kind, w3kind, deep, b0, cellbit,
               cell12, uart, jt):
    """RAM + fill-table words for one battery case."""
    ram = {}
    words = list(range(TABLE_ENTRIES))
    if mode == 'miss1':
        slot = first_fill_id(ident)
        words[slot] = 0x70000000 + slot
    elif mode == 'missloop':
        slot = 19 if ident == 7 else 16
        words[slot] = 0x70000000 + slot
    packed = (0xa5 | (0xa5 << 8) | ((b6 & 0xff) << 16) | (0xa5 << 24)) & MASK
    w2 = 0 if not w2kind else SCRATCH2
    w3 = 0 if not w3kind else SCRATCH3
    for slot in range(TABLE_ENTRIES):
        base = FILL_TABLE_BASE + slot * ENTRY_STRIDE
        ram[base] = words[slot] & MASK
        ram[base + 4] = packed
        ram[base + 8] = w2
        ram[base + 12] = w3
    table_words = {FILL_TABLE_BASE + slot * ENTRY_STRIDE: words[slot] & MASK
                   for slot in range(TABLE_ENTRIES)}
    for address in range(WINDOW_LO, WINDOW_HI, 4):
        ram[address] = SCRATCH
    ram[SCRATCH2] = ((deep[0] & 0xff) | ((deep[1] & 0xff) << 8)
                     | ((deep[2] & 0xffff) << 16)) & MASK
    ram[SCRATCH3] = b0 & 0xff
    bit = ((b6 + 1) & 31) if b6 != -1 else 0
    # Extended/cell bit tests dereference the descriptor's word2,
    # which the fill sets to the domain select word. The PMU select
    # word doubles as the r12 cell, so it carries the cell12 sweep
    # (the extended bit then reads cell12's bits, which still covers
    # taken/missed across the sweep); the MCU select word carries
    # the orthogonal cellbit pattern. The base|0x18 words the fill
    # also writes are never dereferenced by this body and stay
    # unmapped on purpose.
    cell = (1 << bit) & MASK if cellbit else 0
    ram[MCU_BASE | MCU_SELECT] = cell
    ram[MMIO_CELL] = cell12 & MASK
    w1c, w20, w24, w28, w30 = uart
    ram[MMIO_UART + 0x1c] = w1c & MASK
    ram[MMIO_UART + 0x20] = w20 & MASK
    ram[MMIO_UART + 0x24] = w24 & MASK
    ram[MMIO_UART + 0x28] = w28 & MASK
    ram[MMIO_UART + 0x30] = w30 & MASK
    # Walk/mul tails dereference (entry byte + desc word1), where desc
    # word1 is the domain base the fill wrote (PMU_BASE/MCU_BASE).
    for base in (PMU_BASE, MCU_BASE):
        for i in range(256):
            ram[base + i] = PATTERN[i]
    for i, ident_jt in enumerate(JT_IDS):
        ram[JT + 4 * i] = jt[i] & MASK
    # The or+1 divisor at 0xFDC must be nonzero (fail-closed below).
    sel = (w20 | ((w24 << 8) & 7936)) & MASK
    if (sel + 1) & MASK == 0:
        raise ValueError('excluded zero or-divisor case')
    return ram, table_words


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
    addresses = sorted(source_code)
    if source_code[addresses[0]] != ('mov', 'r0, r0', 2):
        raise ValueError('body must open with the entry pad, got %s'
                         % (source_code[addresses[0]],))
    ops = [op for op, _, _ in source_code.values()]
    bsrs = [pc for pc in addresses if source_code[pc][0] == 'bsr']
    if len(bsrs) != 1 or int(source_code[bsrs[0]][1], 0) != FILL:
        raise ValueError('body must call the fill exactly once')
    if any(op == 'jmp' for op in ops):
        raise ValueError('the indirect jump lives in the retained head')
    if ops.count('bkpt') != 1:
        raise ValueError('body must keep the unreachable trap word')
    if ops.count('rts') != 0:
        raise ValueError('the routine never returns')
    if ops.count('mul.u32') != 1 or ops.count('divu') != 4 \
            or ops.count('mult') != 2 or ops.count('rotli') != 6:
        raise ValueError('arithmetic census drifted')
    lrws = sorted(pc for pc in addresses if source_code[pc][0] == 'lrw')
    if len(lrws) != 5:
        raise ValueError('body must materialize five constants, got %d'
                         % len(lrws))
    pools = set()
    for pc in lrws:
        pools.add(int(source_code[pc][1].split(',')[1].strip(), 0))
    if pools != {0xa0005000, 0xfff83000, 0x000f9fff, 0xfffda800,
                 0x002c87ff}:
        raise ValueError('pool set drifted: %s'
                         % sorted(hex(p) for p in pools))
    movihs = sorted(source_code[pc][1] for pc in addresses
                    if source_code[pc][0] == 'movih')
    if movihs != ['r0, 375', 'r2, 1125', 'r2, 1500', 'r3, 2048',
                  'r3, 4', 'r3, 40961', 'r3, 40961']:
        raise ValueError('movih set drifted: %s' % (movihs,))
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('bt', 'bf', 'bez', 'bnez', 'br'):
            for target in re.findall(r'0x[0-9a-fA-F]+', operand):
                address = int(target, 0)
                if not BODY <= address < BODY + 476:
                    raise ValueError('branch leaves the body at %#x' % pc)


def check_tables(stock):
    words = [struct.unpack_from('<I', stock, 0x1f44 + 4 * i)[0]
             for i in range(19)]
    if words != JT_EXPECT:
        raise ValueError('retained jump table drifted: %s'
                         % [hex(w) for w in words])
    return words


def run_side(code, entry, args, ram, label):
    registers = None
    model = Model(ram)
    try:
        execute(code, entry, args, model)
    except StoppedAtFill as stop:
        registers = stop.registers
        model = stop.model
    if registers is None:
        raise ValueError('%s case did not reach the stop point' % label)
    return registers, model.trace, model.ram


def register_reference():
    return ('no upstream register map is used: every address is a '
            'fill-provided descriptor value, a retained table base, or '
            'a modeled MMIO address, and every constant is a stock '
            'immediate; clean-room body from decoded stock flow, no SDK '
            'text reproduced')


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = Path(output) if output else ROOT / 'build/gx8002-uart-stage1-pmusecond'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    body_obj = output / 'pmusecond_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUSECOND_FLAGS,
                    '-c', str(S_SOURCE), '-o', str(body_obj)], check=True)
    fill_obj = output / 'pmufill.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                    '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
    script = output / 'pmusecond.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'pmusecond.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(body_obj), str(fill_obj), '-o', str(elf_path)],
                   check=True)
    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    jt = check_tables(stock)
    # Analysis-only slice wrapper: the stage-1 span is rewrapped with
    # the CK804EF ELF flags and shifted to its runtime base so decoded
    # branch targets are absolute. No stock bytes enter the assembled
    # source objects.
    wrapper = output / 'stock-analysis.elf'
    (output / 'stage1-slice.bin').write_bytes(stock[0x50:0x2050])
    subprocess.run([str(prefix / 'csky-unknown-elf-objcopy'), '-I', 'binary',
                    '-O', 'elf32-csky-little', '-B', 'csky',
                    '--set-section-flags', '.data=alloc,code,load',
                    str(output / 'stage1-slice.bin'), str(wrapper)],
                   check=True)
    data = bytearray(wrapper.read_bytes())
    struct.pack_into('<I', data, 36, 0x21006009)
    wrapper.write_bytes(data)
    adjusted = output / 'stock-analysis-vma.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-objcopy'),
                    '--adjust-vma=0x10000000', str(wrapper), str(adjusted)],
                   check=True)
    # Stock body (head plus body) plus the stock fill it calls.
    stock_code = {}
    for lo, hi in (('0x10000ea0', '0x10001094'), ('0x10000780', '0x10000834')):
        stock_code.update(decode(subprocess.check_output(
            [str(prefix / 'csky-unknown-elf-objdump'), '-D',
             '--start-address=' + lo, '--stop-address=' + hi,
             str(adjusted)], text=True)))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)],
        text=True)
    (output / 'pmusecond.disassembly.txt').write_text(disassembly)
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
        # The source side runs the retained stock head (identical
        # bytes on both sides) into the reviewed body and the linked
        # source fill; the stock side runs the retained head into the
        # stock body and the stock fill.
        source_all = {a: v for a, v in stock_code.items() if a < BODY}
        source_all.update(source_code)
        source_all.update(sources['.text.open_cfw_gx8002_uart_stage1_pmu_fill_desc'])
        for case in battery_cases():
            (ident, r1seed, mode, b6, w2kind, w3kind, deep, b0,
             cellbit, cell12, uart) = case
            ram, table_words = config_ram(ident, mode, b6, w2kind,
                                          w3kind, deep, b0, cellbit,
                                          cell12, uart, jt)
            want = oracle(ident, r1seed, dict(ram), table_words)
            if want['outcome'] != 'stopped':
                raise ValueError('battery missed the stop point on %r' % (case,))
            stock_regs, stock_trace, stock_final = run_side(
                stock_code, ENTRY, (ident, r1seed), dict(ram), 'stock')
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
                source_all, ENTRY, (ident, r1seed), dict(ram), 'source')
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
            live = FULL_REGS if want['full_regs'] else SAFE_REGS
            for reg in live:
                if src_regs[reg] != stock_regs[reg]:
                    raise ValueError('%s differs stock/source on %r'
                                     % (reg, case))
            for reg in live:
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
              'compile_flags': PMUSECOND_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': register_reference(),
              'functions': functions, 'target_cases': cases,
              'stop': 'fourth fill call (MAX_FILLS=3)',
              'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot '
                                 'stage-1 second PMU dispatcher body only '
                                 '(retained entry head plus reviewed body '
                                 '0x10000EB8, exact unfiltered traces)',
              'stock_equivalence_proven': False,
              'leftover_paths': 'the 24-byte retained entry head (frame '
                                'setup, id-range guard, retained jump-table '
                                'dispatch) stays retained stock: the '
                                'assembler places literal pools only at the '
                                'section end, which would displace the '
                                'inline table pool or the coinciding arms. '
                                'The dispatch reads slot id-7, so id 25 '
                                'reads the last in-bounds slot. Chains '
                                'whose last fill misses '
                                'compare trace and RAM exactly but registers '
                                'only on the fill-independent subset. Fill '
                                'scratch registers r2/r3/r12/r13/r18 are '
                                'compared by trace only, not at the stop '
                                'point.',
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Register shifts by a register count use the low 5 '
                         'bits; both sides share the executor so agreement '
                         'holds by construction, hardware shift semantics for '
                         'negative counts remain unqualified.',
                         'Three-operand register shifts never occur in this '
                         'body; the executor keeps the reversed-order '
                         'reading proven by the first dispatcher.',
                         'mul.u32 models the low word only; the high half '
                         'is never read on battery paths. divu fail-closes '
                         'on a zero divisor; every site is provably nonzero '
                         'on reachable paths except the adversarial or== '
                         '0xFFFFFFFF combination, which the battery excludes.',
                         'Push/pop traffic is compared exactly with no '
                         'window exclusion; descriptor values and all other '
                         'accesses are compared exactly. The caller window '
                         'is fully mapped. Hardware timing remains '
                         'unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-pmusecond-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-pmusecond-verification.json').read_text()),
        indent=2))
