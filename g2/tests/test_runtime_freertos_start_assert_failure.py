from __future__ import annotations

import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_start_assert_failure.c"
HEADER = SOURCE.with_suffix(".h")
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
FUNCTION = "open_cfw_freertos_start_assert_failure"

FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]
PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.33.1)",
        "object": (1044, "c280bcff8209f3da27a339a120bce56a996f1c90c8fccf7e9e379b832f6f3557"),
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (1024, "afe647685a9546ddde00f53822f6a19bcfe924836b622519ac34fa4802e0136b"),
    },
}
FUNCTION_PIN = (14, 4, "163edbeed4884668008114837339202f2c9f7ca1aca9a651690b8bca0035d8cb")
SOURCE_PIN = (814, "ea369efd6eb8b7270b96462a3e540655301345e2f0e6aee5817d2d929cf2bff9")
HEADER_PIN = (236, "bad0072522217197e48459f9e05984a5f9e9317ed5fa854e558d174210344a95")


class FreeRTOSStartAssertFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.profile = os.environ.get(
            "OPENCFW_TOOLCHAIN_PROFILE",
            "apple-clang" if sys.platform == "darwin" else "linux-clang",
        )
        cls.object_path = Path(cls.temporary.name) / "assert.o"
        subprocess.run(
            [cls.clang, *FLAGS, "-c", str(SOURCE), "-o", str(cls.object_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_fail_stop_source_is_explicit_and_nonreturning(self) -> None:
        source = SOURCE.read_text()
        header = HEADER.read_text()
        self.assertIn("ulSetInterruptMask", source)
        self.assertIn("(open_cfw_freertos_assert_uintptr)-1", source)
        self.assertIn("for (;;) {", source)
        self.assertIn("__attribute__((noreturn))", header)

    def test_target_object_and_only_outgoing_relocation_are_pinned(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(self.object_path)
        section = apollo_overlay.section_named(sections, ".text." + FUNCTION)
        body = data[
            int(section["offset"]):int(section["offset"]) + int(section["size"])
        ]
        symtab = apollo_overlay.section_named(sections, ".symtab")
        strtab = sections[int(symtab["link"])]
        strings = data[
            int(strtab["offset"]):int(strtab["offset"]) + int(strtab["size"])
        ]
        symbols = []
        for index in range(int(symtab["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symtab["offset"]) + index * 16
            )
            symbols.append(apollo_overlay.elf_string(strings, fields[0], "symbol"))
        relocations = []
        for relocation_section in sections:
            if (
                int(relocation_section["type"]) == 9
                and int(relocation_section["info"]) == int(section["index"])
            ):
                for index in range(int(relocation_section["size"]) // 8):
                    offset, info = struct.unpack_from(
                        "<II", data, int(relocation_section["offset"]) + index * 8
                    )
                    relocations.append((offset, info & 0xFF, symbols[info >> 8]))
        pin = PINS[self.profile]
        self.assertEqual(self.version, pin["version"])
        self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), pin["object"])
        self.assertEqual(
            (len(body), int(section["alignment"]), hashlib.sha256(body).hexdigest()),
            FUNCTION_PIN,
        )
        self.assertEqual(relocations, [(0, 10, "ulSetInterruptMask")])

    def test_artifacts_are_pinned_and_production_routed(self) -> None:
        for path, expected in ((SOURCE, SOURCE_PIN), (HEADER, HEADER_PIN)):
            body = path.read_bytes()
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), expected)
        self.assertIn(str(SOURCE.relative_to(ROOT)), OVERLAY.read_text())
        self.assertIn(FUNCTION, OVERLAY.read_text())
        self.assertIn("freertos_start_assert_failure_source_text", MANIFEST.read_text())
        self.assertIn("freertos-scheduler-start-core-closure", MAKEFILE.read_text())


if __name__ == "__main__":
    unittest.main()
