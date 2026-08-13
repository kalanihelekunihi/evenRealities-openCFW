#!/usr/bin/env python3
"""Focused qualification for the excluded nanopb varint32 EOF decoder."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components/shared/nanopb"
    / "runtime_nanopb_decode_varint32_eof_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_nanopb_decode_varint32_eof_candidate_host.c"
)
AUDIT = (
    ROOT / "docs/research"
    / "nanopb-decode-varint32-eof-source-candidate-audit.md"
)
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
CONFIG = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"

PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
PACKAGE_PIN = (
    3_523_396,
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
)
BOOT_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
)
STOCK_SPAN = (0x0048_F4B8, 0x0048_F5AE)
STOCK_SHA256 = (
    "8583fa17383d72bbdcab6c2a7a20369dc0598d3ac3061feaf8a7b29dfa520150"
)
CALLERS = (0x0048_F5B2, 0x0048_F682)
READBYTE = 0x0048_F454
OUTGOING = ((0x0048_F4C4, READBYTE), (0x0048_F4FA, READBYTE))
ERROR_SLOT = 0x0048_FC84
SECOND_ERROR_SLOT = 0x0049_0114
ERROR_ADDRESS = 0x0078_7C80
ERROR_BYTES = b"varint overflow\0"
ERROR_LITERAL_REFS = (0x0048_F54C, 0x0048_F588, 0x0048_F738)
UPSTREAM_DEFINITION = (
    5762,
    7483,
    "66833ae2defb892aa17162625ef107bda03be44e73f0b120d48e6d2b52770e2c",
)
POINT_RELEASE_DEFINITIONS = {
    "0.4.7": (
        "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba", 5676, 7397,
        UPSTREAM_DEFINITION[2],
    ),
    "0.4.8": (
        "6cfe48d6f1593f8fa5c0f90437f5e6522587745e", 5676, 7397,
        UPSTREAM_DEFINITION[2],
    ),
    "0.4.9": (
        "98bf4db69897b53434f3d0ba72e0a3ab1a902824", 5762, 7483,
        UPSTREAM_DEFINITION[2],
    ),
}
LOCAL_PINS = {
    SOURCE: (
        3310,
        "eb70e18cdd87847926e547390ad1eec29b951e8535435d3f0c07d2b52fee5acd",
    ),
    HEADER: (
        2014,
        "0425d6fff4ce208bf0dcec5bfe4ad95a326201f1519870fa526a50b1108268fa",
    ),
    FIXTURE: (
        7344,
        "8ea8bfe667df85765a690276fd1e7beb1ebbad3915cdf8dd2750f8ad13c2c8fa",
    ),
    AUDIT: (
        4835,
        "237dd95f19a548f827b48b85c13bf6ddca7063b0aec28e494dace60ecea00e5a",
    ),
}
FUNCTION = "open_cfw_nanopb_decode_varint32_eof_source_candidate"
READBYTE_SYMBOL = "open_cfw_nanopb_readbyte"
ERROR_SYMBOL = "open_cfw_nanopb_varint32_overflow_error"
SECTION = ".text." + FUNCTION
RODATA_SECTION = ".rodata." + ERROR_SYMBOL
APPLE_CLANG = "/usr/bin/clang"
APPLE_VERSION = "Apple clang version 21.0.0 (clang-2100.3.30.1)"
OBJECT_PIN = (
    1328,
    "1e83fc04ec39e95c96189dbca42b902dd3bfaead5f08068eb33edc4b6aad54a6",
)
TEXT_PIN = (
    216,
    "557a878baea647ded461e093abe1d1a1c6f3d84820fae2d15f7513f27f122326",
)
RODATA_PIN = (
    16,
    "e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d",
)
TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if (first >> 6) & 0x0F >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        sign << 20
        | ((second >> 11) & 1) << 19
        | ((second >> 13) & 1) << 18
        | (first & 0x003F) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 21
    return address + 4 + immediate


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if halfword & 0xF000 == 0xD000 and (halfword >> 8) & 0x0F < 0x0E:
        immediate = halfword & 0xFF
        if immediate & 0x80:
            immediate -= 0x100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + immediate * 2,)
    return ()


def literal_target(address: int, first: int, second: int) -> int | None:
    pc = (address + 4) & ~3
    if first & 0xF800 == 0x4800:
        return pc + (first & 0xFF) * 4
    if first in (0xF8DF, 0xF85F):
        displacement = second & 0x0FFF
        return pc + displacement if first == 0xF8DF else pc - displacement
    return None


class NanopbDecodeVarint32EofCandidateTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        if cls.clang != APPLE_CLANG or version != APPLE_VERSION:
            raise AssertionError(f"unreviewed target compiler: {cls.clang}: {version}")

        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-decode-varint32-eof-candidate-"
        )
        temporary = Path(cls.temporary.name)
        cls.objects = [temporary / "candidate-a.o", temporary / "candidate-b.o"]
        for output in cls.objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )

        library = temporary / (
            "decode-varint32-eof.dylib"
            if sys.platform == "darwin" else "decode-varint32-eof.so"
        )
        command = [
            cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT), "-I", str(SNAPSHOT), "-include", str(CONFIG),
            str(SOURCE), str(FIXTURE), str(UPSTREAM),
            str(SNAPSHOT / "pb_common.c"),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.host_test = (
            cls.library.open_cfw_test_nanopb_decode_varint32_eof_candidate
        )
        cls.host_test.argtypes = []
        cls.host_test.restype = ctypes.c_int

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import analyze_g2_nanopb_point_release
        cls.apollo_overlay = apollo_overlay
        cls.release_audit = analyze_g2_nanopb_point_release
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_upstream_and_local_files_are_exact(self) -> None:
        for path, expected in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual((path.stat().st_size, sha256(path)), expected)

        start, end, digest = UPSTREAM_DEFINITION
        definition = UPSTREAM.read_bytes()[start:end]
        self.assertTrue(
            definition.startswith(
                b"static bool checkreturn pb_decode_varint32_eof("
            )
        )
        self.assertTrue(definition.endswith(b"*dest = result;\n   return true;\n}"))
        self.assertEqual((len(definition), sha256(definition)), (1721, digest))
        self.assertEqual(
            (UPSTREAM.stat().st_size, sha256(UPSTREAM)),
            (
                53_845,
                "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a",
            ),
        )

        for release, (commit, span_start, span_end, span_digest) in (
            POINT_RELEASE_DEFINITIONS.items()
        ):
            with self.subTest(release=release):
                record = self.release_audit.UPSTREAM_RELEASES[release]
                self.assertEqual(record["commit"], commit)
                self.assertEqual(span_end - span_start, 1721)
                self.assertEqual(span_digest, digest)

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["upstream"]["selected_tag"], "nanopb-0.4.9")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            POINT_RELEASE_DEFINITIONS["0.4.9"][0],
        )

    def test_candidate_is_absent_from_every_production_registration(self) -> None:
        source_path = SOURCE.relative_to(ROOT).as_posix()
        for path in (OVERLAY, MANIFEST, MAKEFILE, PROVENANCE, VERIFIER):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(source_path, text, path)
            self.assertNotIn(FUNCTION, text, path)
        self.assertTrue(SOURCE.name.endswith("_candidate.c"))
        self.assertTrue(HEADER.name.endswith("_candidate.h"))

    def test_stock_boundary_callers_and_outgoing_closure_are_exact(self) -> None:
        self.assertEqual((len(self.package), sha256(self.package)), PACKAGE_PIN)
        start, end = STOCK_SPAN
        body = self.application[start - APPLICATION_BASE:end - APPLICATION_BASE]
        self.assertEqual(len(body), 246)
        self.assertEqual(sha256(body), STOCK_SHA256)

        ingress = {"bl": [], "bw": [], "conditional": [], "narrow": []}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for name, target in (
                ("bl", wide_branch_target(address, first, second, link=True)),
                ("bw", wide_branch_target(address, first, second, link=False)),
                ("conditional", wide_conditional_target(address, first, second)),
            ):
                if target is not None and start <= target < end:
                    ingress[name].append((address, target))
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            if start <= address < end:
                continue
            for target in narrow_targets(
                address,
                struct.unpack_from("<H", self.application, offset)[0],
            ):
                if start <= target < end:
                    ingress["narrow"].append((address, target))
        self.assertEqual(
            ingress["bl"],
            [(address, start) for address in CALLERS],
        )
        self.assertEqual(ingress["bw"], [])
        self.assertEqual(ingress["conditional"], [])
        self.assertEqual(ingress["narrow"], [])

        pointers = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if start <= (value & ~1) < end:
                pointers.append((APPLICATION_BASE + offset, value, offset % 4))
        self.assertEqual(pointers, [])

        outgoing = []
        for offset in range(0, len(body) - 3, 2):
            target = wide_branch_target(
                start + offset,
                *struct.unpack_from("<HH", body, offset),
                link=True,
            )
            if target is not None:
                outgoing.append((start + offset, target))
        self.assertEqual(tuple(outgoing), OUTGOING)

    def test_stock_overflow_data_seam_is_exact(self) -> None:
        slots = []
        for offset in range(len(self.application) - 3):
            if struct.unpack_from("<I", self.application, offset)[0] == ERROR_ADDRESS:
                slots.append((APPLICATION_BASE + offset, offset % 4))
        self.assertEqual(slots, [(ERROR_SLOT, 0), (SECOND_ERROR_SLOT, 0)])

        refs = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            if literal_target(address, first, second) == ERROR_SLOT:
                refs.append(address)
        self.assertEqual(tuple(refs), ERROR_LITERAL_REFS)
        self.assertEqual(
            [address for address in refs if STOCK_SPAN[0] <= address < STOCK_SPAN[1]],
            [0x0048_F54C, 0x0048_F588],
        )

        positions = []
        cursor = 0
        while True:
            cursor = self.application.find(ERROR_BYTES, cursor)
            if cursor < 0:
                break
            positions.append(APPLICATION_BASE + cursor)
            cursor += 1
        self.assertEqual(positions, [ERROR_ADDRESS])

    def test_abi_and_optional_eof_contract_are_explicit(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertEqual(source.count("open_cfw_nanopb_readbyte(stream, &byte)"), 2)
        self.assertIn("stream->bytes_left == 0U && eof != NULL", source)
        self.assertIn("*eof = true", source)
        self.assertNotIn("*eof = false", source)
        self.assertIn('"varint overflow"', source)
        self.assertIn("stream->errmsg == NULL", source)
        self.assertIn("sizeof(bool) == 1U", header)
        self.assertIn("sizeof(uint8_t) == 1U", header)
        self.assertIn("sizeof(uint32_t) == 4U", header)
        self.assertIn("0x0048F454", header)
        self.assertIn("0x00787C80", header)

    def test_no_authenticated_bootloader_homolog(self) -> None:
        boot = BOOT.read_bytes()
        self.assertEqual((len(boot), sha256(boot)), BOOT_PIN)
        start, end = STOCK_SPAN
        body = self.application[start - APPLICATION_BASE:end - APPLICATION_BASE]
        self.assertNotIn(body, boot)
        self.assertNotIn(body[:12], boot)
        self.assertNotIn(body[-12:], boot)

    def test_host_behavior_matches_authenticated_upstream_contract(self) -> None:
        self.assertEqual(self.host_test(), 0)

    def test_target_object_and_relocation_closure_are_exact(self) -> None:
        self.assertEqual(self.objects[0].read_bytes(), self.objects[1].read_bytes())
        for path in self.objects:
            self.assertEqual((path.stat().st_size, sha256(path)), OBJECT_PIN)
        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        executable = [
            section["name"] for section in sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x4
        ]
        self.assertEqual(executable, [SECTION])
        writable = [
            section["name"] for section in sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x3 == 0x3
        ]
        self.assertEqual(writable, [])

        text = next(section for section in sections if section["name"] == SECTION)
        text_body = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        self.assertEqual((len(text_body), sha256(text_body)), TEXT_PIN)
        self.assertEqual(int(text["alignment"]), 4)
        rodata = next(
            section for section in sections if section["name"] == RODATA_SECTION
        )
        rodata_body = data[
            int(rodata["offset"]):int(rodata["offset"]) + int(rodata["size"])
        ]
        self.assertEqual((len(rodata_body), sha256(rodata_body)), RODATA_PIN)
        self.assertEqual(rodata_body, ERROR_BYTES)
        self.assertEqual(int(rodata["alignment"]), 1)

        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symbol_table["offset"]) + index * 16
            )
            symbols.append(
                (self.apollo_overlay.elf_string(strings, fields[0], "symbol"), fields)
            )
        undefined = [name for name, fields in symbols if name and fields[5] == 0]
        self.assertEqual(undefined, [READBYTE_SYMBOL])

        relocations = {}
        for section in sections:
            if int(section["type"]) != 9:
                continue
            target = sections[int(section["info"])]["name"]
            records = []
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II", data, int(section["offset"]) + index * 8
                )
                records.append(
                    (offset, information & 0xFF, symbols[information >> 8][0])
                )
            relocations[target] = records
        self.assertEqual(
            relocations,
            {
                SECTION: [
                    (16, 10, READBYTE_SYMBOL),
                    (106, 10, READBYTE_SYMBOL),
                    (204, 47, ERROR_SYMBOL),
                    (208, 48, ERROR_SYMBOL),
                ],
                ".ARM.exidx" + SECTION: [(0, 42, "")],
            },
        )


if __name__ == "__main__":
    unittest.main()
