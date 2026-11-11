#!/usr/bin/env python3
"""Export checked R1 C-linked flash regions as a sparse Intel HEX image.

The result intentionally excludes the vendor SoftDevice, DFU settings, and
other flash pages that the two strict source links do not own.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


APP_ORIGIN = 0x27000
APP_END = 0xD1000
BOOT_ORIGIN = 0xF8000
BOOT_END = 0xFE000
UICR = {
    '.uicr_bootloader_start_address': (0x10001014, BOOT_ORIGIN),
    '.uicr_mbr_params_page': (0x10001018, BOOT_END),
}
ROOT = Path(__file__).resolve().parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_image(report, *, origin, limit):
    if (not report.get('linked') or not report.get('image_valid') or
            not report.get('ram_layout_valid') or
            report.get('undefined_references') or
            report.get('archive_members') or
            report.get('vector_flash_address') != origin or
            not report.get('participating_c_source_units')):
        raise ValueError(f'incomplete source-linked region at 0x{origin:x}')
    path = Path(report['image_path'])
    data = path.read_bytes()
    if (len(data) != report['image_bytes'] or
            digest(data) != report['image_sha256'] or
            origin + len(data) > limit):
        raise ValueError(f'changed or oversized source region at 0x{origin:x}')
    return data


def checked_provenance(app, boot):
    source_path = Path(app['report']).resolve()
    if (source_path != Path(boot['report']).resolve() or
            digest(source_path.read_bytes()) != app['report_sha256'] or
            app['report_sha256'] != boot['report_sha256'] or
            digest((ROOT / 'r1/src/sources.json').read_bytes()) !=
            app['manifest_sha256'] or
            app['manifest_sha256'] != boot['manifest_sha256']):
        raise ValueError('application and bootloader are not from the current source manifest and report')
    device = json.loads(source_path.read_text())['devices']['r1']
    if (device['manifest_changed_during_build'] or
            device['manifest_sha256'] != app['manifest_sha256']):
        raise ValueError('source report manifest is stale')
    checked = 0
    for unit in device['units']:
        if unit['payload'] not in ('r1-application', 'r1-bootloader') or not unit.get('link', True):
            continue
        source = (source_path.parent / 'generated/r1' / unit['source'][6:]
                  if unit['source'].startswith('{gen}/') else
                  ROOT / unit['source'])
        if digest(source.read_bytes()) != unit['source_sha256']:
            raise ValueError(f'source changed since strict link: {source}')
        checked += 1
    if checked != app['participating_c_source_units'] + boot['participating_c_source_units']:
        raise ValueError('source report has a different participating C set')
    return checked


def record(address, kind, data):
    if len(data) > 255 or not 0 <= address <= 0xffff:
        raise ValueError('invalid Intel HEX record')
    values = bytes((len(data), address >> 8, address & 255, kind)) + data
    checksum = (-sum(values)) & 255
    return ':' + (values + bytes((checksum,))).hex().upper()


def write_hex(path, regions):
    lines = []
    active_high = None
    for address, data in regions:
        offset = 0
        while offset < len(data):
            current = address + offset
            high = current >> 16
            if high != active_high:
                lines.append(record(0, 4, struct.pack('>H', high)))
                active_high = high
            chunk = data[offset:offset + min(16, 0x10000 - (current & 0xffff))]
            lines.append(record(current & 0xffff, 0, chunk))
            offset += len(chunk)
    lines.append(record(0, 1, b''))
    path.write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application-report', type=Path, required=True)
    parser.add_argument('--bootloader-report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    app = json.loads(args.application_report.read_text())
    boot = json.loads(args.bootloader_report.read_text())
    try:
        checked_sources = checked_provenance(app, boot)
        app_data = checked_image(app, origin=APP_ORIGIN, limit=APP_END)
        boot_data = checked_image(boot, origin=BOOT_ORIGIN, limit=BOOT_END)
        uicr = []
        for name, (address, value) in UICR.items():
            item = boot['uicr_words'][name]
            data = Path(item['path']).read_bytes()
            if (item['address'] != address or item['size'] != 4 or
                    item['value'] != value or item['expected_value'] != value or
                    data != struct.pack('<I', value) or digest(data) != item['sha256']):
                raise ValueError(f'invalid C-linked UICR word: {name}')
            uicr.append((address, data))
    except (KeyError, OSError, ValueError) as error:
        parser.error(str(error))
    regions = [(APP_ORIGIN, app_data), (BOOT_ORIGIN, boot_data), *uicr]
    regions.sort()
    if any(left + len(data) > right
           for (left, data), (right, _) in zip(regions, regions[1:])):
        parser.error('source-linked regions overlap')
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('output directory must be empty')
    out.mkdir(parents=True, exist_ok=True)
    hex_path = out / 'r1-source-regions.hex'
    write_hex(hex_path, regions)
    receipt = {
        'schema': 1,
        'application_report': str(args.application_report.resolve()),
        'bootloader_report': str(args.bootloader_report.resolve()),
        'source_report_sha256': app['report_sha256'],
        'manifest_sha256': app['manifest_sha256'],
        'checked_c_sources': checked_sources,
        'regions': [
            {'address': address, 'end': address + len(data),
             'bytes': len(data), 'sha256': digest(data)}
            for address, data in regions
        ],
        'hex_path': str(hex_path),
        'hex_sha256': digest(hex_path.read_bytes()),
        'limits': 'Sparse C-linked application, bootloader and UICR only; excludes Nordic S140/MBR, DFU settings, FDS/FAL contents and package metadata. Not an installable whole-device image.',
    }
    (out / 'report.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
