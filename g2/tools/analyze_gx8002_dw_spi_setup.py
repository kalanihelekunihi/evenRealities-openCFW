#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Relocate an authenticated SDK oracle for comparison only, never firmware input."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32


def analyze():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    relative = 'drivers_lib/spi/dw_spi/spi_master_v3.o'
    blob = '600d763a219007e2af7b5006989d44984abf0861'
    data = authenticated_blob(sdk / relative, blob)
    obj = Elf32(data, relative)
    section = next(s for s in obj.sections if s['name'] == '.text.dw_spi_setup')
    relocations = obj.relocations(section['index'])
    if relocations != [{'offset': 50, 'symbol': 31, 'type': 19, 'addend': 0},
                       {'offset': 108, 'symbol': 3, 'type': 1, 'addend': 0}]:
        raise ValueError('Unexpected setup relocations')
    out = ROOT / 'build/gx8002-board'
    script = out / 'dw-spi-setup-oracle.ld'
    script.write_text('SECTIONS { .text 0x10206190 : { KEEP(*(.text.dw_spi_setup)) } .bss 0x20027ae0 : { *(.bss) } }\ngx_clock_get_module_frequence = 0x10025210;\n')
    target = out / 'dw-spi-setup-oracle.elf'
    subprocess.run([str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-ld'),
                    '--gc-sections', '-T', str(script), str(sdk / relative), '-o', str(target)], check=True)
    linked = Elf32(target.read_bytes(), str(target))
    text = next(s for s in linked.sections if s['name'] == '.text')
    payload = linked.contents(text)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA or payload != stock[0xf71c:0xf790]:
        raise ValueError('Full relocated setup mismatch')
    return {'sdk_commit': SDK_COMMIT, 'object': relative, 'blob': blob,
            'object_sha256': sha(data), 'package_offset': 0xf71c,
            'runtime_address': 0x10206190, 'bytes': len(payload),
            'sha256': sha(payload), 'full_relocated_section_match': True,
            'bindings': {'gx_clock_get_module_frequence': 0x10025210, '.bss': 0x20027ae0},
            'source_admitted': False,
            'limits': ['SDK object linked only as a comparison oracle, never a firmware provider. C reconstruction and target qualification remain required.']}


if __name__ == '__main__':
    report = analyze()
    (ROOT / 'docs/research/gx8002-dw-spi-setup-attribution.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
