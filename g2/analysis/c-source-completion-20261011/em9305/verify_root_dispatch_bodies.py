#!/usr/bin/env python3
"""Recompile root-prepared ARC bodies and compare complete isolated functions.

Absolute child/table bindings are review fixtures, not production providers.
"""
from pathlib import Path
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = ROOT / 'g2/build/arc-gnu-2026.03/toolchain/arc_gnu_prebuilt_elf32_le_linux_install/arc-multilib-elf32/bin/arc-elf32-gcc'
COPY = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-objcopy'
NATIVE = ROOT / 'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin'
BASE = 0x302400
native = NATIVE.read_bytes()
assert hashlib.sha256(native).hexdigest() == '0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'

def run_compiler(args):
    subprocess.run(['docker', 'run', '--rm', '--network', 'none',
                    '--platform', 'linux/amd64', '-v', f'{ROOT}:/work',
                    '-w', '/work', 'opencfw/iar-base:10.10.2-local',
                    str(TOOL.relative_to(ROOT)), '-mcpu=arcem',
                    '-mcode-density', *args], check=True)

results = []
for directory, spans in (
    ('root-dispatch-31d0fc', [(0x31d0fc, 0, 42)]),
    ('root-dispatch-31cb8c', [(0x31cb8c, 0, 16)]),
    ('root-event-31d128', [(0x31d128, 0, 40)]),
    ('root-event-322e80', [(0x322e80, 0, 134)]),
    ('root-dispatch-leaves', [(0x31cb84, 0, 8), (0x31cb9c, 8, 6), (0x31cba4, 16, 12)]),
):
    folder = HERE / directory
    source = folder / 'source.c'
    obj = folder / 'source.o'
    run_compiler(['-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                  '-fno-strict-aliasing', '-Wall', '-Wextra', '-Werror',
                  '-c', str(source.relative_to(ROOT)), '-o', str(obj.relative_to(ROOT))])
    linked = obj
    if (folder / 'review.ld').exists():
        linked = folder / 'review.elf'
        run_compiler(['-nostdlib', '-Wl,-T,' + str((folder / 'review.ld').relative_to(ROOT)),
                      str(obj.relative_to(ROOT)), '-o', str(linked.relative_to(ROOT))])
    raw = folder / 'fresh-review.text.bin'
    subprocess.run([str(COPY), '-O', 'binary', '-j', '.text', str(linked), str(raw)], check=True)
    data = raw.read_bytes()
    for address, offset, size in spans:
        assert data[offset:offset + size] == native[address - BASE:address - BASE + size], hex(address)
        results.append({'address': hex(address), 'whole_function_bytes_equal': size})

receipt = {'status': 'PASS_SEVEN_FRESH_COMPILED_COMPLETE_FUNCTION_BYTE_BINDINGS',
           'functions': results,
           'limits': ['Isolated placement and child/table address bindings only.',
                      'Production table extents, child ABI and complete images remain open.',
                      'No hardware execution.']}
(HERE / 'root-dispatch-bodies-fresh-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
