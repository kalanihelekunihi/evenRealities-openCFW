#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify the image-A SPL boot header/vectors and reset chain.

Two claims are checked independently of the C/assembly literals:

1. The 280-byte BINH header + 64-word vector table (package 0x0000958C) is
   recomputed from analyze_g2_codec_fwpk_segments.py's own authenticated
   parse (not by trusting the numbers written into the C source), and the
   compiled bytes must match both that recomputation and the stock image.
2. The 54-byte reset chain (package 0x000096A4: reset entry + its literal
   pool + default trap handler + the unreachable clear_bss stub) is decoded
   from the linked candidate's own disassembly and driven through a small
   C-SKY interpreter that checks the exact control-register/call effects
   against an independently built oracle, for a spread of CR31 inputs.

spl_board_init_r is a genuine, unreconstructed external call boundary: this
tranche proves only that these exact 54 bytes call it (and the already
source-owned stage-two entry) with the documented stack pointer already in
place; it makes no claim about what spl_board_init_r itself does.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from analyze_g2_codec_fwpk_segments import (
    CODEC_SHA256 as IMAGE_SHA,
    DRAM_BASE,
    STAGE1_BLOCK,
    parse_fwpk,
    parse_main_image,
)
from build_gx8002_spl_reset_candidate import (
    DEFAULT_HANDLER_ADDRESS,
    ENTRY_ADDRESS,
    ENTRY_PACKAGE_OFFSET,
    ENTRY_SIZE,
    HEADER_PACKAGE_OFFSET,
    HEADER_SIZE,
    IMAGE,
    IRAM_BASE,
    SPL_BOARD_INIT_R_ADDRESS,
    SPL_INITIAL_STACK,
    STAGE2_RESET_ENTRY_ADDRESS,
    build,
)
from verify_gx8002_memcpy_source import decode

ROOT = Path(__file__).resolve().parents[1]
HEADER_SYMBOL = 'open_cfw_gx8002_image_a_stage1_header_and_vectors'
ENTRY_SYMBOL = 'open_cfw_gx8002_spl_reset_entry'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_header_and_vectors(stock: bytes) -> bytes:
    """Independently recompute the 280-byte header+vector span from the
    authenticated FWPK/BINH parse, cross-checked against the container
    version and version string (not the header's own literal fields)."""
    parsed = parse_fwpk(stock)
    _, main_record = parsed['records']
    main = parse_main_image(stock[main_record['offset']:])
    image_a = main['image_a']
    if image_a['soft_version'] != '0x00000203':
        raise ValueError('soft version changed')
    if image_a['soft_version'] != parsed['version']:
        raise ValueError('soft version no longer matches FWPK container version')
    if image_a['stage1_block_size'] != STAGE1_BLOCK:
        raise ValueError('stage1 block size no longer matches CONFIG_STAGE1_SRAM_SIZE')
    if image_a['stage1_load_address'] != '0x%08x' % DRAM_BASE:
        raise ValueError('stage1 load address no longer matches CONFIG_STAGE1_DRAM_BASE')
    header = struct.pack('<4sIIIII', b'BINH', 0x55AA55AA, int(image_a['soft_version'], 16),
                          image_a['stage2_size'], image_a['stage1_block_size'],
                          int(image_a['stage1_load_address'], 16))
    vectors = struct.pack('<64I', ENTRY_ADDRESS, *([DEFAULT_HANDLER_ADDRESS] * 63))
    combined = header + vectors
    if len(combined) != HEADER_SIZE:
        raise ValueError('recomputed header+vector size changed')
    return combined


def execute(code, control, seed):
    r = {f'r{i}': (seed + i) & 0xffffffff for i in range(32)}
    pc, trace = ENTRY_ADDRESS, []
    for _ in range(11):
        op, args, width = code[pc]
        p = [x.strip() for x in args.split(',')]
        if op == 'lrw':
            r[p[0]] = int(p[1], 0)
        elif op == 'mtcr':
            reg, cr = args.split(', ', 1)
            trace.append(('control-write', cr, r[reg]))
        elif op == 'mfcr':
            if args != 'r1, cr<31, 0>':
                raise ValueError('unexpected control source')
            r['r1'] = control
            trace.append(('control-read', 'cr<31, 0>', control))
        elif op == 'bclri':
            r[p[0]] &= ~(1 << int(p[1], 0))
        elif op == 'mov':
            r[p[0]] = r[p[1]]
        elif op == 'bsr':
            target = int(args, 0)
            if target not in (SPL_BOARD_INIT_R_ADDRESS, STAGE2_RESET_ENTRY_ADDRESS):
                raise ValueError('unexpected call target')
            trace.append(('call', target, r['r14']))
        else:
            raise ValueError('unexpected instruction ' + op)
        pc += width
    return trace


