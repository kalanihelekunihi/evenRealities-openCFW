#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate and compile upstream Tinyprintf, without source admission."""
import json
import shlex
import subprocess
from analyze_gx8002_upstream_objects import SDK_COMMIT, IMAGE, IMAGE_SHA, authenticated_blob, sha
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    output = ROOT / 'build/gx8002-tinyprintf'
    output.mkdir(parents=True, exist_ok=True)
    if subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip() != SDK_COMMIT:
        raise ValueError('SDK commit changed')
    config = output / 'autoconf.h'
    config.write_text('/* Source-authored configuration: no optional long support. */\n')
    compiler = ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-gcc'
    flags = ['-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin',
             '-ffunction-sections', '-fdata-sections', '-fwrapv']
    source = sdk / 'utility/libc/tinyprintf.c'
    command = [str(compiler), *flags, '-I', str(output), '-I', str(sdk / 'include/utility/libc')]
    dependencies = subprocess.check_output([*command, '-MM', str(source)], text=True)
    paths = shlex.split(dependencies.split(':', 1)[1].replace('\\\n', ' '))
    records = []
    for path in paths:
        from pathlib import Path
        path = Path(path)
        if path == config:
            continue
        relative = path.relative_to(sdk).as_posix()
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', f'{SDK_COMMIT}:{relative}'], text=True).strip()
        data = authenticated_blob(path, blob)
        records.append({'path': relative, 'git_blob': blob, 'sha256': sha(data)})
    obj = output / 'tinyprintf.o'
    subprocess.run([*command, '-c', str(source), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    sections = [{'section': s['name'], 'bytes': s['size'], 'sha256': sha(elf.contents(s)),
                 'relocations': len(elf.relocations(s['index']))}
                for s in elf.sections if s['flags'] & 4 and s['size']]
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock image changed')
    # Recovered entry boundaries; matching sizes alone do not establish behavior.
    entries = {'ui2a': (0xfeac, 120), 'putf': (0xff24, 24),
               'putchw': (0xff3c, 212), 'tfp_format': (0x10010, 416)}
    for row in sections:
        name = row['section'].removeprefix('.text.')
        if name in entries:
            offset, envelope = entries[name]
            row.update(package_offset=offset, stock_envelope_bytes=envelope,
                       stock_sha256=sha(stock[offset:offset + envelope]),
                       fits_original_envelope=row['bytes'] <= envelope)
    report = {'sdk_commit': SDK_COMMIT, 'upstream_files': records, 'compile_flags': flags,
              'configuration_sha256': sha(config.read_bytes()), 'sections': sections,
              'stock_image_sha256': IMAGE_SHA,
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Unmodified upstream compilation only; target behavioral and placement qualification pending.',
                         'Optional long support disabled; stock configuration must be confirmed.',
                         'All external calls and helper routines still require qualification.']}
    (ROOT / 'docs/research/gx8002-tinyprintf-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
