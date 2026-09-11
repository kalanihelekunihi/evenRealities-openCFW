# SPDX-License-Identifier: MIT
"""Build the recovered channel lookup using the native macOS C-SKY toolchain."""
import json
import subprocess

from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

BINDINGS = {}


def build():
    symbol = 'open_cfw_gx8002_channel_lookup'
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_channel_lookup.c'
    out = ROOT / 'build/gx8002-board'
    out.mkdir(parents=True, exist_ok=True)
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    stem = out / 'channel-lookup-candidate'
    flags = ['-Os', *FLAGS[1:], '-fno-shrink-wrap']
    subprocess.run([prefix + 'gcc', *flags, '-c', str(source),
                    '-o', str(stem.with_suffix('.o'))], check=True)
    script = stem.with_suffix('.ld')
    script.write_text('SECTIONS { .text 0x10207ac0 : { *(.text.' + symbol + ') } }\n' +
                      ''.join('%s = %#x;\n' % item for item in BINDINGS.items()))
    target = stem.with_suffix('.elf')
    subprocess.run([prefix + 'ld', '-T', str(script), str(stem.with_suffix('.o')),
                    '-o', str(target)], check=True)
    elf = Elf32(target.read_bytes(), str(target))
    section = next(s for s in elf.sections if s['name'] == '.text')
    payload = elf.contents(section)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA or elf.relocations(section['index']):
        raise ValueError('Channel lookup stock/link mismatch')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('Unresolved channel lookup symbol')
    stem.with_suffix('.disassembly.txt').write_text(subprocess.check_output(
        [prefix + 'objdump', '-d', str(target)], text=True))
    report = {'symbol': symbol, 'section_name': '.text', 'bindings': BINDINGS,
              'flags': flags, 'source_sha256': sha(source.read_bytes()),
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'package_offset': 0x1104c, 'stock_envelope_bytes': 28,
              'stock_sha256': sha(stock[0x1104c:0x11068]), 'fits': len(payload) <= 28,
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Build only. Guard state, helper transactions, ABI and diagnostic source data need qualification.']}
    (ROOT / 'docs/research/gx8002-channel-lookup-candidate.json').write_text(
        json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
