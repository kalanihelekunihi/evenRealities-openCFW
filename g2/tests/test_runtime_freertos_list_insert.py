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
    / "runtime_freertos_list_insert.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_insert_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_insert_upstream_oracle_host.c"
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
START = 0x004560B2
END = 0x004560E8
STOCK_SHA256 = (
    "10c1fa85d530a003183c42d2fc11b80386669d011ce19f7a9c2a6d32516d4c59"
)
STOCK_BYTES = (
    "10b40b6813f1010f01d1026907e010f1080200e0526854682468a342fad25368"
    "4b604b6899608a60516008610168491c016010bc7047"
)
TARGET_SHA256 = (
    "2afa2aa9cade7d864031311300ad5cc1f1e845fb67ad92a7c3ccb26f674d1cb7"
)
TARGET_BYTES = (
    "80b5d1f800c01cf1010207d000f108029646526813686345fad903e0d0f810e0"
    "def804204a609160c1f808e0cef80410086101680131016080bd"
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


class RuntimeFreeRTOSListInsertTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        candidate_library = temporary / (
            "runtime_freertos_list_insert.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_insert.so"
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
            "runtime_freertos_list_insert_oracle.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_insert_oracle.so"
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
            "open_cfw_test_freertos_list_insert_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_freertos_list_insert_",
        )

        cls.target_object = temporary / "runtime_freertos_list_insert.o"
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
        api["set_value"] = getattr(library, prefix + "set_value")
        api["set_value"].argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        api["set_value"].restype = None
        api["execute"] = getattr(library, prefix + "execute")
        api["execute"].argtypes = [ctypes.c_uint32]
        api["execute"].restype = None
        for name in (
            "get_next",
            "get_previous",
            "get_container",
            "get_value",
            "get_owner",
        ):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = [ctypes.c_uint32]
            api[name].restype = ctypes.c_uint32
        for name in (
            "get_before",
            "get_after",
            "get_count",
            "get_index",
        ):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
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
        for identifier in range(1, 7):
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
            api["get_before"](),
            api["get_after"](),
            api["get_count"](),
            api["get_index"](),
            api["get_next"](0),
            api["get_previous"](0),
            tuple(items),
        )

    def apply_both(self, operation: str, *arguments: int) -> None:
        self.candidate_api[operation](*arguments)
        self.oracle_api[operation](*arguments)

    def assert_matches_upstream(self) -> None:
        self.assertEqual(
            self.snapshot(self.candidate_api),
            self.snapshot(self.oracle_api),
        )

    def forward_order(self, api: dict[str, object]) -> list[int]:
        result = []
        identifier = api["get_next"](0)
        while identifier != 0:
            self.assertNotIn(identifier, result)
            result.append(identifier)
            identifier = api["get_next"](identifier)
        return result

    def reverse_order(self, api: dict[str, object]) -> list[int]:
        result = []
        identifier = api["get_previous"](0)
        while identifier != 0:
            self.assertNotIn(identifier, result)
            result.append(identifier)
            identifier = api["get_previous"](identifier)
        return result

    def test_recovered_list_abi_is_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(ListItem32), 0x14)
        self.assertEqual(ListItem32.item_value.offset, 0x00)
        self.assertEqual(ListItem32.next.offset, 0x04)
        self.assertEqual(ListItem32.previous.offset, 0x08)
        self.assertEqual(ListItem32.container.offset, 0x10)
        self.assertEqual(ctypes.sizeof(MiniListItem32), 0x0C)
        self.assertEqual(ctypes.sizeof(List32), 0x14)
        self.assertEqual(List32.item_count.offset, 0x00)
        self.assertEqual(List32.index.offset, 0x04)
        self.assertEqual(List32.end.offset, 0x08)

    def test_empty_list_insertion_matches_pristine_upstream(self) -> None:
        self.apply_both("set_value", 1, 10)
        self.apply_both("execute", 1)
        self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[:6], (0xA5A5C3C3, 0x5A5A3C3C, 1, 0, 1, 1))
        self.assertEqual(
            state[6][0],
            (0, 0, 1, 10, 0x22220000),
        )

    def test_out_of_order_values_are_sorted(self) -> None:
        for identifier, value in (
            (1, 30),
            (2, 10),
            (3, 20),
            (4, 40),
        ):
            self.apply_both("set_value", identifier, value)
            self.apply_both("execute", identifier)
            self.assert_matches_upstream()
        self.assertEqual(
            self.forward_order(self.candidate_api),
            [2, 3, 1, 4],
        )
        self.assertEqual(
            self.reverse_order(self.candidate_api),
            [4, 1, 3, 2],
        )

    def test_equal_values_are_inserted_after_existing_equals(self) -> None:
        for identifier in (1, 2, 3, 4):
            self.apply_both("set_value", identifier, 0x12345678)
            self.apply_both("execute", identifier)
            self.assert_matches_upstream()
        self.assertEqual(
            self.forward_order(self.candidate_api),
            [1, 2, 3, 4],
        )

    def test_unsigned_order_and_port_max_delay_special_case(self) -> None:
        values = (
            (1, 0x80000000),
            (2, 0x00000000),
            (3, 0xFFFFFFFF),
            (4, 0x7FFFFFFF),
            (5, 0xFFFFFFFE),
            (6, 0xFFFFFFFF),
        )
        for identifier, value in values:
            self.apply_both("set_value", identifier, value)
            self.apply_both("execute", identifier)
            self.assert_matches_upstream()
        self.assertEqual(
            self.forward_order(self.candidate_api),
            [2, 4, 1, 5, 3, 6],
        )
        self.assertEqual(
            self.reverse_order(self.candidate_api),
            [6, 3, 5, 1, 4, 2],
        )

    def test_insertion_preserves_index_values_owners_and_canaries(
        self,
    ) -> None:
        expected_values = {}
        for identifier, value in (
            (1, 91),
            (2, 7),
            (3, 44),
            (4, 12),
            (5, 0xFFFFFFFF),
            (6, 44),
        ):
            expected_values[identifier] = value
            self.apply_both("set_value", identifier, value)
            self.apply_both("execute", identifier)
        self.assert_matches_upstream()
        state = self.snapshot(self.candidate_api)
        self.assertEqual(state[:4], (0xA5A5C3C3, 0x5A5A3C3C, 6, 0))
        for identifier, item in enumerate(state[6], start=1):
            self.assertEqual(item[2], 1)
            self.assertEqual(item[3], expected_values[identifier])
            self.assertEqual(item[4], 0x22220000 + identifier - 1)

    def test_target_object_is_one_bounded_leaf_with_no_seams(self) -> None:
        function = self.symbols["open_cfw_freertos_list_insert"]
        self.assertEqual((function[1], function[2]), (1, 58))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertEqual(function[5], 2)
        self.assertEqual(len(self.target_text), 58)
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
            {"open_cfw_freertos_list_insert"},
        )

    def test_source_and_fixtures_are_pinned_to_pristine_upstream(
        self,
    ) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "e2592ce9acbcdaa3fbfaf30635f14fe7"
            "7449310313eb6534a8a4b2b6f3b4be67",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "740210cbf8b14cfb29b73b8d2d69872f"
            "0f9d62b31523d59de56586c7b93547c3",
        )
        self.assertEqual(
            hashlib.sha256(UPSTREAM_FIXTURE.read_bytes()).hexdigest(),
            "063686b37d2802d8669939f3470e8c9f"
            "732b044dbf8748bf8ef92491243a941a",
        )
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "vListInsert()",
            "list.c",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x004560B2, 0x004560E8)",
            "configUSE_MINI_LIST_ITEM=1",
            "configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0",
            "portMAX_DELAY=0xFFFFFFFF",
            "#pragma clang loop unroll(disable)",
            "sizeof(struct open_cfw_freertos_list_insert_item) == 0x14U",
            "sizeof(struct open_cfw_freertos_list_insert_list) == 0x14U",
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
        self.assertEqual(len(stock), 54)
        self.assertEqual(hashlib.sha256(stock).hexdigest(), STOCK_SHA256)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(
            hashlib.sha256(self.span(0x0045609A, START)).hexdigest(),
            "78e2f1765fd9ba8e71098dababdfc4a"
            "4a1aabb73ed1f730d4fc24b94b54a2aba",
        )
        self.assertEqual(
            hashlib.sha256(self.span(END, 0x0045610E)).hexdigest(),
            "e1ca0b525effd60568d00101c0801037"
            "4cebfd3c80ee6ade4fec4da54bcb8794",
        )

    def test_stock_caller_and_reference_topology_is_exact(self) -> None:
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
        expected_callers = [
            (0x004552A0, "00f007ff"),
            (0x00456000, "00f057f8"),
            (0x0045600E, "00f050f8"),
            (0x0047E95A, "d7f7aafb"),
            (0x0047E972, "d7f79efb"),
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
            "a966051c31865cdddfdb9c0467d20f3"
            "bc9c5051e74baba0998c0f8b2664d03a9",
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

        raw_stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value in (START, START | 1):
                raw_stored.append((BASE + offset, value))
            if START < value < END:
                raw_stored.append((BASE + offset, value))
            if value & 1 and START < (value & ~1) < END:
                raw_stored.append((BASE + offset, value))
        self.assertEqual(
            raw_stored,
            [(0x00528207, 0x004560C0)],
        )
        self.assertEqual(
            self.span(0x00528207, 0x0052820B),
            bytes.fromhex("c0604500"),
        )
        self.assertNotEqual(0x00528207 & 3, 0)

        aligned_stored = []
        for offset in range(0, len(self.application) - 3, 4):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                aligned_stored.append((BASE + offset, value))
        self.assertEqual(aligned_stored, [])

        caller_spans = {
            (0x00455282, 0x004552AE): (
                "2821a3c55358d806ed227c81a27746f8"
                "d9c35b648182fc9abb647de72ed9025d"
            ),
            (0x00455FA8, 0x0045601E): (
                "918fddb6333958607bec10181d39ffee5"
                "64ca44f4db6cb43ee362cc62ba4f764"
            ),
            (0x0047E93C, 0x0047E97A): (
                "8428e1dc245cc497ecd09cece3378777"
                "4eb8686182d994d2dccbec942930db62"
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
