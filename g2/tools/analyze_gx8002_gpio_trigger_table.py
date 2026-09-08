#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate GPIO trigger switch targets; analysis only, no payload bytes."""
import json
import struct
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha


def analyze():
    data = IMAGE.read_bytes()
    if sha(data) != IMAGE_SHA:
        raise ValueError('GPIO switch firmware authentication')
    offset = 0x14230
    targets = struct.unpack_from('<8I', data, offset)
    # Targets decoded within gx_gpio_enable_trigger. Values are the actual
    # register offsets used by each target, not guesses from enum names.
    blocks = {0x1020603e: 0x2c, 0x10206028: 0x28, 0x10206054: 0x24,
              0x10205ff0: 0x14, 0x10206004: None, 0x10206012: 0x18}
    if any(target not in blocks for target in targets):
        raise ValueError('GPIO switch target outside decoded blocks')
    return {'firmware_sha256': IMAGE_SHA, 'table_offset': offset,
            'table_sha256': sha(data[offset:offset+32]),
            'entries': [{'trigger': index+1, 'target': target, 'register_offset': blocks[target]}
                        for index, target in enumerate(targets)],
            'source_admitted': False, 'firmware_bytes_emitted': 0,
            'limits': ['Read-only switch attribution. Target block semantics need full decoded qualification. Unsupported trigger values still register the callback and request IRQ1.']}


if __name__ == '__main__':
    report = analyze()
    (ROOT/'docs/research/gx8002-gpio-trigger-table.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
