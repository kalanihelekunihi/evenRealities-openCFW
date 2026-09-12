#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target check for the UART boot stage-1 reset entry (CD-001).

Assembles components/shared/gx8002/runtime_gx8002_uart_boot_stage1_reset.S
(derived from the pinned NationalChip lvp_kws spl_start.S with the
recovered UART-boot configuration), links it at its real runtime address
0x10000100, and checks two claims:

1. The linked 48 bytes are byte-exact against the stock envelope at
   package 0x150..0x180 (code plus literal pool; the stock bkpt alignment
   pad is a zero halfword, matching the assembler-emitted pad).
2. A small decoded C-SKY interpreter drives the linked body across a
   spread of CR31 inputs and register seeds and checks the exact
   control-register/call effects against an independently built oracle:
   PSR set, CR31 bit 3 cleared, VBR = stage-1 vector base, both calls made
   with the documented stack pointer in place.

The init (0x100001bc) and stage-2 entry (0x10002900) targets are genuine,
unreconstructed external call boundaries: this tranche proves only that
these exact 48 bytes reach them with the documented machine state, and
makes no claim about what either target does.
"""
import json
import subprocess
from pathlib import Path

from analyze_gx8002_upstream_objects import (
    IMAGE,
    IMAGE_SHA,
    SDK_COMMIT,
    authenticated_blob,
    sha,
)
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_boot_stage1_reset.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-RESET-NOTICE.txt'
ASM_FLAGS = ['-mcpu=ck804ef', '-mhard-float']

ENTRY_ADDRESS = 0x10000100
PACKAGE_OFFSET = 0x150
ENTRY_SIZE = 48
VECTORS_ADDRESS = 0x10000000
INIT_ADDRESS = 0x100001BC
STAGE2_ADDRESS = 0x10002900
INITIAL_STACK = 0x200027FC

LINKER_SCRIPT = '''SECTIONS {{
  .text {entry:#x} : {{ *(.text.open_cfw_gx8002_uart_boot_stage1_reset) }}
}}
open_cfw_gx8002_uart_stage1_vectors = {vectors:#x};
open_cfw_gx8002_uart_stage1_initial_stack = {stack:#x};
open_cfw_gx8002_uart_stage1_init = {init:#x};
open_cfw_gx8002_uart_stage2_entry = {stage2:#x};
'''

SECTION_NAME = '.text.open_cfw_gx8002_uart_boot_stage1_reset'
SYMBOL = 'open_cfw_gx8002_uart_boot_stage1_reset'


def execute(code, control, seed):
    """Run the decoded reset body; return the control-write/call trace."""
    registers = {f'r{i}': (seed + i) & 0xffffffff for i in range(32)}
    pc, trace = ENTRY_ADDRESS, []
    for _ in range(12):
        op, operand, width = code[pc]
        parts = [p.strip() for p in operand.split(',')] if operand else []
        if op == 'lrw':
            registers[parts[0]] = int(parts[1], 0)
        elif op == 'mtcr':
            register, control_register = operand.split(', ', 1)
            if control_register not in ('cr<0, 0>', 'cr<31, 0>', 'cr<1, 0>'):
                raise ValueError('unexpected control destination ' + control_register)
            trace.append(('control-write', control_register, registers[register]))
        elif op == 'mfcr':
            if operand != 'r1, cr<31, 0>':
                raise ValueError('unexpected control source')
            registers['r1'] = control
            trace.append(('control-read', 'cr<31, 0>', control))
        elif op == 'bclri':
            registers[parts[0]] &= ~(1 << int(parts[1], 0))
        elif op == 'mov':
            if parts[0] not in ('r14', 'sp') or parts[1] != 'r0':
                raise ValueError('unexpected stack setup')
            registers['r14'] = registers['r0']
        elif op == 'bsr':
            target = int(operand, 0)
            if target not in (INIT_ADDRESS, STAGE2_ADDRESS):
                raise ValueError('unexpected call target %#x' % target)
            if registers['r14'] != INITIAL_STACK:
                raise ValueError('reset stack not in place at call to %#x' % target)
            trace.append(('call', target, registers['r14']))
            if target == STAGE2_ADDRESS:
                return trace
        else:
            raise ValueError('unexpected instruction ' + op)
        pc += width
    raise ValueError('execution bound exceeded')


def oracle(control):
    return [
        ('control-write', 'cr<0, 0>', 0x80000200),
        ('control-read', 'cr<31, 0>', control),
        ('control-write', 'cr<31, 0>', control & ~8),
        ('control-write', 'cr<1, 0>', VECTORS_ADDRESS),
        ('call', INIT_ADDRESS, INITIAL_STACK),
        ('call', STAGE2_ADDRESS, INITIAL_STACK),
    ]


def upstream_dependencies(sdk):
    deps = []
    for relative in ('arch/cpu/csky/ck804/spl_start.S', 'LICENSE'):
        blob = subprocess.check_output(
            ['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + relative],
            text=True).strip()
        deps.append({'path': relative, 'git_blob': blob,
                     'sha256': sha(authenticated_blob(sdk / relative, blob))})
    return deps


def verify(prefix=None, sdk=None, output=None):
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    sdk = sdk or ROOT / 'build/upstream-nationalchip-lvp-kws'
    output = output or ROOT / 'build/gx8002-uart-stage1-reset'
    output.mkdir(parents=True, exist_ok=True)

    obj = output / 'reset.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *ASM_FLAGS,
                    '-c', str(SOURCE), '-o', str(obj)], check=True)
    script = output / 'reset.ld'
    script.write_text(LINKER_SCRIPT.format(
        entry=ENTRY_ADDRESS, vectors=VECTORS_ADDRESS, stack=INITIAL_STACK,
        init=INIT_ADDRESS, stage2=STAGE2_ADDRESS))
    elf_path = output / 'reset.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(obj), '-o', str(elf_path)], check=True)

    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    section = next(s for s in elf.sections if s['name'] == '.text')
    if elf.relocations(section['index']):
        raise ValueError('unresolved relocation in linked reset candidate')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol in linked reset candidate')
    payload = elf.contents(section)
    if len(payload) != ENTRY_SIZE:
        raise ValueError('reset candidate envelope changed: %d bytes' % len(payload))
    if PACKAGE_OFFSET % section['align']:
        raise ValueError('reset candidate misaligned for its stock envelope')

    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    stock_span = stock[PACKAGE_OFFSET:PACKAGE_OFFSET + ENTRY_SIZE]
    byte_exact = payload == stock_span
    if not byte_exact:
        raise ValueError('reset candidate is not byte-exact against stock')

    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'reset.disassembly.txt').write_text(disassembly)
    code = decode(disassembly)
    cases = 0
    for control in sorted({0, 0xffffffff, 0x55555555, 0xaaaaaaaa,
                           *(1 << i for i in range(32))}):
        for seed in (0, 0xffffffff, 0x12345678):
            if execute(code, control, seed) != oracle(control):
                raise ValueError('reset control/call trace mismatch')
            cases += 1

    return {
        'functions': [{
            'symbol': SYMBOL,
            'section_name': '.text',
            'ownership_kind': 'compiled_assembly',
            'compiled_bytes': len(payload),
            'compiled_sha256': sha(payload),
            'stock_occurrences': [{
                'symbol': SYMBOL, 'package_offset': PACKAGE_OFFSET,
                'bytes': ENTRY_SIZE, 'sha256': sha(stock_span),
                'region': 'uart_boot_stage1'}]}],
        'evidence': {
            'sdk_commit': SDK_COMMIT,
            'dependencies': upstream_dependencies(sdk),
            'source_sha256': sha(SOURCE.read_bytes()),
            'flags': ASM_FLAGS,
            'compiled_bytes': len(payload),
            'compiled_sha256': sha(payload),
            'byte_exact': True,
        },
        'cases': cases,
        'notice_sha256': sha(NOTICE.read_bytes()),
        'source_admitted': True,
        'hardware_qualified': False,
        'limits': [
            'Stage-1 init (0x100001bc) and the stage-2 entry (0x10002900) are '
            'genuine external call boundaries: their contents are not '
            'reconstructed and remain retained stock at their own addresses.',
            'Control-register/call-trace equivalence over 108 decoded runs; '
            'whatever the callees do to machine state is unmodeled here.',
            'No physical boot, mask-ROM copy, or full-device qualification.',
        ],
    }


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-reset-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-reset-verification.json').read_text()),
        indent=2))
