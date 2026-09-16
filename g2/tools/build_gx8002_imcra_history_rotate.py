# SPDX-License-Identifier: MIT
"""Compile a development-only IMCRA periodic history rotation on native macOS."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    out = ROOT / 'build/gx8002-imcra-history-rotate'
    out.mkdir(exist_ok=True)
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_imcra_history_rotate.c'
    cluster = ROOT / 'build/gx8002-backup-startup-cluster/cluster.elf'
    elf = Elf32(cluster.read_bytes(), 'startup')
    symbols = {s['name']: s for s in elf.symbols()}
    names = ['open_cfw_gx8002_memcpy']
    bindings = {}
    for name in names:
        symbol = symbols[name]
        assert symbol['section'] not in (0, 0xfff1), name
        bindings[name] = symbol['value']
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre + 'gcc', '-Os', *FLAGS[1:], '-c', str(source), '-o', str(out / 'prepare.o')], check=True)
    script = 'SECTIONS { .prepare 0x100167b8 : { *(.text*) } }\n'
    script += ''.join(f'{name} = 0x{address:x};\n' for name, address in bindings.items())
    (out / 'prepare.ld').write_text(script)
    target = out / 'prepare.elf'
    subprocess.run([pre + 'ld', '-T', str(out / 'prepare.ld'),
                    str(out / 'prepare.o'), '-o', str(target)], check=True)
    built = Elf32(target.read_bytes(), 'prepare')
    assert not any(s['name'] and s['section'] == 0 for s in built.symbols())
    assert not any(built.relocations(s['index']) for s in built.sections)
    sections = [s for s in built.sections if s['flags'] & 2 and s['size']]
    assert len(sections) == 1
    (out / 'prepare.disassembly.txt').write_text(subprocess.check_output(
        [pre + 'objdump', '-d', str(target)], text=True))
    report = {'source_sha256': sha(source.read_bytes()),
              'startup_sha256': sha(cluster.read_bytes()),
              'bytes': sections[0]['size'], 'helper_bindings': bindings,
              'source_admitted': False, 'startup_integrated': False,
              'limits': ['Development fragment only; not a complete processing function.',
                         'Helpers resolved by address, not included in this standalone ELF.',
                         'Decoded equivalence and helper mutation verification pending.',
                         'No placement, complete firmware or hardware qualification.']}
    (ROOT / 'docs/research/gx8002-imcra-history-rotate.json').write_text(
        json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
