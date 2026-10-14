#!/usr/bin/env python3
"""Verify compiled radio config bytes against authenticated decoded SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
items = {
    "audio_ble_hci_radio_platform_pin_200001b0": (0x1b0, 4),
    "audio_ble_hci_radio_resource_config_200001b4": (0x1b4, 20),
}
source = ROOT / "components/audio/uart_thread_source_candidate/display_ble_hci_radio_platform_config.c"
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "radio_config.o"
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
print("PASS_BLE_HCI_RADIO_CONFIG_INITIALIZER", len(items))
