#!/usr/bin/env python3
"""Verify mutable display settings startup words against native SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
source = ROOT / "components/audio/uart_thread_source_candidate/display_settings_startup_cells.c"
items = {"audio_settings_display_profile_cell": 0x648,
         "audio_settings_display_brightness_cell": 0x64c}
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "settings_startup.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        for name, offset in items.items():
            symbol = symbols[name]
            assert symbol["st_size"] == 4
            section = elf.get_section(symbol["st_shndx"])
            compiled = section.data()[symbol["st_value"]:symbol["st_value"] + 4]
            expected = bytes(decoded[offset:offset + 4])
            assert compiled == expected, (name, compiled.hex(), expected.hex())
print("PASS_SETTINGS_STARTUP_INITIALIZER", len(items))
