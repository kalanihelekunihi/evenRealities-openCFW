#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build console candidates at recovered addresses; this does not admit them."""
import json
import subprocess
from pathlib import Path

from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]


def build(prefix=None, output=None):
    output = output or ROOT / 'build/gx8002-uart-console'
    output.mkdir(parents=True, exist_ok=True)
    prefix = (prefix or ROOT / 'build/csky-macos/install/bin') / 'csky-unknown-elf-'
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_console.c'
    flags = [f for f in FLAGS if f != '-O2'] + ['-Os', '-fno-inline']
    obj, linked = output / 'console-size.o', output / 'console.elf'
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    rows = [('uart_transmit', 0xc7d8, 20), ('uart_putc', 0xcb40, 36),
            ('console_putc', 0xcd7c, 20)]
    script = output / 'console.ld'
    script.write_text('SECTIONS {\n' + '\n'.join(
        f'.text.open_cfw_gx8002_{name} 0x{offset + 0x101f6a74:x} : '
        f'{{ *(.text.open_cfw_gx8002_{name}) }}' for name, offset, _ in rows
    ) + '\n}\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\n'
        'open_cfw_gx8002_console_port = 0x2002731c;\n')
    subprocess.run([str(prefix) + 'gcc', *flags, '-c', str(source), '-o', str(obj)], check=True)
    subprocess.run([str(prefix) + 'ld', '-T', str(script), str(obj), '-o', str(linked)], check=True)
    elf = Elf32(linked.read_bytes(), str(linked))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unresolved console dependency')
    sections = []
    for name, offset, envelope in rows:
        section = next(s for s in elf.sections if s['name'] == '.text.open_cfw_gx8002_' + name)
        payload = elf.contents(section)
        if len(payload) > envelope or elf.relocations(section['index']):
            raise ValueError('console placement does not fit or retains relocations')
        original = stock[offset:offset + envelope]
        sections.append({'symbol': 'open_cfw_gx8002_' + name, 'package_offset': offset,
                         'bytes': len(payload), 'stock_envelope_bytes': envelope,
                         'sha256': sha(payload), 'stock_sha256': sha(original),
                         'exact_stock_match': payload == original})
    report = {'source_sha256': sha(source.read_bytes()), 'flags': flags,
              'stock_image_sha256': IMAGE_SHA, 'sections': sections,
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Target behavioral comparison is pending.',
                         'Descriptor fields beyond MMIO pointer remain unreconstructed.']}
    (ROOT / 'docs/research/gx8002-uart-console-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
