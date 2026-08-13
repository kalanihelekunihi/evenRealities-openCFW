from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import apollo_overlay  # noqa: E402


TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-Wall",
    "-Wextra",
    "-Werror",
]
SOURCES = {
    "builder": (
        ROOT
        / "components"
        / "apollo_main"
        / "core_overlay"
        / "runtime_easylogger_async_record_build_stock.c",
        ".text",
        [],
    ),
    "output": (
        ROOT
        / "components"
        / "shared"
        / "easylogger"
        / "runtime_easylogger_output_candidate.c",
        ".text.open_cfw_easylogger_output",
        ["-ffunction-sections", "-fdata-sections"],
    ),
}
PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0",
        "builder": {
            "count": 1,
            "sha256": (
                "6b16cb7207a603e404d4b4f49c152961"
                "3ebf70167e396c93f4c72b080a6bc49b"
            ),
            "addends": [-12, -8],
            "first": {
                "symbol": "open_cfw_g2_easylogger_async_enqueue_error",
                "low_offset": 208,
                "high_offset": 212,
                "low_raw": "4ff6f470",
                "high_raw": "cff6f870",
                "low_addend": -12,
                "high_addend": -8,
                "register": 0,
                "anchor": -220,
            },
        },
        "output": {
            "count": 32,
            "sha256": (
                "65769a503f7003ecc824eb3e857951f7"
                "1bcb1f531e53ab93952b8463eb6c73a5"
            ),
            "addends": [-24, -20, -18, -16, -14, -12, -10, -8],
        },
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "builder": {
            "count": 1,
            "sha256": (
                "772e279d3091f05da6fb59354aa17870"
                "1cb5e48016afa11d698926f2c2e7ddad"
            ),
            "addends": [-12, -8],
            "first": {
                "symbol": "open_cfw_g2_easylogger_async_enqueue_error",
                "low_offset": 202,
                "high_offset": 206,
                "low_raw": "4ff6f470",
                "high_raw": "cff6f870",
                "low_addend": -12,
                "high_addend": -8,
                "register": 0,
                "anchor": -214,
            },
        },
        "output": {
            "count": 32,
            "sha256": (
                "3a00628246d540f9fe74482a4ad41969"
                "e05eb78d6118df6dc28dca358ca491c0"
            ),
            "addends": [-28, -24, -22, -20, -18, -16, -14, -12, -10, -8],
        },
    },
}


def signed_movwt_addend(first: int, second: int) -> int:
    value = apollo_overlay.thumb_movwt_immediate(first, second)
    return value - 0x10000 if value & 0x8000 else value


class PrelMovwtInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        for profile, pins in PINS.items():
            if version.startswith(pins["version"]):
                cls.profile = profile
                break
        else:
            raise AssertionError(f"unreviewed target compiler: {version!r}")

    def compile_inventory(
        self,
        temporary: Path,
        name: str,
    ) -> list[dict[str, int | str]]:
        source, text_section_name, extra_flags = SOURCES[name]
        object_path = temporary / f"{name}.o"
        subprocess.run(
            [
                self.clang,
                *TARGET_FLAGS,
                *extra_flags,
                "-c",
                str(source),
                "-o",
                str(object_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        data, sections = apollo_overlay.parse_elf32(object_path)
        symbols = apollo_overlay.parse_elf32_symbols(data, sections)
        text = apollo_overlay.section_named(sections, text_section_name)
        start = int(text["offset"])
        text_bytes = data[start:start + int(text["size"])]
        records: list[tuple[int, int, int]] = []
        for section in sections:
            if (
                int(section["type"]) != apollo_overlay.SHT_REL
                or int(section["info"]) != int(text["index"])
            ):
                continue
            for index in range(int(section["size"]) // 8):
                offset, info = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + index * 8,
                )
                if info & 0xFF in (
                    apollo_overlay.R_ARM_THM_MOVW_PREL_NC,
                    apollo_overlay.R_ARM_THM_MOVT_PREL,
                ):
                    records.append((offset, info & 0xFF, info >> 8))

        inventory = []
        index = 0
        while index < len(records):
            low_offset, low_type, symbol_index = records[index]
            self.assertEqual(
                low_type,
                apollo_overlay.R_ARM_THM_MOVW_PREL_NC,
            )
            self.assertLess(index + 1, len(records))
            high_offset, high_type, high_symbol_index = records[index + 1]
            self.assertEqual(high_type, apollo_overlay.R_ARM_THM_MOVT_PREL)
            self.assertEqual(high_offset, low_offset + 4)
            self.assertEqual(high_symbol_index, symbol_index)
            low_first, low_second = struct.unpack_from(
                "<HH", text_bytes, low_offset
            )
            high_first, high_second = struct.unpack_from(
                "<HH", text_bytes, high_offset
            )
            self.assertEqual(low_first & 0xFBF0, 0xF240)
            self.assertEqual(high_first & 0xFBF0, 0xF2C0)
            self.assertFalse(low_second & 0x8000)
            self.assertFalse(high_second & 0x8000)
            register = (low_second >> 8) & 0x0F
            self.assertEqual(register, (high_second >> 8) & 0x0F)
            low_addend = signed_movwt_addend(low_first, low_second)
            high_addend = signed_movwt_addend(high_first, high_second)
            anchor = low_addend - low_offset
            self.assertEqual(anchor, high_addend - high_offset)
            inventory.append(
                {
                    "symbol": str(symbols[symbol_index]["name"]),
                    "low_offset": low_offset,
                    "high_offset": high_offset,
                    "low_raw": text_bytes[low_offset:low_offset + 4].hex(),
                    "high_raw": text_bytes[high_offset:high_offset + 4].hex(),
                    "low_addend": low_addend,
                    "high_addend": high_addend,
                    "register": register,
                    "anchor": anchor,
                }
            )
            index += 2
        return inventory

    def test_every_builder_and_output_prel_pair_is_authenticated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            for name in SOURCES:
                with self.subTest(profile=self.profile, source=name):
                    inventory = self.compile_inventory(temporary, name)
                    encoded = json.dumps(
                        inventory,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode()
                    pins = PINS[self.profile][name]
                    self.assertEqual(len(inventory), pins["count"])
                    self.assertEqual(hashlib.sha256(encoded).hexdigest(), pins["sha256"])
                    self.assertEqual(
                        sorted(
                            {
                                addend
                                for item in inventory
                                for addend in (
                                    item["low_addend"],
                                    item["high_addend"],
                                )
                            }
                        ),
                        pins["addends"],
                    )
                    if "first" in pins:
                        self.assertEqual(inventory[0], pins["first"])


if __name__ == "__main__":
    unittest.main()
