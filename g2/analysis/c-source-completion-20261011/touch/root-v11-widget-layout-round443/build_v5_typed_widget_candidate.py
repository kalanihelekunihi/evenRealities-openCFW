#!/usr/bin/env python3
"""Generate an experimental editable v5 widget table and compare object bytes."""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
SOURCE = OUT / 'v5_0_0_f0_lp1.c'
IMAGE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
image = IMAGE.read_bytes()
assert hashlib.sha256(image).hexdigest() == '0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
locked = image[32 + 0xb0f8 - 0x3300:32 + 0xb2a8 - 0x3300]
assert hashlib.sha256(locked).hexdigest() == '27ef6582ee031179cdfb25d6e091b0be3f869c1ac1e73eb7f58ebaf2ef8022ce'
probe = subprocess.run(['clang', '-target', 'armv6m-none-eabi', '-mcpu=cortex-m0plus',
                        '-mthumb', '-std=c11', '-ffreestanding', '-Xclang',
                        '-fdump-record-layouts', '-fsyntax-only', str(SOURCE)],
                       text=True, capture_output=True, check=True)
block = (probe.stdout + probe.stderr).split('*** Dumping AST Record Layout')[-1]
assert '[sizeof=144, align=4]' in block
fields = []
parent = None
for line in block.splitlines():
    match = re.match(r'\s*(\d+)\s*\|(\s+)(.*?)\s*$', line)
    if not match:
        continue
    offset, spaces, declaration = int(match.group(1)), len(match.group(2)), match.group(3)
    if spaces not in (3, 5):
        continue
    parts = declaration.rsplit(' ', 1)
    if len(parts) != 2:
        continue
    typ, name = parts
    name = name.lstrip('*')
    if '*' in declaration:
        width = 4
        kind = 'pointer'
    elif typ in ('uint8_t', 'uint16_t', 'uint32_t', 'int16_t'):
        width = {'uint8_t': 1, 'uint16_t': 2, 'uint32_t': 4, 'int16_t': 2}[typ]
        kind = 'scalar'
    else:
        if spaces == 3:
            parent = name
        continue
    field = (f'{parent}.{name}' if spaces == 5 else name)
    fields.append((offset, width, kind, field))
    if spaces == 3:
        parent = None
covered = set()
for offset, width, _, name in fields:
    assert not (set(range(offset, offset + width)) & covered), name
    covered.update(range(offset, offset + width))
padding = sorted(set(range(144)) - covered)
assert padding == [141], padding
assert all(locked[i * 144 + 141] == 0 for i in range(3))
text = SOURCE.read_text().replace('unsigned char widget_size_probe[sizeof(cy_stc_capsense_widget_config_t)];', '')
text += '\n_Static_assert(sizeof(cy_stc_capsense_widget_config_t) == 144, "v5 LP widget ABI");\n'
text += 'const cy_stc_capsense_widget_config_t touch_generated_widget_config[3] = {\n'
for i in range(3):
    text += '  {\n'
    rec = locked[i * 144:(i + 1) * 144]
    for offset, width, kind, name in fields:
        value = int.from_bytes(rec[offset:offset + width], 'little')
        expr = f'(void *)0x{value:08x}u' if kind == 'pointer' else f'0x{value:x}u'
        text += f'    .{name} = {expr},\n'
    text += '  },\n'
text += '};\n'
c = OUT / 'v5_typed_widget_candidate.c'
c.write_text(text)
obj = OUT / 'v5_typed_widget_candidate.o'
subprocess.run(['clang', '-target', 'armv6m-none-eabi', '-mcpu=cortex-m0plus',
                '-mthumb', '-std=c11', '-ffreestanding', '-fno-pic', '-c', str(c),
                '-o', str(obj)], capture_output=True, text=True, check=True)
sym = subprocess.check_output(['arm-none-eabi-nm', '-S', str(obj)], text=True)
assert re.search(r'\b000001b0\s+R\s+touch_generated_widget_config\b', sym), sym
rel = subprocess.check_output(['arm-none-eabi-readelf', '-r', str(obj)], text=True)
assert 'There are no relocations in this file.' in rel, rel
raw = OUT / 'v5_typed_widget_candidate.bin'
subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', '-j', '.rodata',
                str(obj), str(raw)], check=True)
actual = raw.read_bytes()
assert actual == locked, (len(actual), hashlib.sha256(actual).hexdigest())
report = {'status': 'PASS_EXPERIMENTAL_V5_TYPED_WIDGET_BYTE_IDENTITY',
          'source_commit': 'a4aa9306f7e4323994902f0baf5b1570ffbbfe59',
          'firmware_sha256': hashlib.sha256(image).hexdigest(),
          'stock_span_sha256': hashlib.sha256(locked).hexdigest(),
          'compiled_rodata_sha256': hashlib.sha256(actual).hexdigest(),
          'candidate_c_sha256': hashlib.sha256(c.read_bytes()).hexdigest(),
          'candidate_object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
          'fields_per_record': len(fields), 'record_count': 3,
          'relocations': 0,
          'limits': ['The candidate is experimental and excluded from selected firmware sources.',
                     'Byte identity at the current absolute addresses does not prove generated product provenance, final relocatable layout, or hardware behavior.']}
(OUT / 'v5-typed-widget-candidate-receipt.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'])
