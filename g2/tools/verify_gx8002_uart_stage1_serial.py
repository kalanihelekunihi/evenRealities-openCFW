#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for UART boot stage-1 polled-UART leaves.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_serial.c (blocking
transmit, non-blocking receive probe, blocking receive) and the reviewed
assembly in components/shared/gx8002/runtime_gx8002_uart_stage1_putsync.S
(blocking transmit-then-wait) against the stock stage-1 bodies by executing
decoded C-SKY instructions for both across a battery of UART states and
inputs, plus an independent Python oracle.

The UART block base is read once per call from the stage-1 data word at
0x20002014; the line-status register (block offset 0x14) is scripted per
case (poll loops consume successive reads, holding the last value), the
receive register (block offset 0x0) yields scripted words, and transmit
writes are recorded. Compared: the exact access trace (address, width, and
value of every read and write), the final destination word for the probe,
the transmit writes, r0, and callee-saved register preservation.

Behavioral equivalence only: the C bodies synthesize the base-cell address
with movi/bseti where the stock uses a literal pool, and scratch registers
differ. The assembled put_sync body is additionally byte-identical to its
stock envelope (pinned by test), but admission rests on decoded-trace
equivalence like every other tranche.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_serial.c'
S_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_putsync.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-SERIAL-NOTICE.txt'
SERIAL_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize']

MASK = 0xffffffff
BASE_CELL = 0x20002014
DST_CELL = 0x20002000

