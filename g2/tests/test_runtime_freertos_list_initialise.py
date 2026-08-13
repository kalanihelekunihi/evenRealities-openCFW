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
    / "runtime_freertos_list_initialise.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_initialise_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_list_initialise_upstream_oracle_host.c"
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
START = 0x0045607C
END = 0x0045609A
STOCK_SHA256 = (
    "6ea73f3bfc40bb5776bb925a560b7e6e2d2103e96a87756847e625860cdc351d"
)
STOCK_BYTES = (
    "10f1080141605ff0ff31816010f10801c16010f108010161002101607047"
)
TARGET_SHA256 = (
    "608e9d4ec0accd8c26784960dbc2dc4bab55e0d65a29ffcba9ecf9e2576eb96b"
)
TARGET_BYTES = "4ff0ff31024642f8081f00214260c260026101607047"

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


class RuntimeFreeRTOSListInitialiseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        candidate_library = temporary / (
            "runtime_freertos_list_initialise.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_initialise.so"
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
            "runtime_freertos_list_initialise_oracle.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_list_initialise_oracle.so"
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
            "open_cfw_test_freertos_list_initialise_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_freertos_list_initialise_",
        )

        cls.target_object = temporary / "runtime_freertos_list_initialise.o"
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
        api["reset"].argtypes = [ctypes.c_uint32]
        api["reset"].restype = None
        api["execute"] = getattr(library, prefix + "execute")
        api["execute"].argtypes = []
        api["execute"].restype = None
        for name in (
            "get_before",
            "get_after",
            "get_count",
            "get_index",
            "get_end_value",
            "get_end_next",
            "get_end_previous",
        ):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_uint32
        return api

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    @staticmethod
    def snapshot(api: dict[str, object]) -> tuple[int, ...]:
        return (
            api["get_before"](),
            api["get_after"](),
            api["get_count"](),
            api["get_index"](),
            api["get_end_value"](),
            api["get_end_next"](),
            api["get_end_previous"](),
        )

    def reset_both(self, seed: int) -> None:
        self.candidate_api["reset"](seed)
        self.oracle_api["reset"](seed)

    def execute_both(self) -> None:
        self.candidate_api["execute"]()
        self.oracle_api["execute"]()

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

    def test_initialisation_matches_pristine_upstream(self) -> None:
        self.reset_both(0x1234)
        self.execute_both()
        self.assert_matches_upstream()
        self.assertEqual(
            self.snapshot(self.candidate_api),
            (
                0xA5A51234,
                0x5A5A1234,
                0,
                0,
                0xFFFFFFFF,
                0,
                0,
            ),
        )

    def test_initialisation_overwrites_all_list_state_for_varied_inputs(
        self,
    ) -> None:
        for seed in (0, 1, 0x7FFF, 0xFFFF, 0x12345678):
            with self.subTest(seed=seed):
                self.reset_both(seed)
                self.execute_both()
                self.assert_matches_upstream()
                state = self.snapshot(self.candidate_api)
                self.assertEqual(state[2:], (0, 0, 0xFFFFFFFF, 0, 0))
                self.assertEqual(state[0], 0xA5A50000 | (seed & 0xFFFF))
                self.assertEqual(state[1], 0x5A5A0000 | (seed & 0xFFFF))

    def test_repeated_initialisation_is_idempotent_and_bounded(self) -> None:
        self.reset_both(0xBEEF)
        self.execute_both()
        first = self.snapshot(self.candidate_api)
        self.execute_both()
        self.assert_matches_upstream()
        self.assertEqual(self.snapshot(self.candidate_api), first)
        self.assertEqual(first[0:2], (0xA5A5BEEF, 0x5A5ABEEF))

    @_APPLE_ONLY
    def test_target_object_is_one_bounded_leaf_with_no_seams(self) -> None:
        function = self.symbols["open_cfw_freertos_list_initialise"]
        self.assertEqual((function[1], function[2]), (1, 22))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertEqual(function[5], 2)
        self.assertEqual(len(self.target_text), 22)
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
            {"open_cfw_freertos_list_initialise"},
        )

    def test_source_and_fixtures_are_pinned_to_pristine_upstream(
        self,
    ) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "a77b7c99f2cd092b80caae0c247cae70"
            "8ba52a4cd89f723274ddc93fc2442733",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "f4831aeae6a27b0b498e5716f61e57a8"
            "1016b943a18bc072a7bc2176bd4ce11b",
        )
        self.assertEqual(
            hashlib.sha256(UPSTREAM_FIXTURE.read_bytes()).hexdigest(),
            "a8eb4eafa362d4097b533114ba607485"
            "53f851634a91fe8824eb0d2701fae112",
        )
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "vListInitialise()",
            "list.c",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x0045607C, 0x0045609A)",
            "configUSE_MINI_LIST_ITEM=1",
            "configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0",
            "portMAX_DELAY=0xFFFFFFFF",
            "sizeof(struct open_cfw_freertos_list_initialise_item) == 0x14U",
            "sizeof(struct open_cfw_freertos_list_initialise_list) == 0x14U",
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
        self.assertEqual(len(stock), 30)
        self.assertEqual(hashlib.sha256(stock).hexdigest(), STOCK_SHA256)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(
            hashlib.sha256(self.span(0x00456036, START)).hexdigest(),
            "ee4e597cbb3d06e3306132a9b0725e82"
            "ae257b7ff2331cf2abd070e85d6b7fc7",
        )
        self.assertEqual(
            hashlib.sha256(self.span(END, 0x004560B2)).hexdigest(),
            "78e2f1765fd9ba8e71098dababdfc4a"
            "4a1aabb73ed1f730d4fc24b94b54a2aba",
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
            (0x004415A0, "14f06cfd"),
            (0x004415A8, "14f068fd"),
            (0x0045569E, "00f0edfc"),
            (0x004556AE, "00f0e5fc"),
            (0x004556B8, "00f0e0fc"),
            (0x004556BE, "00f0ddfc"),
            (0x004556C6, "00f0d9fc"),
            (0x004556CE, "00f0d5fc"),
            (0x0047EACA, "d7f7d7fa"),
            (0x0047EAD2, "d7f7d3fa"),
            (0x0047EBCC, "d7f756fa"),
            (0x0047EBEC, "d7f746fa"),
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
            "5e740bd209e577e749d813825efdc093"
            "4ffba60442ae33968527992d4ce27e9d",
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
            [
                (0x005DD143, START),
                (0x005DD20D, START),
            ],
        )
        for address, value in raw_stored:
            self.assertNotEqual(address & 3, 0)
            self.assertEqual(value, START)
            self.assertEqual(
                self.span(address, address + 4),
                bytes.fromhex("7c604500"),
            )

        aligned_stored = []
        for offset in range(0, len(self.application) - 3, 4):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                aligned_stored.append((BASE + offset, value))
        self.assertEqual(aligned_stored, [])

        caller_spans = {
            (0x00441516, 0x004415CA): (
                "e5b7c5e487374e7966b8f2febb8aa1b8"
                "04efa516c92f9e436a369ec5df100ad8"
            ),
            (0x0045568C, 0x004556E0): (
                "db9aad99c9dfd14cb9f2eb453dd86af0"
                "5b11ed049eacf8771f25a82382894723"
            ),
            (0x0047EAB8, 0x0047EAF6): (
                "e34431d020471c30b8e3d3fed60fb15e"
                "83b77f49ee2921fcdae5e3be7d589ece"
            ),
            (0x0047EB94, 0x0047EBD8): (
                "8bbcf73cd3d7f93fcd7564b8c5bd06d4"
                "936fb21859cfca99017c2a8c3f5dfc6c"
            ),
            (0x0047EBD8, 0x0047EBF8): (
                "fe1edcf1a00dfbb69d8015b5958d6c24"
                "ffa6591e2fac90bb4e44ed8ebd33baf5"
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
