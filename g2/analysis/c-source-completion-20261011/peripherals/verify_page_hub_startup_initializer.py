#!/usr/bin/env python3
"""Verify Apollo display and hub startup cells against initialized SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
source = ROOT / "components/audio/uart_thread_source_candidate/display_page_hub_startup_cells.c"
items = {"audio_uart_display_page_size_cell": (0x64, 4),
         "audio_uart_hub_role_cell": (0x4526, 2)}
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "startup_cells.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        for name, (offset, size) in items.items():
            symbol = symbols[name]
            assert symbol["st_size"] == size
            section = elf.get_section(symbol["st_shndx"])
            compiled = section.data()[symbol["st_value"]:symbol["st_value"] + size]
            expected = bytes(decoded[offset:offset + size])
            assert compiled == expected, (name, compiled.hex(), expected.hex())
print("PASS_PAGE_HUB_STARTUP_INITIALIZER", len(items))
