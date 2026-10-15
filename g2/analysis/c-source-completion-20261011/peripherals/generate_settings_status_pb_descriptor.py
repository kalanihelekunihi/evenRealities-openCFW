#!/usr/bin/env python3
"""Transcribe the authenticated settings-status nanopb descriptor graph into C."""
from pathlib import Path
import hashlib, struct

root = Path(__file__).resolve().parents[3]
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
base = 0x438000
def u32(a): return struct.unpack_from('<I', blob, a-base)[0]
def u16(a): return struct.unpack_from('<H', blob, a-base)[0]
def descriptor(a):
    fields, subs, default, callback = (u32(a+i*4) for i in range(4))
    count, required, largest = (u16(a+i) for i in (16,18,20))
    assert default == 0 and callback == 0 and required == 0
    words = []
    p = fields
    for _ in range(count):
        first = u32(p)
        width = (first & 3) + 1
        assert width in (1,2), (hex(a),hex(first))
        words += [u32(p+i*4) for i in range(width)]
        p += width*4
    assert u32(p) == 0, (hex(a),hex(p))
    children=[]
    for i in range(64):
        v=u32(subs+i*4)
        if v==0: break
        assert 0x438000 <= v < 0x438000+len(blob)
        children.append(v)
    else: raise AssertionError('unterminated submessage table')
    return count,largest,words,children

nodes={};pending=[0x77772c]
while pending:
    a=pending.pop(0)
    if a in nodes: continue
    nodes[a]=descriptor(a)
    pending.extend(nodes[a][3])
assert len(nodes)==19
lines=['/* Source-owned nanopb graph rooted at native ROM 0x77772c. */',
       '/* Field words and graph edges come from official Apollo s200 2.2.6.10. */',
       '#include <stddef.h>', '#include <stdint.h>',
       'struct pb_msgdesc_candidate {',
       '    const uint32_t *field_info;',
       '    const struct pb_msgdesc_candidate *const *submsg_info;',
       '    const uint8_t *default_value;',
       '    void *field_callback;',
       '    uint16_t field_count, required_field_count, largest_tag;',
       '};',
       '_Static_assert(sizeof(struct pb_msgdesc_candidate)==24u,"ARM nanopb descriptor ABI");',
       '_Static_assert(offsetof(struct pb_msgdesc_candidate,field_count)==16u,"ARM field count offset");']
for a in nodes:
    if a!=0x77772c: lines.append(f'static const struct pb_msgdesc_candidate desc_{a:06x};')
for a,(count,largest,words,children) in nodes.items():
    hexwords=', '.join(f'0x{w:08x}u' for w in words+[0])
    lines.append(f'static const uint32_t fields_{a:06x}[]={{ {hexwords} }};')
    refs=', '.join(f'&desc_{v:06x}' for v in children)
    lines.append(f'static const struct pb_msgdesc_candidate *const sub_{a:06x}[]={{ {refs+", " if refs else ""}0 }};')
    name='audio_settings_status_pb_descriptor' if a==0x77772c else f'desc_{a:06x}'
    storage='const' if a==0x77772c else 'static const'
    lines.append(f'{storage} struct pb_msgdesc_candidate {name}={{ fields_{a:06x}, sub_{a:06x}, 0, 0, {count}u, 0u, {largest}u }};')
path=root/'components/audio/uart_thread_source_candidate/settings_status_pb_descriptor.c'
path.write_text('\n'.join(lines)+'\n')
print(path, len(nodes))
