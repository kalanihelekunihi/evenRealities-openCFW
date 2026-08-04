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
    / "runtime_freertos_list_remove.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_remove_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_remove_upstream_oracle_host.c"
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
START = 0x004560E8
END = 0x0045610E
STOCK_SHA256 = (
    "e1ca0b525effd60568d00101c08010374cebfd3c80ee6ade4fec4da54bcb8794"
)
STOCK_BYTES = (
    "0169826843689a60426883685a604a68824201d182684a60002202610868401e"
    "086008687047"
)
TARGET_SHA256 = (
    "3d14c2cd32b33b3159e12d4e5465a61eeced8033b1cbe2fedc1f1f4c8fcd2e67"
)
TARGET_BYTES = (
    "01694368d1f804c0826884459a60536008bf4a6000220261086801380860086870"
    "47"
)

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


class RuntimeFreeRTOSListRemoveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        candidate_library = temporary / (
            "runtime_freertos_list_remove.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_remove.so"
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
            "runtime_freertos_list_remove_oracle.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_remove_oracle.so"
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
            "open_cfw_test_freertos_list_remove_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_freertos_list_remove_",
        )

        cls.target_object = temporary / "runtime_freertos_list_remove.o"
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

        sys.path.insert(0, str(ROOT / "tools"))
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
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
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
        api["remove"] = getattr(library, prefix + "remove")
        api["remove"].argtypes = [ctypes.c_uint32]
        api["remove"].restype = ctypes.c_uint32
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
        self.reset_both()

    def reset_both(self) -> None:
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

    def remove_both(self, identifier: int) -> int:
        candidate = self.candidate_api["remove"](identifier)
        oracle = self.oracle_api["remove"](identifier)
        self.assertEqual(candidate, oracle)
        return candidate

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

    def test_single_item_removal_matches_pristine_upstream(self) -> None:
        self.apply_both("append", 1)
        self.assertEqual(self.remove_both(1), 0)
        self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[:4], (0, 0, 0, 0))
        self.assertEqual(
            state[4][0],
            (0, 0, 0, 0x11110000, 0x22220000),
        )

    def test_head_middle_and_tail_removal_match_upstream(self) -> None:
        expected = {
            1: (2, 3, [(3, 0), (0, 2)]),
            2: (1, 3, [(3, 0), (0, 1)]),
            3: (1, 2, [(2, 0), (0, 1)]),
        }
        for removed in (1, 2, 3):
            with self.subTest(removed=removed):
                self.reset_both()
                for identifier in (1, 2, 3):
                    self.apply_both("append", identifier)
                self.assertEqual(self.remove_both(removed), 2)
                self.assert_matches_upstream()

                sentinel_next, sentinel_previous, remaining_links = expected[
                    removed
                ]
                state = self.snapshot(self.candidate_api)
                self.assertEqual(state[:4], (2, 0, sentinel_next,
                                             sentinel_previous))
                self.assertEqual(state[4][removed - 1][2], 0)
                remaining = [
                    item[:2]
                    for index, item in enumerate(state[4][:3], start=1)
                    if index != removed
                ]
                self.assertEqual(remaining, remaining_links)

    def test_sequential_removal_returns_exact_remaining_counts(self) -> None:
        for identifier in (1, 2, 3):
            self.apply_both("append", identifier)
        self.assertEqual(self.remove_both(2), 2)
        self.assertEqual(self.remove_both(1), 1)
        self.assertEqual(self.remove_both(3), 0)
        self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[:4], (0, 0, 0, 0))
        self.assertEqual([item[2] for item in state[4][:3]], [0, 0, 0])

    def test_index_is_repaired_only_when_it_points_to_removed_item(
        self,
    ) -> None:
        for identifier in (1, 2, 3):
            self.apply_both("append", identifier)
        self.apply_both("set_index", 2)
        self.assertEqual(self.remove_both(2), 2)
        self.assert_matches_upstream()
        self.assertEqual(self.candidate_api["get_index"](), 1)

        self.reset_both()
        for identifier in (1, 2, 3):
            self.apply_both("append", identifier)
        self.apply_both("set_index", 3)
        self.assertEqual(self.remove_both(2), 2)
        self.assert_matches_upstream()
        self.assertEqual(self.candidate_api["get_index"](), 3)

    def test_removal_preserves_item_value_owner_and_neighbor_fields(
        self,
    ) -> None:
        for identifier in (1, 2, 3):
            self.apply_both("append", identifier)
        self.assertEqual(self.remove_both(2), 2)
        self.assert_matches_upstream()
        removed = self.snapshot(self.candidate_api)[4][1]
        self.assertEqual(
            removed,
            (3, 1, 0, 0x11110001, 0x22220001),
        )

    @_APPLE_ONLY
    def test_target_object_is_one_bounded_leaf_with_no_seams(self) -> None:
        function = self.symbols["open_cfw_freertos_list_remove"]
        self.assertEqual((function[1], function[2]), (1, 34))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertEqual(function[5], 2)
        self.assertEqual(len(self.target_text), 34)
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
            {"open_cfw_freertos_list_remove"},
        )

    def test_source_and_fixtures_are_pinned_to_pristine_upstream(
        self,
    ) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "6b7ecf1d592892e788479002dca376a6"
            "459100f74245809bf2977fa16f035877",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "e359239af6f7d8c7ffe2f73fb6d385e8"
            "bfc3c61060f14907f34f22b52edb56b4",
        )
        self.assertEqual(
            hashlib.sha256(UPSTREAM_FIXTURE.read_bytes()).hexdigest(),
            "fb464294ed2776fc6471904ca20bf4199"
            "c5ef1e0f1b2acd27f7351ba6c39941f",
        )
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "uxListRemove()",
            "list.c",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x004560E8, 0x0045610E)",
            "configUSE_MINI_LIST_ITEM=1",
            "configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0",
            "sizeof(struct open_cfw_freertos_list_remove_item) == 0x14U",
            "sizeof(struct open_cfw_freertos_list_remove_list) == 0x14U",
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
        self.assertEqual(len(stock), 38)
        self.assertEqual(hashlib.sha256(stock).hexdigest(), STOCK_SHA256)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(self.span(END, END + 2), bytes.fromhex("0000"))
        self.assertEqual(
            self.span(END + 2, END + 6),
            bytes.fromhex("2de9f041"),
        )
        self.assertEqual(
            hashlib.sha256(self.span(0x004560B2, START)).hexdigest(),
            "10c1fa85d530a003183c42d2fc11b8038"
            "6669d011ce19f7a9c2a6d32516d4c59",
        )

    def test_stock_caller_and_reference_topology_is_exact(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
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
        expected_callers = [
            (0x00454AC4, "01f010fb"),
            (0x00454AD2, "01f009fb"),
            (0x00454C9A, "01f025fa"),
            (0x004556F2, "00f0f9fc"),
            (0x00455908, "00f0eefb"),
            (0x004559B8, "00f096fb"),
            (0x00455A84, "00f030fb"),
            (0x00455FB8, "00f096f8"),
            (0x0047E84C, "d7f74cfc"),
            (0x0047E9C2, "d7f791fb"),
        ]
        self.assertEqual(callers, expected_callers)
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in expected_callers
                )
            ).hexdigest(),
            "5e769191048e16c897132bef83eff5c61"
            "88ee79f6fd8bacde078d220789e01ee",
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

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value in (START, START | 1):
                stored.append((BASE + offset, value))
            if START < value < END:
                stored.append((BASE + offset, value))
            if value & 1 and START < (value & ~1) < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        caller_spans = {
            (0x00454AAE, 0x00454B4C): (
                "fed4eb28935bf7034f3f1893518e7de0"
                "56995a5083d42863ab007e9e74de2597"
            ),
            (0x00454C12, 0x00454CEC): (
                "fa38a23c007a168f79051504b23dd408"
                "7eb7845da2c3fb933c8083c8ade31152"
            ),
            (0x004556E0, 0x0045571C): (
                "0c2e27502e5f60b2ac93bddd8ca6ebb4"
                "1d183d24da456f1cec160b1ec34818b1"
            ),
            (0x004558CC, 0x0045596E): (
                "7a03706199fa57820990f7cd15a4c9cc"
                "2a222b85e35697625af41eb7c4182806"
            ),
            (0x0045596E, 0x00455A12): (
                "34e2c3a8b02daf3ea3f8d3d382ef3d80"
                "2d48f4d65ee26fa0353d0faab51c7e93"
            ),
            (0x00455A1C, 0x00455ACA): (
                "457932fc906a97ce86aa034cd06c428d"
                "b6d4943538b18c58e22775f1acc6ee68"
            ),
            (0x00455FA8, 0x0045601E): (
                "918fddb6333958607bec10181d39ffee"
                "564ca44f4db6cb43ee362cc62ba4f764"
            ),
            (0x0047E83A, 0x0047E878): (
                "94ed9421f98b5f3dd08dd15024fb413d"
                "cee8c28ef9f3b9d6c548b11e56b26335"
            ),
            (0x0047E97A, 0x0047EA90): (
                "7b11858bca279a51a5b6b9565b9ba9b6"
                "c5da9eed337ef50206f57ac314f4257f"
            ),
        }
        for (start, end), expected_sha256 in caller_spans.items():
            with self.subTest(caller_span=(start, end)):
                self.assertEqual(
                    hashlib.sha256(self.span(start, end)).hexdigest(),
                    expected_sha256,
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
