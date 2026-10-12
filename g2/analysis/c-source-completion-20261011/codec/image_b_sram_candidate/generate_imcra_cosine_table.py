#!/usr/bin/env python3
"""Generate the typed 513-point IMCRA sine table from its mathematical rule."""
import hashlib
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[5]
IMAGE = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
OUTPUT = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_imcra_cosine_lookup.c'
SHA = 'd23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941'
stock = IMAGE.read_bytes()
assert hashlib.sha256(stock).hexdigest() == SHA
start = 0x100148d4 - 0x10003000
native = [struct.unpack_from('<I', stock, start + 4 * i)[0] for i in range(513)]
generated = [struct.unpack('<I', struct.pack('<f', math.sin(2 * math.pi * i / 512)))[0]
             for i in range(513)]
assert [(i, generated[i], native[i]) for i in range(513)
        if generated[i] != native[i]] == [
            (256, 0x250d3132, 0x2768d16e),
            (512, 0xa58d3132, 0xa7e8d16e)]
generated[256] = 0x2768d16e
generated[512] = 0xa7e8d16e
assert generated == native

def quarter_word(index):
    if index <= 128:
        return generated[index]
    if index < 256:
        return generated[256 - index]
    if index == 256:
        return generated[256]
    if index <= 384:
        return generated[index - 256] ^ 0x80000000
    if index < 512:
        return generated[512 - index] ^ 0x80000000
    return generated[512]

assert [quarter_word(index) for index in range(513)] == native

def literal(word):
    value = struct.unpack('<f', struct.pack('<I', word))[0]
    return value.hex() + 'f'

quarter = generated[:129]
lines = []
for index in range(0, len(quarter), 4):
    lines.append('    ' + ', '.join(literal(word) for word in quarter[index:index + 4]) + ',')
header = '''/* SPDX-License-Identifier: MIT
 * Typed quarter-wave source for image-B native cosine interpolator
 * 0x1000ee64..0x1000eedb. Native table starts at 0x100148d4.
 * All 513 original float32 words are reconstructed exactly by quarter-wave
 * symmetry; exceptional native zero-crossing residuals 256 and 512 remain
 * explicit product values. Formula and reconstructed words checked against
 * binh_b_stage2.bin
 * SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * This is a behavioral size variant, with execution time and exceptional
 * FPU inputs still unqualified on hardware.
 */
#include <stdint.h>

static const float sine_quarter[129] = {
'''
footer = '''};

static const uint32_t residual_256 = UINT32_C(0x2768d16e);
static const uint32_t residual_512 = UINT32_C(0xa7e8d16e);

static float float_bits(uint32_t word)
{
    union { uint32_t word; float value; } converted;
    converted.word = word;
    return converted.value;
}

static float sine_at(uint32_t index)
{
    if (index <= 128u) return sine_quarter[index];
    if (index < 256u) return sine_quarter[256u - index];
    if (index == 256u) return float_bits(residual_256);
    if (index <= 384u) return -sine_quarter[index - 256u];
    if (index < 512u) return -sine_quarter[512u - index];
    return float_bits(residual_512);
}

float gx8002_image_b_cosine_lookup_1000ee64(float angle)
{
    float phase = 0.25f + angle * float_bits(UINT32_C(0x3e22f983));
    int32_t integer = (int32_t)phase;
    if (phase < 0.0f) --integer;
    float scaled = (phase - (float)integer) * 512.0f;
    uint32_t index = ((uint32_t)scaled) & 511u;
    float fraction = scaled - (float)index;
    return fraction * sine_at(index + 1u) +
           (1.0f - fraction) * sine_at(index);
}
'''
OUTPUT.write_text(header + '\n'.join(lines) + '\n' + footer)
print(f'{OUTPUT}: {len(generated)} verified float32 samples from {len(quarter)} source words')
