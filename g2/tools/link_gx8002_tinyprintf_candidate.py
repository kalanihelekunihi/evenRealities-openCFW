#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link upstream formatter candidates at recovered entries, without admission."""
import json
import subprocess
from build_gx8002_tinyprintf_padding import candidate
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE, sha
from link_gx8002_uart_console import ROOT


def link():
    evidence = candidate()
    output = ROOT / 'build/gx8002-tinyprintf'
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    prefix = ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-'
    source = (output / 'tinyprintf-padding.c').read_text()
    declaration = 'static void ui2a(unsigned int num, struct param *p)'
    if source.count(declaration) != 1:
        raise ValueError('upstream ui2a declaration changed')
    attribute = '__attribute__((optimize("no-guess-branch-probability", "no-if-conversion")))\n'
    source = source.replace(declaration, attribute + declaration)
    path = output / 'tinyprintf-placement.c'
    path.write_text(source)
    obj = output / 'tinyprintf-placement.o'
    subprocess.run([str(prefix) + 'gcc', *evidence['compile_flags'], '-I', str(output),
                    '-I', str(sdk / 'utility/libc'), '-I', str(sdk / 'include/utility/libc'),
                    '-c', str(path), '-o', str(obj)], check=True)
    entries = [('ui2a', 0xfeac, 120), ('putf', 0xff24, 24),
               ('putchw', 0xff3c, 212), ('tfp_format', 0x10010, 416)]
    script = output / 'formatter.ld'
    script.write_text('SECTIONS {\n' + '\n'.join(
        f'.text.{name} 0x{offset + 0x101f6a74:x} : {{ *(.text.{name}) }}'
        for name, offset, size in entries) +
        '\n/DISCARD/ : { *(.text.vfprintf) *(.text.fprintf) *(.text.printf_) '
        '*(.text.vsnprintf_) *(.text.snprintf_) }\n}\nfputc = 0x10206c70;\n')
    linked = output / 'formatter.elf'
    subprocess.run([str(prefix) + 'ld', '-T', str(script), str(obj), '-o', str(linked)], check=True)
    elf = Elf32(linked.read_bytes(), str(linked))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unresolved formatter symbol')
    rows = []
    stock = IMAGE.read_bytes()
    for name, offset, size in entries:
        section = next(s for s in elf.sections if s['name'] == '.text.' + name)
        payload = elf.contents(section)
        if len(payload) > size or elf.relocations(section['index']):
            raise ValueError('formatter overlap or relocation')
        original = stock[offset:offset + size]
        rows.append({'symbol': name, 'package_offset': offset, 'compiled_bytes': len(payload),
                     'compiled_sha256': sha(payload), 'stock_envelope_bytes': size,
                     'stock_sha256': sha(original), 'byte_exact': payload == original})
    report = {'padding_evidence': evidence, 'ui2a_attribute': attribute.strip(),
              'source_sha256': sha(path.read_bytes()), 'functions': rows,
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Linked placement only; target behavior remains unqualified.',
                         'fputc entry resolves to recovered console port but is not included in this ELF.',
                         'Unqualified printf and memory-stream wrappers are discarded, not replaced.']}
    (ROOT / 'docs/research/gx8002-tinyprintf-linked-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(link(), indent=2))
