#!/usr/bin/env python3
"""Decode the authenticated Apollo Main initialized low-RAM record."""
import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
DECODED_SHA = "df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743"


def decode():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("official Apollo payload changed")
    word = lambda address: struct.unpack_from("<I", payload, address - 0x438000)[0]
    record = 0x75d3f4
    source = record + word(record)
    encoded = word(record + 4)
    destination = word(record + 8)
    if (source, encoded, destination) != (0x79189e, 0x54e0, 0x20000000):
        raise RuntimeError("Apollo low-RAM startup record changed")
    position, end, output = source, source + (encoded >> 1), bytearray()
    while position < end:
        token = payload[position - 0x438000]
        position += 1
        literals, match = token & 3, token >> 4
        if not literals:
            literals = payload[position - 0x438000] + 3
            position += 1
        if match == 15:
            match += payload[position - 0x438000]
            position += 1
        for _ in range(literals - 1):
            output.append(payload[position - 0x438000])
            position += 1
        if match:
            offset = payload[position - 0x438000]
            position += 1
            high = (token >> 2) & 3
            if high == 3:
                high = payload[position - 0x438000]
                position += 1
            offset += high << 8
            if not (0 < offset <= len(output)):
                raise RuntimeError("invalid low-RAM back reference")
            for _ in range(match + 2):
                output.append(output[-offset])
    if position != end or len(output) != 0x4558 or \
            hashlib.sha256(output).hexdigest() != DECODED_SHA:
        raise RuntimeError("Apollo low-RAM decoded data changed")
    return bytes(output)


if __name__ == "__main__":
    print("PASS_MAIN_LOW_RAM_DECODE", len(decode()), DECODED_SHA)
