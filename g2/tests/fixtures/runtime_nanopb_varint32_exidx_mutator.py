#!/usr/bin/env python3
"""Test-only Clang proxy that corrupts a compiled varint32 exidx companion."""

from __future__ import annotations

import os
from pathlib import Path
import struct
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


def main() -> int:
    real_clang = os.environ.get("OPENCFW_REAL_CLANG", "/usr/bin/clang")
    result = subprocess.run([real_clang, *sys.argv[1:]], check=False)
    if result.returncode:
        return result.returncode

    mode = os.environ.get("OPENCFW_EXIDX_MUTATION")
    if mode not in {"personality-data", "cross-function", "extra-relocation"}:
        return 0
    if "-o" not in sys.argv:
        return 0
    output = Path(sys.argv[sys.argv.index("-o") + 1])
    if not output.is_file() or output.suffix != ".o":
        return 0

    data, sections = apollo_overlay.parse_elf32(output)
    private_name = ".text.open_cfw_nanopb_decode_varint32_eof"
    private_sections = [item for item in sections if item["name"] == private_name]
    if not private_sections:
        return 0
    private = private_sections[0]
    companion = apollo_overlay.section_named(
        sections, ".ARM.exidx" + private_name
    )
    relocation = next(
        item for item in sections
        if int(item["type"]) == apollo_overlay.SHT_REL
        and int(item["info"]) == int(companion["index"])
    )
    mutated = bytearray(data)

    if mode == "personality-data":
        struct.pack_into("<I", mutated, int(companion["offset"]) + 4, 0x80000000)
    elif mode == "extra-relocation":
        section_table = struct.unpack_from("<I", mutated, 0x20)[0]
        section_entry_size = struct.unpack_from("<H", mutated, 0x2E)[0]
        size_field = (
            section_table + int(relocation["index"]) * section_entry_size + 20
        )
        struct.pack_into("<I", mutated, size_field, 16)
    else:
        public = apollo_overlay.section_named(
            sections, ".text.open_cfw_nanopb_decode_varint32"
        )
        symbols = apollo_overlay.parse_elf32_symbols(data, sections)
        public_section_symbols = [
            index for index, symbol in enumerate(symbols)
            if int(symbol["type"]) == apollo_overlay.STT_SECTION
            and int(symbol["binding"]) == apollo_overlay.STB_LOCAL
            and int(symbol["section_index"]) == int(public["index"])
        ]
        if len(public_section_symbols) != 1:
            raise RuntimeError(
                "cross-function mutation requires one public section symbol"
            )
        offset, information = struct.unpack_from(
            "<II", mutated, int(relocation["offset"])
        )
        struct.pack_into(
            "<II",
            mutated,
            int(relocation["offset"]),
            offset,
            (public_section_symbols[0] << 8) | (information & 0xFF),
        )

    output.write_bytes(mutated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
