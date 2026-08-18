from __future__ import annotations

import os

import ctypes
import hashlib
import json
import random
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
    / "runtime_freertos_heap4.c"
)
FIXTURE = (
    ROOT / "tests" / "fixtures" / "runtime_freertos_heap4_host.c"
)
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_heap4_upstream_oracle_host.c"
)
UPSTREAM = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "MemMang"
    / "heap_4.c"
)
FREERTOS_INCLUDE = ROOT / "third_party" / "freertos-kernel" / "include"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
CURRENT_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)

APPLICATION_BASE = 0x0043_8000
HEAP_BASE = 0x2000_4558
HEAP_BYTES = 0x0002_F000
TARGET_HEADER_BYTES = 8
NULL_OFFSET = 0xFFFF_FFFF

STOCK_FUNCTIONS = {
    "malloc": (
        0x0045_6110,
        0x0045_6210,
        "8d86a7daf341ad836729e4abdd25b66b"
        "45f97a56d6d1077c07bf0c5718f8dc57",
    ),
    "free": (
        0x0045_6210,
        0x0045_6280,
        "d754aec282080b2deafeb6756cbacc15"
        "6af70a311499ee4d73eeb7497f12b032",
    ),
    "init": (
        0x0045_6280,
        0x0045_62DA,
        "0b6c69c306e3a8e734f524f0cc38146c"
        "f761f996a14bd61ef81651fd6ebd6b0f",
    ),
    "insert_free_block": (
        0x0045_62DA,
        0x0045_6338,
        "88820119c56a0487020dceef91194de8"
        "299b056d25f887ff87badb84c0806a10",
    ),
}
STOCK_CLOSURE_SHA256 = (
    "a805cb30f37d145d55e1785435f941a8"
    "50b85b5ab3af7d1a21752fe75130d266"
)
STOCK_CALLERS = {
    0x0045_6110: [
        (0x0044_1660, "14f056fd"),
        (0x0044_93EC, "0cf090fe"),
        (0x0044_9CB4, "0cf02cfa"),
        (0x0044_9CDC, "0cf018fa"),
        (0x0045_48CC, "01f020fc"),
        (0x0045_48D8, "01f01afc"),
        (0x0047_E6EA, "d7f711fd"),
        (0x0047_EBDC, "d7f798fa"),
        (0x0057_DE18, "d8f67af9"),
        (0x0057_DF4A, "d8f6e1f8"),
        (0x0058_47C6, "d1f6a3fc"),
    ],
    0x0045_6210: [
        (0x0044_1EBE, "14f0a7f9"),
        (0x0044_948E, "0cf0bffe"),
        (0x0044_9582, "0cf045fe"),
        (0x0044_9D32, "0cf06dfa"),
        (0x0045_48F4, "01f08cfc"),
        (0x0045_5844, "00f0e4fc"),
        (0x0045_584A, "00f0e1fc"),
        (0x0045_585A, "00f0d9fc"),
        (0x0047_EA76, "d7f7cbfb"),
        (0x0057_DE96, "d8f6bbf9"),
    ],
    0x0045_6280: [(0x0045_6128, "00f0aaf8")],
    0x0045_62DA: [
        (0x0045_61BA, "00f08ef8"),
        (0x0045_626E, "00f034f8"),
    ],
}
STOCK_CALLER_DIGESTS = {
    0x0045_6110: (
        "d462d089b939012d13528427b3f788d2"
        "339ad392617849ab9305e3fe9302e77b"
    ),
    0x0045_6210: (
        "962e1ea2286d11969de5f736bfffe8f"
        "940bfe168ef72318272102ed99676d96a"
    ),
    0x0045_6280: (
        "d57084b9276cc1b4182ecc532efd3107c"
        "f2998b41641ac5a6740375283d22f9b"
    ),
    0x0045_62DA: (
        "e525ad8f6485be36e240ee1118597c83"
        "5d5f6bb26a28b77a916d1b85ec512928"
    ),
}
STOCK_OUTGOING = [
    (0x0045_6118, "fef730fe", 0x0045_4D7C),
    (0x0045_6128, "00f0aaf8", 0x0045_6280),
    (0x0045_61A2, "a3f17fff", 0x005F_A0A4),
    (0x0045_61BA, "00f08ef8", 0x0045_62DA),
    (0x0045_61E8, "fef7f0fd", 0x0045_4DCC),
    (0x0045_61F0, "17f035fb", 0x0046_D85E),
    (0x0045_61FC, "a3f152ff", 0x005F_A0A4),
    (0x0045_6228, "a3f13cff", 0x005F_A0A4),
    (0x0045_623C, "a3f132ff", 0x005F_A0A4),
    (0x0045_625E, "fef78dfd", 0x0045_4D7C),
    (0x0045_626E, "00f034f8", 0x0045_62DA),
    (0x0045_627A, "fef7a7fd", 0x0045_4DCC),
]

