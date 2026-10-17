#!/usr/bin/env python3
"""Verify four tag icons and the initialized low-RAM pointer table."""
import hashlib
import importlib.util
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_tag_icon_map_2000052c.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
DECODE = G2 / "analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py"
OUT = G2 / "build/c-firmware/20261017/main-conversate-tag-icon-map-2000052c"
OBJECT = OUT / "icon-map.o"
RECEIPT = OUT / "oracle-receipt.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ADDRESSES = (0x76a2bc, 0x76a498, 0x76a460, 0x76a4b4)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    spec = importlib.util.spec_from_file_location("low_ram", DECODE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ram = module.decode()
    expected = (0,) + ADDRESSES
    assert struct.unpack_from("<5I", ram, 0x52c) == expected
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-ffreestanding", "-fno-builtin", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    records = []
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        for address in ADDRESSES:
            raw = payload[address - 0x438000:address - 0x438000 + 28]
            (magic, dimensions, stride, size, pixel, reserve_a,
             reserve_b) = struct.unpack("<7I", raw)
            assert (magic, dimensions, stride, size, reserve_a,
                    reserve_b) == (0x619, 0x180018, 0x18, 0x240, 0, 0)
            pixels = payload[pixel - 0x438000:pixel - 0x438000 + size]
            desc = elf.get_section_by_name(f".g2_conversate_tag_icon_{address:06x}")
            pix = elf.get_section_by_name(f".g2_conversate_tag_icon_pixels_{pixel:06x}")
            assert pix.data() == pixels
            compiled = desc.data()
            assert len(compiled) == 28 and compiled[:16] == raw[:16]
            assert compiled[16:20] == bytes(4) and compiled[20:] == raw[20:]
            rel = elf.get_section_by_name(f".rel.g2_conversate_tag_icon_{address:06x}")
            entries = list(rel.iter_relocations())
            assert len(entries) == 1 and entries[0]["r_offset"] == 16
            symbol = elf.get_section(rel["sh_link"]).get_symbol(entries[0]["r_info_sym"])
            assert symbol.name == f"audio_conversate_tag_icon_pixels_{pixel:06x}"
            records.append({"descriptor": hex(address), "pixels": hex(pixel),
                            "descriptor_sha256": hashlib.sha256(raw).hexdigest(),
                            "pixels_sha256": hashlib.sha256(pixels).hexdigest()})
        table = elf.get_section_by_name(".g2_conversate_tag_icon_map_2000052c")
        assert table.data() == bytes(20)
        rel = elf.get_section_by_name(".rel.g2_conversate_tag_icon_map_2000052c")
        entries = list(rel.iter_relocations())
        assert [r["r_offset"] for r in entries] == [4, 8, 12, 16]
        names = [elf.get_section(rel["sh_link"]).get_symbol(r["r_info_sym"]).name
                 for r in entries]
        assert names == [f"audio_conversate_tag_icon_{a:06x}" for a in ADDRESSES]
    record = {
        "status": "PASS_MAIN_CONVERSATE_TAG_ICON_MAP_2000052C_SOURCE_DATA",
        "stock_payload_sha256": PAYLOAD_SHA,
        "low_ram_decoded_sha256": hashlib.sha256(ram).hexdigest(),
        "table_address": "0x2000052c", "table_entries": 5,
        "icons": records, "pixel_bytes_total": 4 * 0x240,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE)},
        "object": {"path": str(OBJECT.relative_to(ROOT)), "sha256": sha(OBJECT)},
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Final placement of the initialized RAM table and adjacent words, wider icon catalog and hardware rendering remain open.",
    }
    RECEIPT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], sha(RECEIPT))


if __name__ == "__main__":
    main()
