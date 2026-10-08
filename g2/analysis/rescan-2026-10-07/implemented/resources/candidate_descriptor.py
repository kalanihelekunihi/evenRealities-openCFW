#!/usr/bin/env python3
"""Validate one explicitly held-out LVGL image descriptor candidate.

Validation establishes bounded structured bytes only. It does not promote an
asset to consumer-attributed coverage or infer a general resource format.
"""
from __future__ import annotations
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PAYLOAD_SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
CANDIDATE_RUNTIME = 0x7682B0
BASE = 0x437FE0
CANDIDATES = ROOT / 'g2/analysis/firmware-byte-map-2026-10-05/display-image-candidates.json'

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def validate_candidate(payload: bytes, candidate: dict) -> dict:
    if sha256(payload) != PAYLOAD_SHA:
        raise ValueError('authenticated payload hash mismatch')
    return validate_descriptor(payload, candidate)

def validate_descriptor(payload: bytes, candidate: dict) -> dict:
    """Validate the structure after caller has authenticated the payload."""
    if candidate['descriptor_runtime'] != CANDIDATE_RUNTIME:
        raise ValueError('candidate identity mismatch')
    off = candidate['descriptor_payload_offset']
    if off + BASE != candidate['descriptor_runtime']:
        raise ValueError('descriptor address-domain mismatch')
    if not 0 <= off <= len(payload)-28:
        raise ValueError('descriptor extent out of bounds')
    header = payload[off:off+28]
    magic, color, flags, width, height, stride, reserved, size, ptr, storage, handlers = struct.unpack('<BBHHHHHIIII', header)
    if (magic, color, flags, reserved, storage, handlers) != (25, 6, 0, 0, 0, 0):
        raise ValueError('unsupported descriptor layout')
    if (width, height, stride) != (candidate['width'], candidate['height'], candidate['stride']):
        raise ValueError('candidate geometry mismatch')
    lo, hi = candidate['data_payload_range']
    if not (0 <= lo < hi <= len(payload)):
        raise ValueError('pixel extent out of bounds')
    if stride != width or size != hi-lo or size != stride*height or ptr-BASE != lo:
        raise ValueError('descriptor extent/pointer mismatch')
    refs = candidate.get('pointer_reference_payload_offsets', [])
    if not refs:
        raise ValueError('candidate has no recorded pointer reference')
    for ref_off in refs:
        if not 0 <= ref_off <= len(payload)-4:
            raise ValueError('pointer reference offset out of bounds')
        if struct.unpack_from('<I', payload, ref_off)[0] != candidate['descriptor_runtime']:
            raise ValueError('pointer reference value mismatch')
    pixels = payload[lo:hi]
    if sha256(pixels) != candidate['pixel_sha256']:
        raise ValueError('candidate pixel hash mismatch')
    return {
        'descriptor_runtime': hex(CANDIDATE_RUNTIME),
        'descriptor_payload_range': [off, off+28],
        'descriptor_sha256': sha256(header),
        'pixel_payload_range': [lo, hi],
        'pixel_sha256': sha256(pixels),
        'dimensions': [width, height],
        'classification': candidate['classification'],
        'pointer_references': [{'payload_offset': off, 'runtime_address': hex(off+BASE),
                                'value': hex(struct.unpack_from('<I', payload, off)[0])}
                               for off in refs],
        'coverage_effect': 'none; unresolved candidate remains unresolved without constructor/consumer closure',
    }

def load_candidate() -> dict:
    records = json.loads(CANDIDATES.read_text())
    matches = [r for r in records if r['descriptor_runtime'] == CANDIDATE_RUNTIME]
    if len(matches) != 1:
        raise ValueError('held-out candidate record missing or ambiguous')
    c = matches[0]
    if c['classification'] != 'unresolved structured image candidate':
        raise ValueError('held-out record no longer has expected unresolved status')
    return c

def main() -> int:
    payload_path = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
    report = validate_candidate(payload_path.read_bytes(), load_candidate())
    receipt = {
        'status': 'PASS',
        'helper_sha256': sha256(Path(__file__).read_bytes()),
        'candidate_inventory_sha256': sha256(CANDIDATES.read_bytes()),
        'input_payload_sha256': sha256(payload_path.read_bytes()),
        'input_payload_size': payload_path.stat().st_size,
        'result': report,
    }
    receipt_path = Path(__file__).with_name('candidate-descriptor-receipt.json')
    receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
