#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify the CD-008-owned zero-fill span inside the image-A stage-1 block.

Compiles the reviewed data source, independently confirms the assumed span
is exactly zero in the authenticated stock image, and requires the compiled
bytes to match the stock bytes at package offset 0x0000A837.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from analyze_g2_codec_fwpk_segments import CODEC_SHA256 as IMAGE_SHA
from build_transparent_image import Elf32

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / 'blobs/official/g2-2.2.6.10/firmware_codec.bin'
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_image_a_stage1_body_pad.c'
HEADER = SOURCE.with_suffix('.h')
SYMBOL = 'open_cfw_gx8002_image_a_stage1_body_pad'
SECTION_NAME = '.rodata.' + SYMBOL
PACKAGE_OFFSET = 0x0000A837
PAD_SIZE = 3413
FLAGS = ['-O2', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin',
         '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _compile(output_dir: Path) -> bytes:
    output_dir.mkdir(parents=True, exist_ok=True)
    obj = output_dir / 'image-a-stage1-body-pad.o'
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([prefix + 'gcc', *FLAGS, '-I', str(SOURCE.parent),
                     '-c', str(SOURCE), '-o', str(obj)], check=True,
                    capture_output=True, text=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == SECTION_NAME)
    if elf.relocations(section['index']):
        raise ValueError('unresolved relocation in generated data section')
    payload = elf.contents(section)
    if len(payload) != PAD_SIZE:
        raise ValueError('compiled pad size changed')
    return payload


def verify(output=None) -> dict:
    stock = IMAGE.read_bytes()
    if len(stock) != 326092 or sha(stock) != IMAGE_SHA:
        raise ValueError('codec baseline changed')
    stock_slice = stock[PACKAGE_OFFSET:PACKAGE_OFFSET + PAD_SIZE]
    if len(stock_slice) != PAD_SIZE:
        raise ValueError('stock slice out of range')
    if any(stock_slice):
        raise ValueError('assumed zero-fill span is not all-zero in stock')

    out_dir = ROOT / 'build/continue-analysis/CD-008'
    payload = _compile(out_dir)
    if payload != stock_slice:
        raise ValueError('compiled data does not match stock bytes')

    return {
        'functions': [{
            'symbol': SYMBOL,
            'section_name': SECTION_NAME,
            'ownership_kind': 'generated_source_data',
            'compiled_bytes': PAD_SIZE,
            'compiled_sha256': sha(payload),
            'stock_occurrences': [{
                'symbol': SYMBOL,
                'package_offset': PACKAGE_OFFSET,
                'bytes': PAD_SIZE,
                'sha256': sha(stock_slice),
                'region': 'image_a_stage1_body_pad',
            }],
        }],
        'source_admitted': True,
        'hardware_qualified': False,
        'source_sha256': sha(SOURCE.read_bytes()),
        'header_sha256': sha(HEADER.read_bytes()),
        'limits': [
            'Covers only the trailing zero-fill inside the stage-1 block, package '
            '[0x0000A837, 0x0000B58C); the preceding SPL reset chain and the '
            'unreconstructed spl_board_init_r span remain separate items.',
        ],
    }


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-image-a-stage1-body-pad-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
