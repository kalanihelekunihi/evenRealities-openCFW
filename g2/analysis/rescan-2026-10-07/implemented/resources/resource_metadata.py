#!/usr/bin/env python3
"""Authenticate and export only previously mapped resource byte intervals.

This is metadata-bound exact slicing, not a format detector or resource census.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

MAP_PATH = Path(__file__).with_name('dependency-map.json')
L8_MAP = Path(__file__).resolve().parents[4] / 'tools/manifests/g2-l8-resource-map.json'

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_l8_map() -> dict:
    spec = json.loads(L8_MAP.read_text())
    # Do not loosen this helper into an arbitrary offset extractor: accept only
    # the map that was reviewed and used in the original bounded extraction.
    expected = '33115d16c9917b0908943c4f2c91b0f8955b3b255bf5a06fe10adf736841595d'
    if sha256(L8_MAP.read_bytes()) != expected:
        raise ValueError('reviewed L8 map identity mismatch')
    return spec

def validate_payload(payload: bytes, spec: dict) -> None:
    if len(payload) != spec['payload_size'] or sha256(payload) != spec['payload_sha256']:
        raise ValueError('payload identity mismatch')
    for asset in spec['assets']:
        lo, hi = asset['pixel_payload_range']
        if not (0 <= lo < hi <= len(payload)) or hi-lo != asset['width']*asset['height']:
            raise ValueError(f"invalid mapped range: {asset['asset']}")
        if sha256(payload[lo:hi]) != asset['pixel_sha256']:
            raise ValueError(f"mapped byte hash mismatch: {asset['asset']}")

def export_metadata(payload_path: Path, output: Path) -> dict:
    spec = load_l8_map()
    payload = payload_path.read_bytes()
    validate_payload(payload, spec)
    output.mkdir(parents=True, exist_ok=False)
    assets = []
    for asset in spec['assets']:
        lo, hi = asset['pixel_payload_range']
        data = payload[lo:hi]
        name = asset['asset'] + '.l8'
        (output / name).write_bytes(data)
        assets.append({
            'file': name,
            'format': 'LVGL v9 L8 (prior reviewed classification; not inferred here)',
            'payload_sha256': spec['payload_sha256'],
            'payload_range': [lo, hi],
            'sha256': sha256(data),
            'width': asset['width'], 'height': asset['height'], 'stride': asset['stride'],
            'classification_status': 'prior evidence only; zero newly classified bytes',
            'license': spec['license'],
            'provenance': spec['evidence'],
        })
    result = {'schema_version': 1, 'input_sha256': spec['payload_sha256'],
              'input_size': spec['payload_size'], 'assets': assets,
              'limitations': ['Only six pre-mapped images are exported.',
                              'No new format or consumer inference is performed.',
                              'Missing external NOR assets require the corresponding authorized image.']}
    (output / 'resource-metadata.json').write_text(json.dumps(result, indent=2)+'\n')
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = export_metadata(args.payload, args.output_dir)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'resource metadata export failed: {error}\n')
    print(f"PASS: exported {len(result['assets'])} previously mapped resources; newly classified bytes: 0")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
