#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify I2S C leaves by exact decoded instructions modulo scratch registers."""
import argparse
import itertools
import json
import re
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, sha, SDK_COMMIT
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS, disassemble

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_i2s.c'
NAMES = ('gx_audio_in_set_i2s_clock', 'gx_audio_in_set_i2sin_mode', 'gx_audio_in_set_i2sout_mode')


def scratch_renaming(original, compiled):
    """Keep r0 (argument/return), SP, link and callee-saved registers fixed."""
    for permutation in itertools.permutations(('r1', 'r2', 'r3')):
        mapping = dict(zip(('r1', 'r2', 'r3'), permutation))
        renamed = [(op, re.sub(r'\br[123]\b', lambda m: mapping[m[0]], args)) for op, args in compiled]
        if renamed == original:
            return mapping
    raise ValueError('target instruction sequence differs beyond scratch-register allocation')


def verify(prefix, sdk, output):
    candidates = analyze(sdk)
    output.mkdir(parents=True, exist_ok=True)
    obj = output / 'runtime_gx8002_i2s.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *FLAGS, '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unexpected external reference')
    original, _ = disassemble(prefix / 'csky-unknown-elf-objdump', sdk / 'drivers_lib/audio_in/v2.0/audio_in.o')
    compiled, text = disassemble(prefix / 'csky-unknown-elf-objdump', obj)
    if set(compiled) != set(NAMES):
        raise ValueError('I2S function inventory changed')
    results = []
    for name in NAMES:
        section = next(s for s in elf.sections if s['name'] == '.text.' + name)
        matches = [m for m in candidates['matches'] if m['symbol'] == name]
        if not matches or any(section['size'] != m['bytes'] for m in matches) or elf.relocations(section['index']):
            raise ValueError('I2S function envelope or relocations changed')
        if [op for op, _ in compiled[name]] != ['movih', 'ld.w', 'ins', 'movi', 'st.w', 'rts']:
            raise ValueError('I2S read/insert/write leaf structure changed')
        mapping = scratch_renaming(original[name], compiled[name])
        results.append({'symbol': name, 'compiled_bytes': section['size'],
                        'compiled_sha256': sha(elf.contents(section)), 'scratch_register_mapping': mapping,
                        'stock_occurrences': matches})
    report = {'sdk_commit': SDK_COMMIT, 'source_sha256': sha(SOURCE.read_bytes()), 'compile_flags': FLAGS,
              'functions': results, 'compiled_function_bytes': sum(r['compiled_bytes'] for r in results),
              'stock_occurrence_bytes': sum(m['bytes'] for r in results for m in r['stock_occurrences']),
              'firmware_bytes_emitted': 0, 'hardware_qualified': False,
              'qualification': 'Exact GNU-decoded instructions modulo consistent r1/r2/r3 allocation.',
              'limits': ['Bitfield layout is target-compiler-dependent and checked on every build.',
                         'Whole-device timing and integration remain unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    (output / 'disassembly.txt').write_text(text)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/csky-macos/install/bin')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-i2s-source')
    args = parser.parse_args()
    print(json.dumps(verify(args.prefix.resolve(), args.sdk.resolve(), args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
