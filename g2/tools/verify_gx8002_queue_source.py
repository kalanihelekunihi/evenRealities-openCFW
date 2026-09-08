#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate and compile upstream queue C; identify exact stock functions."""
import json
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = [('LvpQueueInit', 0x10528, 20), ('LvpQueueIsEmpty', 0x10588, 10), ('LvpQueueIsFull', 0x10594, 24)]


def verify(prefix, sdk, output):
    if subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip() != SDK_COMMIT:
        raise ValueError('SDK revision changed')
    records = []
    for name in ('lvp/common/lvp_queue.c', 'lvp/common/lvp_queue.h', 'include/lvp_attr.h'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD:' + name], text=True).strip()
        records.append({'path': name, 'git_blob': blob, 'sha256': sha(authenticated_blob(sdk / name, blob))})
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'stdio.h').write_text('/* This translation unit uses no stdio declarations. */\n')
    (output / 'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    obj = output / 'queue.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *FLAGS, '-I', str(output),
                    '-I', str(sdk / 'include'), '-c', str(sdk / 'lvp/common/lvp_queue.c'), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    functions = []
    for name, offset, size in FUNCTIONS:
        section = next(s for s in elf.sections if s['name'] == '.text.' + name)
        payload = elf.contents(section)
        if payload != stock[offset:offset + size] or elf.relocations(section['index']):
            raise ValueError('queue source differs from stock: ' + name)
        functions.append({'symbol': name, 'compiled_bytes': size, 'compiled_sha256': sha(payload),
                          'stock_occurrences': [{'symbol': name, 'package_offset': offset,
                                                 'bytes': size, 'sha256': sha(payload), 'region': 'image_a_xip_text'}]})
    report = {'sdk_commit': SDK_COMMIT, 'upstream_files': records, 'compile_flags': FLAGS,
              'configuration': {'CONFIG_ARCH_GRUS': 1, 'stdio_header': 'empty; no stdio declarations used'},
              'functions': functions, 'source_admitted': True,
              'limits': ['Only three named sections match; other compiled queue functions are not qualified.',
                         'Queue callers must supply positive, consistent dimensions; concurrent access is not synchronized.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'build/csky-macos/install/bin', ROOT / 'build/upstream-nationalchip-lvp-kws',
                           ROOT / 'build/gx8002-queue'), indent=2))
