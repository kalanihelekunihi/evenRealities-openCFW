#!/usr/bin/env python3
"""Verify shared device-manager state prefix against initialized SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
source = ROOT / "components/audio/uart_thread_source_candidate/display_device_manager_state_prefix.c"
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "device_manager_state.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        state = symbols["audio_device_manager_state"]
        alias = symbols["audio_ble_device_manager_state"]
        assert state["st_size"] == 16
        assert state["st_shndx"] == alias["st_shndx"]
        assert state["st_value"] == alias["st_value"]
        section = elf.get_section(state["st_shndx"])
        assert section["sh_addralign"] >= 4
        compiled = section.data()[state["st_value"]:state["st_value"] + 16]
        expected = bytes(decoded[0x60c:0x61c])
        assert compiled == expected, (compiled.hex(), expected.hex())
print("PASS_DEVICE_MANAGER_STATE_PREFIX", len(compiled))
