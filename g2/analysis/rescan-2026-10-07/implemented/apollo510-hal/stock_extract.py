#!/usr/bin/env python3
"""Verify and print address-bound stock bytes for two Apollo510 leaf bodies."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
EXPECTED_SHA256 = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
LOAD = 0x410000
RANGES = ((0x41583C, 8), (0x41CA2C, 48))


def main() -> None:
    image = IMAGE.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    assert digest == EXPECTED_SHA256, (digest, EXPECTED_SHA256)
    for address, size in RANGES:
        offset = address - LOAD
        body = image[offset:offset + size]
        assert len(body) == size
        print(f"stock sha256={digest} load=0x{LOAD:08x} range=0x{address:08x}+{size}")
        print(f"bytes={body.hex()}")
    # The setter's PC-relative literal is at 0x415fdc and resolves to this slot.
    literal_off = 0x415FDC - LOAD
    literal = int.from_bytes(image[literal_off:literal_off + 4], "little")
    assert literal == 0x200270CC, hex(literal)
    # 41ca2c's call opcode is BL 0x41cd1a; lock the raw halfwords as well.
    assert image[0x41CA3A - LOAD:0x41CA3E - LOAD] == bytes.fromhex("00 f0 6e f9")
    print(f"0x41583c literal[0x415fdc]=0x{literal:08x}")
    print("0x41ca2c BL at 0x41ca3a: bytes=00f06ef9 target=0x41cd1a")
    print("stock extraction: hash, ranges, literal, and call-site checks passed")


if __name__ == "__main__":
    main()
