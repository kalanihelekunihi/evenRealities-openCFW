#!/usr/bin/env python3
"""Bounded typed ROM pin-record comparison against locked Touch stock bytes."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/touch/reset_layout_candidate_20261010/reset_pin_config.c"
STOCK = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_touch.bin"
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d"
with tempfile.TemporaryDirectory(prefix="touch-pins-") as tmp:
    obj = Path(tmp) / "pins.o"
    data = Path(tmp) / "pins.bin"
    subprocess.run(["clang", "-target", "armv6m-none-eabi", "-mcpu=cortex-m0plus",
                    "-mthumb", "-Og", "-ffreestanding", "-fno-builtin", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "--dump-section",
                    f".touch_rom.pin_config={data}", str(obj)], check=True)
    generated = data.read_bytes()
    image = STOCK.read_bytes()[32:]
    expected = image[0xb34c - 0x3300:0xb34c - 0x3300 + 40]
    assert len(generated) == 40 and generated == expected
    print("PASS: 5 typed pin records, 40/40 stock ROM bytes at 0xb34c; SHA256", hashlib.sha256(generated).hexdigest())
