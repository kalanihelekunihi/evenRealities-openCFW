# SPDX-License-Identifier: MIT
"""Build the recovered board pin initializer using the native macOS C-SKY toolchain."""
import json
import subprocess

from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha, SDK_COMMIT, authenticated_blob
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

BINDINGS = {'open_cfw_gx8002_padmux_init':0x10206630,
            'open_cfw_gx8002_padmux_check':0x102065b8,
            'open_cfw_gx8002_gpio_set_direction':0x10205f24,
            'open_cfw_gx8002_printf':0x10206c24,
            'open_cfw_gx8002_board_pin_setup':0x1020681c}


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    headers={}
    for rel in ('include/driver/gx_padmux.h','include/driver/gx_gpio.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=authenticated_blob(sdk/rel,blob)
        headers[rel]={'blob':blob,'sha256':sha(data)}
    symbol = 'open_cfw_gx8002_board_pin_initialize'
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_board_pin_initialize.c'
    out = ROOT / 'build/gx8002-board'
    out.mkdir(parents=True, exist_ok=True)
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    stem = out / 'board-pin-initialize-candidate'
    flags = ['-Os', *FLAGS[1:], '-fno-shrink-wrap']
    subprocess.run([prefix + 'gcc', *flags, '-isystem', str(ROOT/'build/upstream-nationalchip-lvp-kws/include'), '-c', str(source),
                    '-o', str(stem.with_suffix('.o'))], check=True)
    script = stem.with_suffix('.ld')
    script.write_text('SECTIONS { .text 0x102068a0 : { *(.text.' + symbol + ') } }\n' +
                      ''.join('%s = %#x;\n' % item for item in BINDINGS.items()))
    target = stem.with_suffix('.elf')
    subprocess.run([prefix + 'ld', '-T', str(script), str(stem.with_suffix('.o')),
                    '-o', str(target)], check=True)
    elf = Elf32(target.read_bytes(), str(target))
    section = next(s for s in elf.sections if s['name'] == '.text')
    payload = elf.contents(section)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA or elf.relocations(section['index']):
        raise ValueError('Board pin setup stock/link mismatch')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('Unresolved board pin initializer symbol')
    stem.with_suffix('.disassembly.txt').write_text(subprocess.check_output(
        [prefix + 'objdump', '-d', str(target)], text=True))
    report = {'sdk_commit':SDK_COMMIT,'headers':headers,'symbol': symbol, 'section_name': '.text', 'bindings': BINDINGS,
              'flags': flags, 'source_sha256': sha(source.read_bytes()),
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'package_offset': 0xfe2c, 'stock_envelope_bytes': 104,
              'stock_sha256': sha(stock[0xfe2c:0xfe94]), 'fits': len(payload) <= 104,
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Build only. Guard state, helper transactions, ABI and diagnostic source data need qualification.']}
    (ROOT / 'docs/research/gx8002-board-pin-initialize-candidate.json').write_text(
        json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