UPSTREAM_SIZE = 20_608
UPSTREAM_SHA256 = (
    "d48a51e34caed771e6650d95f6c2527e"
    "52fde2a6ebc6f83b49d003aef0135e05"
)
UPSTREAM_GIT_BLOB_SHA1 = "3af0caf2b60fc4adfb103a115fefbf1b09b21dd8"

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
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]
TARGET_FUNCTIONS = {
    "open_cfw_freertos_heap4_malloc": (
        308,
        "1eef99d8ee53c6747ae90d596021fce5"
        "278c97e42db224a32ac89d0bb5b5615c",
        [
            (38, 10, "open_cfw_freertos_heap4_init"),
            (190, 10, "ulSetInterruptMask"),
            (224, 10, "ulSetInterruptMask"),
            (242, 10, "open_cfw_freertos_heap4_insert_free_block"),
        ],
    ),
    "open_cfw_freertos_heap4_free": (
        114,
        "2107578655326abf1271a1d2ce8a7b65"
        "1601d905a6c763aae59060c84e38616c",
        [
            (16, 10, "ulSetInterruptMask"),
            (38, 10, "ulSetInterruptMask"),
            (94, 10, "open_cfw_freertos_heap4_insert_free_block"),
        ],
    ),
    "open_cfw_freertos_heap4_init": (
        66,
        "05577f0229a6b66050f597d7da19ccac"
        "03c34f15db84db9b29dcbab7d96cd140",
        [],
    ),
    "open_cfw_freertos_heap4_insert_free_block": (
        118,
        "624b33dc7c6d16d3c87be6fc2dd409bf"
        "4461a8b08ff94cda3664682839d0aed2",
        [],
    ),
}
TARGET_CLOSURE_SIZE = 606
TARGET_CLOSURE_SHA256 = (
    "ef7d6943041aa414d0485fe4d95c6b3b"
    "7ff17a12c0b4a2a67047994cdff00119"
)
SOURCE_SIZE = 16_885
SOURCE_SHA256 = (
    "d848b90a00da24db963c49dbff247231"
    "4b2a76c6cf269efef46e6cac56889986"
)
PRODUCTION_OVERLAY_SIZE = 142_986
PRODUCTION_OVERLAY_SHA256 = (
    "3d5c9fe87fd46cbc40bb5670653f45d3"
            "d61f9d777168aa47b70fb10712698ab4"
)
PRODUCTION_COMPONENT_SIZE = 3_666_382
PRODUCTION_COMPONENT_SHA256 = (
    "a4552ff210b6af33b7826a6b9aaefa6e"
            "01c7e6e976c9a852498570ededcf058f"
)
PRODUCTION_FUNCTIONS = {
    "open_cfw_freertos_heap4_init": {
        "offset": 114_088,
        "size": 66,
        "padding_before": 0,
        "runtime_address": 0x007B_00CC,
        "sha256": TARGET_FUNCTIONS["open_cfw_freertos_heap4_init"][1],
    },
    "open_cfw_freertos_heap4_insert_free_block": {
        "offset": 114_156,
        "size": 118,
        "padding_before": 2,
        "runtime_address": 0x007B_0110,
        "sha256": TARGET_FUNCTIONS[
            "open_cfw_freertos_heap4_insert_free_block"
        ][1],
    },
    "open_cfw_freertos_heap4_malloc": {
        "offset": 114_276,
        "size": 308,
        "padding_before": 2,
        "runtime_address": 0x007B_0188,
        "sha256": (
            "89bc685c866987fca82d83b0cb397b49"
            "eb1e63ac6e380c3b9825ae2a1c057451"
        ),
    },
    "open_cfw_freertos_heap4_free": {
        "offset": 114_584,
        "size": 114,
        "padding_before": 0,
        "runtime_address": 0x007B_02BC,
        "sha256": (
            "146aa07eef93afc02e5caff75e7a569b"
            "f39e3da390383d91ccf45ae0f6b19f1c"
        ),
    },
}
PRODUCTION_PATCHES = [
    (
        "replace_freertos_heap4_malloc",
        123_184,
        0x0045_6110,
        256,
        "open_cfw_freertos_heap4_malloc",
    ),
    (
        "replace_freertos_heap4_free",
        123_440,
        0x0045_6210,
        112,
        "open_cfw_freertos_heap4_free",
    ),
    (
        "replace_freertos_heap4_init",
        123_552,
        0x0045_6280,
        90,
        "open_cfw_freertos_heap4_init",
    ),
    (
        "replace_freertos_heap4_insert_free_block",
        123_642,
        0x0045_62DA,
        94,
        "open_cfw_freertos_heap4_insert_free_block",
    ),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeFreeRTOSHeap4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-freertos-heap4-",
            dir=temporary_parent,
        )
        temporary = Path(cls.temporary.name)

        cls.candidate = cls.compile_host_library(
            FIXTURE,
            temporary / (
                "runtime_freertos_heap4.dylib"
                if sys.platform == "darwin"
                else "runtime_freertos_heap4.so"
            ),
            [],
        )
        cls.oracle = cls.compile_host_library(
            ORACLE_FIXTURE,
            temporary / (
                "runtime_freertos_heap4_oracle.dylib"
                if sys.platform == "darwin"
                else "runtime_freertos_heap4_oracle.so"
            ),
            ["-I", str(FREERTOS_INCLUDE)],
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_freertos_heap4_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_freertos_heap4_",
        )

        cls.target_object = temporary / "runtime_freertos_heap4.o"
        cls.target_compile = subprocess.run(
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

        cls.apollo_overlay = apollo_overlay
        cls.elf, cls.sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        cls.sections_by_name = {
            str(section["name"]): section for section in cls.sections
        }
        symbol_table = apollo_overlay.section_named(
            cls.sections,
            ".symtab",
        )
        string_table = cls.sections[int(symbol_table["link"])]
        strings = cls.elf[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                cls.elf,
                int(symbol_table["offset"]) + index * 16,
            )
            cls.symbols.append(
                (
                    apollo_overlay.elf_string(
                        strings,
                        fields[0],
                        "symbol",
                    ),
                    fields,
                )
            )
        cls.symbols_by_name = {
            name: fields for name, fields in cls.symbols if name
        }
        cls.current_config = json.loads(CURRENT_CONFIG.read_text())
        cls.current_output = temporary / "current-overlay"
        cls.current_report = apollo_overlay.build(
            root=ROOT,
            config_path=CURRENT_CONFIG,
            output_dir=cls.current_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.current_overlay = (
            cls.current_output / "apollo_core_overlay.bin"
        ).read_bytes()
        cls.current_component = (
            cls.current_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def compile_host_library(
        fixture: Path,
        output: Path,
        extra_flags: list[str],
    ) -> ctypes.CDLL:
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            *extra_flags,
            str(fixture),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(output)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(output)])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return ctypes.CDLL(str(output))

    @staticmethod
    def bind_api(
        library: ctypes.CDLL,
        prefix: str,
    ) -> dict[str, object]:
        api: dict[str, object] = {}
        for name in ("reset", "init"):
            function = getattr(library, prefix + name)
            function.argtypes = []
            function.restype = None
            api[name] = function
        for name in ("malloc", "free"):
            function = getattr(library, prefix + name)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32
            api[name] = function
        for name in (
            "get_struct_size",
            "get_minimum_block_size",
            "get_end_offset",
            "get_start_next_offset",
            "get_free_bytes",
            "get_minimum_bytes",
            "get_allocation_count",
            "get_free_count",
            "get_suspend_count",
            "get_resume_count",
            "get_malloc_failed_count",
            "get_assert_count",
        ):
            function = getattr(library, prefix + name)
            function.argtypes = []
            function.restype = ctypes.c_uint32
            api[name] = function
        for name in ("get_block_next_offset", "get_block_size"):
            function = getattr(library, prefix + name)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32
            api[name] = function
        return api

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    @staticmethod
    def reset_both(
        candidate: dict[str, object],
        oracle: dict[str, object],
    ) -> None:
        candidate["reset"]()
        oracle["reset"]()

    @staticmethod
    def scalar_state(api: dict[str, object]) -> tuple[int, ...]:
        return tuple(
            int(api[name]())
            for name in (
                "get_struct_size",
                "get_minimum_block_size",
                "get_end_offset",
                "get_start_next_offset",
                "get_free_bytes",
                "get_minimum_bytes",
                "get_allocation_count",
                "get_free_count",
                "get_suspend_count",
                "get_resume_count",
                "get_malloc_failed_count",
                "get_assert_count",
            )
        )

    @staticmethod
    def free_list_state(
        api: dict[str, object],
    ) -> tuple[tuple[int, int, int], ...]:
        end = int(api["get_end_offset"]())
        current = int(api["get_start_next_offset"]())
        result = []
        for _ in range(1024):
            if current in (end, NULL_OFFSET):
                break
            next_offset = int(api["get_block_next_offset"](current))
            result.append(
                (
                    current,
                    int(api["get_block_size"](current)),
                    next_offset,
                )
            )
            current = next_offset
        else:
            raise AssertionError("heap free list is cyclic or unbounded")
        result.append(
            (
                current,
                0 if current == end else NULL_OFFSET,
                NULL_OFFSET,
            )
        )
        return tuple(result)

    def assert_matches_oracle(self) -> None:
        self.assertEqual(
            self.scalar_state(self.candidate_api),
            self.scalar_state(self.oracle_api),
        )
        self.assertEqual(
            self.free_list_state(self.candidate_api),
            self.free_list_state(self.oracle_api),
        )

    def malloc_both(self, wanted_size: int) -> int:
        candidate = int(self.candidate_api["malloc"](wanted_size))
        oracle = int(self.oracle_api["malloc"](wanted_size))
        self.assertEqual(candidate, oracle)
        self.assert_matches_oracle()
        return candidate

    def free_both(self, payload_offset: int) -> int:
        candidate = int(self.candidate_api["free"](payload_offset))
        oracle = int(self.oracle_api["free"](payload_offset))
        self.assertEqual(candidate, oracle)
        self.assert_matches_oracle()
        return candidate

    def target_text(self, function: str) -> bytes:
        section = self.sections_by_name[f".text.{function}"]
        return self.elf[
            int(section["offset"]):
            int(section["offset"]) + int(section["size"])
        ]

    def target_relocations(
        self,
        function: str,
    ) -> list[tuple[int, int, str]]:
        text = self.sections_by_name[f".text.{function}"]
        result = []
        for section in self.sections:
            if (
                int(section["type"]) != 9
                or int(section["info"]) != int(text["index"])
            ):
                continue
            for entry in range(
                int(section["offset"]),
                int(section["offset"]) + int(section["size"]),
                8,
            ):
                offset, information = struct.unpack_from(
                    "<II",
                    self.elf,
                    entry,
                )
                result.append(
                    (
                        offset,
                        information & 0xFF,
                        self.symbols[information >> 8][0],
                    )
                )
        return result

    def test_authenticated_upstream_heap4_is_exact(self) -> None:
        upstream = UPSTREAM.read_bytes()
        self.assertEqual(len(upstream), UPSTREAM_SIZE)
        self.assertEqual(sha256(upstream), UPSTREAM_SHA256)
        self.assertEqual(git_blob_sha1(upstream), UPSTREAM_GIT_BLOB_SHA1)
        self.assertEqual(upstream.count(b"\r\n"), 537)
        self.assertNotIn(b"\n", upstream.replace(b"\r\n", b""))
        self.assertIn(
            "../../third_party/freertos-kernel/portable/MemMang/heap_4.c",
            ORACLE_FIXTURE.read_text(encoding="utf-8"),
        )

    def test_source_exports_fixed_g2_state_and_explicit_seams(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for symbol in TARGET_FUNCTIONS:
            self.assertIn(symbol, source)
        for token in (
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "0x20004558U",
            "0x0002F000U",
            "0x20074158U",
            "0x2007465CU",
            "0x20074660U",
            "0x20074664U",
            "0x20074668U",
            "0x2007466CU",
            "0x00454D7DU",
            "0x00454DCDU",
            "0x0046D85FU",
            "extern unsigned int ulSetInterruptMask(void);",
            "sizeof(struct open_cfw_freertos_heap4_block) == 8U",
            "OPEN_CFW_FREERTOS_HEAP4_ALLOCATED_BIT = 0x80000000U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include", source)
        self.assertNotIn("memset", source)
        self.assertNotIn("OPEN_CFW_FREERTOS_HEAP4_HOST_TEST", source)

        target_end = (
            HEAP_BASE + HEAP_BYTES - TARGET_HEADER_BYTES
        ) & ~7
        self.assertEqual(target_end, 0x2003_3550)
        self.assertEqual(target_end - HEAP_BASE, 0x0002_EFF8)

    def test_direct_init_alignment_and_initial_accounting_match_upstream(
        self,
    ) -> None:
        self.reset_both(self.candidate_api, self.oracle_api)
        self.candidate_api["init"]()
        self.oracle_api["init"]()
        self.assert_matches_oracle()

        header = int(self.candidate_api["get_struct_size"]())
        end = int(self.candidate_api["get_end_offset"]())
        self.assertEqual(header, 16)
        self.assertEqual(
            int(self.candidate_api["get_minimum_block_size"]()),
            32,
        )
        self.assertEqual(end, HEAP_BYTES - header)
        self.assertEqual(
            int(self.candidate_api["get_start_next_offset"]()),
            0,
        )
        self.assertEqual(
            int(self.candidate_api["get_free_bytes"]()),
            end,
        )
        self.assertEqual(
            int(self.candidate_api["get_minimum_bytes"]()),
            end,
        )
        self.assertEqual(
            self.free_list_state(self.candidate_api),
            ((0, end, end), (end, 0, NULL_OFFSET)),
        )

    def test_alignment_split_and_first_fit_match_pristine_upstream(
        self,
    ) -> None:
        self.reset_both(self.candidate_api, self.oracle_api)
        requests = (1, 7, 8, 9, 15, 16, 17, 31, 32, 63, 64, 255)
        results = [self.malloc_both(size) for size in requests]
        self.assertTrue(all(result != NULL_OFFSET for result in results))
        self.assertTrue(all(result & 7 == 0 for result in results))
        self.assertEqual(results[0], 16)

        header = int(self.candidate_api["get_struct_size"]())
        for result in results:
            block_size = int(
                self.candidate_api["get_block_size"](result - header)
            )
            self.assertNotEqual(block_size & 0x8000_0000, 0)
            self.assertEqual(block_size & 7, 0)
        self.assertEqual(
            int(self.candidate_api["get_allocation_count"]()),
            len(requests),
        )
        self.assertEqual(
            int(self.candidate_api["get_suspend_count"]()),
            len(requests),
        )
        self.assertEqual(
            int(self.candidate_api["get_resume_count"]()),
            len(requests),
        )

    def test_exact_fit_and_strict_minimum_split_rule(self) -> None:
        for remainder in (0, 32):
            with self.subTest(remainder=remainder):
                self.reset_both(self.candidate_api, self.oracle_api)
                self.candidate_api["init"]()
                self.oracle_api["init"]()
                initial = int(self.candidate_api["get_free_bytes"]())
                header = int(self.candidate_api["get_struct_size"]())
                requested = initial - remainder - header - 8
                self.assertEqual(requested & 7, 0)
                payload = self.malloc_both(requested)
                self.assertEqual(payload, header)
                self.assertEqual(
                    int(self.candidate_api["get_free_bytes"]()),
                    0,
                )
                self.assertEqual(
                    int(self.candidate_api["get_start_next_offset"]()),
                    int(self.candidate_api["get_end_offset"]()),
                )
                self.assertEqual(
                    int(self.candidate_api["get_block_size"](0)),
                    initial | 0x8000_0000,
                )

    def test_overflow_invalid_size_and_failure_hook_ordering(self) -> None:
        self.reset_both(self.candidate_api, self.oracle_api)
        for wanted_size in (
            0,
            0x7FFF_FFF8,
            0x8000_0000,
            0xFFFF_FFF8,
            0x0003_0000,
        ):
            self.assertEqual(
                self.malloc_both(wanted_size),
                NULL_OFFSET,
            )
        self.assertEqual(
            int(self.candidate_api["get_malloc_failed_count"]()),
            5,
        )
        self.assertEqual(
            int(self.candidate_api["get_suspend_count"]()),
            5,
        )
        self.assertEqual(
            int(self.candidate_api["get_resume_count"]()),
            5,
        )
        self.assertEqual(
            int(self.candidate_api["get_allocation_count"]()),
            0,
        )
        self.assertEqual(
            int(self.candidate_api["get_assert_count"]()),
            0,
        )

    def test_free_coalesces_both_directions_and_restores_accounting(
        self,
    ) -> None:
        self.reset_both(self.candidate_api, self.oracle_api)
        initial = None
        payloads = [self.malloc_both(size) for size in (24, 40, 56)]
        initial = (
            int(self.candidate_api["get_free_bytes"]())
            + sum(
                int(
                    self.candidate_api["get_block_size"](
                        payload -
                        int(self.candidate_api["get_struct_size"]())
                    )
                ) & 0x7FFF_FFFF
                for payload in payloads
            )
        )
        minimum = int(self.candidate_api["get_minimum_bytes"]())

        self.assertEqual(self.free_both(payloads[0]), 0)
        self.assertEqual(self.free_both(payloads[2]), 0)
        fragmented = self.free_list_state(self.candidate_api)
        self.assertEqual(len(fragmented), 3)

        self.assertEqual(self.free_both(payloads[1]), 0)
        self.assertEqual(
            self.free_list_state(self.candidate_api),
            (
                (0, initial, int(self.candidate_api["get_end_offset"]())),
                (
                    int(self.candidate_api["get_end_offset"]()),
                    0,
                    NULL_OFFSET,
                ),
            ),
        )
        self.assertEqual(
            int(self.candidate_api["get_free_bytes"]()),
            initial,
        )
        self.assertEqual(
            int(self.candidate_api["get_minimum_bytes"]()),
            minimum,
        )
        self.assertEqual(
            int(self.candidate_api["get_allocation_count"]()),
            3,
        )
        self.assertEqual(
            int(self.candidate_api["get_free_count"]()),
            3,
        )

    def test_double_free_asserts_before_scheduler_or_accounting_changes(
        self,
    ) -> None:
        self.reset_both(self.candidate_api, self.oracle_api)
        payload = self.malloc_both(48)
        self.assertEqual(self.free_both(payload), 0)
        before = self.scalar_state(self.candidate_api)
        free_list = self.free_list_state(self.candidate_api)
        self.assertEqual(self.free_both(payload), 1)
        after = self.scalar_state(self.candidate_api)
        self.assertEqual(after[:-1], before[:-1])
        self.assertEqual(after[-1], before[-1] + 1)
        self.assertEqual(
            self.free_list_state(self.candidate_api),
            free_list,
        )

    def test_null_free_is_a_true_no_op(self) -> None:
        self.reset_both(self.candidate_api, self.oracle_api)
        self.candidate_api["init"]()
        self.oracle_api["init"]()
        before = self.scalar_state(self.candidate_api)
        self.assertEqual(self.free_both(NULL_OFFSET), 0)
        self.assertEqual(self.scalar_state(self.candidate_api), before)

    def test_deterministic_fragmentation_oracle_covers_accounting(
        self,
    ) -> None:
        self.reset_both(self.candidate_api, self.oracle_api)
        generator = random.Random(0x1051_04)
        live: list[int] = []
        sizes = [
            1,
            2,
            7,
            8,
            9,
            15,
            16,
            24,
            31,
            32,
            33,
            64,
            127,
            255,
            1024,
            4095,
            8192,
        ]
        last_minimum = HEAP_BYTES
        for _ in range(300):
            if live and generator.randrange(4) == 0:
                index = generator.randrange(len(live))
                self.assertEqual(self.free_both(live.pop(index)), 0)
            else:
                payload = self.malloc_both(generator.choice(sizes))
                if payload != NULL_OFFSET:
                    live.append(payload)
            current_minimum = int(
                self.candidate_api["get_minimum_bytes"]()
            )
            self.assertLessEqual(current_minimum, last_minimum)
            self.assertLessEqual(
                int(self.candidate_api["get_free_bytes"]()),
                HEAP_BYTES,
            )
            last_minimum = current_minimum

        generator.shuffle(live)
        for payload in live:
            self.assertEqual(self.free_both(payload), 0)
        self.assertEqual(
            int(self.candidate_api["get_free_bytes"]()),
            int(self.candidate_api["get_end_offset"]()),
        )
        self.assertEqual(
            int(self.candidate_api["get_allocation_count"]()),
            int(self.candidate_api["get_free_count"]()),
        )

    def test_stock_spans_hashes_and_contiguous_closure_are_exact(
        self,
    ) -> None:
        closure = bytearray()
        for name, (start, end, expected_hash) in STOCK_FUNCTIONS.items():
            with self.subTest(function=name):
                body = self.span(start, end)
                self.assertEqual(len(body), end - start)
                self.assertEqual(sha256(body), expected_hash)
                closure.extend(body)
        self.assertEqual(len(closure), 552)
        self.assertEqual(sha256(bytes(closure)), STOCK_CLOSURE_SHA256)

    def test_stock_callers_outgoing_branches_and_references_are_exact(
        self,
    ) -> None:
        entries = set(STOCK_CALLERS)
        closure_start = min(entries)
        closure_end = max(end for _start, end, _hash in STOCK_FUNCTIONS.values())
        observed = {entry: [] for entry in entries}
        jumps = []
        external_interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target in entries:
                    if link:
                        observed[target].append((address, encoded.hex()))
                    else:
                        jumps.append((address, target, encoded.hex()))
                if (
                    closure_start < target < closure_end
                    and target not in entries
                    and not closure_start <= address < closure_end
                ):
                    external_interior.append(
                        (address, target, link, encoded.hex())
                    )
        self.assertEqual(observed, STOCK_CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(external_interior, [])
        for entry, callers in observed.items():
            self.assertEqual(
                sha256(
                    b"".join(
                        struct.pack("<I", address)
                        for address, _encoded in callers
                    )
                ),
                STOCK_CALLER_DIGESTS[entry],
            )

        outgoing = []
        for address in range(closure_start, closure_end - 3, 2):
            encoded = self.span(address, address + 4)
            try:
                target = self.apollo_overlay.decode_thumb_branch(
                    address,
                    encoded,
                    link=True,
                )
            except self.apollo_overlay.BuildError:
                continue
            if target != address:
                outgoing.append((address, encoded.hex(), target))
        self.assertEqual(outgoing, STOCK_OUTGOING)

        narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in narrow_branch_targets(address, halfword):
                if (
                    closure_start <= target < closure_end
                    and not closure_start <= address < closure_end
                ):
                    narrow.append((address, target, halfword))
        self.assertEqual(narrow, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if closure_start <= (value & ~1) < closure_end:
                stored.append((APPLICATION_BASE + offset, value))
        self.assertEqual(stored, [(0x005A_6C69, 0x0045_62C0)])
        self.assertEqual(0x005A_6C69 & 3, 1)

    @_APPLE_ONLY
    def test_target_function_sections_hashes_relocations_and_closure(
        self,
    ) -> None:
        self.assertEqual(self.target_compile.stderr, "")
        ordered = []
        for function in (
            "open_cfw_freertos_heap4_malloc",
            "open_cfw_freertos_heap4_free",
            "open_cfw_freertos_heap4_init",
            "open_cfw_freertos_heap4_insert_free_block",
        ):
            expected_size, expected_hash, expected_relocations = (
                TARGET_FUNCTIONS[function]
            )
            with self.subTest(function=function):
                section = self.sections_by_name[f".text.{function}"]
                body = self.target_text(function)
                ordered.append(body)
                self.assertEqual(len(body), expected_size)
                self.assertEqual(sha256(body), expected_hash)
                self.assertEqual(int(section["alignment"]), 4)
                self.assertEqual(int(section["flags"]) & 7, 6)
                self.assertEqual(
                    self.target_relocations(function),
                    expected_relocations,
                )

                symbol = self.symbols_by_name[function]
                self.assertEqual(symbol[3] >> 4, 1)
                self.assertEqual(symbol[3] & 0x0F, 2)
                self.assertEqual(symbol[5], int(section["index"]))
                self.assertEqual(symbol[1] & ~1, 0)
                self.assertEqual(symbol[2], expected_size)

        closure = b"".join(ordered)
        self.assertEqual(len(closure), TARGET_CLOSURE_SIZE)
        self.assertEqual(sha256(closure), TARGET_CLOSURE_SHA256)
        self.assertLess(len(closure), 0x800)

        undefined = {
            name
            for name, fields in self.symbols
            if name and fields[5] == 0
        }
        self.assertEqual(undefined, {"ulSetInterruptMask"})

        writable_allocated = [
            (
                str(section["name"]),
                int(section["size"]),
                int(section["flags"]),
            )
            for section in self.sections
            if (
                int(section["size"]) > 0
                and int(section["flags"]) & 0x2
                and int(section["flags"]) & 0x1
            )
        ]
        self.assertEqual(writable_allocated, [])

        executable_sections = {
            str(section["name"])
            for section in self.sections
            if (
                int(section["size"]) > 0
                and int(section["flags"]) & 0x4
            )
        }
        self.assertEqual(
            executable_sections,
            {f".text.{function}" for function in TARGET_FUNCTIONS},
        )

    @_APPLE_ONLY
    def test_production_heap4_closure_redirects_and_artifacts_are_exact(
        self,
    ) -> None:
        names = list(PRODUCTION_FUNCTIONS)
        config_leaves = [
            next(
                leaf
                for leaf in self.current_config["relocated_leaves"]
                if leaf["function"] == name
            )
            for name in names
        ]
        report_leaves = [
            next(
                leaf
                for leaf in self.current_report["relocated_leaves"]
                if leaf["extraction"]["function"] == name
            )
            for name in names
        ]
        self.assertEqual(
            [
                function
                for function in self.current_config["functions"]
                if function in PRODUCTION_FUNCTIONS
            ],
            names,
        )
        self.assertEqual(
            [leaf["function"] for leaf in config_leaves],
            names,
        )
        self.assertEqual(
            [leaf["extraction"]["function"] for leaf in report_leaves],
            names,
        )
        self.assertEqual(
            self.current_config["expected"],
            {
                "overlay_size": PRODUCTION_OVERLAY_SIZE,
                "overlay_sha256": PRODUCTION_OVERLAY_SHA256,
                "component_size": PRODUCTION_COMPONENT_SIZE,
                "component_sha256": PRODUCTION_COMPONENT_SHA256,
            },
        )

        overlay_base = int(
            self.current_report["overlay"]["overlay_runtime_address"]
        )
        for config_leaf, report_leaf in zip(
            config_leaves,
            report_leaves,
        ):
            name = config_leaf["function"]
            expected = PRODUCTION_FUNCTIONS[name]
            raw_hash = TARGET_FUNCTIONS[name][1]
            with self.subTest(function=name):
                self.assertEqual(
                    {
                        "path": config_leaf["source"]["path"],
                        "size": config_leaf["source"]["size"],
                        "sha256": config_leaf["source"]["sha256"],
                    },
                    {
                        "path": (
                            "components/apollo_main/core_overlay/"
                            "runtime_freertos_heap4.c"
                        ),
                        "size": SOURCE_SIZE,
                        "sha256": SOURCE_SHA256,
                    },
                )
                self.assertEqual(
                    config_leaf["expected"],
                    {
                        "size": expected["size"],
                        "sha256": expected["sha256"],
                        "alignment": 4,
                        "offset": expected["offset"],
                        "unrelocated_sha256": raw_hash,
                    },
                )
                placement = report_leaf["placement"]
                self.assertEqual(
                    placement,
                    {
                        "alignment": 4,
                        "offset": expected["offset"],
                        "padding_before": expected["padding_before"],
                        "runtime_address": expected["runtime_address"],
                        "runtime_address_hex": (
                            f"0x{expected['runtime_address']:08X}"
                        ),
                        "size": expected["size"],
                    },
                )
                extraction = report_leaf["extraction"]
                self.assertEqual(extraction["sha256"], expected["sha256"])
                self.assertEqual(
                    extraction["unrelocated_sha256"],
                    raw_hash,
                )
                self.assertEqual(
                    overlay_base + expected["offset"],
                    expected["runtime_address"],
                )
                body = self.current_overlay[
                    expected["offset"]:
                    expected["offset"] + expected["size"]
                ]
                self.assertEqual(sha256(body), expected["sha256"])

        component = self.current_report["component"]
        self.assertEqual(
            (len(self.current_overlay), sha256(self.current_overlay)),
            (PRODUCTION_OVERLAY_SIZE, PRODUCTION_OVERLAY_SHA256),
        )
        self.assertEqual(
            (len(self.current_component), sha256(self.current_component)),
            (PRODUCTION_COMPONENT_SIZE, PRODUCTION_COMPONENT_SHA256),
        )
        self.assertEqual(component["replaced_stock_function_bytes"], 84_836)
        self.assertEqual(component["generated_patch_site_bytes"], 84_654)
        self.assertEqual(component["generated_wrapper_bytes"], 32)
        self.assertEqual(component["source_owned_in_place_bytes"], 182)
        self.assertEqual(component["source_owned_bytes"], 121_900)
        self.assertEqual(component["opaque_base_bytes"], 3_438_528)

        patches = [
            next(
                patch
                for patch in self.current_report["overlay"]["patched_sites"]
                if patch["name"] == specification[0]
            )
            for specification in PRODUCTION_PATCHES
        ]
        self.assertEqual(
            [patch["name"] for patch in patches],
            [specification[0] for specification in PRODUCTION_PATCHES],
        )
        for patch, specification in zip(
            patches,
            PRODUCTION_PATCHES,
        ):
            name, payload_offset, stock_address, stock_size, target = (
                specification
            )
            with self.subTest(patch=name):
                target_address = PRODUCTION_FUNCTIONS[target][
                    "runtime_address"
                ]
                replacement = bytes.fromhex(patch["replacement_hex"])
                self.assertEqual(patch["payload_offset"], payload_offset)
                self.assertEqual(len(replacement), stock_size)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        stock_address,
                        replacement[:4],
                        link=False,
                    ),
                    target_address,
                )
                self.assertEqual(
                    self.current_component[
                        payload_offset:payload_offset + stock_size
                    ],
                    replacement,
                )
                stock_start, stock_end, stock_hash = STOCK_FUNCTIONS[
                    target.removeprefix("open_cfw_freertos_heap4_")
                ]
                self.assertEqual(stock_address, stock_start)
                self.assertEqual(stock_size, stock_end - stock_start)
                self.assertEqual(
                    sha256(self.span(stock_start, stock_end)),
                    stock_hash,
                )


if __name__ == "__main__":
    unittest.main()
