#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Locate named NationalChip object-code candidates; never emit firmware bytes.

The SDK's precompiled drivers are comparison oracles, not source providers.
Exact section matches remain candidates until callable boundaries and behavior
are independently established. This tool neither compiles nor runs SDK code.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from build_transparent_image import Elf32

ROOT = Path(__file__).resolve().parents[1]
SDK_COMMIT = '8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5'
IMAGE = ROOT / 'blobs/official/g2-2.2.6.10/firmware_codec.bin'
IMAGE_SHA = 'b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0'
LEDGER = ROOT / 'tools/manifests/gx8002-source-readiness.tsv'
LEDGER_SHA = 'd89d6c7b26d7e4453bc1bab436868d554a9f39ab52308931c0fb5ceea485b32e'


class AuditError(RuntimeError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticated_blob(path, git_blob):
    data = path.read_bytes()
    actual = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
    if actual != git_blob:
        raise AuditError(f'upstream Git blob changed: {path}')
    return data


def occurrences(image, needle, low, high):
    """Yield complete matches confined to one authenticated executable span."""
    offset = image.find(needle, low, high)
    while offset >= 0:
        yield offset
        offset = image.find(needle, offset + 1, high)


def covered_bytes(matches):
    intervals = sorted((m['package_offset'], m['package_offset'] + m['bytes']) for m in matches)
    end, total = 0, 0
    for low, high in intervals:
        total += max(0, high - max(low, end))
        end = max(end, high)
    return total


def analyze(sdk):
    head = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip()
    if head != SDK_COMMIT:
        raise AuditError('SDK commit differs from the reviewed inspection baseline')
    tree = subprocess.check_output(['git', '-C', str(sdk), 'ls-tree', '-r', 'HEAD'], text=True)
    blobs = {}
    for line in tree.splitlines():
        metadata, name = line.split('\t', 1)
        mode, kind, digest = metadata.split()
        if kind == 'blob' and name.startswith('drivers_lib/') and name.endswith('.o'):
            if mode not in ('100644', '100755'):
                raise AuditError('unexpected upstream object file mode')
            blobs[name] = digest
    if not blobs:
        raise AuditError('SDK contains no driver object inventory')
    image = IMAGE.read_bytes()
    if len(image) != 326092 or sha(image) != IMAGE_SHA or sha(LEDGER.read_bytes()) != LEDGER_SHA:
        raise AuditError('codec image or readiness ledger authentication failed')
    with LEDGER.open(newline='') as handle:
        regions = [r for r in csv.DictReader(handle, delimiter='\t')
                   if r['byte_class'] == 'opaque_executable']
    matches, compared, objects = [], 0, []
    for name, digest in sorted(blobs.items()):
        path = sdk / name
        data = authenticated_blob(path, digest)
        if data[:6] != b'\x7fELF\x01\x01' or struct.unpack_from('<H', data, 18)[0] != 252:
            raise AuditError(f'not a C-SKY ELF32 little-endian object: {name}')
        elf = Elf32(data, name)
        objects.append({'path': name, 'git_blob': digest, 'sha256': sha(data)})
        for section in elf.sections:
            if not section['name'].startswith('.text.') or section['size'] < 16:
                continue
            if any(r['type'] in (4, 9) and r['info'] == section['index'] for r in elf.sections):
                continue
            if not section['flags'] & 4:
                continue
            compared += 1
            needle = elf.contents(section)
            if len(needle) != section['size']:
                raise AuditError('truncated executable section')
            for region in regions:
                low, high = int(region['start'], 0), int(region['end_exclusive'], 0)
                for offset in occurrences(image, needle, low, high):
                    matches.append({'object': name, 'symbol': section['name'][6:],
                                    'bytes': len(needle), 'package_offset': offset,
                                    'region': region['region'], 'sha256': sha(needle)})
    return {'schema_version': 1, 'sdk_url': 'https://github.com/NationalChip/lvp_kws',
            'sdk_commit': head, 'firmware_sha256': IMAGE_SHA,
            'ledger_sha256': LEDGER_SHA, 'objects': objects,
            'sections_compared': compared, 'matched_symbols': len({m['symbol'] for m in matches}),
            'matched_occurrences': len(matches), 'candidate_matched_byte_union': covered_bytes(matches),
            'matches': matches, 'candidate_only': True, 'source_admitted': False,
            'firmware_bytes_emitted': 0, 'hardware_operations': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = analyze(args.sdk.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text)
    print(json.dumps({k: v for k, v in result.items() if k not in ('objects', 'matches')}, indent=2))


if __name__ == '__main__':
    main()
