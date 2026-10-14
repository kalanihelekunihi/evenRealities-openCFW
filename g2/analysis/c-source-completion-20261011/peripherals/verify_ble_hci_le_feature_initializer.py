#!/usr/bin/env python3
"""Bind C LE feature words to the authenticated compressed SRAM initializer."""
from pathlib import Path
import hashlib
import struct
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[3]
RAW = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
BASE, RECORD = 0x438000, 0x75d3f4
relative, packed, destination = struct.unpack_from("<III", RAW, RECORD - BASE)
stream = RAW[RECORD + relative - BASE:RECORD + relative - BASE + (packed >> 1)]
cursor = 0
decoded = bytearray()
while cursor < len(stream):
    token = stream[cursor]
    cursor += 1
    literals = token & 3
    if literals == 0:
        literals = stream[cursor] + 3
        cursor += 1
    matches = token >> 4
    if matches == 15:
        matches = stream[cursor] + 15
        cursor += 1
    decoded.extend(stream[cursor:cursor + literals - 1])
    cursor += literals - 1
    if matches:
        low = stream[cursor]
        cursor += 1
        high = (token >> 2) & 3
        if high == 3:
            high = stream[cursor]
            cursor += 1
        distance = low + (high << 8)
        assert 0 < distance <= len(decoded)
        for _ in range(matches + 2):
            decoded.append(decoded[-distance])
assert destination == 0x20000000 and len(decoded) == 17752
assert hashlib.sha256(decoded).hexdigest() == "df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743"
expected = bytes(decoded[0x28:0x30])
assert expected == bytes.fromhex("ff37000000000000")

source = ROOT / "components/audio/uart_thread_source_candidate/display_ble_hci_le_features.c"
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "features.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream_file:
        elf = ELFFile(stream_file)
        symbol = next(s for s in elf.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_ble_hci_le_supported_features")
        assert symbol["st_size"] == 8
        section = elf.get_section(symbol["st_shndx"])
        compiled = section.data()[symbol["st_value"]:symbol["st_value"] + 8]
        assert compiled == expected, (compiled.hex(), expected.hex())
print("PASS_BLE_HCI_LE_FEATURE_INITIALIZER", expected.hex())
