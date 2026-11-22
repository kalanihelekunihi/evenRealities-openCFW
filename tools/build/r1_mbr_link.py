#!/usr/bin/env python3
"""Strict standalone link and first-page export of the R1 C MBR candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.report.resolve()
    output = args.out.resolve()
    device = json.loads(report_path.read_text())['devices']['r1']
    payload = device['payloads']['r1-mbr']
    manifest = ROOT / 'r1/src/sources.json'
    if device['manifest_changed_during_build'] or sha(manifest) != device['manifest_sha256']:
        parser.error('MBR compile report has a stale manifest')
    if payload['compiled'] != payload['units'] or payload['failed'] or payload['duplicate_strong_symbols']:
        parser.error('MBR source compilation is incomplete')
    if payload['compose']['returncode'] or payload['compose']['undefined']:
        parser.error('MBR relocatable composition has unresolved symbols')
    units = [u for u in device['units'] if u['payload'] == 'r1-mbr' and u.get('link', True)]
    if not units:
        parser.error('no MBR C units in compile report')
    objects = []
    for unit in units:
        source = ROOT / unit['source']
        obj = Path(unit['object'])
        if (not source.resolve().is_relative_to((ROOT / 'r1/src/mbr').resolve()) or
                source.suffix != '.c' or not source.is_file() or sha(source) != unit['source_sha256'] or
                not obj.is_file() or sha(obj) != unit['object_sha256']):
            parser.error('MBR source/object changed since compilation: ' + unit['source'])
        objects.append(obj)
    if output.exists() and any(output.iterdir()):
        parser.error('output directory must be empty')
    output.mkdir(parents=True, exist_ok=True)
    linker = shutil.which('arm-none-eabi-ld')
    objcopy = shutil.which('arm-none-eabi-objcopy')
    nm = shutil.which('arm-none-eabi-nm')
    readelf = shutil.which('arm-none-eabi-readelf')
    if not all((linker, objcopy, nm, readelf)):
        parser.error('ARM GNU linker, objcopy, nm and readelf are required')
    layout = ROOT / 'r1/config-recovered/openr1_mbr.ld'
    elf = output / 'mbr.elf'
    command = [linker, '--gc-sections', '-T', str(layout), '-Map', str(output / 'mbr.map'),
               '-o', str(elf), *map(str, objects)]
    linked = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (output / 'link.log').write_text(linked.stdout + linked.stderr)
    symbols = {}
    binary = output / 'mbr.bin'
    checks = {}
    if linked.returncode == 0:
        for line in subprocess.check_output([nm, '-S', '--defined-only', str(elf)], text=True).splitlines():
            fields = line.split()
            if len(fields) >= 3:
                symbols[fields[-1]] = int(fields[0], 16)
        exported = subprocess.run([objcopy, '-O', 'binary', '--gap-fill=0xff',
                                   '--pad-to=0x1000', str(elf), str(binary)],
                                  capture_output=True, text=True)
        if exported.returncode:
            (output / 'export.log').write_text(exported.stdout + exported.stderr)
        if binary.is_file():
            data = binary.read_bytes()
            checks = {
                'page_bytes': len(data),
                'initial_sp': struct.unpack_from('<I', data)[0] if len(data) >= 4 else None,
                'reset_vector': struct.unpack_from('<I', data, 4)[0] if len(data) >= 8 else None,
                'config_words': list(struct.unpack_from('<II', data, 0xff8)) if len(data) == 4096 else [],
                'stage_tag': struct.unpack_from('<I', data, 0x7fc)[0] if len(data) == 4096 else None,
                'cordio_init_tag': struct.unpack_from('<I', data, 0x8fc)[0] if len(data) == 4096 else None,
                'command_tag': struct.unpack_from('<I', data, 0xafc)[0] if len(data) == 4096 else None,
                'stage_entry_non_erased': any(b != 0xff for b in data[0x800:symbols.get('__mbr_stage_end', 0)])
                                            if len(data) == 4096 and 0x800 < symbols.get('__mbr_stage_end', 0) <= 0x8fc
                                            else False,
                'cordio_init_non_erased': any(b != 0xff for b in data[0x900:symbols.get('__mbr_cordio_init_end', 0)])
                                          if len(data) == 4096 and 0x900 < symbols.get('__mbr_cordio_init_end', 0) <= 0xff8
                                          else False,
                'command_entry_non_erased': any(b != 0xff for b in data[0xb00:symbols.get('__mbr_command_end', 0)])
                                            if len(data) == 4096 and 0xb00 < symbols.get('__mbr_command_end', 0) <= 0xff8
                                            else False,
                'gaps_erased': (all(b == 0xff for b in data[symbols.get('__mbr_text_end', 0):0x7fc]) and
                                all(b == 0xff for b in data[symbols.get('__mbr_stage_end', 0):0x8fc]) and
                                all(b == 0xff for b in data[symbols.get('__mbr_cordio_init_end', 0):0xafc]) and
                                all(b == 0xff for b in data[symbols.get('__mbr_command_end', 0):0xff8]))
                               if len(data) == 4096 and
                               0x200 <= symbols.get('__mbr_text_end', 0) <= 0x7fc and
                               0x800 < symbols.get('__mbr_stage_end', 0) <= 0x8fc and
                               0x900 < symbols.get('__mbr_cordio_init_end', 0) <= 0xafc and
                               0xb00 < symbols.get('__mbr_command_end', 0) <= 0xff8 else False,
            }
        relocations = subprocess.check_output([readelf, '-r', str(elf)], text=True)
        checks['relocation_free'] = 'There are no relocations in this file.' in relocations
    valid = (linked.returncode == 0 and checks.get('page_bytes') == 4096 and
             symbols.get('r1_mbr_vectors') == 0 and
             checks.get('initial_sp') == 0x20001000 and
             checks.get('reset_vector') == (symbols.get('Reset_Handler', 0) | 1) and
             checks.get('config_words') == [0xf8000, 0xfe000] and
             symbols.get('r1_mbr_stage_bootloader') == 0x800 and
             symbols.get('r1_mbr_cordio_region_init') == 0x900 and
             symbols.get('r1_mbr_command_non_init') == 0xb00 and
             checks.get('stage_tag') == 0x52315354 and
             checks.get('cordio_init_tag') == 0x52314349 and
             checks.get('command_tag') == 0x5231434d and
             checks.get('stage_entry_non_erased') and
             checks.get('cordio_init_non_erased') and
             checks.get('command_entry_non_erased') and
             checks.get('gaps_erased') and checks.get('relocation_free'))
    if not valid:
        binary.unlink(missing_ok=True)
        elf.unlink(missing_ok=True)
    receipt = {
        'schema': 1, 'linked': valid, 'link_returncode': linked.returncode,
        'checks': checks, 'symbols': symbols,
        'image_path': str(binary) if valid else None,
        'image_sha256': sha(binary) if valid else None,
        'layout_sha256': sha(layout), 'manifest_sha256': device['manifest_sha256'],
        'participating_c_source_units': len(units),
        'inputs_sha256': {str(p): sha(p) for p in objects},
        'argv': command,
        'limits': 'Standalone first page with tagged staging and Cordio initialization entries. BLE DFU, interruption replay and physical boot require separate verification.',
    }
    (output / 'report.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'linked': valid, 'checks': checks, 'report': str(output / 'report.json')}))
    return 0 if valid else 1


if __name__ == '__main__':
    raise SystemExit(main())
