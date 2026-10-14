#!/usr/bin/env python3
"""Verify Apollo Main advertising configuration pointers against SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
source = ROOT / "components/audio/uart_thread_source_candidate/display_ble_adv_config_state.c"
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "adv_config.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        symbol = symbols["audio_ble_adv_config_state"]
        assert symbol["st_size"] == 32
        section = elf.get_section(symbol["st_shndx"])
        assert section["sh_addralign"] >= 4
        compiled = section.data()[symbol["st_value"]:symbol["st_value"] + 32]
        expected = bytes(decoded[0x3838:0x3858])
        assert compiled == expected, (compiled.hex(), expected.hex())
        assert compiled[-4:] == b"\0" * 4
print("PASS_BLE_ADV_CONFIG_INITIALIZER", len(compiled))
