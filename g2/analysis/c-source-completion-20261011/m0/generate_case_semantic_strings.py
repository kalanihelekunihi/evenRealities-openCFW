#!/usr/bin/env python3
"""Source-own authenticated printable CASE strings and relocate source references.

Only NUL-terminated ASCII/control text is admitted. This is semantic C data,
not an encoded firmware payload or a copy of unknown stock regions.
"""
from pathlib import Path
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
COMPONENT = ROOT / 'g2/components/case'
OUTPUT = COMPONENT / 'semantic_strings_candidate_20261011'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
STOCK_SHA = '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
MANIFEST = HERE / 'case-semantic-strings.json'
PATTERN = re.compile(r'0x0800[0-9A-Fa-f]{4}u')
MACRO = re.compile(r'CASE_STRING_ADDR\((0800[0-9A-Fa-f]{4})\)')

def string_at(payload, address):
    offset = address - 0x08000000
    if not 0 <= offset < len(payload):
        return None
    window = payload[offset:offset + 256]
    end = window.find(b'\0')
    if end <= 0 or not all(32 <= byte <= 126 or byte in (9, 10, 13) for byte in window[:end]):
        return None
    return window[:end]

def c_escape(data):
    result = []
    for byte in data:
        if byte == 34:
            result.append('\\"')
        elif byte == 92:
            result.append('\\\\')
        elif 32 <= byte <= 126:
            result.append(chr(byte))
        else:
            result.append('\\%03o' % byte)
    return ''.join(result)

assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == STOCK_SHA
payload = STOCK.read_bytes()[32:]
if '--discover' in sys.argv:
    sources = [p for p in COMPONENT.rglob('*.c') if OUTPUT not in p.parents]
    references = {}
    for source in sources:
        for match in PATTERN.finditer(source.read_text()):
            address = int(match.group()[:-1], 16)
            data = string_at(payload, address)
            if data is not None:
                references[address] = data
    assert len(references) == 190, len(references)
    rows = [{'native_address': f'0x{address:08x}', 'length_with_nul': len(data) + 1,
             'semantic_text': data.decode('ascii'),
             'sha256_with_nul': hashlib.sha256(data + b'\0').hexdigest()}
            for address, data in sorted(references.items())]
    MANIFEST.write_text(json.dumps({'status': 'AUTHENTICATED_SEMANTIC_TEXT_ONLY',
                                    'stock_sha256': STOCK_SHA, 'rows': rows}, indent=2) + '\n')
    for source in sources:
        original = source.read_text()
        def replace(match):
            address = int(match.group()[:-1], 16)
            return f'CASE_STRING_ADDR({address:08x})' if address in references else match.group()
        changed = PATTERN.sub(replace, original)
        if changed != original:
            changed = '#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"\n' + changed
            source.write_text(changed)

if '--add-used-macros' in sys.argv:
    saved = json.loads(MANIFEST.read_text())
    by_address = {int(row['native_address'], 16): row for row in saved['rows']}
    for source in COMPONENT.rglob('*.c'):
        if OUTPUT in source.parents:
            continue
        for match in MACRO.finditer(source.read_text()):
            address = int(match.group(1), 16)
            if address in by_address:
                continue
            data = string_at(payload, address)
            if data is None:
                raise SystemExit(f'nonsemantic string address {address:#x} in {source}')
            by_address[address] = {'native_address': f'0x{address:08x}',
                                   'length_with_nul': len(data) + 1,
                                   'semantic_text': data.decode('ascii'),
                                   'sha256_with_nul': hashlib.sha256(data + b'\0').hexdigest()}
    saved['rows'] = [by_address[address] for address in sorted(by_address)]
    MANIFEST.write_text(json.dumps(saved, indent=2) + '\n')

if '--prune-unused' in sys.argv:
    saved = json.loads(MANIFEST.read_text())
    used = set()
    for source in COMPONENT.rglob('*.c'):
        if OUTPUT not in source.parents:
            used |= {int(match.group(1), 16) for match in MACRO.finditer(source.read_text())}
    saved['rows'] = [row for row in saved['rows'] if int(row['native_address'], 16) in used]
    MANIFEST.write_text(json.dumps(saved, indent=2) + '\n')

manifest = json.loads(MANIFEST.read_text())
assert manifest['stock_sha256'] == STOCK_SHA
rows = manifest['rows']
for row in rows:
    address = int(row['native_address'], 16)
    data = string_at(payload, address)
    assert data is not None and len(data) + 1 == row['length_with_nul']
    assert hashlib.sha256(data + b'\0').hexdigest() == row['sha256_with_nul']
OUTPUT.mkdir(exist_ok=True)
header = ['/* SPDX-License-Identifier: MIT',
          ' * CASE semantic text from authenticated stock string literals.',
          ' * Each original address has distinct C object identity.', ' */',
          '#ifndef CASE_SEMANTIC_STRINGS_H', '#define CASE_SEMANTIC_STRINGS_H',
          '#include <stdint.h>',
          '#define CASE_STRING_ADDR(suffix) ((uint32_t)(uintptr_t)case_string_##suffix)']
body = ['/* SPDX-License-Identifier: MIT',
        ' * Authenticated CASE semantic NUL-terminated strings.',
        ' * Provenance: case-semantic-strings.json; exact bytes, no stock payload.',
        ' */', '#include "case_semantic_strings.h"']
for row in rows:
    suffix = row['native_address'][2:]
    data = string_at(payload, int(row['native_address'], 16))
    header.append(f'extern const char case_string_{suffix}[];')
    body.append(f'const char case_string_{suffix}[] = "{c_escape(data)}";')
header.append('#endif')
(OUTPUT / 'case_semantic_strings.h').write_text('\n'.join(header) + '\n')
(OUTPUT / 'case_semantic_strings.c').write_text('\n'.join(body) + '\n')
print(json.dumps({'strings': len(rows), 'sum_bytes_with_nul': sum(x['length_with_nul'] for x in rows),
                  'output': str(OUTPUT.relative_to(ROOT))}, indent=2))
