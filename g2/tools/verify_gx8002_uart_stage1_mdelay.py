#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for the UART boot stage-1 mdelay leaf.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_mdelay.c (an inlined
SDK `spl_mdelay`/`spl_udelay(1000)` pair) against the stock stage-1 body
by executing decoded C-SKY instructions for both across a battery of
millisecond counts and counter seeds, plus an independent Python oracle.

Leaf: the millisecond delay at runtime 0x100003FC, package 0x44C, 112
bytes of code: a post-decrement outer loop of n one-millisecond waits,
each a single 64-bit counter-2 snapshot plus 1000 with a
strict-less-than poll, then a pop-then-chain into the retained
rail-configure flow at 0x1000046C. Compared: the exact access trace
(kind, address, width, and value of every read and write outside the
stack window), r0/r4/r5/r6/r14/r15 at the handoff, and the final
counter cells.

Behavioral equivalence only: the C uses branch/condition shapes of its
own where stock uses redundant moves, and synthesizes the counter base
with movih where stock does the same; the single inline pop restores
exactly the registers the prologue saved (shape asserted below). The
r1-r3/r7+ scratch values at the handoff are caller scratch and are not
compared; the stack-window slot assignment is compiler scratch (as with
the allowed scratch-register renaming) and is excluded from the trace
and RAM comparison, while the final counter cells are compared exactly.
The link register clobbered by the chaining branch is dead (the 0x46C
flow saves it on entry and never returns) and is compared only up to
the chaining instruction, which the executor does not step past.
Admission rests on decoded-trace equivalence.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_mdelay.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-MDELAY-NOTICE.txt'
MDELAY_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize',
                '-fno-jump-tables']

MASK = 0xffffffff
CTR_BASE = 0xa0400000
CTR_LO = 0xa0400004
CTR_HI = 0xa0400008
ADVANCE = 577
SP0 = 0x20002800
WINDOW_LO = SP0 - 64
WINDOW_HI = SP0 + 16
HANDOFF = 0x1000046c

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_mdelay', 0x100003fc, 0x44c, 112,
     'mdelay', 'compiled_c'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_mdelay 0x100003fc : { *(.text.open_cfw_gx8002_uart_stage1_mdelay) }
}
open_cfw_gx8002_uart_boot_stage1_46c_entry = 0x1000046c;
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
CALLEE_SAVED = ('r4', 'r5', 'r6', 'r15')
PUSH_REGS = ('r4', 'r5', 'r15')


class Handoff(Exception):
    """Reaches the 0x46C chaining boundary; carries the register file."""

    def __init__(self, registers):
        super().__init__('handoff')
        self.registers = dict(registers)


class CounterModel:
    """Counter-2 cells with a deterministic advance plus a stack window."""

    def __init__(self, lo, hi):
        self.ram = {CTR_LO: lo & MASK, CTR_HI: hi & MASK}
        for address in range(WINDOW_LO, WINDOW_HI, 4):
            self.ram[address] = (0x5a000000 + (address - WINDOW_LO)) & MASK
        self.trace = []

    def in_window(self, address):
        return WINDOW_LO <= address < WINDOW_HI

    def read_word(self, address):
        if address == CTR_HI:
            value = self.ram[address] & MASK
            self.trace.append(('read', address, 4, value))
            total = (((self.ram[CTR_HI] << 32) | self.ram[CTR_LO]) + ADVANCE) & 0xffffffffffffffff
            self.ram[CTR_LO] = total & MASK
            self.ram[CTR_HI] = (total >> 32) & MASK
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


