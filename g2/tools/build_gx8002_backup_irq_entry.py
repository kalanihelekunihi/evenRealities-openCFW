# SPDX-License-Identifier: MIT
"""Build the shared source IRQ architecture entry for backup SRAM on macOS."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32


def build():
    out = ROOT/'build/gx8002-backup-irq-entry'
    out.mkdir(exist_ok=True)
    source = ROOT/'components/shared/gx8002/runtime_gx8002_irq_compact_entry.S'
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags = ['-mcpu=ck804ef', '-mhard-float', '-mistack']
    subprocess.run([pre+'gcc', *flags, '-c', str(source), '-o', str(out/'entry.o')], check=True)
    (out/'entry.ld').write_text('SECTIONS { .text 0x10004880 : { *(.text.open_cfw_gx8002_irq_compact_entry) } }\nopen_cfw_gx8002_irq_table = 0x200173a8;\n')
    subprocess.run([pre+'ld', '-T', str(out/'entry.ld'), str(out/'entry.o'), '-o', str(out/'entry.elf')], check=True)
    elf = Elf32((out/'entry.elf').read_bytes(), 'backup IRQ')
    alloc = [s for s in elf.sections if s['flags'] & 2 and s['size']]
    assert len(alloc) == 1
    section = alloc[0]
    assert section['name'] == '.text' and section['address'] == 0x10004880
    assert not elf.relocations(section['index'])
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    payload = elf.contents(section)
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    assert len(payload) == 80 and payload == stock[0x3d1c0:0x3d210]
    (out/'entry.disassembly.txt').write_text(subprocess.check_output([pre+'objdump', '-d', str(out/'entry.elf')], text=True))
    report = {'source_sha256': sha(source.read_bytes()), 'flags': flags,
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'package_offset': 0x3d1c0, 'runtime_address': 0x10004880,
              'irq_table': 0x200173a8, 'byte_exact': True,
              'source_kind': 'architecture_assembly', 'source_admitted': False,
              'hardware_qualified': False}
    (ROOT/'docs/research/gx8002-backup-irq-entry-candidate.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
