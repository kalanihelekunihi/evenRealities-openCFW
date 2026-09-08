#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link recovered IRQ registration and authenticated upstream VIC wrappers."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_csi_source import HEADERS
from link_gx8002_uart_console import ROOT


def link():
    output = ROOT / 'build/gx8002-irq'
    output.mkdir(exist_ok=True)
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    prefix = ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-'
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_irq.c'
    dependencies = []
    for name in (*HEADERS, 'LICENSE'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + name], text=True).strip()
        dependencies.append({'path': name, 'git_blob': blob, 'sha256': sha(authenticated_blob(sdk / name, blob))})
    flags = ['-Os', *FLAGS[1:], '-fno-shrink-wrap']
    command = [str(prefix) + 'gcc', *flags]
    for directory in ('arch/soc/grus/include', 'include/utility', 'include/utility/libc'):
        command += ['-isystem', str(sdk / directory)]
    obj = output / 'irq.o'
    subprocess.run([*command, '-c', str(source), '-o', str(obj)], check=True)
    rows = [('irq_enable', 0x174c0, 28), ('irq_disable', 0x174dc, 28), ('request_irq', 0x17550, 36),
            ('irq_save', 0x17574, 12), ('irq_restore', 0x17580, 8),
            ('irq_restore_enabled', 0x174f8, 24), ('irq_save_disable', 0x17520, 40)]
    script = output / 'irq.ld'
    script.write_text('SECTIONS {\n' + ''.join(
        f'.text.open_cfw_gx8002_{name} {offset + 0x1000dfec:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n'
        for name, offset, size in rows) + '}\nopen_cfw_gx8002_irq_table = 0x20026ef4;\nopen_cfw_gx8002_irq_saved_enable = 0x20026eec;\n')
    linked = output / 'irq.elf'
    subprocess.run([str(prefix) + 'ld', '-T', str(script), str(obj), '-o', str(linked)], check=True)
    elf = Elf32(linked.read_bytes(), str(linked))
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA: raise ValueError('stock identity changed')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()): raise ValueError('unresolved IRQ symbol')
    sections = []
    for name, offset, size in rows:
        section = next(s for s in elf.sections if s['name'] == '.text.open_cfw_gx8002_' + name)
        payload = elf.contents(section)
        if len(payload) > size or section['address'] != offset + 0x1000dfec or elf.relocations(section['index']): raise ValueError('IRQ placement failure')
        if name in ('irq_save', 'irq_restore'):
            expected_size = 10 if name == 'irq_save' else 6
            if (len(payload) != expected_size or payload != stock[offset:offset+expected_size]
                    or payload[-2:] != b'\x3c\x78' or stock[offset+expected_size:offset+size] != b'\0\0'):
                raise ValueError('upstream PSR instruction body or trailing padding changed')
        sections.append({'symbol': 'open_cfw_gx8002_' + name, 'package_offset': offset, 'compiled_bytes': len(payload), 'compiled_sha256': sha(payload), 'stock_envelope_bytes': size, 'stock_sha256': sha(stock[offset:offset+size]), 'byte_exact': payload == stock[offset:offset+size], 'compiled_body_byte_exact': payload == stock[offset:offset+len(payload)]})
    report = {'sdk_commit': SDK_COMMIT, 'upstream_dependencies': dependencies, 'source_sha256': sha(source.read_bytes()), 'flags': flags, 'sections': sections, 'source_admitted': False, 'limits': ['Instruction behavior comparison pending.', 'IRQ table storage and generic dispatcher remain retained.', 'No hardware qualification.']}
    (ROOT / 'docs/research/gx8002-irq-linked-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    return report

if __name__ == '__main__': print(json.dumps(link(), indent=2))