def execute(code, start, arg0, model):
    """Run decoded code with r0=arg0 against the counter model.

    Returns (registers, trace). Raises Handoff at the chaining boundary.
    """
    registers = {f'r{i}': (0x98760000 + i * 0x111111) & MASK for i in range(32)}
    registers.update(r0=arg0 & MASK, r14=SP0)
    condition = False
    pc = start
    for _ in range(500000):
        if pc == HANDOFF:
            raise Handoff(registers)
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
        elif op in ('tlsli', 'lsli'):
            registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & MASK
        elif op == 'add.64':
            lo = (registers[parts[1]] + registers[parts[2]]) & MASK
            carry = 1 if registers[parts[1]] + registers[parts[2]] > MASK else 0
            dst_hi = 'r%d' % (int(parts[0][1:]) + 1)
            src_hi = 'r%d' % (int(parts[1][1:]) + 1)
            add_hi = 'r%d' % (int(parts[2][1:]) + 1)
            registers[dst_hi] = (registers[src_hi] + registers[add_hi] + carry) & MASK
            registers[parts[0]] = lo
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
        elif op == 'bez':
            if registers[parts[0]] == 0:
                following = int(parts[1], 0)
        elif op == 'bnez':
            if registers[parts[0]] != 0:
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
            if int(parts[0], 0) == HANDOFF:
                raise Handoff(registers)
            raise ValueError('unexpected call to ' + operand)
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def outside_window(trace):
    """Drop stack-window traffic (compiler scratch slot assignment)."""
    return [entry for entry in trace if not WINDOW_LO <= entry[1] < WINDOW_HI]


def oracle(msec, lo, hi):
    """Independent model: (handoff r0, counter RAM, non-window trace).

    Stated from the decoded structure, not from decoded instructions:
    n post-decrement milliseconds, each one 64-bit snapshot plus 1000
    with a strict-less-than poll against the same advancing counter.
    """
    ram = {CTR_LO: lo & MASK, CTR_HI: hi & MASK}
    trace = []

    def snap():
        low = ram[CTR_LO]
        trace.append(('read', CTR_LO, 4, low))
        high = ram[CTR_HI]
        trace.append(('read', CTR_HI, 4, high))
        total = (((high << 32) | low) + ADVANCE) & 0xffffffffffffffff
        ram[CTR_LO] = total & MASK
        ram[CTR_HI] = (total >> 32) & MASK
        return (high << 32) | low

    left = msec & MASK
    left = (left - 1) & MASK
    if left != MASK:
        while True:
            deadline = (snap() + 1001) & 0xffffffffffffffff
            while snap() < deadline:
                pass
            left = (left - 1) & MASK
            if left == MASK:
                break
    return MASK, dict(ram), list(trace)


def battery_cases():
    counts = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17, 32, 64, 255]
    los = [0, 1, 0xfffff000, 0x12345678, 0xffffffff]
    his = [0, 0xffffffff]
    cases = []
    for msec in counts:
        for lo in los:
            for hi in his:
                cases.append((msec, lo, hi))
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


