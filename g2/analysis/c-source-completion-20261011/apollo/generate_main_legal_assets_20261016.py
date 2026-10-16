#!/usr/bin/env python3
"""Generate C-owned LegalRegulatory text/image resources from authenticated data."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_assets.c'
HEADER = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_assets.h'
MANIFEST = G2 / 'analysis/c-source-completion-20261011/apollo/legal-regulatory-assets-provenance.json'
BASE = 0x438000
FIRST = 0x5bf8ac
END = 0x5bf944

def sha(data): return hashlib.sha256(data).hexdigest()

def byte_lines(data):
    return ['    ' + ', '.join(f'0x{b:02x}' for b in data[i:i+16]) + ','
            for i in range(0, len(data), 16)]

def main():
    image = PAYLOAD.read_bytes()[32:]
    if sha(image) != PAYLOAD_SHA:
        raise RuntimeError('authenticated Apollo main payload changed')
    header = '''/* Authenticated LegalRegulatory resources and stock pointer-row order. */
#ifndef OPENCFW_LEGAL_REGULATORY_ASSETS_H
#define OPENCFW_LEGAL_REGULATORY_ASSETS_H
#include <stdint.h>
struct legal_regulatory_image {
    uint32_t format;
    uint16_t width;
    uint16_t height;
    uint32_t stride;
    uint32_t pixel_bytes;
    const uint8_t *pixels;
    uint32_t reserved_0;
    uint32_t reserved_1;
};
extern const void *const audio_legal_asset_slots[38];
#endif
'''
    lines = ['/* C source for the 38 stock LegalRegulatory resource pointers.',
             ' * Generated from authenticated non-executable data; regenerate with',
             ' * generate_main_legal_assets_20261016.py after source verification. */',
             '#include "legal_regulatory_assets.h"', '']
    rows = []
    for slot in range(FIRST, END, 4):
        pointer = struct.unpack_from('<I', image, slot - BASE)[0]
        if not BASE <= pointer < BASE + len(image):
            raise RuntimeError(f'asset pointer outside payload at {slot:x}')
        prefix = image[pointer - BASE:pointer - BASE + 28]
        name = f'audio_legal_asset_{slot:x}'
        if prefix[:4] == (0x619).to_bytes(4, 'little'):
            format_code, wh, stride, length, pixels_addr, r0, r1 = struct.unpack('<7I', prefix)
            width, height = wh & 0xffff, wh >> 16
            if not (0 < length < 0x10000 and r0 == r1 == 0 and
                    BASE <= pixels_addr < BASE + len(image) and
                    pixels_addr + length <= BASE + len(image)):
                raise RuntimeError(f'asset descriptor changed at {slot:x}')
            pixels = image[pixels_addr - BASE:pixels_addr - BASE + length]
            pixel_name = f'legal_pixels_{slot:x}'
            lines += [f'static const uint8_t {pixel_name}[{length}] = {{',
                      *byte_lines(pixels), '};',
                      f'const struct legal_regulatory_image {name} = {{',
                      f'    0x{format_code:x}u, {width}u, {height}u, {stride}u, {length}u,',
                      f'    {pixel_name}, 0u, 0u', '};', '']
            rows.append({'slot': f'0x{slot:06x}', 'stock_pointer': f'0x{pointer:06x}',
                         'kind': 'image', 'symbol': name, 'descriptor_sha256': sha(prefix),
                         'width': width, 'height': height, 'pixel_bytes': length,
                         'pixel_stock_pointer': f'0x{pixels_addr:06x}',
                         'pixel_sha256': sha(pixels)})
        else:
            tail = image[pointer - BASE:]
            end = tail.find(b'\0')
            if end < 0 or end > 4096:
                raise RuntimeError(f'asset string extent changed at {slot:x}')
            content = tail[:end + 1]
            lines += [f'const uint8_t {name}[{len(content)}] = {{',
                      *byte_lines(content), '};', '']
            rows.append({'slot': f'0x{slot:06x}', 'stock_pointer': f'0x{pointer:06x}',
                         'kind': 'text', 'symbol': name, 'bytes': len(content),
                         'sha256': sha(content)})
    if len(rows) != 38 or sum(r['kind'] == 'image' for r in rows) != 10:
        raise RuntimeError('legal resource row inventory changed')
    lines.append('const void *const audio_legal_asset_slots[38] = {')
    for row in rows:
        expr = f'&{row["symbol"]}' if row['kind'] == 'image' else row['symbol']
        lines.append(f'    {expr}, /* {row["slot"]} */')
    lines += ['};', '']
    HEADER.write_text(header)
    SOURCE.write_text('\n'.join(lines))
    manifest = {'status': 'SOURCE_OWNED_LEGAL_REGULATORY_RESOURCES',
                'official_payload_sha256': PAYLOAD_SHA,
                'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE.read_bytes()),
                'header': str(HEADER.relative_to(ROOT)), 'header_sha256': sha(HEADER.read_bytes()),
                'rows': rows, 'row_count': len(rows)}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(manifest['status'], len(rows), sum(r['kind'] == 'image' for r in rows), sha(MANIFEST.read_bytes()))

if __name__ == '__main__': main()
