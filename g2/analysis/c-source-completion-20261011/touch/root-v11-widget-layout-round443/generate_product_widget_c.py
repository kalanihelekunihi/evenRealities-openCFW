#!/usr/bin/env python3
"""Transcribe the locked widget records into an authored, editable C ABI table."""
import hashlib
import re
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
SOURCE = OUT / 'v5_0_0_f0_lp1.c'
TARGET = ROOT / 'g2/components/touch/reset_layout_candidate_20261010/reset_generated_widget_config.c'
image = (ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
assert hashlib.sha256(image).hexdigest() == '0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
locked = image[32 + 0xb0f8 - 0x3300:32 + 0xb2a8 - 0x3300]
assert hashlib.sha256(locked).hexdigest() == '27ef6582ee031179cdfb25d6e091b0be3f869c1ac1e73eb7f58ebaf2ef8022ce'
probe = subprocess.run(['clang', '-target', 'armv6m-none-eabi', '-mcpu=cortex-m0plus',
                        '-mthumb', '-std=c11', '-ffreestanding', '-Xclang',
                        '-fdump-record-layouts', '-fsyntax-only', str(SOURCE)],
                       text=True, capture_output=True, check=True)
block = (probe.stdout + probe.stderr).split('*** Dumping AST Record Layout')[-1]
assert '[sizeof=144, align=4]' in block
top = []
for line in block.splitlines():
    match = re.match(r'\s*(\d+)\s*\|(\s+)(.*?)\s*$', line)
    if match and len(match.group(2)) == 3:
        offset, declaration = int(match.group(1)), match.group(3)
        if offset == 0 and declaration.startswith('struct '):
            continue
        typ, name = declaration.rsplit(' ', 1)
        top.append((offset, typ, name.lstrip('*')))
assert top[0][0] == 0 and top[-1][0] == 142
lines = ['/* SPDX-License-Identifier: MIT',
         ' * Authored ABI transcription of three locked G2 Touch widget records.',
         ' * Field offsets match pinned Infineon CapSense 5.0 LP type at commit',
         ' * a4aa9306f7e4323994902f0baf5b1570ffbbfe59. Fixed stock pointers',
         ' * require linker placement and product configuration validation.',
         ' */', '#include <stdint.h>', '#include <stddef.h>', '',
         'typedef struct {']
fields = []
for n, (offset, typ, name) in enumerate(top):
    end = top[n + 1][0] if n + 1 < len(top) else 144
    width = end - offset
    if '*' in typ or name.startswith('ptr'):
        assert width == 4, name
        ctype, kind = 'uint32_t', 'word'
    elif typ in ('uint8_t', 'uint16_t', 'uint32_t'):
        ctype, kind = typ, 'word'
        natural = {'uint8_t': 1, 'uint16_t': 2, 'uint32_t': 4}[typ]
        assert width in (natural, natural + 1), name
        if width != natural:
            assert name == 'iirCoeffHw'
            assert all(locked[i * 144 + offset + natural] == 0 for i in range(3))
    else:
        assert width == 8, (name, width)
        ctype, kind = 'uint8_t', 'array'
    lines.append(f'    {ctype} {name}' + ('[8];' if kind == 'array' else ';'))
    if name == 'iirCoeffHw':
        lines.append('    uint8_t reserved_padding_after_iirCoeffHw;')
    fields.append((offset, width, name, kind))
lines += ['} touch_widget_config_abi;',
          '_Static_assert(sizeof(touch_widget_config_abi) == 144, "widget stride");']
for offset, _, name, _ in fields:
    lines.append(f'_Static_assert(offsetof(touch_widget_config_abi, {name}) == {offset}, "{name} offset");')
lines += ['', 'const touch_widget_config_abi touch_generated_widget_config[3]',
          '    __attribute__((section(".touch_rodata.widget_config"), used)) = {']
for i in range(3):
    lines.append('    {')
    rec = locked[i * 144:(i + 1) * 144]
    for offset, width, name, kind in fields:
        data = rec[offset:offset + (1 if name == 'iirCoeffHw' else width)]
        if kind == 'array':
            val = '{' + ', '.join(f'0x{b:02x}' for b in data) + '}'
        else:
            val = f'0x{int.from_bytes(data, "little"):x}u'
        lines.append(f'        .{name} = {val},')
    lines.append('    },')
lines += ['};', '']
TARGET.write_text('\n'.join(lines))
print(TARGET.relative_to(ROOT), hashlib.sha256(TARGET.read_bytes()).hexdigest())
