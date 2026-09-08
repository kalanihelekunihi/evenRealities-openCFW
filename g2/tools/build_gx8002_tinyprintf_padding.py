#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile the reviewed padding-loop patch; no target equivalence admission."""
import json
import subprocess
from build_gx8002_tinyprintf_candidate import build
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from link_gx8002_uart_console import ROOT


def candidate():
    baseline = build()
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    output = ROOT / 'build/gx8002-tinyprintf'
    source = output / 'tinyprintf-padding.c'
    source.write_bytes((sdk / 'utility/libc/tinyprintf.c').read_bytes())
    patch = ROOT / 'tools/upstream-patches/tinyprintf-padding-loop.patch'
    subprocess.run(['patch', '--batch', str(source), str(patch)], check=True, capture_output=True)
    flags = baseline['compile_flags'] + ['-fno-tree-loop-optimize']
    obj = output / 'tinyprintf-padding.o'
    subprocess.run([str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-gcc'), *flags,
                    '-I', str(output), '-I', str(sdk / 'utility/libc'),
                    '-I', str(sdk / 'include/utility/libc'), '-c', str(source), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.putchw')
    report = {'upstream': baseline, 'patch_sha256': sha(patch.read_bytes()),
              'patched_source_sha256': sha(source.read_bytes()), 'compile_flags': flags,
              'compiled_bytes': section['size'], 'compiled_sha256': sha(elf.contents(section)),
              'stock_envelope_bytes': 212, 'source_admitted': False,
              'limits': ['Host equivalence does not establish target instruction equivalence.',
                         'External call relocations and target behavior remain unqualified.']}
    (ROOT / 'docs/research/gx8002-tinyprintf-padding-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(candidate(), indent=2))
