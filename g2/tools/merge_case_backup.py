#!/usr/bin/env python3
"""Combine byte-matched case OTA applications with captured device-specific tails.

Offline only. Output is a reference archive, not an EVENOTA or flashing package.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path

BANK_SIZE = 0x40000
DATA_START = 0x3F000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def merge_bank(raw, bank):
    require(8 <= len(raw) <= DATA_START, 'Application overlaps device data or is too short')
    require(len(bank) == BANK_SIZE, 'Invalid bank size')
    require(bank[:len(raw)] == raw, 'Application is not an exact backup match')
    require(all(b == 255 for b in bank[len(raw):DATA_START]), 'Unexpected non-erased application tail')
    return raw + bank[len(raw):]


def write_verified(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == data, f'Refusing to overwrite different file: {path}')
    else:
        path.write_bytes(data)
        path.chmod(0o600)
    require(path.read_bytes() == data, f'Output verification failed: {path}')
    return {'file': path.name, 'size': len(data), 'sha256': sha(data)}


def build(source, backup_path, output):
    backup_bytes = backup_path.read_bytes()
    backup = json.loads(backup_bytes)
    require(backup.get('schemaVersion') == 1, 'Expected schema-1 case backup')
    flash = base64.b64decode(backup['flashBase64'], validate=True)
    options = base64.b64decode(backup['optionBytesBase64'], validate=True)
    require(len(flash) == 2 * BANK_SIZE and len(options) == 128, 'Invalid capture sizes')
    require(sha(flash) == backup['flashSha256'], 'Flash SHA-256 mismatch')
    require(sha(options) == backup['optionSha256'], 'Option SHA-256 mismatch')
    word = int.from_bytes(options[:4], 'little')
    require(int.from_bytes(options[4:8], 'little') == (~word & 0xffffffff), 'Invalid option complement')
    report = {
        'schemaVersion': 1, 'purpose': 'Device-specific offline recovery/reference archive; not an OTA package',
        'backup': str(backup_path), 'backupSha256': sha(backup_bytes),
        'capturedAt': backup.get('capturedAt'),
        'addressSemantics': 'Captured CPU flash aliases, with original option bytes retained separately; not physical-bank numbering',
        'glassesInstalledMemoryReadback': False,
        'glassesLimitation': 'Only original archived OTA components are available; no new MRAM, INFO0/INFOC, calibration or pairing-key coverage.',
        'capturedFiles': [], 'releases': [], 'unmatchedReleases': [],
    }
    for name, data, address in [('case-captured-flash.bin', flash, 0x08000000), ('case-captured-options.bin', options, 0x1fff7800)]:
        record = write_verified(output / name, data)
        record['captureBase'] = hex(address)
        report['capturedFiles'].append(record)
    report['deviceDataPages'] = [
        {'captureAddress': hex(0x08000000 + offset), 'size': 2048,
         'nonErasedBytes': sum(b != 255 for b in flash[offset:offset + 2048]),
         'sha256': sha(flash[offset:offset + 2048])}
        for offset in [0x3f000, 0x3f800, 0x7f000, 0x7f800]
    ]
    releases = {}
    for root in [source / 'firmware-archive/source-files', source / 'public/firmware-updates/source-files']:
        for path in sorted(root.glob('*/metadata.json')):
            meta = json.loads(path.read_text())
            if meta.get('channel') != 'official':
                continue
            version = meta['version']
            require(Path(version).name == version, 'Invalid version path')
            if version in releases:
                require(releases[version][1]['sourceSha256'] == meta['sourceSha256'], 'Conflicting release mirrors')
            releases[version] = (path, meta)
    for version, (path, meta) in sorted(releases.items()):
        payloads = {}
        for component in meta['components']:
            name = component['name'].replace('/', '_')
            require(Path(name).name == name, 'Invalid component path')
            data = (path.parent / name).read_bytes()
            require(len(data) == component['size'] and sha(data) == component['sha256'], f'Component mismatch: {version}/{name}')
            payloads[name] = data
        box = payloads['firmware_box.bin']
        raw = box[32:]
        require(box[:4] == b'EVEN' and int.from_bytes(box[8:12], 'big') == len(raw), 'Invalid case wrapper')
        checksum = sum(int.from_bytes(raw[i:i+4].ljust(4, b'\0'), 'big') for i in range(0, len(raw), 4)) & 0xffffffff
        require(checksum == int.from_bytes(box[12:16], 'big'), 'Case checksum mismatch')
        require(raw == (path.parent / 'firmware_box.raw.bin').read_bytes(), 'Raw extraction mismatch')
        matches = [offset for offset in [0, BANK_SIZE] if flash[offset:offset+len(raw)] == raw]
        if not matches:
            report['unmatchedReleases'].append({'version': version, 'caseVersion': meta.get('caseVersion'), 'reason': 'No exact application match; no cross-version device-data merge attempted'})
            continue
        folder = output / version
        files = [write_verified(folder / name, data) for name, data in payloads.items()]
        files.append(write_verified(folder / 'firmware_box.raw.bin', raw))
        merged = []
        for offset in matches:
            bank = merge_bank(raw, flash[offset:offset + BANK_SIZE])
            record = write_verified(folder / f'case-merged-alias-{0x08000000 + offset:08x}.bin', bank)
            record.update({'captureBase': hex(0x08000000 + offset), 'applicationBytes': len(raw),
                           'backupTailBytes': BANK_SIZE - len(raw), 'equalsCapturedBank': True})
            merged.append(record)
        report['releases'].append({'version': version, 'caseVersion': meta.get('caseVersion'),
                                   'sourceMetadata': str(path), 'sourceBundleSha256': meta['sourceSha256'],
                                   'files': files, 'mergedCaseBanks': merged})
    write_verified(output / 'manifest.json', (json.dumps(report, indent=2) + '\n').encode())
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--backup', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.source.resolve(), args.backup.resolve(), args.output.resolve())
    print(json.dumps({'mergedReleases': [r['version'] for r in result['releases']],
                      'unmatchedReleases': len(result['unmatchedReleases']), 'output': str(args.output)}, indent=2))
