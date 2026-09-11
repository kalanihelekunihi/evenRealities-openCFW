#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""IEEE754 binary16 (half-precision) quantization for gxDNN tensor elements.

Every gxDNN tensor element decoded so far uses a two-byte half-precision
float (gx8002-gxdnn-cmodel.md, "Tensor indexing and broadcast": "Each
element is two bytes"). That document's "Pinned half source table match"
and "Half arithmetic upstream lead" sections match the codec's compiled
conversion tables bit-for-bit against ROCm/half commit
207ee58595a64b5c4a70df221f1e6e704b807811 (pinned in
docs/research/gx8002-half-table-matches.json), and
docs/research/gx8002-half-arithmetic-verification.json independently
cross-checks 30,000+ rounded arithmetic cases against Python's own IEEE
pack/unpack. Both are round-to-nearest-even standard IEEE754 binary16,
which is exactly what Python's `struct` "e" format code implements. This
module reuses that authenticated, standard codec rather than reinventing
half-precision rounding.

This module produces quantized bytes for command-emitter tensor buffers; it
does not supply, admit, or reproduce the GX8002 codec's shipped 120,800-byte
weight block as source. See
docs/research/gx8002-command-emitter-generator.md for what remains open.
"""
import struct


def quantize_half(value: float) -> int:
    """Round `value` to the nearest representable half-precision value
    (ties to even) and return its 16-bit unsigned bit pattern."""
    return struct.unpack('<H', struct.pack('<e', value))[0]


def dequantize_half(bits: int) -> float:
    if not (0 <= bits < 0x10000):
        raise ValueError('half value must be a 16-bit pattern')
    return struct.unpack('<e', struct.pack('<H', bits))[0]


def quantize_tensor(values) -> bytes:
    """Quantize a sequence of floats into a little-endian half-precision
    tensor buffer, matching the codec's two-bytes-per-element layout."""
    return b''.join(struct.pack('<H', quantize_half(v)) for v in values)


def dequantize_tensor(data: bytes):
    if len(data) % 2:
        raise ValueError('half tensor buffer must have even length')
    return [dequantize_half(word) for (word,) in struct.iter_unpack('<H', data)]
