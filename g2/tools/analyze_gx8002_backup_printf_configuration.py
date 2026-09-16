# SPDX-License-Identifier: MIT
"""Authenticate stock format dispatch and probe matching upstream compilation."""
import json
import struct
import subprocess
from build_gx8002_backup_printf_candidate import build, ROOT, Elf32, sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA


def analyze():
    evidence = build()
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    # The decoded switch at package 0x4183c subtracts 37 and bounds at 84;
    # 0x41848 loads this table, followed by indexed word load and indirect jump.
    table_offset = 0x12ff4 + 0x38940
    dispatch = {chr(i): struct.unpack_from('<I', stock, table_offset + 4 * (i - 37))[0]
                for i in range(37, 121)}
    fallback = 0x10008f30
    assert all(dispatch[c] == fallback for c in 'eEgG')
    assert dispatch['f'] == dispatch['F'] == 0x1000914e
    assert dispatch['f'] != fallback
    pow10 = b''.join(struct.pack('<d', 10.0 ** i) for i in range(10))
    assert stock[0x4ba84:0x4bad4] == pow10
    out = ROOT / 'build/gx8002-backup-printf/configuration-probes'
    out.mkdir(exist_ok=True)
    records = []
    for index, flags in enumerate((['-Os'], ['-O2'], ['-Os', '-finline-functions'],
                                   ['-O2', '-fno-shrink-wrap'])):
        command = evidence['command'].copy()
        command[command.index('-Os'):command.index('-Os') + 1] = flags + ['-DPRINTF_DISABLE_SUPPORT_EXPONENTIAL']
        path = out / (str(index) + '.o')
        command[-1] = str(path)
        subprocess.run(command, check=True)
        elf = Elf32(path.read_bytes(), 'printf probe')
        sections = {s['name']: s['size'] for s in elf.sections if s['flags'] & 2 and s['size']}
        assert not any('_etoa' in name for name in sections)
        assert any('_ntoa_long_long' in name for name in sections)
        records.append({'command': command, 'object_sha256': sha(path.read_bytes()), 'sections': sections,
                        'undefined_symbols': [s['name'] for s in elf.symbols() if s['name'] and s['section'] == 0]})
    result = {'upstream': evidence, 'stock_sha256': IMAGE_SHA,
              'dispatch': {c: hex(dispatch[c]) for c in '%bcdiouxXpsfFeEgG'},
              'power_table': {'offset': 0x4ba84, 'bytes': len(pow10), 'source_expression': '10.0 ** i for i in range(10)'},
              'variants': records, 'source_admitted': False,
              'limits': ['Stock e/E/g/G switch entries reach the ordinary-character fallback; f/F have a distinct path. This supports disabling exponential support for the compatibility baseline, not removing stock floating-point support.',
                         'Probe objects are not integrated or execution-qualified. Default full-feature SDK candidate remains available.']}
    (ROOT / 'docs/research/gx8002-backup-printf-configuration.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    for row in analyze()['variants']:
        print(row['sections'])
