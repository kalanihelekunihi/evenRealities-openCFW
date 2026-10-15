#!/usr/bin/env python3
"""Generate source-owned CRC data from the polynomials recovered in R1."""
from pathlib import Path


def tables():
    crc16, crc32 = [], []
    for byte in range(256):
        a, b = byte, byte << 24
        for _ in range(8):
            a = (a >> 1) ^ (0xa001 if a & 1 else 0)
            b = ((b << 1) ^ (0x1edc6f41 if b & 0x80000000 else 0)) & 0xffffffff
        crc16.append(a)
        crc32.append(b)
    return crc16, crc32


def render():
    text = '/* Generated from CRC-16/MODBUS and non-reflected Castagnoli polynomials. */\n'
    for width, values in zip((16, 32), tables()):
        text += f'static const uint{width}_t r1_stock_crc{width}_table[256] = {{\n'
        for offset in range(0, 256, 8):
            text += '    ' + ', '.join(f'0x{value:0{width//4}x}u' for value in values[offset:offset+8]) + ',\n'
        text += '};\n'
    return text


if __name__ == '__main__':
    (Path(__file__).resolve().parents[1] / 'source/stock_checksum_tables.inc').write_text(render())
