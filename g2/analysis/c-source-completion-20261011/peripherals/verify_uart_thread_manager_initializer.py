#!/usr/bin/env python3
"""Verify UART thread-manager startup bytes against authenticated SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from verify_ble_hci_le_feature_initializer import ROOT, decoded

payload = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
assert hashlib.sha256(payload.read_bytes()).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
source = ROOT / "components/audio/uart_thread_source_candidate/display_uart_thread_manager_state.c"
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "uart_thread_manager.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-ffreestanding", "-c", str(source), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbol = next(s for s in elf.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_uart_thread_manager_state")
        assert symbol["st_size"] == 36
        section = elf.get_section(symbol["st_shndx"])
        assert section["sh_addralign"] >= 4
        compiled = section.data()[symbol["st_value"]:symbol["st_value"] + 36]
        expected = bytes(decoded[0x40d8:0x40fc])
        assert compiled == expected, (compiled.hex(), expected.hex())
print("PASS_UART_THREAD_MANAGER_INITIALIZER", len(compiled))
