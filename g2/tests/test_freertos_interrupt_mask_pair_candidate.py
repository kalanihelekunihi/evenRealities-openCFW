from __future__ import annotations

import os

import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = (
    ROOT / "research" / "candidates" / "freertos_interrupt_mask_pair.S"
)
UPSTREAM = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "portasm.s"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE_SIZE = 32
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
SET_START = 0x005F_A0A4
SET_END = 0x005F_A0BA
CLEAR_END = 0x005F_A0C8

SET_BYTES = bytes.fromhex(
    "eff31180"
    "4ff03001"
    "81f31188"
    "bff34f8f"
    "bff36f8f"
    "7047"
)
CLEAR_BYTES = bytes.fromhex(
    "80f31188"
    "bff34f8f"
    "bff36f8f"
    "7047"
)
PAIR_BYTES = SET_BYTES + CLEAR_BYTES
SET_SHA256 = (
    "f6bd0708e653c8e8880e33e298f9dc8"
    "ede1305c9386ea4ca5ff554d4022dc323"
)
CLEAR_SHA256 = (
    "97532a7902b38e1551198dd647d0fcdc"
    "3a6f19315b6491058a813c7643e0028a"
)
PAIR_SHA256 = (
    "422a4cac7b1abe90c7c7b0c431e2d85e"
    "f4d733cffb2da3b2708311f183cce849"
)
UPSTREAM_SHA256 = (
    "eaa83b3867edec5560c69f2a21facd7a"
    "ff3c0f3bfcdfc5751722375ae328ee8f"
)
CLEAR_CALLERS = (
    0x0043_C9F2,
    0x0044_1A38,
    0x0044_1B02,
    0x0044_1E5C,
    0x0044_210E,
    0x0044_212E,
    0x0044_9D96,
    0x0044_9E3C,
    0x0045_5F54,
    0x0045_6420,
    0x0047_ED6E,
    0x0057_E0E6,
)
CLEAR_CALLSITE_SHA256 = (
    "5047082ba3888cae8330f9276620611cd"
    "f412c86fee71d1cd0ffc97447fd2746"
)
CLEAR_UNALIGNED_RAW_WORD_MATCH = (0x0062_FCDF, 0x005F_A0BA)

TARGET_PROFILES = {
    "cortex-m55": [
        "--target=arm-none-eabi",
        "-mcpu=cortex-m55",
        "-mthumb",
    ],
    "overlay-compatible": [
        "--target=thumbv7em-none-eabi",
        "-mthumb",
    ],
}


class FreeRTOSInterruptMaskPairCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.objects: dict[str, Path] = {}
        for profile, target_flags in TARGET_PROFILES.items():
            output = temporary / f"{profile}.o"
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *target_flags,
                    "-ffreestanding",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-c",
                    str(CANDIDATE),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.objects[profile] = output

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def official_span(start: int, end: int) -> bytes:
        package = OFFICIAL.read_bytes()
        if hashlib.sha256(package).hexdigest() != PACKAGE_SHA256:
            raise AssertionError("official package SHA-256 drift")
        application = package[PACKAGE_PREAMBLE_SIZE:]
        if hashlib.sha256(application).hexdigest() != APPLICATION_SHA256:
            raise AssertionError("installed application SHA-256 drift")
        first = start - APPLICATION_BASE
        last = end - APPLICATION_BASE
        return application[first:last]

    def parse_object(
        self, path: Path
    ) -> tuple[bytes, dict[str, tuple[int, ...]], list[tuple[int, int, str]]]:
        data, sections = self.apollo_overlay.parse_elf32(path)
        text = self.apollo_overlay.section_named(sections, ".text")
        text_bytes = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]

        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        parsed_symbols: list[tuple[str, tuple[int, ...]]] = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = self.apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            parsed_symbols.append((name, fields))
        symbols = {name: fields for name, fields in parsed_symbols if name}

        relocations: list[tuple[int, int, str]] = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(section["offset"]) + index * 8,
                    )
                    relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            parsed_symbols[information >> 8][0],
                        )
                    )
        return text_bytes, symbols, relocations

    def test_upstream_source_and_candidate_license_are_pinned(self) -> None:
        upstream = UPSTREAM.read_bytes()
        self.assertEqual(hashlib.sha256(upstream).hexdigest(), UPSTREAM_SHA256)
        upstream_text = upstream.decode("utf-8")
        set_start = upstream_text.index("ulSetInterruptMask:")
        clear_start = upstream_text.index("vClearInterruptMask:", set_start)
        pair_end = upstream_text.index("PendSV_Handler:", clear_start)
        pair = upstream_text[set_start:pair_end]
        for fragment in (
            "mrs r0, basepri",
            "mov r1, #configMAX_SYSCALL_INTERRUPT_PRIORITY",
            "msr basepri, r1",
            "msr basepri, r0",
            "dsb",
            "isb",
            "bx lr",
        ):
            self.assertIn(fragment, pair)

        candidate = CANDIDATE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", candidate)
        self.assertIn("Permission is hereby granted", candidate)
        self.assertIn(
            "commit def7d2df2b0506d3d249334974f51e427c17a41c",
            candidate,
        )
        self.assertIn(
            "configMAX_SYSCALL_INTERRUPT_PRIORITY = 0x30",
            candidate,
        )
        self.assertIn("not registered by either production", candidate)

    def test_official_pair_boundary_and_hashes_are_exact(self) -> None:
        set_body = self.official_span(SET_START, SET_END)
        clear_body = self.official_span(SET_END, CLEAR_END)
        self.assertEqual(set_body, SET_BYTES)
        self.assertEqual(clear_body, CLEAR_BYTES)
        self.assertEqual(hashlib.sha256(set_body).hexdigest(), SET_SHA256)
        self.assertEqual(hashlib.sha256(clear_body).hexdigest(), CLEAR_SHA256)
        self.assertEqual(
            hashlib.sha256(set_body + clear_body).hexdigest(),
            PAIR_SHA256,
        )

    def test_target_profiles_emit_the_exact_closed_pair(self) -> None:
        for profile, path in self.objects.items():
            with self.subTest(profile=profile):
                text, symbols, relocations = self.parse_object(path)
                self.assertEqual(text, PAIR_BYTES)
                self.assertEqual(hashlib.sha256(text).hexdigest(), PAIR_SHA256)
                self.assertEqual(relocations, [])

                self.assertEqual(set(symbols), {
                    "$t",
                    "ulSetInterruptMask",
                    "vClearInterruptMask",
                })
                set_symbol = symbols["ulSetInterruptMask"]
                clear_symbol = symbols["vClearInterruptMask"]
                self.assertEqual(set_symbol[1] & ~1, 0)
                self.assertEqual(set_symbol[2], len(SET_BYTES))
                self.assertEqual(clear_symbol[1] & ~1, len(SET_BYTES))
                self.assertEqual(clear_symbol[2], len(CLEAR_BYTES))
                self.assertEqual(set_symbol[3], 0x12)
                self.assertEqual(clear_symbol[3], 0x12)
                self.assertEqual(set_symbol[4], 0)
                self.assertEqual(clear_symbol[4], 0)
                self.assertNotEqual(set_symbol[5], 0)
                self.assertEqual(set_symbol[5], clear_symbol[5])

    def test_target_pair_has_no_private_dependency_or_extra_code(self) -> None:
        for profile, path in self.objects.items():
            with self.subTest(profile=profile):
                text, symbols, relocations = self.parse_object(path)
                undefined = {
                    name
                    for name, fields in symbols.items()
                    if name and fields[5] == 0
                }
                self.assertEqual(undefined, set())
                self.assertEqual(relocations, [])
                self.assertEqual(len(text), 36)
                self.assertEqual(text[:22], SET_BYTES)
                self.assertEqual(text[22:], CLEAR_BYTES)

    def test_clear_leaf_reference_topology_is_bounded(self) -> None:
        import analyze_g2_freertos_assert_port_seam as seam

        package = OFFICIAL.read_bytes()
        application = package[PACKAGE_PREAMBLE_SIZE:]
        calls: list[int] = []
        jumps: list[int] = []
        interior: list[tuple[int, int]] = []
        narrow: list[tuple[int, int]] = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", application, offset)
            for link, collection in ((True, calls), (False, jumps)):
                target = seam.thumb_wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target == SET_END:
                    collection.append(address)
                if (
                    target is not None
                    and SET_END < target < CLEAR_END
                    and not SET_END <= address < CLEAR_END
                ):
                    interior.append((address, target))
        for offset in range(0, len(application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", application, offset)[0]
            for target in seam.narrow_branch_targets(address, halfword):
                if (
                    SET_END <= target < CLEAR_END
                    and not SET_END <= address < CLEAR_END
                ):
                    narrow.append((address, target))

        raw_matches: list[tuple[int, int]] = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            if SET_END <= (value & ~1) < CLEAR_END:
                raw_matches.append((APPLICATION_BASE + offset, value))

        self.assertEqual(tuple(calls), CLEAR_CALLERS)
        self.assertEqual(
            hashlib.sha256(
                b"".join(struct.pack("<I", address) for address in calls)
            ).hexdigest(),
            CLEAR_CALLSITE_SHA256,
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(narrow, [])
        self.assertEqual(raw_matches, [CLEAR_UNALIGNED_RAW_WORD_MATCH])
        self.assertNotEqual(CLEAR_UNALIGNED_RAW_WORD_MATCH[0] & 0x3, 0)


if __name__ == "__main__":
    unittest.main()
