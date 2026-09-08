#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile/link the application resume callback and require exact stock bytes."""
import json
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_app_resume.c'
LINKER = '''SECTIONS {
 .text.open_cfw_gx8002_app_resume 0x10208c7c : { *(.text.open_cfw_gx8002_app_resume) }
 open_cfw_gx8002_app_core_ops = 0x20026d38;
 /DISCARD/ : { *(.comment) *(.note*) }
}
'''


def verify(prefix, sdk, output):
    if subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip() != SDK_COMMIT:
        raise ValueError('SDK revision changed')
    name = 'lvp/app_core/lvp_app.h'
    digest = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD:' + name], text=True).strip()
    header = authenticated_blob(sdk / name, digest)
    dependency = 'lvp/app_core/lvp_app_core.h'
    dep_digest = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD:' + dependency], text=True).strip()
    dep_header = authenticated_blob(sdk / dependency, dep_digest)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (output / 'setter.ld').write_text(LINKER)
    obj = output / 'setter.o'
    linked = output / 'setter.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *FLAGS, '-fno-shrink-wrap', '-I', str(output),
                    '-I', str(sdk / 'lvp/app_core'), '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(output / 'setter.ld'),
                    str(obj), '-o', str(linked)], check=True)
    elf = Elf32(linked.read_bytes(), str(linked))
    sections = [s for s in elf.sections if s['flags'] & 4 and s['size']]
    if len(sections) != 1 or sections[0]['name'] != '.text.open_cfw_gx8002_app_resume':
        raise ValueError('unexpected linked executable section')
    section = sections[0]
    payload = elf.contents(section)
    if payload != stock[0x12208:0x12224] or elf.relocations(section['index']):
        raise ValueError('linked setter differs from stock')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unresolved setter dependency')
    report = {'symbol': 'open_cfw_gx8002_app_resume', 'source_sha256': sha(SOURCE.read_bytes()),
              'compile_flags': [*FLAGS, '-fno-shrink-wrap'], 'linker_script_sha256': sha(LINKER.encode()),
              'sdk_commit': SDK_COMMIT,
              'upstream_header': {'path': name, 'git_blob': digest, 'sha256': sha(header)},
              'dependency_header': {'path': dependency, 'git_blob': dep_digest, 'sha256': sha(dep_header)},
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'stock_occurrences': [{'symbol': 'open_cfw_gx8002_app_resume', 'package_offset': 0x12208,
                                     'bytes': 28, 'sha256': sha(payload), 'region': 'image_a_xip_text'}],
              'resolved_data_symbol': {'symbol': 'open_cfw_gx8002_app_core_ops', 'address': '0x20026d38'},
              'source_admitted': True, 'hardware_qualified': False,
              'limits': ['Application pointer and callback target remain runtime-owned data.',
                         'Exact linked bytes corroborate the existing XIP translation, not hardware boot qualification.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'build/csky-macos/install/bin',
                           ROOT / 'build/upstream-nationalchip-lvp-kws',
                           ROOT / 'build/gx8002-app-core'), indent=2))
