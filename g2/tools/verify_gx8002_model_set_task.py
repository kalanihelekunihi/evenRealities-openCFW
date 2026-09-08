#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile/link the saved-task setter and require exact stock bytes."""
import json
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_model_set_task.c'
LINKER = '''SECTIONS {
 .text.LvpSetSnpuTask 0x10208c14 : { *(.text.LvpSetSnpuTask) }
 open_cfw_gx8002_memcpy = 0x10025738;
 /DISCARD/ : { *(.comment) *(.note*) }
}
'''


def verify(prefix, sdk, output):
    if subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip() != SDK_COMMIT:
        raise ValueError('SDK revision changed')
    name = 'include/driver/gx_snpu.h'
    digest = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD:' + name], text=True).strip()
    header = authenticated_blob(sdk / name, digest)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (output / 'setter.ld').write_text(LINKER)
    obj = output / 'setter.o'
    linked = output / 'setter.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *FLAGS, '-I', str(output),
                    '-I', str(sdk / 'include'), '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(output / 'setter.ld'),
                    str(obj), '-o', str(linked)], check=True)
    elf = Elf32(linked.read_bytes(), str(linked))
    sections = [s for s in elf.sections if s['flags'] & 4 and s['size']]
    if len(sections) != 1 or sections[0]['name'] != '.text.LvpSetSnpuTask':
        raise ValueError('unexpected linked executable section')
    section = sections[0]
    payload = elf.contents(section)
    if payload != stock[0x121a0:0x121b4] or elf.relocations(section['index']):
        raise ValueError('linked setter differs from stock')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unresolved setter dependency')
    report = {'symbol': 'LvpSetSnpuTask', 'source_sha256': sha(SOURCE.read_bytes()),
              'compile_flags': FLAGS, 'linker_script_sha256': sha(LINKER.encode()),
              'sdk_commit': SDK_COMMIT,
              'upstream_header': {'path': name, 'git_blob': digest, 'sha256': sha(header)},
              'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
              'stock_occurrences': [{'symbol': 'LvpSetSnpuTask', 'package_offset': 0x121a0,
                                     'bytes': 20, 'sha256': sha(payload), 'region': 'image_a_xip_text'}],
              'resolved_source_dependency': {'symbol': 'open_cfw_gx8002_memcpy',
                                             'runtime_address': '0x10025738', 'package_offset': '0x1774c'},
              'source_admitted': True, 'hardware_qualified': False,
              'limits': ['Experimental hybrid requires the recovered memcpy at its original entry.',
                         'Exact linked bytes corroborate the existing XIP translation, not hardware boot qualification.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'build/csky-macos/install/bin',
                           ROOT / 'build/upstream-nationalchip-lvp-kws',
                           ROOT / 'build/gx8002-model-set-task'), indent=2))
