#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Measure a bounded compiler-option matrix; never admit code from size alone."""
import itertools
import json
import subprocess
from build_gx8002_tinyprintf_candidate import build
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT


def probe():
    baseline = build()
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    output = ROOT / 'build/gx8002-tinyprintf'
    compiler = ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-gcc'
    options = ['-fno-tree-loop-optimize', '-fno-ivopts', '-fno-tree-dominator-opts',
               '-fno-guess-branch-probability', '-fno-if-conversion', '-fno-if-conversion2',
               '-fno-shrink-wrap', '-fno-crossjumping', '-fno-tree-pre']
    variants = [()] + [(x,) for x in options] + list(itertools.combinations(options, 2))
    rows = []
    for index, extra in enumerate(variants):
        obj = output / f'probe-{index}.o'
        subprocess.run([str(compiler), *baseline['compile_flags'], *extra,
                        '-I', str(output), '-I', str(sdk / 'include/utility/libc'),
                        '-c', str(sdk / 'utility/libc/tinyprintf.c'), '-o', str(obj)], check=True)
        elf = Elf32(obj.read_bytes(), str(obj))
        sizes = {s['name']: s['size'] for s in elf.sections if s['flags'] & 4 and s['size']}
        fits = all(sizes.get('.text.' + name, 10**9) <= limit for name, limit in
                   [('ui2a', 120), ('putf', 24), ('putchw', 212), ('tfp_format', 416)])
        rows.append({'object': obj.name, 'extra_flags': list(extra), 'section_sizes': sizes,
                     'four_known_entries_fit': fits})
    report = {'authenticated_baseline': baseline, 'variants': rows, 'source_admitted': False,
              'limits': ['Size probe only; semantics, external calls and placement remain unqualified.']}
    (ROOT / 'docs/research/gx8002-tinyprintf-flag-probe.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps([r for r in rows if r['four_known_entries_fit']], indent=2))
    return report


if __name__ == '__main__':
    probe()
