#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile the reviewed dcache-disable assembly and require exact stock equivalence.

Counterpart to verify_gx8002_csi_source.py (gx_dcache_enable). The stock
object's single-bit CACHE->CER clear compiles to a different instruction
(andni, not bclri) under this pinned toolchain's C lowering, so the
upstream algorithm is pinned as reviewed inline assembly (see
runtime_gx8002_dcache_disable.c) instead of C; this script authenticates
that assembly against the pinned SDK's gx_dcache.o byte for byte.
"""
import argparse
import json
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, sha, SDK_COMMIT
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_dcache_disable.c'


def verify(prefix, sdk, output):
    candidates = analyze(sdk)
    output.mkdir(parents=True, exist_ok=True)
    obj = output / 'runtime_gx8002_dcache_disable.o'
    command = [str(prefix / 'csky-unknown-elf-gcc'), *FLAGS, '-c', str(SOURCE), '-o', str(obj)]
    import subprocess
    subprocess.run(command, check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.gx_dcache_disable')
    payload = elf.contents(section)
    matches = [m for m in candidates['matches'] if m['symbol'] == 'gx_dcache_disable']
    if not matches or any(m['bytes'] != len(payload) or m['sha256'] != sha(payload) for m in matches):
        raise ValueError('reviewed dcache-disable assembly no longer exactly matches authenticated stock')
    if elf.relocations(section['index']) or any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('reviewed dcache-disable assembly gained external references')
    executable = [s for s in elf.sections if s['flags'] & 4 and s['size']]
    if executable != [section]:
        raise ValueError('unexpected additional executable sections')
    report = {'symbol': 'gx_dcache_disable', 'section_name': '.text.gx_dcache_disable',
              'ownership_kind': 'compiled_assembly',
              'sdk_commit': SDK_COMMIT, 'source_sha256': sha(SOURCE.read_bytes()),
              'compile_flags': FLAGS,
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'stock_occurrences': matches,
              'firmware_bytes_emitted': 0, 'production_source_admitted': False,
              'hardware_qualified': False}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/csky-macos/install/bin')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-dcache-disable-source')
    args = parser.parse_args()
    print(json.dumps(verify(args.prefix.resolve(), args.sdk.resolve(), args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
