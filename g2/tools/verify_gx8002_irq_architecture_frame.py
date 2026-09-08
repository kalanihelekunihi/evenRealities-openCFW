#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check decoded IRQ saves against reviewed ISA stack layout, without timing claims."""
import hashlib
import json
import subprocess
from verify_gx8002_irq_software_frame import ROOT, build, decode, execute

MANUAL_SHA = '579bd296dbf88b0b6842a473432e65199b87c0c19fcf04bb214f67241c68d509'


def verify():
    if hashlib.sha256((ROOT/'build/csky-isa-manual.pdf').read_bytes()).hexdigest() != MANUAL_SHA:
        raise ValueError('manual hash mismatch')
    evidence = build()
    prefix = ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    code = decode(subprocess.check_output([str(prefix)+'objdump', '-d',
                                          str(ROOT/'build/gx8002-irq/entry.elf')], text=True))
    cases = 0
    for seed in (0, 1, 0xffffffff, 0x55555555, 0xaaaaaaaa, 0x80000000):
        for depth in range(4):
            result = execute(code, 0x10025574, seed, depth, architecture=True)
            if result != {'calls': 1, 'software_frame_bytes': 100,
                          'modeled_peak_bytes': 136*(depth+1)}:
                raise ValueError('architecture frame mismatch')
            cases += 1
    report = {'build': evidence, 'manual_sha256': MANUAL_SHA,
              'manual_printed_pages': [180, 182, 297, 299], 'cases': cases,
              'instruction_managed_bytes_per_level': 32,
              'software_bytes_per_returning_callback_level': 104,
              'modeled_peak_bytes': [136, 272, 408, 544], 'source_admitted': False,
              'limits': ['Models stack transfers and saved control values, not PSR enable-bit timing or exception arrival.',
                         'Nested entry is injected at the callback point; other interrupt points remain unqualified.',
                         'Callback clobbers are modeled; arbitrary callback stack usage and physical stack capacity are not bounded.',
                         'Vendor ISA document is mirrored externally; GX8002-specific errata remain unqualified.']}
    (ROOT/'docs/research/gx8002-irq-architecture-frame-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(cases)
    return report


if __name__ == '__main__':
    verify()
