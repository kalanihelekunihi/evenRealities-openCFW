#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build recovered startup BSS clear on native macOS; no admission implied."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, sha, authenticated_blob
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT
from verify_gx8002_analog_source import FLAGS


def build():
    sdk = ROOT/'build/upstream-nationalchip-lvp-kws'
    relative = 'arch/cpu/csky/ck804/start.S'
    blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', f'{SDK_COMMIT}:{relative}'], text=True).strip()
    upstream = authenticated_blob(sdk/relative, blob)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock hash mismatch')
    output = ROOT/'build/gx8002-clear-bss'
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT/'components/shared/gx8002/runtime_gx8002_clear_bss.c'
    prefix = ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    subprocess.run([str(prefix)+'gcc', '-Os', *FLAGS[1:], '-c', str(source),
                    '-o', str(output/'clear.o')], check=True)
    script = output/'clear.ld'
    script.write_text('''SECTIONS {
.text 0x10023528 : { *(.text.open_cfw_gx8002_clear_bss) }
}
open_cfw_gx8002_bss_start = 0x20026d80;
open_cfw_gx8002_bss_end = 0x2002ecec;
''')
    linked = output/'clear.elf'
    subprocess.run([str(prefix)+'ld', '-T', str(script), str(output/'clear.o'),
                    '-o', str(linked)], check=True)
    elf = Elf32(linked.read_bytes(), str(linked))
    section = next(s for s in elf.sections if s['name'] == '.text')
    if section['size'] > 36 or elf.relocations(section['index']) or any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('invalid clear candidate')
    disassembly = subprocess.check_output([str(prefix)+'objdump', '-d', str(linked)], text=True)
    (output/'clear.disassembly.txt').write_text(disassembly)
    report = {'sdk_commit': SDK_COMMIT, 'upstream_start_sha256': sha(upstream),
              'source_sha256': sha(source.read_bytes()), 'compiled_bytes': section['size'],
              'compiled_sha256': sha(elf.contents(section)), 'stock_package_offset': 0x1553c,
              'stock_envelope_bytes': 36, 'stock_sha256': sha(stock[0x1553c:0x15560]),
              'bss_start': 0x20026d80, 'bss_end': 0x2002ecec, 'cleared_bytes': 0x7f6c,
              'source_admitted': False, 'limits': ['Target trace comparison remains required.']}
    (ROOT/'docs/research/gx8002-clear-bss-candidate.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