def upstream_files(sdk):
    from analyze_gx8002_upstream_objects import SDK_COMMIT, authenticated_blob
    deps = []
    for relative in ('arch/soc/grus/spl/spl_counter.c', 'LICENSE'):
        blob = subprocess.check_output(
            ['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + relative],
            text=True).strip()
        deps.append({'path': relative, 'git_blob': blob,
                     'sha256': sha(authenticated_blob(sdk / relative, blob))})
    return deps


def check_shape(source_code, entry, size):
    """Fail closed on prologue/transfer drift (the pop balances the push)."""
    addresses = sorted(source_code)
    first = source_code[addresses[0]]
    if first[0] != 'push' or expand_regs(first[1]) != list(PUSH_REGS):
        raise ValueError('prologue push changed: ' + repr(first))
    pops = [pc for pc in addresses if source_code[pc][0] == 'pop']
    if len(pops) != 1 or source_code[pops[0]][1] != 'r4-r5, r15':
        raise ValueError('expected one pop r4-r5, r15, found: ' +
                         repr([source_code[pc] for pc in pops]))
    calls = [pc for pc in addresses if source_code[pc][0] == 'bsr']
    if len(calls) != 1 or int(source_code[calls[0]][1], 0) != HANDOFF:
        raise ValueError('expected one chaining bsr to %#x' % HANDOFF)
    for pc in addresses:
        op, operand, _ = source_code[pc]
        if op in ('subi', 'addi') and operand.split(',')[0].strip() == 'r14':
            raise ValueError('unexpected stack-pointer frame at %#x' % pc)
        if op in ('bt', 'bf', 'br', 'bez', 'bnez'):
            target = int(operand.split(',')[-1], 0)
            if not entry <= target < entry + size:
                raise ValueError('branch leaves the section at %#x' % pc)
        if op in ('rts', 'bkpt', 'jmp', 'jmpi', 'jsr'):
            raise ValueError('unexpected transfer %s at %#x' % (op, pc))


def seed(reg):
    index = int(reg[1:])
    if reg == 'r14':
        return SP0
    return (0x98760000 + index * 0x111111) & MASK


def run_side(code, start, msec, lo, hi):
    """Execute one side to the handoff; return (regs, model)."""
    model = CounterModel(lo, hi)
    try:
        execute(code, start, msec, model)
    except Handoff as done:
        return done.registers, model
    raise ValueError('side returned instead of chaining')


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-mdelay'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    c_obj = output / 'mdelay_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *MDELAY_FLAGS,
                    '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
    script = output / 'mdelay.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'mdelay.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(c_obj), '-o', str(elf_path)], check=True)
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
    stock_code = decode(subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-D',
         '--start-address=0x100003fc', '--stop-address=0x1000046c',
         str(adjusted)], text=True))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'mdelay.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
    functions = []
    cases = 0
    for symbol, entry, offset, size, kind, ownership in SPECS:
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) > size or offset % section['align']:
            raise ValueError('candidate does not fit original placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        check_shape(source_code, entry, len(payload))
        for msec, lo, hi in battery_cases():
            want_r0, want_ram, want_trace = oracle(msec, lo, hi)
            for code, start, label in ((stock_code, entry, 'stock'),
                                       (source_code, entry, 'source')):
                regs, model = run_side(code, start, msec, lo, hi)
                got_trace = outside_window(model.trace)
                if got_trace != want_trace:
                    raise ValueError('%s trace/oracle mismatch (msec=%d lo=%#x hi=%#x)' %
                                     (label, msec, lo, hi))
                for address in (CTR_LO, CTR_HI):
                    if model.ram[address] != want_ram[address]:
                        raise ValueError('%s counter mismatch (msec=%d lo=%#x hi=%#x)' %
                                         (label, msec, lo, hi))
                if regs['r0'] != want_r0:
                    raise ValueError('%s handoff r0 mismatch (msec=%d lo=%#x hi=%#x)' %
                                     (label, msec, lo, hi))
                for reg in ('r4', 'r5', 'r6', 'r14', 'r15'):
                    if regs[reg] != seed(reg):
                        raise ValueError('%s %s not preserved (msec=%d lo=%#x hi=%#x)' %
                                         (label, reg, msec, lo, hi))
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    report = {'c_source_sha256': sha(C_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': MDELAY_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'arch/soc/grus/spl/spl_counter.c '
                                    '(gx_get_time_us reads GXSCPU_VA_COUNTER_2_VALUE '
                                    '+0x04 then GXSCPU_VA_COUNTER_2_ACCSNAP +0x08 under '
                                    'GX_REG_BASE_COUNTER = 0xA0400000; spl_udelay spins '
                                    'while now < snapshot + usec + 1; spl_mdelay loops '
                                    'spl_udelay(1000); 1 MHz rate gives 1 ms per 1000 '
                                    'ticks); clean-room body from decoded stock flow, '
                                    'no SDK text reproduced',
              'upstream_files': upstream_files(sdk),
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'millisecond-delay leaf only',
              'stock_equivalence_proven': False,
              'handoff': {'address': hex(HANDOFF), 'carried_r0': '0xffffffff',
                          'compared_registers': ['r0', 'r4', 'r5', 'r6', 'r14', 'r15'],
                          'r15_note': 'compared up to the chaining instruction, which the '
                                      'executor does not step past; the retained 0x46C flow '
                                      'saves r15 on entry and never returns',
                          'counter_advance_per_snapshot': ADVANCE,
                          'stack_window': [hex(WINDOW_LO), hex(WINDOW_HI)]},
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'Counter-2 is modeled RAM advancing %d ticks per snapshot, not '
                         'hardware time. Millisecond counts above 255 are not in the '
                         'battery (same code paths, longer runs). Stack-window slot '
                         'assignment is excluded as compiler scratch; final counter '
                         'cells are compared exactly. '
                         'Hardware timing remains unqualified.' % ADVANCE]}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-mdelay-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-mdelay-verification.json').read_text()),
        indent=2))
