from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_task_current.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_task_current_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

BASE = 0x00438000
START = 0x0045589C
END = 0x004558A4
CURRENT_TCB_WORD = 0x20074A20
LITERAL = 0x0045605C
STOCK_BYTES = "dff8bc0700687047"
STOCK_SHA256 = (
    "c7437c4b802c4991fe9a7bda7e790a1e252276812c72d57ef2b0db2cc18ac661"
)
TARGET_BYTES = "44f62020c2f2070000687047"
TARGET_SHA256 = (
    "1f544f3f3ad352dc5493c0588030e18636a6705a67aea031264ab89c98a3ee0b"
)
CALLERS = [
    (0x00441726, "14f0b9f8"),
    (0x00441768, "14f098f8"),
    (0x004491AC, "0cf076fb"),
    (0x0044AAEA, "0af0d7fe"),
    (0x004D46F4, "81f7d2f8"),
    (0x0057DE9A, "d7f6fffc"),
    (0x0057E1AA, "d7f677fb"),
]
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


class RuntimeFreeRTOSTaskCurrentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_freertos_task_current.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_task_current.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.set_current = (
            cls.loaded.open_cfw_test_freertos_task_current_set
        )
        cls.set_current.argtypes = [ctypes.c_size_t]
        cls.set_current.restype = None
        cls.get_current = (
            cls.loaded.open_cfw_test_freertos_task_current_get
        )
        cls.get_current.argtypes = []
        cls.get_current.restype = ctypes.c_size_t

        cls.target_object = temporary / "runtime_freertos_task_current.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.text_relocations = []
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
                    cls.text_relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            cls.parsed_symbols[information >> 8][0],
                        )
                    )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def test_official_package_and_source_snapshot_are_authenticated(
        self,
    ) -> None:
        package = OFFICIAL.read_bytes()
        self.assertEqual(len(package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(len(self.application), 3_523_364)
        self.assertEqual(
            hashlib.sha256(self.application).hexdigest(),
            "19044a72bdfeb04c6b1b104d87da7b98"
            "e13cc18928528d84d999b6bcc0ba9701",
        )
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            hashlib.sha256(UPSTREAM_TASKS.read_bytes()).hexdigest(),
            "14020d617b96dd2814e1211f6e3b645b"
            "cf5e2bd3179c23fe7dd16bc666fe9463",
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)

    def test_stock_body_bytes_hash_and_neighbors_are_exact(self) -> None:
        body = self.span(START, END)
        self.assertEqual(len(body), 8)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            hashlib.sha256(self.span(0x00455876, START)).hexdigest(),
            "a789916ee424c824c5c5f2302e62e4a8"
            "61f0fa1289917d9c0e095947bce82598",
        )
        self.assertEqual(
            hashlib.sha256(self.span(END, 0x004558C4)).hexdigest(),
            "619a0c1adee43616c7a6e9566fec269cd"
            "838c72d14e62358b80cb21fbe76ad53",
        )

    def test_stock_literal_names_the_current_tcb_word(self) -> None:
        instruction = self.span(START, START + 4)
        first, second = struct.unpack("<HH", instruction)
        self.assertEqual(first & 0xFFF0, 0xF8D0)
        self.assertEqual((first >> 7) & 1, 1)
        self.assertEqual(second >> 12, 0)
        self.assertEqual(second & 0x0FFF, 0x7BC)
        pc = (START + 4) & ~3
        self.assertEqual(pc + (second & 0x0FFF), LITERAL)
        self.assertEqual(
            struct.unpack("<I", self.span(LITERAL, LITERAL + 4))[0],
            CURRENT_TCB_WORD,
        )
        self.assertEqual(
            self.span(START + 4, END),
            bytes.fromhex("00687047"),
        )

    def test_host_candidate_returns_the_word_without_dereferencing_tcb(
        self,
    ) -> None:
        values = [0, 1, 0x20000000, 0xFFFFFFFF]
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            values.append(0x1234567887654321)
        for value in values:
            with self.subTest(value=value):
                self.set_current(value)
                self.assertEqual(self.get_current(), value)

    def test_target_candidate_is_one_bounded_relocation_free_leaf(
        self,
    ) -> None:
        function = self.symbols[
            "open_cfw_freertos_task_get_current_task_handle"
        ]
        self.assertEqual((function[1], function[2]), (1, 12))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertEqual(function[5], 2)
        self.assertEqual(self.target_text.hex(), TARGET_BYTES)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            TARGET_SHA256,
        )
        self.assertEqual(self.text_relocations, [])
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [],
        )
        self.assertEqual(
            {
                name
                for name, fields in self.symbols.items()
                if fields[3] & 0x0F == 2 and fields[5] != 0
            },
            {"open_cfw_freertos_task_get_current_task_handle"},
        )

    def test_source_is_a_pinned_upstream_algorithm_with_one_g2_seam(
        self,
    ) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "bb012d4f9eece5882eafcd05d60ed503"
            "cb6113ad6c167e6abf7132136f3cfc9c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "01629111c334a1fe5869b0f82440c2f4e"
            "ae65f01fbde978c88d33c9d71a0985b",
        )
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "xTaskGetCurrentTaskHandle()",
            "tasks.c",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x0045589C, 0x004558A4)",
            "0x20074A20U",
            "result = OPEN_CFW_FREERTOS_TASK_CURRENT_TCB",
        ):
            self.assertIn(token, source)
        for disallowed in (
            "#include",
            "struct ",
            "->",
            "typedef void (*",
        ):
            self.assertNotIn(disallowed, source)

    def test_whole_image_direct_branch_topology_is_closed(self) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        calls = []
        jumps = []
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, calls), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == START:
                    observed.append((address, encoded.hex()))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    interior.append(
                        (address, target, link, encoded.hex())
                    )
        self.assertEqual(calls, CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in CALLERS
                )
            ).hexdigest(),
            "a22105e1442e84e34d21999b89f988c6"
            "3154933abc8956da81428f09975ab464",
        )

        narrow_references = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in self.narrow_branch_targets(address, halfword):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    narrow_references.append((address, target, halfword))
        self.assertEqual(narrow_references, [])

    def test_whole_image_has_no_stored_entry_or_interior_pointer(
        self,
    ) -> None:
        raw_stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value in (START, START | 1):
                raw_stored.append((BASE + offset, value))
            if START < value < END:
                raw_stored.append((BASE + offset, value))
            if value & 1 and START < (value & ~1) < END:
                raw_stored.append((BASE + offset, value))
        self.assertEqual(raw_stored, [])

    @staticmethod
    def narrow_branch_targets(
        address: int,
        halfword: int,
    ) -> list[int]:
        if halfword & 0xF800 == 0xE000:
            immediate = halfword & 0x07FF
            if immediate & 0x0400:
                immediate -= 0x0800
            return [address + 4 + immediate * 2]
        if (
            halfword & 0xF000 == 0xD000
            and ((halfword >> 8) & 0x0F) < 0x0E
        ):
            immediate = halfword & 0x00FF
            if immediate & 0x0080:
                immediate -= 0x0100
            return [address + 4 + immediate * 2]
        if halfword & 0xF500 == 0xB100:
            immediate = (
                ((halfword >> 9) & 1) << 6
                | ((halfword >> 3) & 0x1F) << 1
            )
            return [address + 4 + immediate]
        return []


if __name__ == "__main__":
    unittest.main()
