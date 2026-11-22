#!/usr/bin/env python3
"""Export the checked R1 C-linked code regions as sparse Intel HEX.

This includes the C MBR and Cordio region as well as application, bootloader
and UICR words. DFU settings and persisted user data remain separate inputs.
"""
import argparse
import json
from pathlib import Path
import struct

from r1_source_regions import (APP_ORIGIN, APP_END, BOOT_ORIGIN, BOOT_END,
                               ROOT, UICR, checked_image,
                               checked_provenance, digest, write_hex)


def checked_mbr(report, source_device, manifest_sha):
    checks = report.get('checks', {})
    required = ('stage_entry_non_erased', 'cordio_init_non_erased',
                'command_entry_non_erased', 'gaps_erased', 'relocation_free')
    if (not report.get('linked') or report.get('manifest_sha256') != manifest_sha or
            report.get('participating_c_source_units') != 1 or
            checks.get('page_bytes') != 4096 or
            any(checks.get(key) is not True for key in required) or
            report.get('layout_sha256') !=
                digest((ROOT / 'r1/config-recovered/openr1_mbr.ld').read_bytes())):
        raise ValueError('C MBR link or layout verification is incomplete')
    units = [unit for unit in source_device['units']
             if unit['payload'] == 'r1-mbr' and unit.get('link', True)]
    if (len(units) != 1 or
            not units[0]['source'].startswith('r1/src/') or
            not units[0]['source'].endswith('.c')):
        raise ValueError('C MBR source ownership changed')
    unit = units[0]
    source = ROOT / unit['source']
    obj = Path(unit['object'])
    if (digest(source.read_bytes()) != unit['source_sha256'] or
            digest(obj.read_bytes()) != unit['object_sha256'] or
            report.get('inputs_sha256') != {str(obj): unit['object_sha256']}):
        raise ValueError('C MBR input differs from the source report')
    image = Path(report['image_path'])
    data = image.read_bytes()
    if len(data) != 4096 or digest(data) != report['image_sha256']:
        raise ValueError('C MBR image differs from the verified link')
    return data


def checked_cordio(app):
    if (not app.get('ble_descriptor_valid') or
            not app.get('ble_data_valid') or
            app.get('ble_flash_descriptor_address') != 0x1000 or
            app.get('ble_flash_descriptor_bytes') != 220 or
            app.get('ble_flash_headroom_bytes', -1) < 0 or
            app.get('ble_ram_headroom_bytes', -1) < 0):
        raise ValueError('lower C controller descriptor or layout is invalid')
    data = Path(app['ble_image_path']).read_bytes()
    if (len(data) != app['ble_image_bytes'] or
            len(data) != app['ble_flash_used_bytes'] or
            digest(data) != app['ble_image_sha256'] or
            0x1000 + len(data) > APP_ORIGIN):
        raise ValueError('lower C controller image differs from verified link')
    return data


def checked_uicr(boot):
    result = []
    for name, (address, value) in UICR.items():
        item = boot['uicr_words'][name]
        data = Path(item['path']).read_bytes()
        if (item['address'] != address or item['size'] != 4 or
                item['value'] != value or item['expected_value'] != value or
                data != struct.pack('<I', value) or
                digest(data) != item['sha256']):
            raise ValueError(f'invalid C-linked UICR word: {name}')
        result.append((address, data))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application-report', type=Path, required=True)
    parser.add_argument('--bootloader-report', type=Path, required=True)
    parser.add_argument('--mbr-report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        app = json.loads(args.application_report.read_text())
        boot = json.loads(args.bootloader_report.read_text())
        mbr = json.loads(args.mbr_report.read_text())
        if boot.get('source_ble_ram_layout') is not True:
            raise ValueError('bootloader does not use the lower C controller RAM layout')
        count = checked_provenance(app, boot)
        source_path = Path(app['report']).resolve()
        source_device = json.loads(source_path.read_text())['devices']['r1']
        regions = [(0x0000, checked_mbr(mbr, source_device,
                                        app['manifest_sha256'])),
                   (0x1000, checked_cordio(app)),
                   (APP_ORIGIN, checked_image(app, origin=APP_ORIGIN,
                                              limit=APP_END)),
                   (BOOT_ORIGIN, checked_image(boot, origin=BOOT_ORIGIN,
                                               limit=BOOT_END)),
                   *checked_uicr(boot)]
    except (KeyError, OSError, ValueError) as error:
        parser.error(str(error))
    regions.sort()
    if any(left + len(data) > right
           for (left, data), (right, _) in zip(regions, regions[1:])):
        parser.error('source-linked regions overlap')
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('output directory must be empty')
    out.mkdir(parents=True, exist_ok=True)
    image = out / 'r1-source-code.hex'
    write_hex(image, regions)
    receipt = {
        'schema': 1,
        'application_report': str(args.application_report.resolve()),
        'bootloader_report': str(args.bootloader_report.resolve()),
        'mbr_report': str(args.mbr_report.resolve()),
        'source_report_sha256': app['report_sha256'],
        'manifest_sha256': app['manifest_sha256'],
        'checked_c_sources': count + 1,
        'regions': [
            {'address': address, 'end': address + len(data),
             'bytes': len(data), 'sha256': digest(data)}
            for address, data in regions
        ],
        'hex_path': str(image),
        'hex_sha256': digest(image.read_bytes()),
        'limits': 'Source-built code regions and UICR only. DFU settings, FDS/FAL contents, package metadata, stock byte identity, and hardware boot require separate verification.',
    }
    (out / 'report.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'hex_path': str(image), 'checked_c_sources': count + 1,
                      'regions': len(regions), 'report': str(out / 'report.json')}))


if __name__ == '__main__':
    main()