def oracle(control):
    return [
        ('control-write', 'cr<0, 0>', 0x80000200),
        ('control-read', 'cr<31, 0>', control),
        ('control-write', 'cr<31, 0>', control & ~8),
        ('control-write', 'cr<1, 0>', IRAM_BASE),
        ('call', SPL_BOARD_INIT_R_ADDRESS, SPL_INITIAL_STACK),
        ('call', STAGE2_RESET_ENTRY_ADDRESS, SPL_INITIAL_STACK),
    ]


def verify(prefix=None, output=None) -> dict:
    stock = IMAGE.read_bytes()
    if len(stock) != 326092 or sha(stock) != IMAGE_SHA:
        raise ValueError('codec baseline changed')
    expected = expected_header_and_vectors(stock)
    stock_header = stock[HEADER_PACKAGE_OFFSET:HEADER_PACKAGE_OFFSET + HEADER_SIZE]
    if expected != stock_header:
        raise ValueError('independently recomputed header/vectors do not match stock bytes')
    stock_entry = stock[ENTRY_PACKAGE_OFFSET:ENTRY_PACKAGE_OFFSET + ENTRY_SIZE]

    out_dir = (output or ROOT / 'build/continue-analysis/CD-008')
    evidence = build(prefix, out_dir)
    if not (evidence['header_byte_exact'] and evidence['entry_byte_exact']):
        raise ValueError('compiled SPL reset candidate is not byte-exact against stock')
    if evidence['header_bytes'] != expected:
        raise ValueError('compiled header/vectors do not match the independent recomputation')

    code = decode(Path(evidence['disassembly_path']).read_text())
    cases = 0
    for control in sorted({0, 0xffffffff, 0x55555555, 0xaaaaaaaa, *(1 << i for i in range(32))}):
        for seed in (0, 0xffffffff, 0x12345678):
            if execute(code, control, seed) != oracle(control):
                raise ValueError('reset chain control/call trace mismatch')
            cases += 1

    notice = ROOT / 'components/shared/gx8002/NATIONALCHIP-SPL-STARTUP-NOTICE.txt'
    return {
        'functions': [
            {
                'symbol': HEADER_SYMBOL,
                'section_name': '.rodata.header',
                'ownership_kind': 'generated_source_data',
                'compiled_bytes': HEADER_SIZE,
                'compiled_sha256': sha(evidence['header_bytes']),
                'stock_occurrences': [{
                    'symbol': HEADER_SYMBOL, 'package_offset': HEADER_PACKAGE_OFFSET,
                    'bytes': HEADER_SIZE, 'sha256': sha(stock_header),
                    'region': 'image_a_stage1_header_and_vectors',
                }],
            },
            {
                'symbol': ENTRY_SYMBOL,
                'section_name': '.text',
                'ownership_kind': 'compiled_assembly',
                'compiled_bytes': ENTRY_SIZE,
                'compiled_sha256': sha(evidence['entry_bytes']),
                'stock_occurrences': [{
                    'symbol': ENTRY_SYMBOL, 'package_offset': ENTRY_PACKAGE_OFFSET,
                    'bytes': ENTRY_SIZE, 'sha256': sha(stock_entry),
                    'region': 'image_a_spl_reset_chain',
                }],
            },
        ],
        'source_admitted': True, 'hardware_qualified': False, 'cases': cases,
        'notice_sha256': sha(notice.read_bytes()),
        'limits': [
            'spl_board_init_r (0x10000acc) is a genuine external call boundary: its '
            'content is not reconstructed and remains retained stock at its own address.',
            'The stack pointer at the second call is this code\'s own SPL_INITIAL_STACK '
            'value; whatever spl_board_init_r itself does to the stack before that call '
            'executes is unmodeled here.',
            'No physical boot, mask-ROM copy, or full-device qualification.',
        ],
    }


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-spl-reset-entry-verification.json').write_text(
        json.dumps({k: v for k, v in verify().items()}, indent=2) + '\n')
