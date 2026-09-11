#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile the GX8002 stage-2 libc leaf candidates (strcmp/strchr/strlen/strnlen).

Clean-room source; the pinned NationalChip lvp_kws checkout tracks only
memset.c for this directory, not these four symbols (see the header comment
in the source file). No SDK object is linked into the output.
"""
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_stage2_libc.c'
HEADER = SOURCE.with_suffix('.h')
BUILD_FLAGS = ['-Os', *FLAGS[1:]]

# Original stock envelopes in boot_stage2 (package offsets == runtime IRAM
# offsets from load address 0x10002800; see docs/research/gx8002-stage2-libc-source.md).
STOCK_OCCURRENCES = {
    'open_cfw_gx8002_stage2_strcmp': {'package_offset': 0x62c0, 'bytes': 36,
        'sha256': '90dbc680c495fc3c287b8a977f126add18808e3786e9a5a00daa2c8163ba375b'},
    'open_cfw_gx8002_stage2_strchr': {'package_offset': 0x6330, 'bytes': 26,
        'sha256': 'ab85ef2bdf620645e2accb724c5eac5682d82514020454d94deeeb29d35ddb10'},
    'open_cfw_gx8002_stage2_strlen': {'package_offset': 0x634c, 'bytes': 74,
        'sha256': 'e50dc29cc2485ae3a9ec64dce0f6b95824f18a0640dcf4dd0397c5241d3175aa'},
    'open_cfw_gx8002_stage2_strnlen': {'package_offset': 0x63a0, 'bytes': 40,
        'sha256': '863a46266b1380c23cf55b739b924219b41bc0a9cb0ae09349b2f545b0e9865d'},
}


def build(prefix=None, output=None):
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    output = output or ROOT / 'build/gx8002-stage2-libc'
    output.mkdir(parents=True, exist_ok=True)
    obj = output / 'stage2_libc.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *BUILD_FLAGS,
                     '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('stage2 libc candidate has undefined symbols')
    functions = []
    for symbol, occurrence in STOCK_OCCURRENCES.items():
        section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation in ' + symbol)
        payload = elf.contents(section)
        if len(payload) > occurrence['bytes']:
            raise ValueError(symbol + ' candidate exceeds stock envelope')
        (output / (symbol + '.disassembly.txt')).write_text(
            subprocess.check_output([str(prefix / 'csky-unknown-elf-objdump'), '-d', str(obj)], text=True))
        functions.append({'symbol': symbol, 'section_name': section['name'],
                           'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
                           'stock_occurrences': [{**occurrence, 'symbol': symbol, 'region': 'boot_stage2'}]})
    return {'object': str(obj), 'source_sha256': sha(SOURCE.read_bytes()),
            'header_sha256': sha(HEADER.read_bytes()), 'flags': BUILD_FLAGS, 'functions': functions}


if __name__ == '__main__':
    import json
    print(json.dumps(build(), indent=2))
