#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Require exact watchdog-stop code, including its explicit bit-clear instruction."""
import json
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]


def verify(prefix, sdk, output):
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_watchdog_stop.c'
    obj = output / 'stop.o'
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *FLAGS, '-c', str(source), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    sections = [s for s in elf.sections if s['flags'] & 4 and s['size']]
    if len(sections) != 1 or sections[0]['name'] != '.text.open_cfw_gx8002_watchdog_stop':
        raise ValueError('unexpected watchdog source sections')
    section = sections[0]
    payload = elf.contents(section)
    if payload != stock[0xfd38:0xfd44] or elf.relocations(section['index']):
        raise ValueError('watchdog stop no longer exactly matches stock')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unexpected watchdog dependency')
    report = {'symbol': 'open_cfw_gx8002_watchdog_stop', 'source_sha256': sha(source.read_bytes()),
              'compile_flags': FLAGS, 'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'stock_occurrences': [{'symbol': 'open_cfw_gx8002_watchdog_stop', 'package_offset': 0xfd38,
                                     'bytes': 12, 'sha256': sha(payload), 'region': 'image_a_xip_text'}],
              'implementation': 'C volatile MMIO with one explicit BCLRI inline assembly instruction',
              'source_admitted': True, 'hardware_qualified': False,
              'limits': ['Experimental hybrid only; full device behavior remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'build/csky-macos/install/bin', None,
                           ROOT / 'build/gx8002-watchdog-stop'), indent=2))
