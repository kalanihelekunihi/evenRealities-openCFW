#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify the recovered analog config-update-enable leaf against stock bytes.

gx_analog_config_update_enable has no upstream .c body in the pinned SDK
checkout (only the compiled drivers_lib/misc/grus/misc.o and the misc.h
declaration/doc-comment). The candidate's compiled section is checked for
exact byte equality against the authenticated firmware envelope at package
offset 0x2A8C (UART boot stage 2), which independently confirms the
decompiled function this file's source comment describes.
"""
import json
import subprocess
from pathlib import Path

from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, IMAGE, IMAGE_SHA, authenticated_blob, sha
from verify_gx8002_logging import check_paths
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_analog_config_update_enable.c'
SYMBOL = 'open_cfw_gx8002_analog_config_update_enable'
PACKAGE_OFFSET = 0x2A8C
ENVELOPE_BYTES = 20


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = output or ROOT / 'build/gx8002-analog-config-update-enable'
    out.mkdir(parents=True, exist_ok=True)
    rel = 'include/driver/misc.h'
    blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', f'{SDK_COMMIT}:{rel}'], text=True).strip()
    header = authenticated_blob(sdk / rel, blob)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    obj = out / 'analog-config-update-enable.o'
    subprocess.run([pre + 'gcc', *FLAGS, '-c', str(SOURCE), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name'] == '.text.' + SYMBOL)
    if not section['flags'] & 4 or elf.relocations(section['index']):
        raise ValueError('analog config-update-enable section/relocations')
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('unexpected external symbol')
    payload = elf.contents(section)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('analog config-update-enable stock identity')
    envelope = stock[PACKAGE_OFFSET:PACKAGE_OFFSET + ENVELOPE_BYTES]
    if payload != envelope:
        raise ValueError('analog config-update-enable compiled bytes differ from stock envelope')
    (out / 'analog-config-update-enable.disassembly.txt').write_text(
        subprocess.check_output([pre + 'objdump', '-dr', str(obj)], text=True))
    row = {'symbol': SYMBOL, 'section_name': section['name'], 'compiled_bytes': len(payload),
           'compiled_sha256': sha(payload), 'ownership_kind': 'compiled_c',
           'stock_occurrences': [{'symbol': SYMBOL, 'package_offset': PACKAGE_OFFSET,
                                   'bytes': ENVELOPE_BYTES, 'sha256': sha(envelope),
                                   'region': 'boot_stage2'}]}
    return {'functions': [row], 'sdk_commit': SDK_COMMIT,
            'header': {'path': rel, 'blob': blob, 'sha256': sha(header)},
            'source_sha256': sha(SOURCE.read_bytes()), 'verifier_sha256': sha(Path(__file__).read_bytes()),
            'flags': FLAGS, 'source_admitted': True, 'hardware_qualified': False,
            'policy': 'Exact byte match against the authenticated UART boot stage 2 envelope.',
            'limits': ['No SDK .c body is available; the object-code match and the misc.h '
                       'declaration/doc-comment are the only upstream evidence.',
                       'PMU/analog trim hardware behavior is not qualified.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-analog-config-update-enable-verification.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('Qualified analog config-update-enable leaf')
