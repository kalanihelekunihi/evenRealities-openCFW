#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Structural proof of a single volatile word load and unchanged return ABI."""
import json
import shutil
from build_gx8002_snpu_get_state_candidate import ROOT, build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

ADDRESS = 0x10205e28
OFFSET = 0xf3b4


def prove(code):
    wanted = ((ADDRESS, 'lrw', 'r3, 0x20027350', 2),
              (ADDRESS + 2, 'ld.w', 'r0, (r3, 0x0)', 2),
              (ADDRESS + 4, 'rts', '', 2))
    for pc, op, args, width in wanted:
        if code.get(pc) != (op, args, width):
            raise ValueError('state getter is not the qualified single-load leaf')
    return {'reads': 1, 'writes': 0, 'state_address': 0x20027350,
            'return': 'all 32 loaded bits in r0', 'callee_saved_registers': 'unchanged'}


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    evidence = build()
    code = decode((ROOT / 'build/gx8002-board/snpu-get-state-candidate.disassembly.txt').read_text())
    semantics = prove(code)
    if evidence['compiled_bytes'] != 12 or evidence['compiled_sha256'] != evidence['stock_sha256']:
        raise ValueError('state getter compiled/stock equality')
    row = {key: evidence[key] for key in ('symbol', 'section_name', 'compiled_bytes', 'compiled_sha256')}
    row['stock_occurrences'] = [{'symbol': evidence['symbol'], 'package_offset': OFFSET,
                                'bytes': 12, 'sha256': evidence['stock_sha256'],
                                'region': 'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'build/gx8002-board/snpu-get-state-candidate.elf', output / 'snpu-get-state.elf')
    return {'functions': [row], 'evidence': evidence, 'semantics': semantics,
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Single volatile read proven structurally; stock and compiled payloads identical. This does not establish ownership of all state writers or validate hardware scheduling.']}


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-snpu-get-state-verification.json').write_text(json.dumps(verify(), indent=2) + '\n')
