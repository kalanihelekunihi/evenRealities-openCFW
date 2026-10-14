#!/usr/bin/env python3
"""Verify relocatable CMSIS attribute shapes against native ROM and SRAM."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).with_name("display_driver_attributes.c")
blob = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()
assert hashlib.sha256(blob).hexdigest() == \
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
raw = blob[32:]
import sys
sys.path.insert(0, str(ROOT / "analysis/c-source-completion-20261011/peripherals"))
from verify_ble_hci_le_feature_initializer import decoded

thread_native = bytearray(raw[0x75381c-0x438000:0x753840-0x438000])
queue_native = bytearray(decoded[0x67c:0x694])
assert len(thread_native) == 36 and len(queue_native) == 24
assert raw[0x77ed98-0x438000:0x77edac-0x438000].split(b"\0")[0] == b"displaydrv_mgr_task"
assert raw[0x77edac-0x438000:0x77edc0-0x438000].split(b"\0")[0] == b"display_mgr_Queue"
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / "attrs.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-Wall", "-Wextra",
                    "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        for name, native, pointer_offsets in (
            ("audio_display_driver_thread_attrs", thread_native, (0,)),
            ("audio_display_driver_queue_attrs", queue_native, (0, 8, 16)),
        ):
            symbol = symbols[name]
            assert symbol["st_size"] == len(native)
            section = elf.get_section(symbol["st_shndx"])
            compiled = bytearray(section.data()[symbol["st_value"]:
                                                symbol["st_value"] + len(native)])
            reloc = elf.get_section_by_name(".rel" + section.name)
            assert reloc is not None
            positions = {r["r_offset"] - symbol["st_value"] for r in reloc.iter_relocations()
                         if symbol["st_value"] <= r["r_offset"] < symbol["st_value"] + len(native)}
            assert positions == set(pointer_offsets), (name, positions)
            for offset in pointer_offsets:
                compiled[offset:offset+4] = b"\0" * 4
                native[offset:offset+4] = b"\0" * 4
            assert compiled == native, (name, compiled.hex(), native.hex())
        for name, expected in (("thread_name", b"displaydrv_mgr_task\0"),
                               ("queue_name", b"display_mgr_Queue\0")):
            symbol = symbols[name]
            section = elf.get_section(symbol["st_shndx"])
            assert section.data()[symbol["st_value"]:symbol["st_value"]+symbol["st_size"]] == expected
        for name, size in (("audio_display_driver_queue_control_block", 0x50),
                           ("audio_display_driver_queue_storage", 0xd80)):
            symbol = symbols[name]
            assert symbol["st_size"] == size
            assert elf.get_section(symbol["st_shndx"])["sh_type"] == "SHT_NOBITS"
print("PASS_DISPLAY_DRIVER_ATTRIBUTES", 2)
