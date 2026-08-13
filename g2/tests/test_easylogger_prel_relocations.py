from __future__ import annotations

import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))

import apollo_overlay  # noqa: E402


BUILDER_SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_easylogger_async_record_build_stock.c"
)
OUTPUT_SOURCE = (
    ROOT
    / "components"
    / "shared"
    / "easylogger"
    / "runtime_easylogger_output_candidate.c"
)

COMMON_FLAGS = [
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

PROFILES = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0",
        "builder": {
            "text_size": 228,
            "text_sha256": (
                "dce01b3325dc6e08acc71c5497238460f"
                "679058d75d5b1e99d0df9e5fb5cb00a"
            ),
            "pair_count": 1,
            "inventory_sha256": (
                "27f0b750eec02dbcaacff923e1da7cdd"
                "f88a845eefb15e6a327655cf5b82609c"
            ),
            "first": (
                ".text:00D0:open_cfw_g2_easylogger_async_enqueue_error:"
                "0:-12:-8:F64F70F4:F6CF70F8"
            ),
        },
        "output": {
            "text_size": 1614,
            "text_sha256": (
                "479d6304345334af023d5a1ee464a88b"
                "76e05b6d93596c3addc186df516a25dc"
            ),
            "pair_count": 32,
            "inventory_sha256": (
                "7d78748d9c8a02685558d889b7d8752c"
                "db1410b71e05d6d0580d88527b59caf2"
            ),
            "first": (
                ".text.open_cfw_easylogger_output:002C:.L.str:"
                "0:-20:-16:F64F70EC:F6CF70F0"
            ),
            "last": (
                ".text.open_cfw_easylogger_output:0628:.L.str.13:"
                "2:-14:-10:F64F72F2:F6CF72F6"
            ),
        },
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "builder": {
            "text_size": 222,
            "text_sha256": (
                "f0450e46b276e5d61334e2931c8441af"
                "9fe9105649434573a25ab3c4d8301f2c"
            ),
            "pair_count": 1,
            "inventory_sha256": (
                "9b75a26337e9d507d8de415b071b80ac"
                "29cb0fa74c5a7cae8bec5d73930b2f63"
            ),
            "first": (
                ".text:00CA:open_cfw_g2_easylogger_async_enqueue_error:"
                "0:-12:-8:F64F70F4:F6CF70F8"
            ),
        },
        "output": {
            "text_size": 1618,
            "text_sha256": (
                "315168b42e7f58b9bc9b14a47511866f"
                "8fffa930f8eb8499631cab34d9ade958"
            ),
            "pair_count": 32,
            "inventory_sha256": (
                "642bd01d79860b25e216808750c57670"
                "a63a19e44953916a8687cdaaaffe46a0"
            ),
            "first": (
                ".text.open_cfw_easylogger_output:002C:.L.str:"
                "0:-20:-16:F64F70EC:F6CF70F0"
            ),
            "last": (
                ".text.open_cfw_easylogger_output:062C:.L.str.13:"
                "2:-14:-10:F64F72F2:F6CF72F6"
            ),
        },
    },
}


class EasyLoggerPrelRelocationInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("OPENCFW_CLANG")
        cls.clang = configured or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        matches = [
            name
            for name, profile in PROFILES.items()
            if version.startswith(str(profile["version"]))
        ]
        if len(matches) != 1:
            raise unittest.SkipTest(f"unreviewed compiler: {version}")
        cls.profile_name = matches[0]
        cls.profile = PROFILES[cls.profile_name]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        cls.objects = {}
        for name, source, extra_flags in (
            ("builder", BUILDER_SOURCE, []),
            (
                "output",
                OUTPUT_SOURCE,
                ["-ffunction-sections", "-fdata-sections"],
            ),
        ):
            output = temporary / f"{name}.o"
            subprocess.run(
                [
                    cls.clang,
                    *COMMON_FLAGS,
                    *extra_flags,
                    "-c",
                    str(source),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.objects[name] = output

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def _inventory(
        self,
        object_path: Path,
        *,
        text_section_name: str,
        rodata_section_name: str,
    ) -> tuple[bytes, list[str]]:
        data, sections = apollo_overlay.parse_elf32(object_path)
        symbols = apollo_overlay.parse_elf32_symbols(data, sections)
        text = apollo_overlay.section_named(sections, text_section_name)
        text_bytes = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        rodata = apollo_overlay.section_named(sections, rodata_section_name)
        records: list[str] = []
        entries: list[tuple[int, int, int]] = []
        for relocation_section in sections:
            if (
                int(relocation_section["type"]) != apollo_overlay.SHT_REL
                or int(relocation_section["info"]) != int(text["index"])
            ):
                continue
            self.assertEqual(int(relocation_section["entry_size"]), 8)
            for index in range(int(relocation_section["size"]) // 8):
                offset, info = struct.unpack_from(
                    "<II",
                    data,
                    int(relocation_section["offset"]) + index * 8,
                )
                if info & 0xFF in (
                    apollo_overlay.R_ARM_THM_MOVW_PREL_NC,
                    apollo_overlay.R_ARM_THM_MOVT_PREL,
                ):
                    entries.append((offset, info & 0xFF, info >> 8))
        entries.sort()
        self.assertEqual(len(entries) % 2, 0)
        for index in range(0, len(entries), 2):
            low_offset, low_type, low_symbol_index = entries[index]
            high_offset, high_type, high_symbol_index = entries[index + 1]
            self.assertEqual(low_type, apollo_overlay.R_ARM_THM_MOVW_PREL_NC)
            self.assertEqual(high_type, apollo_overlay.R_ARM_THM_MOVT_PREL)
            self.assertEqual(high_offset, low_offset + 4)
            self.assertEqual(high_symbol_index, low_symbol_index)
            self.assertLess(low_symbol_index, len(symbols))
            symbol = symbols[low_symbol_index]
            self.assertEqual(int(symbol["section_index"]), int(rodata["index"]))
            self.assertEqual(int(symbol["binding"]), apollo_overlay.STB_LOCAL)
            self.assertEqual(int(symbol["type"]), apollo_overlay.STT_OBJECT)
            self.assertEqual(int(symbol["visibility"]), 0)

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
            self.assertEqual((high_second >> 8) & 0x0F, register)
            low_addend = apollo_overlay.thumb_movwt_immediate(
                low_first,
                low_second,
            )
            high_addend = apollo_overlay.thumb_movwt_immediate(
                high_first,
                high_second,
            )
            if low_addend & 0x8000:
                low_addend -= 0x10000
            if high_addend & 0x8000:
                high_addend -= 0x10000
            self.assertEqual(high_addend, low_addend + 4)
            records.append(
                f"{text_section_name}:{low_offset:04X}:{symbol['name']}:"
                f"{register}:{low_addend}:{high_addend}:"
                f"{low_first:04X}{low_second:04X}:"
                f"{high_first:04X}{high_second:04X}"
            )
        return text_bytes, records

    def test_builder_and_output_prel_pair_inventories_are_exact(self) -> None:
        for name, text_section, rodata_section in (
            ("builder", ".text", ".rodata"),
            (
                "output",
                ".text.open_cfw_easylogger_output",
                ".rodata.str1.1",
            ),
        ):
            with self.subTest(profile=self.profile_name, closure=name):
                text_bytes, records = self._inventory(
                    self.objects[name],
                    text_section_name=text_section,
                    rodata_section_name=rodata_section,
                )
                expected = self.profile[name]
                self.assertEqual(len(text_bytes), expected["text_size"])
                self.assertEqual(
                    hashlib.sha256(text_bytes).hexdigest(),
                    expected["text_sha256"],
                )
                self.assertEqual(len(records), expected["pair_count"])
                inventory = "\n".join(records).encode("utf-8")
                self.assertEqual(
                    hashlib.sha256(inventory).hexdigest(),
                    expected["inventory_sha256"],
                )
                self.assertEqual(records[0], expected["first"])
                self.assertEqual(records[-1], expected.get("last", records[0]))


if __name__ == "__main__":
    unittest.main()
