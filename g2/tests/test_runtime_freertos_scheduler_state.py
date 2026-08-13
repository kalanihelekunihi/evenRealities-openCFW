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
    / "runtime_freertos_scheduler_state.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_scheduler_state_host.c"
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
START = 0x004558A4
END = 0x004558C4
RUNNING_WORD = 0x20074A3C
SUSPENDED_WORD = 0x20074A58
RUNNING_LITERAL = 0x00456064
SUSPENDED_LITERAL = 0x00456068
STOCK_BYTES = (
    "dff8bc070068002801d1012007e0dff8"
    "b4070068002801d1022000e000207047"
)
STOCK_SHA256 = (
    "619a0c1adee43616c7a6e9566fec269cd838c72d14e62358b80cb21fbe76ad53"
)
TARGET_BYTES = (
    "44f63c20c2f207000168002904bf0120"
    "7047c06900284ff0000008bf02207047"
)
TARGET_SHA256 = (
    "93ec039f8b8fd056e62524a8ae691c9e0cbe2be878b2610347deb960d930fe2c"
)
CALLERS = [
    (0x00441852, "14f027f8"),
    (0x00441B48, "13f0acfe"),
    (0x00441C74, "13f016fe"),
    (0x0044901E, "0cf041fc"),
    (0x0044904C, "0cf02afc"),
    (0x0044906E, "0cf019fc"),
    (0x004490A4, "0cf0fefb"),
    (0x0044AAE2, "0af0dffe"),
    (0x0047E7DE, "d7f761f8"),
    (0x0047EC44, "d6f72efe"),
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


class RuntimeFreeRTOSSchedulerStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_freertos_scheduler_state.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_scheduler_state.so"
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
        cls.set_state = (
            cls.loaded.open_cfw_test_freertos_scheduler_state_set
        )
        cls.set_state.argtypes = [ctypes.c_int32, ctypes.c_uint32]
        cls.set_state.restype = None
        cls.get_state = (
            cls.loaded.open_cfw_test_freertos_scheduler_state_get
        )
        cls.get_state.argtypes = []
        cls.get_state.restype = ctypes.c_int32
        cls.running_reads = (
            cls.loaded.open_cfw_test_freertos_scheduler_state_running_reads
        )
        cls.running_reads.argtypes = []
        cls.running_reads.restype = ctypes.c_uint32
        cls.suspended_reads = (
            cls.loaded.open_cfw_test_freertos_scheduler_state_suspended_reads
        )
        cls.suspended_reads.argtypes = []
        cls.suspended_reads.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_freertos_scheduler_state.o"
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
        self.assertEqual(len(body), 32)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            hashlib.sha256(self.span(0x0045589C, START)).hexdigest(),
            "c7437c4b802c4991fe9a7bda7e790a1e"
            "252276812c72d57ef2b0db2cc18ac661",
        )
        self.assertEqual(
            self.span(END, 0x004558CC).hex(),
            "00000000a03d0020",
        )
        self.assertEqual(
            hashlib.sha256(self.span(END, 0x004558CC)).hexdigest(),
            "100260c9dee102e78bd4e6abef6f51428"
            "506ae5d24384ab87fa2e44b42244bbe",
        )

    def test_stock_literals_name_both_scheduler_global_words(self) -> None:
        first, second = struct.unpack("<HH", self.span(START, START + 4))
        self.assertEqual(first, 0xF8DF)
        self.assertEqual(second, 0x07BC)
        first_target = ((START + 4) & ~3) + (second & 0x0FFF)
        self.assertEqual(first_target, RUNNING_LITERAL)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(RUNNING_LITERAL, RUNNING_LITERAL + 4),
            )[0],
            RUNNING_WORD,
        )

        second_start = 0x004558B2
        first, second = struct.unpack(
            "<HH",
            self.span(second_start, second_start + 4),
        )
        self.assertEqual(first, 0xF8DF)
        self.assertEqual(second, 0x07B4)
        second_target = (
            ((second_start + 4) & ~3) + (second & 0x0FFF)
        )
        self.assertEqual(second_target, SUSPENDED_LITERAL)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(SUSPENDED_LITERAL, SUSPENDED_LITERAL + 4),
            )[0],
            SUSPENDED_WORD,
        )
        self.assertEqual(
            self.span(RUNNING_LITERAL, SUSPENDED_LITERAL + 4).hex(),
            "3c4a0720584a0720",
        )

    def test_stock_global_writer_seams_confirm_running_and_depth_roles(
        self,
    ) -> None:
        self.assertEqual(
            self.span(0x00454D4A, 0x00454D52).hex(),
            "0120dff8c4150860",
        )
        running_literal = (
            ((0x00454D4C + 4) & ~3) + 0x5C4
        )
        self.assertEqual(running_literal, 0x00455314)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(running_literal, running_literal + 4),
            )[0],
            RUNNING_WORD,
        )

        self.assertEqual(
            self.span(0x00454D7C, 0x00454D88).hex(),
            "dff8e8060168491c01607047",
        )
        suspended_literal = (
            ((0x00454D7C + 4) & ~3) + 0x6E8
        )
        self.assertEqual(suspended_literal, 0x00455468)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(suspended_literal, suspended_literal + 4),
            )[0],
            SUSPENDED_WORD,
        )
        self.assertEqual(
            self.span(0x00454DD2, 0x00454DF4).hex(),
            "dff894663068002806d1a5f162f90020"
            "5ff0ff310860fee7edf771f93068401e3060",
        )
        resume_literal = (
            ((0x00454DD2 + 4) & ~3) + 0x694
        )
        self.assertEqual(resume_literal, suspended_literal)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(resume_literal, resume_literal + 4),
            )[0],
            SUSPENDED_WORD,
        )

    def test_host_candidate_preserves_truth_table_and_load_order(
        self,
    ) -> None:
        cases = [
            (0, 0, 1, 1, 0),
            (0, 1, 1, 1, 0),
            (0, 0xFFFFFFFF, 1, 1, 0),
            (1, 0, 2, 1, 1),
            (1, 1, 0, 1, 1),
            (1, 2, 0, 1, 1),
            (-1, 0, 2, 1, 1),
            (-1, 0xFFFFFFFF, 0, 1, 1),
        ]
        for running, suspended, expected, running_reads, suspended_reads in (
            cases
        ):
            with self.subTest(running=running, suspended=suspended):
                self.set_state(running, suspended)
                self.assertEqual(self.get_state(), expected)
                self.assertEqual(self.running_reads(), running_reads)
                self.assertEqual(self.suspended_reads(), suspended_reads)

    def test_target_candidate_is_one_bounded_relocation_free_leaf(
        self,
    ) -> None:
        function = self.symbols[
            "open_cfw_freertos_task_get_scheduler_state"
        ]
        self.assertEqual((function[1], function[2]), (1, 32))
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
            {"open_cfw_freertos_task_get_scheduler_state"},
        )

    def test_source_is_a_pinned_upstream_algorithm_with_two_g2_seams(
        self,
    ) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1cc12269588475d1b6b0ab96790c5caa"
            "dff7b11a942079993c957ab456b0e4cb",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "3da5604e2dcded353217e829bcc01b23a"
            "63b13c54e951454c378fd8b152d97e0",
        )
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "xTaskGetSchedulerState()",
            "tasks.c",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x004558A4, 0x004558C4)",
            "0x20074A3CU",
            "0x20074A58U",
            "OPEN_CFW_TASK_SCHEDULER_NOT_STARTED",
            "OPEN_CFW_TASK_SCHEDULER_RUNNING",
            "OPEN_CFW_TASK_SCHEDULER_SUSPENDED",
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
            "609013b7cfb9a23d1572508ddc6d8da5"
            "466fff4dcdd9083f11de9d47cd848733",
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
