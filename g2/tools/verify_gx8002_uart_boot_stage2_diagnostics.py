#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile UART-boot stage-2 diagnostic strings and authenticate them against
both the stock codec image and the pinned NationalChip/lvp_kws printf call
sites their text is taken from.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, sha, authenticated_blob
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_logging import check_paths

ROOT = Path(__file__).resolve().parents[1]

# (symbol_suffix, package_offset, upstream_relative_path, printf_call_regex)
ROWS = [
    ('cpu_exception', 0x82ec, 'arch/soc/grus/trap_c.c', r'printf\("(CPU Exception : %u)"'),
    ('vreg_dump', 0x8300, 'arch/soc/grus/trap_c.c', r'printf\("(vr%d: %08x\\t)"'),
    ('reg_dump', 0x830c, 'arch/soc/grus/trap_c.c', r'printf\("(r%d: %08x\\t)"'),
    ('epsr', 0x8318, 'arch/soc/grus/trap_c.c', r'printf\("(epsr: %8x\\n)"'),
    ('epc', 0x8324, 'arch/soc/grus/trap_c.c', r'printf\("(epc : %8x\\n)"'),
    ('pin_set_error', 0x834c, 'boards/nationalchip/grus_bk32887_1v/misc_board.c',
     r'printf\("(pin %d set error!\\n)"'),
]


def upstream_literal(sdk, relative, pattern, cache=None):
    if cache is None:
        cache = {}
    if relative not in cache:
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + relative],
                                        text=True).strip()
        cache[relative] = authenticated_blob(sdk / relative, blob).decode('utf-8')
    match = re.search(pattern, cache[relative])
    if not match:
        raise ValueError('upstream literal not found: ' + pattern)
    # Undo C source escaping for the two-character sequences used here.
    return match[1].encode().decode('unicode_escape').encode('latin1')


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock changed')
    head = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip()
    if head != SDK_COMMIT:
        raise ValueError('SDK commit differs from the reviewed inspection baseline')

    out = ROOT / 'build/gx8002-board'
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_boot_stage2_diagnostics.c'
    obj = out / 'uart-boot-stage2-diagnostics.o'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([pre + 'gcc', *FLAGS, '-c', str(source), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))

    allowed = {'.rodata.open_cfw_gx8002_uart_boot_stage2_str_' + row[0] for row in ROWS}
    if any(s['size'] and s['flags'] & 2 and s['name'] not in allowed for s in elf.sections):
        raise ValueError('Unaccounted diagnostic section')
    functions = []
    for suffix, offset, relative, pattern in ROWS:
        symbol = 'open_cfw_gx8002_uart_boot_stage2_str_' + suffix
        section_name = '.rodata.' + symbol
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if section['align'] != 1 or elf.relocations(section['index']):
            raise ValueError('diagnostic string layout: ' + symbol)
        literal = upstream_literal(sdk, relative, pattern) + b'\0'
        if payload != literal:
            raise ValueError('diagnostic string does not match pinned upstream literal: ' + symbol)
        if payload != stock[offset:offset + len(payload)]:
            raise ValueError('diagnostic string does not match stock UART-boot stage-2 bytes: ' + symbol)
        functions.append({'symbol': symbol, 'section_name': section_name, 'ownership_kind': 'generated_source_data',
                           'compiled_bytes': len(payload), 'compiled_sha256': sha(payload),
                           'stock_occurrences': [{'symbol': symbol, 'package_offset': offset, 'bytes': len(payload),
                                                   'sha256': sha(payload), 'region': 'uart_boot_stage2_iram'}]})

    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(obj, output / 'uart-boot-stage2-diagnostics.o')

    return {'functions': functions, 'source_sha256': sha(source.read_bytes()), 'flags': FLAGS,
            'verifier_sha256': sha(Path(__file__).read_bytes()),
            'sdk_commit': SDK_COMMIT, 'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Six literal printf format strings only, from the trap-dump register printer and the '
                       'board padmux-init error path. The surrounding trap handler, register-dump loop, and '
                       'padmux board-init control flow in this UART-boot stage-2 copy are not reconstructed; '
                       'that code, an allocator/comparator cluster earlier in the same span, several duplicate '
                       'driver-message and flash-device-name strings, and a U-Boot-derived command-table cluster '
                       '(already flagged as GPL-licensed and unauthorized for reuse in '
                       'docs/research/peripheral-oss-library-provenance-audit.md) remain retained stock in this '
                       'span.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-uart-boot-stage2-diagnostics-verification.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print('UART-boot stage-2 diagnostics:', len(result['functions']), 'strings')
