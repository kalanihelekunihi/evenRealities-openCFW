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
    / "runtime_freertos_list_insert_end.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_insert_end_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_insert_end_upstream_oracle_host.c"
)
FREERTOS_INCLUDE = ROOT / "third_party" / "freertos-kernel" / "include"
FREERTOS_LIST = ROOT / "third_party" / "freertos-kernel" / "list.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

BASE = 0x00438000
START = 0x0045609A
END = 0x004560B2
STOCK_SHA256 = (
    "78e2f1765fd9ba8e71098dababdfc4a4a1aabb73ed1f730d4fc24b94b54a2aba"
)
STOCK_BYTES = "42684a6093688b6093685960916008610168491c01607047"

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


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class ListItem32(ctypes.Structure):
    _fields_ = [
        ("item_value", ctypes.c_uint32),
        ("next", ctypes.c_uint32),
        ("previous", ctypes.c_uint32),
        ("owner", ctypes.c_uint32),
        ("container", ctypes.c_uint32),
    ]


class MiniListItem32(ctypes.Structure):
    _fields_ = [
        ("item_value", ctypes.c_uint32),
        ("next", ctypes.c_uint32),
        ("previous", ctypes.c_uint32),
    ]


class List32(ctypes.Structure):
    _fields_ = [
        ("item_count", ctypes.c_uint32),
        ("index", ctypes.c_uint32),
        ("end", MiniListItem32),
    ]


class RuntimeFreeRTOSListInsertEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        candidate_library = temporary / (
            "runtime_freertos_list_insert_end.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_insert_end.so"
        )
        candidate_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            candidate_command.extend(
                ["-dynamiclib", "-o", str(candidate_library)]
            )
        else:
            candidate_command.extend(
                ["-shared", "-fPIC", "-o", str(candidate_library)]
            )
        subprocess.run(
            candidate_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.candidate = ctypes.CDLL(str(candidate_library))

        oracle_library = temporary / (
            "runtime_freertos_list_insert_end_oracle.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_insert_end_oracle.so"
        )
        oracle_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(FREERTOS_INCLUDE),
            str(UPSTREAM_FIXTURE),
        ]
        if sys.platform == "darwin":
            oracle_command.extend(
                ["-dynamiclib", "-o", str(oracle_library)]
            )
        else:
            oracle_command.extend(
                ["-shared", "-fPIC", "-o", str(oracle_library)]
            )
        subprocess.run(
            oracle_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.oracle = ctypes.CDLL(str(oracle_library))

        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_freertos_list_insert_end_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_freertos_list_insert_end_",
        )

        cls.target_object = temporary / "runtime_freertos_list_insert_end.o"
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

    @staticmethod
    def bind_api(
        library: ctypes.CDLL,
        prefix: str,
    ) -> dict[str, object]:
        api: dict[str, object] = {}
        api["reset"] = getattr(library, prefix + "reset")
        api["reset"].argtypes = []
        api["reset"].restype = None
        api["append"] = getattr(library, prefix + "append")
        api["append"].argtypes = [ctypes.c_uint32]
        api["append"].restype = None
        api["set_index"] = getattr(library, prefix + "set_index")
        api["set_index"].argtypes = [ctypes.c_uint32]
        api["set_index"].restype = None
        for name in ("get_next", "get_previous", "get_container"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = [ctypes.c_uint32]
            api[name].restype = ctypes.c_uint32
        for name in ("get_count", "get_index"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_uint32
        for name in ("get_value", "get_owner"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = [ctypes.c_uint32]
            api[name].restype = ctypes.c_uint32
        return api

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.candidate_api["reset"]()
        self.oracle_api["reset"]()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    @staticmethod
    def snapshot(api: dict[str, object]) -> tuple[object, ...]:
        items = []
        for identifier in range(1, 5):
            items.append(
                (
                    api["get_next"](identifier),
                    api["get_previous"](identifier),
                    api["get_container"](identifier),
                    api["get_value"](identifier),
                    api["get_owner"](identifier),
                )
            )
        return (
            api["get_count"](),
            api["get_index"](),
            api["get_next"](0),
            api["get_previous"](0),
            tuple(items),
        )

    def apply_both(self, operation: str, argument: int) -> None:
        self.candidate_api[operation](argument)
        self.oracle_api[operation](argument)

    def assert_matches_upstream(self) -> None:
        self.assertEqual(
            self.snapshot(self.candidate_api),
            self.snapshot(self.oracle_api),
        )

    def test_recovered_list_abi_is_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(ListItem32), 0x14)
        self.assertEqual(ListItem32.next.offset, 0x04)
        self.assertEqual(ListItem32.previous.offset, 0x08)
        self.assertEqual(ListItem32.container.offset, 0x10)
        self.assertEqual(ctypes.sizeof(MiniListItem32), 0x0C)
        self.assertEqual(ctypes.sizeof(List32), 0x14)
        self.assertEqual(List32.item_count.offset, 0x00)
        self.assertEqual(List32.index.offset, 0x04)
        self.assertEqual(List32.end.offset, 0x08)

    def test_empty_list_insertion_matches_pristine_upstream(self) -> None:
        self.apply_both("append", 1)
        self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[:4], (1, 0, 1, 1))
        self.assertEqual(
            state[4][0],
            (0, 0, 1, 0x11110000, 0x22220000),
        )

    def test_multiple_insertions_preserve_upstream_order(self) -> None:
        for identifier in (1, 2, 3):
            self.apply_both("append", identifier)
            self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[:4], (3, 0, 1, 3))
        self.assertEqual(
            [item[:3] for item in state[4][:3]],
            [
                (2, 0, 1),
                (3, 1, 1),
                (0, 2, 1),
            ],
        )

    def test_non_end_index_inserts_immediately_before_index(self) -> None:
        for identifier in (1, 2):
            self.apply_both("append", identifier)
        self.apply_both("set_index", 1)
        self.apply_both("append", 3)
        self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[:4], (3, 1, 3, 2))
        self.assertEqual(
            [item[:3] for item in state[4][:3]],
            [
                (2, 3, 1),
                (0, 1, 1),
                (1, 0, 1),
            ],
        )

    def test_insertion_preserves_item_value_owner_and_list_index(self) -> None:
        self.apply_both("append", 4)
        self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[1], 0)
        self.assertEqual(
            state[4][3],
            (0, 0, 1, 0x11110003, 0x22220003),
        )
        for untouched in state[4][:3]:
            self.assertEqual(
                untouched[0:3],
                (0xFFFFFFFF, 0xFFFFFFFF, 0),
            )

    @_APPLE_ONLY
    def test_target_object_is_one_bounded_leaf_with_no_seams(self) -> None:
        function = self.symbols["open_cfw_freertos_list_insert_end"]
        self.assertEqual((function[1], function[2]), (1, 26))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertEqual(function[5], 2)
        self.assertEqual(len(self.target_text), 26)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "98c584a428121891341d0c3eb9a705a6"
            "ca6334d98139ae07f51ec7e7ff09e467",
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
            {"open_cfw_freertos_list_insert_end"},
        )

    def test_source_is_pinned_upstream_and_has_no_opaque_seam(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1ec84660c68ad9fbd7c22840f1650499"
            "7618c37e8dd9a0d492c78804f79cb2ca",
        )
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "vListInsertEnd()",
            "list.c",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x0045609A, 0x004560B2)",
            "configUSE_MINI_LIST_ITEM=1",
            "configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0",
            "sizeof(struct open_cfw_freertos_list_insert_end_item) == 0x14U",
            "sizeof(struct open_cfw_freertos_list_insert_end_list) == 0x14U",
        ):
            self.assertIn(token, source)
        for opaque_seam in (
            "#include",
            "extern ",
            "__UINTPTR_TYPE__",
            "typedef void (*",
        ):
            self.assertNotIn(opaque_seam, source)
        self.assertIn(
            "../../third_party/freertos-kernel/list.c",
            UPSTREAM_FIXTURE.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            hashlib.sha256(FREERTOS_LIST.read_bytes()).hexdigest(),
            "db5c169cf3efd68da1c6a923ac84eebc"
            "724d602c940bde0b9b5f01f05028fde4",
        )

    def test_stock_body_hash_bytes_and_boundaries_are_exact(self) -> None:
        stock = self.span(START, END)
        self.assertEqual(len(stock), 24)
        self.assertEqual(hashlib.sha256(stock).hexdigest(), STOCK_SHA256)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(self.span(END, END + 2), bytes.fromhex("10b4"))
        self.assertEqual(
            hashlib.sha256(self.span(0x0045607C, START)).hexdigest(),
            "6ea73f3bfc40bb5776bb925a560b7e6e"
            "2d2103e96a87756847e625860cdc351d",
        )

    def test_stock_caller_interior_and_stored_topology_is_exact(self) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
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
        self.assertEqual(callers, [(0x00454AF0, "01f0d3fa")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])

        narrow_interior = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            targets = self.narrow_branch_targets(address, halfword)
            for target in targets:
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    narrow_interior.append((address, target, halfword))
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            if value in (START, START | 1):
                stored.append((BASE + offset, value))
            if START < value < END:
                stored.append((BASE + offset, value))
            if value & 1 and START < (value & ~1) < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        caller = self.span(0x00454AAE, 0x00454B4C)
        self.assertEqual(len(caller), 158)
        self.assertEqual(
            hashlib.sha256(caller).hexdigest(),
            "fed4eb28935bf7034f3f1893518e7de0"
            "56995a5083d42863ab007e9e74de2597",
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                self.application,
                0x00455318 - BASE,
            )[0],
            0x20073D38,
        )

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
