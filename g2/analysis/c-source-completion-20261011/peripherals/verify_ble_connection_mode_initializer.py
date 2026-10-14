#!/usr/bin/env python3
"""Verify two mutable BLE connection-mode initializers against SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
source = ROOT / "components/audio/uart_thread_source_candidate/display_ble_connection_modes.c"
locations = {"audio_ble_requested_conn_mode": 0x4541,
             "audio_ble_current_conn_mode": 0x4542}
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "connection_modes.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        for name, offset in locations.items():
            symbol = symbols[name]
            assert symbol["st_size"] == 1
            section = elf.get_section(symbol["st_shndx"])
            compiled = section.data()[symbol["st_value"]:symbol["st_value"] + 1]
            expected = bytes(decoded[offset:offset + 1])
            assert compiled == expected == b"\xa4", (name, compiled.hex(), expected.hex())
        marker = symbols["audio_ble_connection_marker"]
        current = symbols["audio_ble_current_conn_mode"]
        assert marker["st_shndx"] == current["st_shndx"]
        assert marker["st_value"] == current["st_value"]
        assert marker["st_size"] in (0, 1)
print("PASS_BLE_CONNECTION_MODE_INITIALIZER_AND_ALIAS", len(locations))
