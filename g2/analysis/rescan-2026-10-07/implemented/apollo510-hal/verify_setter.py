#!/usr/bin/env python3
"""Compile the native setter and check its emitted register/memory contract."""

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = Path(__file__).resolve().parent / "native/external_mode_setter.c"
EXPECTED_SHA256 = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"


def main() -> None:
    image = IMAGE.read_bytes()
    assert hashlib.sha256(image).hexdigest() == EXPECTED_SHA256
    # Stock opcodes: ldr literal, store r0 through r1, return via lr.
    assert image[0x41583C - 0x410000:0x415844 - 0x410000] == bytes.fromhex(
        "df f8 9c 17 08 60 70 47")
    assert int.from_bytes(image[0x415FDC - 0x410000:0x415FE0 - 0x410000],
                          "little") == 0x200270CC

    with tempfile.TemporaryDirectory() as temp:
        obj = Path(temp) / "setter.o"
        subprocess.run([
            "clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
            "-fomit-frame-pointer", "-c", str(SOURCE), "-o", str(obj),
        ], check=True)
        disassembly = subprocess.run(["arm-none-eabi-objdump", "-dr", str(obj)],
                                     check=True, text=True,
                                     stdout=subprocess.PIPE).stdout
    # The candidate's literal placement differs; verify the same argument,
    # address, store, and return contract instead of claiming byte equality.
    assert re.search(r"ldr\s+r1,\s*\[pc,\s*#4\]", disassembly)
    assert re.search(r"str\s+r0,\s*\[r1,\s*#0\]", disassembly)
    assert re.search(r"bx\s+lr", disassembly)
    assert re.search(r"\.word\s+0x200270cc", disassembly)
    print("setter contract: stock bytes/hash and compiled C store/return contract agree")
    print("byte identity: not claimed (different literal placement and padding)")


if __name__ == "__main__":
    main()
