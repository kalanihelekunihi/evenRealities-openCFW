#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile a pinned upstream CSI adapter and require exact stock equivalence."""
import argparse
import json
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, authenticated_blob, sha, SDK_COMMIT
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_dcache_enable.c'
HEADERS = ('arch/soc/grus/include/core_ck804.h', 'arch/soc/grus/include/csi_gcc.h',
           'include/utility/libc/stdlib.h', 'include/utility/libc/klibc/extern.h',
           'include/utility/libc/klibc/inline.h', 'include/utility/util.h')


def verify(prefix, sdk, output):
    candidates = analyze(sdk)
    dependencies = []
    for name in (*HEADERS, 'LICENSE'):
        digest = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD:' + name], text=True).strip()
        data = authenticated_blob(sdk / name, digest)
        dependencies.append({'path': name, 'git_blob': digest, 'sha256': sha(data)})
    output.mkdir(parents=True, exist_ok=True)
    obj = output / 'runtime_gx8002_dcache_enable.o'
    includes = [str(sdk / p) for p in ('arch/soc/grus/include', 'include/utility', 'include/utility/libc')]
    command = [str(prefix / 'csky-unknown-elf-gcc'), *FLAGS]
    for directory in includes:
        command += ['-isystem', directory]
    subprocess.run([*command, '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.gx_dcache_enable')
    payload = elf.contents(section)
    matches = [m for m in candidates['matches'] if m['symbol'] == 'gx_dcache_enable']
    if not matches or any(m['bytes'] != len(payload) or m['sha256'] != sha(payload) for m in matches):
        raise ValueError('upstream CSI adapter no longer exactly matches authenticated stock')
    if elf.relocations(section['index']) or any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('upstream CSI adapter gained external references')
    executable = [s for s in elf.sections if s['flags'] & 4 and s['size']]
    if executable != [section]:
        raise ValueError('unexpected additional executable sections')
    report = {'sdk_commit': SDK_COMMIT, 'source_sha256': sha(SOURCE.read_bytes()),
              'upstream_dependencies': dependencies, 'compile_flags': FLAGS,
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'exact_stock_occurrences': matches,
              'firmware_bytes_emitted': 0, 'production_source_admitted': False,
              'hardware_qualified': False}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/csky-macos/install/bin')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-csi-source')
    args = parser.parse_args()
    print(json.dumps(verify(args.prefix.resolve(), args.sdk.resolve(), args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
