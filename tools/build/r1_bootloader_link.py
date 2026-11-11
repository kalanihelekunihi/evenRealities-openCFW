#!/usr/bin/env python3
"""Strict GNU link diagnostic for an R1 source-composition report.

No implicit runtime archives, unresolved-symbol suppression, or crypto substitutes.
A successful link alone does not establish board compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = args.report.resolve()
    out = args.out.resolve()
    device = json.loads(report.read_text())['devices']['r1']
    payload = device['payloads']['r1-bootloader']
    if device['manifest_changed_during_build'] or digest(ROOT / 'r1/src/sources.json') != device['manifest_sha256']:
        parser.error('report manifest is stale or changed during compilation')
    if payload['failed'] or payload['duplicate_strong_symbols'] or payload['compiled'] != payload['units']:
        parser.error('bootloader composition is incomplete or has duplicate providers')
    compose = payload['compose']
    if compose['returncode'] != 0:
        parser.error('relocatable composition failed')
    units = [u for u in device['units'] if u['payload'] == 'r1-bootloader' and u.get('link', True)]
    objects = [Path(u['object']) for u in units]
    if not objects or any(not p.is_file() for p in objects):
        parser.error('participating objects are unavailable')
    for unit, obj in zip(units, objects):
        if digest(obj) != unit['object_sha256']:
            parser.error('participating object changed: ' + str(obj))
        source = (report.parent / 'generated/r1' / unit['source'][6:]
                  if unit['source'].startswith('{gen}/') else ROOT / unit['source'])
        if unit['source'].startswith('{gen}/'):
            source_root = report.parent / 'generated/r1'
        elif unit['source'].startswith('r1/src/'):
            source_root = ROOT / 'r1/src'
        elif unit['source'].startswith('third-party/upstream/'):
            source_root = ROOT / 'third-party/upstream'
        elif unit['source'].startswith('vendor-cache/r1/'):
            source_root = ROOT / 'vendor-cache/r1'
        else:
            parser.error('bootloader link input is outside R1 C source roots: ' + unit['source'])
        if source.suffix != '.c' or not source.resolve().is_relative_to(source_root.resolve()):
            parser.error('bootloader link input is not an R1 C source: ' + str(source))
        if not source.is_file() or digest(source) != unit['source_sha256']:
            parser.error('source changed since compilation: ' + str(source))
    linker = shutil.which('arm-none-eabi-ld')
    if not linker:
        parser.error('arm-none-eabi-ld is required')
    if out.exists() and any(out.iterdir()):
        parser.error('output directory must be empty')
    out.mkdir(parents=True, exist_ok=True)
    layout = ROOT / 'r1/config-recovered/openr1_bootloader.ld'
    mdk = ROOT / 'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/modules/nrfx/mdk'
    elf = out / 'bootloader.elf'
    command = [linker, '--gc-sections', '-L', str(mdk), '-T', str(layout),
               '-Map', str(out / 'bootloader.map'), '-o', str(elf), *map(str, objects)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    log = result.stdout + result.stderr
    (out / 'link.log').write_text(log)
    undefined = sorted(set(re.findall(r"undefined reference to [`']([^'`]+)'", log)))
    map_text = (out / 'bootloader.map').read_text() if (out / 'bootloader.map').is_file() else ''
    ram_region = re.search(r'^RAM\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)',
                           map_text, re.MULTILINE)
    ram_origin = int(ram_region.group(1), 16) if ram_region else None
    ram_capacity = int(ram_region.group(2), 16) if ram_region else None
    def map_symbol(name):
        match = re.search(r'^\s*0x([0-9a-fA-F]+)\s+' + re.escape(name) +
                          r'\s*=', map_text, re.MULTILINE)
        return int(match.group(1), 16) if match else None
    bss_end = map_symbol('__bss_end__')
    heap_base = map_symbol('__HeapBase')
    heap_limit = map_symbol('__HeapLimit')
    stack_limit = map_symbol('__StackLimit')
    stack_top = map_symbol('__StackTop')
    ram_layout_valid = (None not in (ram_origin, ram_capacity, bss_end,
                                     heap_base, heap_limit, stack_limit, stack_top) and
                        ram_origin <= bss_end <= heap_base < heap_limit <= stack_limit < stack_top and
                        stack_top == ram_origin + ram_capacity and
                        heap_limit - heap_base >= 16384 and
                        stack_top - stack_limit >= 16384)
    vector_address = None
    vector_bytes = 0
    initial_sp = None
    reset_vector = None
    reset_address = None
    image = out / 'bootloader.bin'
    image_bytes = None
    image_sha256 = None
    image_valid = False
    uicr_words = {}
    if result.returncode == 0:
        nm = shutil.which('arm-none-eabi-nm')
        objcopy = shutil.which('arm-none-eabi-objcopy')
        readelf = shutil.which('arm-none-eabi-readelf')
        if not nm or not objcopy or not readelf:
            parser.error('arm-none-eabi-nm, objcopy and readelf are required to verify the image')
        for line in subprocess.check_output([nm, '-S', '--defined-only', str(elf)], text=True).splitlines():
            fields = line.split()
            if len(fields) >= 4 and fields[-1] == '__isr_vector':
                vector_address, vector_bytes = int(fields[0], 16), int(fields[1], 16)
            if len(fields) >= 3 and fields[-1] == 'Reset_Handler':
                reset_address = int(fields[0], 16)
        text_section = out / 'bootloader.text.bin'
        subprocess.check_call([objcopy, '--dump-section', '.text=' + str(text_section), str(elf)])
        if text_section.stat().st_size >= 8:
            initial_sp, reset_vector = struct.unpack_from('<II', text_section.read_bytes())
    vector_valid = (vector_address == 0xf8000 and vector_bytes == 512 and
                    initial_sp == stack_top and reset_address is not None and
                    reset_vector == (reset_address | 1))
    if result.returncode == 0 and vector_valid and ram_layout_valid:
        sections = subprocess.check_output([readelf, '-SW', str(elf)], text=True)
        uicr_sections = {
            '.uicr_bootloader_start_address': (0x10001014, 0xf8000),
            '.uicr_mbr_params_page': (0x10001018, 0xfe000),
        }
        for section, (address, expected) in uicr_sections.items():
            placement = re.search(r'^\s*\[\s*\d+\]\s+' + re.escape(section) +
                                  r'\s+PROGBITS\s+([0-9a-fA-F]+)\s+\S+\s+([0-9a-fA-F]+)',
                                  sections, re.MULTILINE)
            actual_address = int(placement.group(1), 16) if placement else None
            actual_size = int(placement.group(2), 16) if placement else None
            word_path = out / (section[1:] + '.bin')
            dump_result = subprocess.run([objcopy, '--dump-section',
                                          section + '=' + str(word_path), str(elf)],
                                         capture_output=True, text=True)
            contents = word_path.read_bytes() if dump_result.returncode == 0 and word_path.is_file() else b''
            value = struct.unpack('<I', contents)[0] if len(contents) == 4 else None
            uicr_words[section] = {
                'address': actual_address, 'size': actual_size,
                'value': value, 'expected_value': expected,
                'path': str(word_path) if (actual_address, actual_size, value) == (address, 4, expected) else None,
                'sha256': digest(word_path) if (actual_address, actual_size, value) == (address, 4, expected) else None,
            }
            if (actual_address, actual_size, value) != (address, 4, expected):
                word_path.unlink(missing_ok=True)
        # UICR words have distant addresses and would turn an ordinary raw
        # objcopy into a huge sparse file. Emit only the bootloader flash
        # region; the settings and MBR pages are NOLOAD in this layout.
        image_result = subprocess.run([objcopy, '-O', 'binary',
                                       '--remove-section=.uicr_bootloader_start_address',
                                       '--remove-section=.uicr_mbr_params_page',
                                       str(elf), str(image)],
                                      capture_output=True, text=True)
        if image_result.returncode == 0 and image.is_file():
            image_bytes = image.stat().st_size
            if 512 <= image_bytes <= 0x6000:
                with image.open('rb') as stream:
                    image_sp, image_reset = struct.unpack('<II', stream.read(8))
                image_valid = (image_sp == initial_sp and image_reset == reset_vector and
                               all(item['path'] is not None
                                   for item in uicr_words.values()))
            if image_valid:
                image_sha256 = digest(image)
        if not image_valid:
            (out / 'image.log').write_text(image_result.stdout + image_result.stderr)
            image.unlink(missing_ok=True)
    linked = result.returncode == 0 and vector_valid and ram_layout_valid and image_valid
    if not linked:
        elf.unlink(missing_ok=True)
    receipt = {
        'schema': 1, 'returncode': result.returncode, 'linked': linked,
        'vector_flash_address': vector_address, 'vector_bytes': vector_bytes,
        'initial_sp': initial_sp, 'reset_vector': reset_vector,
        'reset_handler_address': reset_address, 'vector_valid': vector_valid,
        'image_valid': image_valid, 'image_path': str(image) if image_valid else None,
        'image_bytes': image_bytes, 'image_sha256': image_sha256,
        'image_flash_capacity_bytes': 0x6000,
        'ram_origin': ram_origin, 'ram_capacity_bytes': ram_capacity,
        'bss_end': bss_end, 'heap_base': heap_base, 'heap_limit': heap_limit,
        'stack_limit': stack_limit, 'stack_top': stack_top,
        'heap_reservation_bytes': (heap_limit - heap_base
                                   if heap_limit is not None and heap_base is not None else None),
        'stack_reservation_bytes': (stack_top - stack_limit
                                    if stack_top is not None and stack_limit is not None else None),
        'ram_headroom_bytes': (stack_limit - heap_limit
                               if stack_limit is not None and heap_limit is not None else None),
        'ram_layout_valid': ram_layout_valid,
        'uicr_words': uicr_words,
        'report': str(report), 'report_sha256': digest(report),
        'manifest_sha256': device['manifest_sha256'],
        'participating_c_source_units': len(units),
        'linker_version': subprocess.check_output([linker, '--version'], text=True).splitlines()[0],
        'inputs_sha256': {str(p): digest(p) for p in [layout, mdk / 'nrf_common.ld', *objects]},
        'argv': command, 'undefined_references': undefined,
        'limits': 'The raw bootloader flash region excludes UICR, settings and MBR pages; full bundle contents and physical boot require separate verification.'}
    (out / 'report.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'linked': receipt['linked'], 'undefined_references': undefined,
                      'vector_valid': vector_valid, 'ram_layout_valid': ram_layout_valid,
                      'image_valid': image_valid,
                      'image_bytes': image_bytes, 'report': str(out / 'report.json')}))
    return result.returncode or (0 if linked else 1)


if __name__ == '__main__':
    raise SystemExit(main())
