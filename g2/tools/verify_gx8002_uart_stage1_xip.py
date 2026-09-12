#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target execution check for UART boot stage-1 XIP leaves.

Compares the reviewed clean-room C in
components/shared/gx8002/runtime_gx8002_uart_stage1_xip.c against the
stock stage-1 bodies by executing decoded C-SKY instructions for both
across a battery of inputs, plus an independent Python oracle.

Leaves: the XIP-controller flash read routine (runtime 0x100018c0,
control word 0xC07, count = len - 1, data-ready bit 3, received words
narrowed to bytes) and the XIP-controller flash write routine (runtime
0x10001940, control word 0x407, count = len, transmit-ready bit 1,
source bytes widened to words). Compared: the exact access trace
(kind, address, width, and value of every read and write), final
destination RAM, source preservation, and callee-saved preservation.

Behavioral equivalence only: the C synthesizes the controller base
with movi/tlsli where the stock uses movih, and scratch registers may
differ. Admission rests on decoded-trace equivalence. The r0 return
value is intentionally not compared: both leaves are void and the
stock leaves r0 holding path-dependent residue.
"""
import json
import re
import struct
import subprocess
from pathlib import Path
from verify_gx8002_memcpy_source import decode
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_xip.c'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-XIP-NOTICE.txt'
XIP_FLAGS = ['-Os', *FLAGS[1:], '-fno-tree-loop-optimize']

MASK = 0xffffffff
XIP = 0xa2000000
UNLOCK = 0xa20000f4
STATUS = XIP + 0x28
RESIDUAL_READ = XIP + 0x24
RESIDUAL_WRITE = XIP + 0x20
DATA = XIP + 0x60
ARENA = 0x20001000


def residual_address(kind):
    return RESIDUAL_READ if kind == 'xip_read' else RESIDUAL_WRITE

# (symbol, runtime entry, package offset, stock envelope bytes, kind).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_xip_read', 0x100018c0, 0x1910, 128,
     'xip_read'),
    ('open_cfw_gx8002_uart_stage1_xip_write', 0x10001940, 0x1990, 128,
     'xip_write'),
]

LINKER_SCRIPT = '''SECTIONS {
  .text.open_cfw_gx8002_uart_stage1_xip_read 0x100018c0 : { *(.text.open_cfw_gx8002_uart_stage1_xip_read) }
  .text.open_cfw_gx8002_uart_stage1_xip_write 0x10001940 : { *(.text.open_cfw_gx8002_uart_stage1_xip_write) }
}
'''

MEM_OPERAND = re.compile(r'(r\d+), \((r\d+)(?:, (0x[0-9a-fA-F]+))?\)')
CALLEE_SAVED = ('r4', 'r5', 'r6', 'r7', 'r14', 'r15')


class XipModel:
    """Scripted XIP controller plus byte-addressed RAM arena."""

    def __init__(self, scripts, ram):
        self.scripts = {address: list(values)
                        for address, values in scripts.items()}
        self.ram = dict(ram)
        self.trace = []

    def read_word(self, address):
        if address in self.scripts:
            values = self.scripts[address]
            value = values.pop(0) if len(values) > 1 else values[0]
            value &= MASK
        elif ARENA <= address < ARENA + 0x1000:
            value = sum(self.ram.get(address + i, 0) << (8 * i)
                        for i in range(4)) & MASK
        else:
            raise ValueError('unexpected read at ' + hex(address))
        self.trace.append(('read', address, 4, value))
        return value

    def read_byte(self, address):
        word = self.read_word(address & ~0x3)
        value = (word >> ((address & 0x3) * 8)) & 0xff
        self.trace.pop()
        self.trace.append(('read', address, 1, value))
        return value

    def write_word(self, address, value):
        value &= MASK
        if ARENA <= address < ARENA + 0x1000:
            for i in range(4):
                self.ram[address + i] = (value >> (8 * i)) & 0xff
        elif not (XIP <= address < XIP + 0x10000 or address == UNLOCK):
            raise ValueError('unexpected write at ' + hex(address))
        self.trace.append(('write', address, 4, value))

    def write_byte(self, address, value):
        value &= 0xff
        if not ARENA <= address < ARENA + 0x1000:
            raise ValueError('unexpected write at ' + hex(address))
        self.ram[address] = value
        self.trace.append(('write', address, 1, value))


def execute(code, start, cmd, ptr, length, model):
    """Run decoded code with r0=cmd, r1=ptr, r2=length."""
    registers = {f'r{i}': 0x98760000 + i for i in range(32)}
    registers.update(r0=cmd & MASK, r1=ptr & MASK, r2=length & MASK)
    saved = {name: registers[name] for name in CALLEE_SAVED}
    condition = False
    pc = start
    for _ in range(4000):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        following = pc + width
        if op == 'movi':
            registers[parts[0]] = int(parts[1], 0) & MASK
        elif op == 'movih':
            registers[parts[0]] = (int(parts[1], 0) << 16) & MASK
        elif op == 'mov':
            registers[parts[0]] = registers[parts[1]]
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
            if len(parts) == 2:
                registers[parts[0]] = (registers[parts[0]] - registers[parts[1]]) & MASK
            else:
                registers[parts[0]] = (registers[parts[1]] - registers[parts[2]]) & MASK
        elif op == 'and':
            registers[parts[0]] = registers[parts[1]] & registers[parts[2]]
        elif op == 'andi':
            registers[parts[0]] = registers[parts[1]] & int(parts[2], 0)
        elif op == 'or':
            registers[parts[0]] = registers[parts[1]] | registers[parts[2]]
        elif op == 'lsl':
            registers[parts[0]] = (registers[parts[1]] << (registers[parts[2]] & 31)) & MASK
        elif op in ('tlsli', 'lsli'):
            registers[parts[0]] = (registers[parts[1]] << int(parts[2], 0)) & MASK
        elif op == 'rotl':
            count = registers[parts[1]] & 31
            value = registers[parts[0]]
            registers[parts[0]] = ((value << count) | (value >> ((32 - count) & 31))) & MASK
        elif op == 'rotli':
            count = int(parts[2], 0) & 31
            value = registers[parts[1]]
            registers[parts[0]] = ((value << count) | (value >> ((32 - count) & 31))) & MASK
        elif op == 'zextb':
            registers[parts[0]] = registers[parts[1]] & 0xff
        elif op == 'cmpne':
            condition = registers[parts[0]] != registers[parts[1]]
        elif op == 'ld.w':
            match = MEM_OPERAND.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3) or '0', 0)) & MASK
            registers[match.group(1)] = model.read_word(address)
        elif op == 'st.w':
            match = MEM_OPERAND.fullmatch(operand)
            address = (registers[match.group(2)] + int(match.group(3) or '0', 0)) & MASK
            model.write_word(address, registers[match.group(1)])
        elif op == 'ldbi.b':
            match = MEM_OPERAND.fullmatch(operand)
            address = registers[match.group(2)] & MASK
            registers[match.group(1)] = model.read_byte(address)
            registers[match.group(2)] = (address + 1) & MASK
        elif op == 'stbi.b':
            match = MEM_OPERAND.fullmatch(operand)
            address = registers[match.group(2)] & MASK
            model.write_byte(address, registers[match.group(1)])
            registers[match.group(2)] = (address + 1) & MASK
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
        elif op == 'rts':
            preserved = all(registers[name] == saved[name] for name in CALLEE_SAVED)
            return list(model.trace), dict(model.ram), preserved
        else:
            raise ValueError('unsupported instruction: ' + op)
        pc = following
    raise ValueError('execution bound exceeded')


def consume(script):
    """Next scripted value with hold-last semantics."""
    value = script.pop(0) if len(script) > 1 else script[0]
    return value & MASK


def oracle(kind, cmd, ptr, length, status, residual, data, init_ram):
    """Independent model: (expected trace, expected final ram).

    Stated from the documented controller behavior, not from decoded
    instructions: idle wait, status snapshot into the config block,
    command issue, byte movement, residual/idle tail.
    """
    status = list(status)
    residual = list(residual)
    data = list(data)
    trace = []
    ram = dict(init_ram)

    def poll(address, mask, want):
        while True:
            if address == STATUS:
                value = consume(status)
            elif address == residual_address(kind):
                value = consume(residual)
            else:
                value = consume(data)
            trace.append(('read', address, 4, value))
            if (value & mask) == want:
                return value

    status_word = poll(STATUS, 0x1, 0x0)
    # The stock masks the status with `andi` before testing it, so the
    # snapshot stored into the config block is the masked idle bit
    # (always zero at loop exit), not the full status word.
    snapshot = status_word & 0x1
    for address in (XIP + 0x08, XIP + 0x4c):
        trace.append(('write', address, 4, snapshot))
    ctrl = 0xc07 if kind == 'xip_read' else 0x407
    trace.append(('write', XIP + 0x00, 4, ctrl))
    count = (length - 1) & MASK if kind == 'xip_read' else length & MASK
    trace.append(('write', XIP + 0x04, 4, count))
    trace.append(('write', XIP + 0x10, 4, 1))
    mode = snapshot if kind == 'xip_read' else (length << 16) & MASK
    trace.append(('write', XIP + 0x18, 4, mode))
    trace.append(('write', UNLOCK, 4, snapshot))
    trace.append(('write', XIP + 0x08, 4, 1))
    trace.append(('write', DATA, 4, cmd & MASK))
    for index in range(length):
        if kind == 'xip_read':
            poll(STATUS, 0x8, 0x8)
            word = consume(data)
            trace.append(('read', DATA, 4, word))
            ram[ptr + index] = word & 0xff
            trace.append(('write', ptr + index, 1, word & 0xff))
        else:
            poll(STATUS, 0x2, 0x2)
            byte = ram[ptr + index]
            trace.append(('read', ptr + index, 1, byte))
            trace.append(('write', DATA, 4, byte))
    while True:
        value = consume(residual)
        trace.append(('read', residual_address(kind), 4, value))
        if value == 0:
            break
    poll(STATUS, 0x1, 0x0)
    return trace, ram


def battery_cases(kind):
    lens = [0, 1, 2, 5]
    cmds = [0x00000000, 0x0000009f, 0x12345678, 0xffffffff]
    busy_scripts = [[0x00000000], [0x00000001, 0x00000001, 0x00000000],
                    [0x00000005, 0x00000004, 0x00000000]]
    residual_scripts = [[0x00000000], [0x00000002, 0x00000000]]
    tail_scripts = [[0x00000000], [0x00000001, 0x00000000]]
    if kind == 'xip_read':
        ready_scripts = [[0x00000008], [0x00000000, 0x00000000, 0x00000008],
                         [0x00000003, 0x00000008]]
    else:
        ready_scripts = [[0x00000002], [0x00000000, 0x00000000, 0x00000002],
                         [0x00000001, 0x00000002]]
    data_words = [0x00000000, 0x00000041, 0xdeadbeef, 0x12345678,
                  0xffffff00, 0x000000ff]
    src_bytes = [0x00, 0x41, 0xbe, 0x78, 0x00, 0xff]
    cases = []
    for length in lens:
        for cmd in cmds:
            for busy in busy_scripts:
                for ready in ready_scripts:
                    for residual in residual_scripts:
                        for tail in tail_scripts:
                            seed = len(cases)
                            ptr = ARENA + 0x100 * (seed % 8)
                            payload = [data_words[(seed + index) % len(data_words)]
                                       for index in range(max(length, 1))]
                            ram = {}
                            for index in range(8):
                                if kind == 'xip_read':
                                    ram[ptr + index] = 0xa5
                                else:
                                    ram[ptr + index] = src_bytes[(seed + index)
                                                                 % len(src_bytes)]
                            status = (list(busy) + list(ready) * max(length, 1)
                                      + list(tail))
                            scripts = {STATUS: status,
                                       RESIDUAL_READ: list(residual),
                                       RESIDUAL_WRITE: list(residual),
                                       DATA: list(payload)}
                            cases.append((cmd, ptr, length, scripts, ram))
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
    for relative in ('arch/soc/grus/include/base_addr.h', 'LICENSE'):
        blob = subprocess.check_output(
            ['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + relative],
            text=True).strip()
        deps.append({'path': relative, 'git_blob': blob,
                     'sha256': sha(authenticated_blob(sdk / relative, blob))})
    return deps


def verify(prefix=None, sdk=None, output=None):
    from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT
    from build_transparent_image import Elf32
    output = output or ROOT / 'build/gx8002-uart-stage1-xip'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    c_obj = output / 'xip_c.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *XIP_FLAGS,
                    '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
    script = output / 'xip.ld'
    script.write_text(LINKER_SCRIPT)
    elf_path = output / 'xip.elf'
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
         '--start-address=0x100018c0', '--stop-address=0x100019c0',
         str(adjusted)], text=True))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'xip.disassembly.txt').write_text(disassembly)
    sources = split_sections(disassembly)
    functions = []
    cases = 0
    for symbol, entry, offset, size, kind in SPECS:
        section_name = '.text.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) > size or offset % section['align']:
            raise ValueError('candidate does not fit original placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        source_code = sources[section_name]
        for cmd, ptr, length, scripts, ram in battery_cases(kind):
            want_trace, want_ram = oracle(kind, cmd, ptr, length,
                                          scripts[STATUS],
                                          scripts[residual_address(kind)],
                                          scripts[DATA], ram)
            for code, start, label in ((stock_code, entry, 'stock'),
                                       (source_code, entry, 'source')):
                model = XipModel({address: list(values)
                                  for address, values in scripts.items()},
                                 ram)
                got_trace, got_ram, preserved = execute(code, start, cmd, ptr,
                                                        length, model)
                if got_trace != want_trace or got_ram != want_ram:
                    raise ValueError('%s/oracle mismatch for %s (cmd=%#x len=%d)'
                                     % (label, symbol, cmd, length))
                if not preserved:
                    raise ValueError('callee-saved violation for ' + symbol)
            cases += 1
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'ownership_kind': 'compiled_c',
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    report = {'c_source_sha256': sha(C_SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'compile_flags': XIP_FLAGS,
              'sdk_commit': SDK_COMMIT,
              'register_reference': 'arch/soc/grus/include/base_addr.h '
                                    '(GX_REG_BASE_XIP = 0xA2000000); clean-room '
                                    'bodies from decoded stock flow, no SDK '
                                    'text reproduced',
              'upstream_files': upstream_files(sdk),
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'XIP transfer leaves only',
              'stock_equivalence_proven': False,
              'limits': ['Restricted instruction interpreter, not a processor emulator.',
                         'MMIO trace equivalence over a finite battery plus an independent '
                         'oracle; controller reads are scripted (hold-last), not derived '
                         'from prior writes. The r0 return value is not compared: both '
                         'leaves are void and the stock leaves path-dependent residue. '
                         'Hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-xip-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-xip-verification.json').read_text()),
        indent=2))