# (symbol, runtime entry, package offset, stock envelope bytes, kind, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_put', 0x10000584, 0x5d4, 28,
     'put', 'compiled_c'),
    ('open_cfw_gx8002_uart_stage1_put_sync', 0x100005a0, 0x5f0, 36,
     'put_sync', 'compiled_assembly'),
    ('open_cfw_gx8002_uart_stage1_try_get', 0x10000620, 0x670, 32,
     'try_get', 'compiled_c'),
    ('open_cfw_gx8002_uart_stage1_get_char', 0x10000640, 0x690, 28,
     'get_char', 'compiled_c'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_put 0x10000584 : { *(.text.open_cfw_gx8002_uart_stage1_put) }
  .text.open_cfw_gx8002_uart_stage1_put_sync 0x100005a0 : { *(.text.open_cfw_gx8002_uart_stage1_put_sync) }
  .text.open_cfw_gx8002_uart_stage1_try_get 0x10000620 : { *(.text.open_cfw_gx8002_uart_stage1_try_get) }
  .text.open_cfw_gx8002_uart_stage1_get_char 0x10000640 : { *(.text.open_cfw_gx8002_uart_stage1_get_char) }
}
'''

LOAD_STORE = re.compile(r'(r\d+), \((r\d+), (0x[0-9a-fA-F]+)\)')
CALLEE_SAVED = ('r4', 'r5', 'r6', 'r7', 'r14', 'r15')


class UartModel:
    """Scripted stage-1 UART: base cell, destination word, LSR/RBR scripts."""

    def __init__(self, base, dst_init, lsr_script, rbr_script):
        self.ram = {BASE_CELL: base & MASK, DST_CELL: dst_init & MASK}
        self.lsr_script = list(lsr_script)
        self.rbr_script = list(rbr_script)
        self.lsr_index = 0
        self.rbr_index = 0
        self.thr_writes = []
        self.trace = []

    def next_lsr(self):
        value = self.lsr_script[min(self.lsr_index, len(self.lsr_script) - 1)]
        self.lsr_index += 1
        return value & MASK

    def next_rbr(self):
        value = self.rbr_script[min(self.rbr_index, len(self.rbr_script) - 1)]
        self.rbr_index += 1
        return value & MASK

    def read_word(self, address, base):
        if address == base + 0x14:
            value = self.next_lsr()
        elif address == base + 0x0:
            value = self.next_rbr()
        elif address in self.ram:
            value = self.ram[address]
        else:
            raise ValueError('unexpected read at ' + hex(address))
        self.trace.append(('read', address, value))
        return value

    def write_word(self, address, value, base):
        value &= MASK
        if address == base + 0x0:
            self.thr_writes.append(value)
        elif address == DST_CELL:
            self.ram[address] = value
        else:
            raise ValueError('unexpected write at ' + hex(address))
        self.trace.append(('write', address, value))

    def write_byte(self, address, value):
        if address != DST_CELL:
            raise ValueError('unexpected byte write at ' + hex(address))
        value &= 0xff
        self.ram[DST_CELL] = (self.ram[DST_CELL] & 0xffffff00) | value
        self.trace.append(('write', address, value))


def execute(code, start, arg, model):
    """Run decoded code with r0=arg against the UART model.

    Returns (r0, dst word, transmit writes, trace, callee-saved preserved).
    """
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=arg & MASK)
    saved = dict(registers)
    base = model.ram[BASE_CELL]
    pc = start
    for _ in range(400):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        if op == 'movi':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'bseti':
            registers[parts[0]] = (registers[parts[0]] | (1 << int(parts[1], 0))) & MASK
        elif op == 'lrw':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'addi':
            registers[parts[0]] = (registers[parts[1]] + int(parts[2], 0)) & MASK
        elif op == 'subi':
            registers[parts[0]] = (registers[parts[0]] - int(parts[1], 0)) & MASK
        elif op == 'andi':
            registers[parts[0]] = registers[parts[1]] & int(parts[2], 0)
        elif op == 'zextb':
            registers[parts[0]] = registers[parts[1]] & 0xff
        elif op == 'ld.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            registers[match.group(1)] = model.read_word(address, base)
        elif op == 'st.w':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            model.write_word(address, registers[match.group(1)], base)
        elif op == 'st.b':
            match = LOAD_STORE.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3), 0)) & MASK
            model.write_byte(address, registers[match.group(1)])
        elif op == 'bez':
            if registers[parts[0]] == 0:
                following = int(parts[1], 0)
        elif op == 'br':
            following = int(parts[0], 0)
        elif op == 'rts':
            preserved = all(registers[r] == saved[r] for r in CALLEE_SAVED)
            return (registers['r0'], model.ram[DST_CELL],
                    list(model.thr_writes), list(model.trace), preserved)
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def oracle(kind, arg, base, dst_init, lsr_script, rbr_script):
    """Independent model: (r0, destination word, transmit writes, trace)."""
    trace = [('read', BASE_CELL, base & MASK)]
    lsr = list(lsr_script)
    rbr = list(rbr_script)
    dst = dst_init & MASK
    thr = []

    def poll(mask):
        while True:
            value = lsr[0] if len(lsr) == 1 else lsr.pop(0)
            trace.append(('read', base + 0x14, value & MASK))
            if value & mask:
                return

    if kind in ('put', 'put_sync'):
        poll(0x40)
        trace.append(('write', base + 0x0, arg & MASK))
        thr.append(arg & MASK)
        if kind == 'put_sync':
            poll(0x40)
        return arg & MASK, dst, thr, trace
    value = lsr[0] if len(lsr) == 1 else lsr.pop(0)
    trace.append(('read', base + 0x14, value & MASK))
    if kind == 'try_get':
        if value & 1:
            word = rbr[0] if len(rbr) == 1 else rbr.pop(0)
            trace.append(('read', base + 0x0, word & MASK))
            trace.append(('write', DST_CELL, word & 0xff))
            dst = (dst & 0xffffff00) | (word & 0xff)
            return 0, dst, thr, trace
        return MASK, dst, thr, trace
    while not (value & 1):
        value = lsr[0] if len(lsr) == 1 else lsr.pop(0)
        trace.append(('read', base + 0x14, value & MASK))
    word = rbr[0] if len(rbr) == 1 else rbr.pop(0)
    trace.append(('read', base + 0x0, word & MASK))
    return word & 0xff, dst, thr, trace


def battery_cases(kind):
    bases = [0xa0100000, 0xa0200000]
    if kind == 'put':
        args = [0x00, 0x01, 0x47, 0xff, 0x80, 0x12345678]
        scripts = [[0x40], [0x00, 0x40], [0xbf, 0x40],
                   [0x00] * 5 + [0xc0], [0x01, 0x80, 0x43]]
        return [(a, b, 0, s, [0]) for b in bases for s in scripts for a in args]
    if kind == 'put_sync':
        args = [0x00, 0x01, 0x47, 0xff, 0x80, 0x12345678]
        first = [[0x40], [0x00, 0x40], [0x00] * 5 + [0xc0]]
        second = [[0x40], [0x00, 0x40], [0xbf, 0x40]]
        return [(a, b, 0, f, s) for b in bases for f in first
                for s in second for a in args]
    if kind == 'try_get':
        states = [0x00, 0x01, 0x40, 0x41, 0xfe, 0xff, 0xfffffffe, 0xffffffff]
        words = [0x00, 0x41, 0xff, 0x12345678]
        return [(DST_CELL, b, d, [s], [w]) for b in bases for s in states
                for w in words for d in (0x00000000, 0xffffffff)]
    states = [[0x01], [0x00, 0x01], [0xfe, 0x41],
              [0x00] * 5 + [0x80000001], [0x40, 0x01]]
    words = [0x00, 0x41, 0xff, 0x78, 0x12345678, 0xffffffff]
    seeds = [0x00000000, 0xdeadbeef, DST_CELL]
    return [(seed, b, 0xaaaaaaaa, s, [w]) for b in bases for s in states
            for w in words for seed in seeds]


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
    for relative in ('arch/soc/grus/spl/spl_uart.c',
                     'arch/soc/grus/include/base_addr.h', 'LICENSE'):
        blob = subprocess.check_output(
            ['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + relative],
            text=True).strip()
        deps.append({'path': relative, 'git_blob': blob,
                     'sha256': sha(authenticated_blob(sdk / relative, blob))})
    return deps


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-serial'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    c_obj = output / 'serial_c.o'
    s_obj = output / 'putsync_s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *SERIAL_FLAGS,
                    '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
    subprocess.run([str(prefix / 'csky-unknown-elf-as'), '-mcpu=ck804ef',
                    '-mhard-float', str(S_SOURCE), '-o', str(s_obj)], check=True)
    script = output / 'serial.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'serial.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(c_obj), str(s_obj), '-o', str(elf_path)], check=True)
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
         '--start-address=0x10000580', '--stop-address=0x10000660',
         str(adjusted)], text=True))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'serial.disassembly.txt').write_text(disassembly)
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
        for arg, base, dst_init, lsr_script, rbr_script in battery_cases(kind):
            want = oracle(kind, arg, base, dst_init, lsr_script, rbr_script)
            for code, start, label in ((stock_code, entry, 'stock'),
                                       (source_code, entry, 'source')):
                model = UartModel(base, dst_init, lsr_script, rbr_script)
                got = execute(code, start, arg, model)[:4]
                if got != want:
                    raise ValueError('%s/oracle mismatch for %s at %#x %#x'
                                     % (label, symbol, arg, base))
                model = UartModel(base, dst_init, lsr_script, rbr_script)
                if not execute(code, start, arg, model)[4]:
                    raise ValueError('callee-saved violation for ' + symbol)
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    report = {'c_source_sha256': sha(C_SOURCE.read_bytes()),
              's_source_sha256': sha(S_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': SERIAL_FLAGS,
              'assemble_flags': ['-mcpu=ck804ef', '-mhard-float'],
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'arch/soc/grus/spl/spl_uart.c '
                                    '(serial_put/serial_put_sync/serial_try_get/'
                                    'serial_get_char behavior and conventions) and '
                                    'arch/soc/grus/include/base_addr.h (UART block '
                                    'addresses); clean-room bodies from decoded stock '
                                    'flow, no SDK text reproduced, GPL SDK headers '
                                    'not used',
              'upstream_files': upstream_files(sdk),
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'polled-UART leaves only',
              'stock_equivalence_proven': False,
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'MMIO trace equivalence over a finite battery plus an independent '
                         'oracle; the LSR/RBR scripts are finite with hold-last and no '
                         'external concurrent updates are modeled. The base-cell word is '
                         'fixed per case. Hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-serial-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-serial-verification.json').read_text()),
        indent=2))