#!/usr/bin/env python3
"""Attempt a strict final link of the individual R1 application C objects.

The report is diagnostic until every import resolves and the image fits.
No stock executable region or unresolved-symbol override is admitted.
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


def final_registry_script(source, destination, *, dynamic_log=False):
    """Turn a zero-based relocatable registry into final-address sections.

    The source fragment remains the sole owner of ordering and record-count
    assertions. The generated script is only a placement adaptation.
    """
    content = source.read_text()
    content, count = re.subn(r'(?m)^(\s*\.[A-Za-z0-9_]+) 0 :', r'\1 :', content)
    if count == 0:
        raise ValueError(f'no relocatable sections in {source}')
    if dynamic_log:
        pattern = r'(?ms)^ \.log_dynamic_data : ALIGN\(4\)\n \{.*?^ \}\n'
        match = re.search(pattern, content)
        if not match:
            raise ValueError('log registry has an unexpected dynamic section')
        dynamic = match.group().rstrip()[:-1] + '} > RAM\n'
        content = content[:match.start()] + content[match.end():]
        content = content.replace('  __stop_log_const_data = .;\n }',
                                  '  __stop_log_const_data = .;\n } > FLASH', 1)
        body, assertions = content.split('\nASSERT(', 1)
        body = body.rstrip() + ' INSERT AFTER .text;'
        # The dynamic records follow all initialized RAM orphan sections.
        # GNU ld assigns the corresponding contiguous flash load address.
        content = (body + '\nSECTIONS\n{\n' + dynamic +
                   '} INSERT AFTER .data;\nASSERT(' + assertions)
    else:
        content = content.replace('\n }\n', '\n } > FLASH\n')
        content = content.replace('\n}\nASSERT(', '\n} INSERT AFTER .text;\nASSERT(', 1)
    destination.write_text(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = args.report.resolve()
    out = args.out.resolve()
    device = json.loads(report.read_text())['devices']['r1']
    payload = device['payloads']['r1-application']
    manifest = ROOT / 'r1/src/sources.json'
    if device['manifest_changed_during_build'] or digest(manifest) != device['manifest_sha256']:
        parser.error('report manifest is stale or changed during compilation')
    if payload['failed'] or payload['duplicate_strong_symbols'] or payload['compiled'] != payload['units']:
        parser.error('application composition is incomplete or has duplicate providers')
    compose = payload['compose']
    if compose['returncode'] != 0:
        parser.error('relocatable composition failed')
    obj = Path(compose['output'])
    if not obj.is_file() or digest(obj) != compose['sha256']:
        parser.error('composed application object is missing or changed')
    objects = []
    c_source_units = 0
    for unit in device['units']:
        if unit['payload'] != 'r1-application' or not unit.get('link', True):
            continue
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
            parser.error('application link input is outside R1 C source roots: ' + unit['source'])
        if source.suffix != '.c' or not source.resolve().is_relative_to(source_root.resolve()):
            parser.error('application link input is not an R1 C source: ' + str(source))
        if not source.is_file() or digest(source) != unit['source_sha256']:
            parser.error('source changed since compilation: ' + str(source))
        unit_obj = Path(unit['object'])
        if not unit_obj.is_file() or digest(unit_obj) != unit['object_sha256']:
            parser.error('object changed since compilation: ' + str(unit_obj))
        objects.append(unit_obj)
        c_source_units += 1
    compiler = shutil.which('arm-none-eabi-gcc')
    if not compiler:
        parser.error('arm-none-eabi-gcc is required for the final link')
    nm = shutil.which('arm-none-eabi-nm')
    objcopy = shutil.which('arm-none-eabi-objcopy')
    if not nm or not objcopy:
        parser.error('arm-none-eabi-nm and objcopy are required to verify the image')
    symbols = subprocess.check_output([nm, '-S', '--defined-only',
                                       '--extern-only', *map(str, objects)], text=True)
    reset_defined = any(line.split()[-1] == 'Reset_Handler'
                        for line in symbols.splitlines() if line.split())
    vector_bytes = next((int(words[1], 16) for line in symbols.splitlines()
                         if (words := line.split()) and len(words) >= 4
                         and words[-1] == 'r1_application_vectors'), 0)
    # The pinned nRF52840 startup owns 128 vector words, including reserved
    # slots. A partial initial-SP cell cannot boot even if the linker succeeds.
    vector_complete = vector_bytes == 128 * 4
    if out.exists() and any(out.iterdir()):
        parser.error('output directory must be empty')
    out.mkdir(parents=True, exist_ok=True)
    layout = ROOT / 'r1/config-recovered/openr1_sdk.ld'
    registry_sources = [ROOT / 'r1/src/config/runtime' / name for name in
                        ('native_log_registry.ld', 'native_sdk_observers.ld',
                         'native_ble_observers.ld')]
    registry_scripts = []
    for source in registry_sources:
        target = out / ('final_' + source.name)
        final_registry_script(source, target, dynamic_log=source.name == 'native_log_registry.ld')
        registry_scripts.append(target)
    mdk = ROOT / 'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/modules/nrfx/mdk'
    elf = out / 'application.elf'
    command = [compiler, '-mcpu=cortex-m4', '-mthumb', '-mfpu=fpv4-sp-d16',
               '-mfloat-abi=hard', '-nostartfiles', '-Wl,--gc-sections',
               '-Wl,-Map=' + str(out / 'application.map'), '-L', str(mdk),
               *(item for script in registry_scripts for item in ('-T', str(script))),
               '-T', str(layout), '-o', str(elf), *map(str, objects)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    log = result.stdout + result.stderr
    (out / 'link.log').write_text(log)
    undefined = sorted(set(re.findall(r"undefined reference to [`']([^'`]+)'", log)))
    overflow = re.search(r"region [`']FLASH' overflowed by (\d+) bytes", log)
    map_text = (out / 'application.map').read_text() if (out / 'application.map').is_file() else ''
    archive_members = sorted(set(re.findall(r'(?m)^(\S+\.a\([^)]+\))', map_text)))
    flash_region = re.search(r'^FLASH\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)',
                             map_text, re.MULTILINE)
    flash_used = re.search(r'^\s*0x([0-9a-fA-F]+)\s+TotalFlashUsed =',
                           map_text, re.MULTILINE)
    flash_capacity = int(flash_region.group(2), 16) if flash_region else None
    total_flash_used = int(flash_used.group(1), 16) if flash_used else None
    total_flash_overflow = (max(0, total_flash_used - flash_capacity)
                            if flash_capacity is not None and total_flash_used is not None else None)
    ram_region = re.search(r'^RAM\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)',
                           map_text, re.MULTILINE)
    ram_origin = int(ram_region.group(1), 16) if ram_region else None
    ram_capacity = int(ram_region.group(2), 16) if ram_region else None
    def map_symbol(name):
        match = re.search(r'^\s*0x([0-9a-fA-F]+)\s+' + re.escape(name) +
                          r'\s*=', map_text, re.MULTILINE)
        return int(match.group(1), 16) if match else None
    bss_end = map_symbol('__bss_end__')
    heap_limit = map_symbol('__HeapLimit')
    stack_limit = map_symbol('__StackLimit')
    stack_top = map_symbol('__StackTop')
    ram_layout_valid = (None not in (ram_origin, ram_capacity, bss_end,
                                     heap_limit, stack_limit, stack_top) and
                        ram_origin <= bss_end <= heap_limit <= stack_limit < stack_top and
                        stack_top == ram_origin + ram_capacity and
                        stack_top - stack_limit >= 8192)
    vector_placement = re.search(r'^\s*0x([0-9a-fA-F]+)\s+r1_application_vectors\s*$',
                                 map_text, re.MULTILINE)
    vector_address = int(vector_placement.group(1), 16) if vector_placement else None
    vector_at_origin = vector_address == 0x27000
    link_valid = (result.returncode == 0 and not archive_members and
                  reset_defined and vector_complete and
                  vector_at_origin and total_flash_overflow == 0 and
                  ram_layout_valid)
    image = out / 'application.bin'
    image_bytes = None
    image_sha256 = None
    initial_sp = None
    reset_vector = None
    reset_address = None
    image_valid = False
    if link_valid:
        for line in subprocess.check_output([nm, '--defined-only', str(elf)], text=True).splitlines():
            fields = line.split()
            if len(fields) >= 3 and fields[-1] == 'Reset_Handler':
                reset_address = int(fields[0], 16)
        image_result = subprocess.run([objcopy, '-O', 'binary', str(elf), str(image)],
                                      capture_output=True, text=True)
        if image_result.returncode == 0 and image.is_file():
            image_bytes = image.stat().st_size
            if image_bytes >= 512:
                with image.open('rb') as stream:
                    initial_sp, reset_vector = struct.unpack('<II', stream.read(8))
            image_valid = (image_bytes <= flash_capacity and
                           image_bytes <= total_flash_used and
                           initial_sp == stack_top and reset_address is not None and
                           reset_vector == (reset_address | 1))
            if image_valid:
                image_sha256 = digest(image)
        if not image_valid:
            (out / 'image.log').write_text(image_result.stdout + image_result.stderr)
            image.unlink(missing_ok=True)
    linked = link_valid and image_valid
    if not linked:
        elf.unlink(missing_ok=True)
    receipt = {
        'schema': 1, 'linked': linked, 'reset_handler_defined': reset_defined,
        'vector_bytes': vector_bytes, 'vector_complete': vector_complete,
        'vector_flash_address': vector_address, 'vector_at_origin': vector_at_origin,
        'initial_sp': initial_sp, 'reset_vector': reset_vector,
        'reset_handler_address': reset_address, 'image_valid': image_valid,
        'image_path': str(image) if image_valid else None,
        'image_bytes': image_bytes, 'image_sha256': image_sha256,
        'returncode': result.returncode, 'report': str(report),
        'report_sha256': digest(report), 'manifest_sha256': device['manifest_sha256'],
        'composed_object_sha256': compose['sha256'],
        'individual_objects': len(objects),
        'participating_c_source_units': c_source_units,
        'compiler_version': subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
        'inputs_sha256': {str(p): digest(p) for p in
                          (layout, mdk / 'nrf_common.ld', *registry_sources,
                           *registry_scripts, *objects)},
        'argv': command, 'undefined_references': undefined,
        'archive_members': archive_members,
        'ld_region_overflow_bytes': int(overflow.group(1)) if overflow else None,
        'flash_capacity_bytes': flash_capacity,
        'total_flash_used_bytes': total_flash_used,
        'flash_overflow_bytes': total_flash_overflow,
        'ram_origin': ram_origin, 'ram_capacity_bytes': ram_capacity,
        'bss_end': bss_end, 'heap_limit': heap_limit,
        'stack_limit': stack_limit, 'stack_top': stack_top,
        'stack_reservation_bytes': (stack_top - stack_limit
                                    if stack_top is not None and stack_limit is not None else None),
        'ram_headroom_bytes': (stack_limit - heap_limit
                               if stack_limit is not None and heap_limit is not None else None),
        'ram_layout_valid': ram_layout_valid,
        'limits': 'The raw application region excludes SoftDevice, bootloader, settings and package metadata; source linkage does not establish stock byte identity or hardware boot.'
    }
    (out / 'report.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'linked': receipt['linked'], 'undefined_references': len(undefined),
                      'archive_members': len(archive_members),
                      'flash_overflow_bytes': receipt['flash_overflow_bytes'],
                      'ld_region_overflow_bytes': receipt['ld_region_overflow_bytes'],
                      'ram_layout_valid': ram_layout_valid,
                      'ram_headroom_bytes': receipt['ram_headroom_bytes'],
                      'reset_handler_defined': reset_defined,
                      'vector_bytes': vector_bytes, 'vector_at_origin': vector_at_origin,
                      'image_valid': image_valid, 'image_bytes': image_bytes,
                      'report': str(out / 'report.json')}))
    return 0 if linked else (result.returncode or 1)


if __name__ == '__main__':
    raise SystemExit(main())
