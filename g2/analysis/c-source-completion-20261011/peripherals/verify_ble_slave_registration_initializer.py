#!/usr/bin/env python3
"""Verify the native 12-byte mutable slave registration table initializer."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
source = ROOT / "components/audio/uart_thread_source_candidate/display_ble_slave_registration_table.c"
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "slave_registration.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        symbol = symbols["audio_ble_slave_registration_table"]
        assert symbol["st_size"] == 12
        section = elf.get_section(symbol["st_shndx"])
        compiled = section.data()[symbol["st_value"]:symbol["st_value"] + 12]
        expected = bytes(decoded[0x3e0:0x3ec])
        assert compiled == expected, (compiled.hex(), expected.hex())
print("PASS_BLE_SLAVE_REGISTRATION_INITIALIZER", compiled.hex())
