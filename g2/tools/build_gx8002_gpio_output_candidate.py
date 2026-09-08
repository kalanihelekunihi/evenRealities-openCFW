#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile GPIO direction/level C using the authenticated SDK interface."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-board'
    evidence = {}
    for name, rel in (('oracle', 'drivers_lib/gpio/gpio_mini.o'), ('header', 'include/driver/gx_gpio.h')):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + rel], text=True).strip()
        data = authenticated_blob(sdk / rel, blob)
        evidence[name] = {'path': rel, 'blob': blob, 'sha256': sha(data)}
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_gpio_output.c'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    flags = ['-Os', *FLAGS[1:]]
    obj = out / 'gpio-output-candidate.o'
    subprocess.run([pre + 'gcc', *flags, '-I' + str(sdk / 'include'), '-c', str(source), '-o', str(obj)], check=True)
    rows = [('direction', 0xf4b0, 100), ('level', 0xf514, 44)]
    script = out / 'gpio-output-candidate.ld'
    script.write_text('SECTIONS {\n' + ''.join(f'.text.{name} {offset+0x101f6a74:#x} : {{ *(.text.open_cfw_gx8002_gpio_set_{name}) }}\n' for name, offset, size in rows) + '}\n')
    path = out / 'gpio-output-candidate.elf'
    subprocess.run([pre + 'ld', '-T', str(script), str(obj), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), str(path))
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA or any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('GPIO output stock/link authentication')
    functions = []
    for name, offset, size in rows:
        sec = next(s for s in elf.sections if s['name'] == '.text.' + name)
        payload = elf.contents(sec)
        if elf.relocations(sec['index']):
            raise ValueError('GPIO output relocation')
        functions.append({'symbol': 'open_cfw_gx8002_gpio_set_' + name, 'section_name': sec['name'],
                          'package_offset': offset, 'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
                          'stock_envelope_bytes': size, 'stock_sha256': sha(stock[offset:offset+size]), 'fits': len(payload) <= size})
    (out / 'gpio-output-candidate.disassembly.txt').write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    report = {'sdk_commit': SDK_COMMIT, **evidence, 'source_sha256': sha(source.read_bytes()), 'flags': flags,
              'functions': functions, 'source_admitted': False, 'limits': ['Candidate compilation only. Ordered MMIO and input/ABI target qualification required. No SDK object linked.']}
    (ROOT / 'docs/research/gx8002-gpio-output-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
