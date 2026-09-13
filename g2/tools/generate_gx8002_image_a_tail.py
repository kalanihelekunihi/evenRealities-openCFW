# SPDX-License-Identifier: MIT
"""Generate image-A format padding/checksum/extent from a rebuilt image.

No executable bytes are returned. The preceding block is read only as CRC
input; this helper does not assert ownership of that block's implementation.
"""
import struct
from analyze_g2_codec_fwpk_segments import crc32_mpeg2

BLOCK = 0x958c
PAD = 0xb58c
CRC = 0xc588
XIP = 0xc590
XIP_END = 0x15414


def generate(image):
    if len(image) != 326092:
        raise ValueError('Unexpected fixed-layout codec size')
    # The CRC covers block bytes24..12283, including the generated padding.
    covered = bytes(image[BLOCK+24:PAD]) + bytes(CRC-PAD)
    checksum = crc32_mpeg2(covered)
    return bytes(CRC-PAD) + struct.pack('<II', checksum, XIP_END-XIP)
