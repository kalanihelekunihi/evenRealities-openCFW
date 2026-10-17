#!/usr/bin/env python3
"""Check source-owned Conversate menu icon bytes and pointer relocation."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_menu_icon_76a2a0.c"
OUT = G2 / "build/c-firmware/20261017/main-conversate-menu-icon-76a2a0"
OBJECT = OUT / "icon.o"
RECEIPT = OUT / "oracle-receipt.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    payload = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    descriptor = payload[0x76a2a0 - 0x438000:0x76a2a0 - 0x438000 + 28]
    words = struct.unpack("<7I", descriptor)
    assert words == (0x619, 0x180018, 0x18, 0x240, 0x6ac3c0, 0, 0)
    pixels = payload[0x6ac3c0 - 0x438000:0x6ac3c0 - 0x438000 + 0x240]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-ffreestanding", "-fno-builtin", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        pixel_section = elf.get_section_by_name(".g2_conversate_menu_icon_pixels_6ac3c0")
        desc_section = elf.get_section_by_name(".g2_conversate_menu_icon_76a2a0")
        assert pixel_section.data() == pixels
        compiled = desc_section.data()
        assert len(compiled) == 28 and compiled[:16] == descriptor[:16]
        assert compiled[16:20] == bytes(4) and compiled[20:] == descriptor[20:]
        reloc = elf.get_section_by_name(".rel.g2_conversate_menu_icon_76a2a0")
        assert reloc is not None
        entries = list(reloc.iter_relocations())
        assert len(entries) == 1 and entries[0]["r_offset"] == 16
        symbol = elf.get_section(reloc["sh_link"]).get_symbol(entries[0]["r_info_sym"])
        assert symbol.name == "audio_conversate_menu_icon_pixels_6ac3c0"
    record = {
        "status": "PASS_MAIN_CONVERSATE_MENU_ICON_76A2A0_SOURCE_DATA",
        "stock_payload_sha256": PAYLOAD_SHA,
        "stock_descriptor_address": "0x76a2a0",
        "stock_pixels_address": "0x6ac3c0",
        "stock_descriptor_sha256": hashlib.sha256(descriptor).hexdigest(),
        "stock_pixels_sha256": hashlib.sha256(pixels).hexdigest(),
        "pixel_bytes": len(pixels),
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE)},
        "object": {"path": str(OBJECT.relative_to(ROOT)), "sha256": sha(OBJECT)},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Exact final ROM placement, enclosing menu route and hardware rendering remain open.",
    }
    RECEIPT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], sha(RECEIPT))


if __name__ == "__main__":
    main()
