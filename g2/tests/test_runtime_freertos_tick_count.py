from __future__ import annotations

import os

import ctypes
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "shared"
    / "freertos"
    / "runtime_freertos_tick_count.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_tick_count_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_FREERTOS_H = (
    ROOT / "third_party" / "freertos-kernel" / "include" / "FreeRTOS.h"
)
UPSTREAM_PORT_MACROS = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "portmacrocommon.h"
)
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
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CURRENT_OVERLAY_BUILD = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "build"
)
CURRENT_OVERLAY_REPORT = CURRENT_OVERLAY_BUILD / "build-report.json"
CURRENT_OVERLAY = CURRENT_OVERLAY_BUILD / "apollo_core_overlay.bin"
CURRENT_COMPONENT = (
    CURRENT_OVERLAY_BUILD / "ota_s200_firmware_ota.bin"
)
CORE_SOURCE_MANIFEST = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)
CORE_SOURCE_REPORT = ROOT / "build" / "source" / "build-report.json"
CORE_SOURCE_PACKAGE = (
    ROOT
    / "build"
    / "source"
    / "package"
    / "g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
)

SOURCE_SHA256 = (
    "948d1b2de6026adc7cf84a34a359c859"
    "c32126b3afcafe92c2347f5f7ab56363"
)
HEADER_SHA256 = (
    "adc4065b3504a7eacb2e29e2d3576369"
    "17e2b690afc49b265689e36d66171dae"
)
HOST_FIXTURE_SHA256 = (
    "88457f3b3957e83dde5b3a4791b1e241"
    "08d0f05d02a48e8766f650a76549f013"
)

BASE = 0x00438000
TASK_START = 0x00454EFE
TASK_END = 0x00454F06
FROM_ISR_START = 0x00454F06
FROM_ISR_END = 0x00454F10
TICK_COUNT_LITERAL = 0x004557AC
TICK_COUNT_WORD = 0x20074A34

TARGET_COMMON_FLAGS = [
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
LEAVES = {
    "TASK": {
        "symbol": "open_cfw_freertos_task_get_tick_count",
        "size": 4,
        "bytes": "fff7febf",
        "sha256": (
            "90a54a1f68a806a1795bd04485690823"
            "5426b3c0f67be605fb94d3d5344a747f"
        ),
        "undefined": {"open_cfw_freertos_tick_count_read"},
        "relocations": [
            (0, 30, "open_cfw_freertos_tick_count_read"),
        ],
    },
    "FROM_ISR": {
        "symbol": "open_cfw_freertos_task_get_tick_count_from_isr",
        "size": 4,
        "bytes": "fff7febf",
        "sha256": (
            "90a54a1f68a806a1795bd04485690823"
            "5426b3c0f67be605fb94d3d5344a747f"
        ),
        "undefined": {"open_cfw_freertos_tick_count_read"},
        "relocations": [
            (0, 30, "open_cfw_freertos_tick_count_read"),
        ],
    },
    "PROVIDER": {
        "symbol": "open_cfw_freertos_tick_count_read",
        "size": 12,
        "bytes": "44f63420c2f2070000687047",
        "sha256": (
            "cfebf8fa4a718de0d3d1b954cad1c9a2"
            "1dad627dfe62e3810da7d9e6e0423416"
        ),
        "undefined": set(),
        "relocations": [],
    },
}
U32_EDGE_VALUES = (
    0x00000000,
    0x00000001,
    0x00000002,
    0x0000FFFF,
    0x00010000,
    0x55555555,
    0x7FFFFFFE,
    0x7FFFFFFF,
    0x80000000,
    0x80000001,
    0xAAAAAAAA,
    0xFFFFFFFE,
    0xFFFFFFFF,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeFreeRTOSTickCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            dir=temporary_parent
        )
        temporary = Path(cls.temporary.name)

        library = temporary / library_name(
            "runtime_freertos_tick_count"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(HOST_FIXTURE),
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

        cls.set_ticks = (
            cls.loaded.open_cfw_test_freertos_tick_count_set
        )
        cls.set_ticks.argtypes = [ctypes.c_uint32]
        cls.set_ticks.restype = None

        cls.get_task = (
            cls.loaded.open_cfw_test_freertos_tick_count_get_task
        )
        cls.get_task.argtypes = []
        cls.get_task.restype = ctypes.c_uint32

        cls.get_from_isr = (
            cls.loaded.open_cfw_test_freertos_tick_count_get_from_isr
        )
        cls.get_from_isr.argtypes = []
        cls.get_from_isr.restype = ctypes.c_uint32

        cls.get_provider = (
            cls.loaded.open_cfw_test_freertos_tick_count_get_provider
        )
        cls.get_provider.argtypes = []
        cls.get_provider.restype = ctypes.c_uint32

        cls.get_reads = (
            cls.loaded.open_cfw_test_freertos_tick_count_reads
        )
        cls.get_reads.argtypes = []
        cls.get_reads.restype = ctypes.c_uint32

        cls.target_objects = {}
        for leaf_name in LEAVES:
            target_object = temporary / (
                f"runtime_freertos_tick_count_{leaf_name.lower()}.o"
            )
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *TARGET_COMMON_FLAGS,
                    "-DOPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF",
                    (
                        "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_"
                        f"{leaf_name}"
                    ),
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(target_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.target_objects[leaf_name] = target_object

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw
        cls.overlay_config = json.loads(
            OVERLAY_CONFIG.read_text(encoding="utf-8")
        )
        cls.production = apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY_CONFIG,
            output_dir=temporary / "production",
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        (
            cls.package_manifest,
            cls.package_root,
            cls.package_payloads,
        ) = open_cfw.verify_manifest(CORE_SOURCE_MANIFEST)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def span(application: bytes, start: int, end: int) -> bytes:
        return application[start - BASE:end - BASE]

    def test_authenticated_upstream_snapshot_and_atomic_port_selection(
        self,
    ) -> None:
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            sha256(UPSTREAM_TASKS),
            "14020d617b96dd2814e1211f6e3b645b"
            "cf5e2bd3179c23fe7dd16bc666fe9463",
        )
        self.assertEqual(
            sha256(UPSTREAM_FREERTOS_H),
            "03e9c94aba57e3cf7f4f73bc2d3eb4a"
            "96ae38f3425eedb5450622ca286475a0b",
        )
        self.assertEqual(
            sha256(UPSTREAM_PORT_MACROS),
            "c184e6b1727732bbdd0d4dd33b9af4e"
            "a25d13040620666123941fff464bffc99",
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)
        self.assertIn(
            "portTICK_TYPE_IS_ATOMIC    1",
            UPSTREAM_PORT_MACROS.read_text(encoding="utf-8"),
        )

        upstream = UPSTREAM_TASKS.read_text(encoding="utf-8")
        task_start = upstream.index(
            "TickType_t xTaskGetTickCount( void )"
        )
        from_isr_start = upstream.index(
            "TickType_t xTaskGetTickCountFromISR( void )",
            task_start,
        )
        next_start = upstream.index(
            "UBaseType_t uxTaskGetNumberOfTasks( void )",
            from_isr_start,
        )
        task_body = upstream[task_start:from_isr_start]
        from_isr_body = upstream[from_isr_start:next_start]
        self.assertEqual(task_body.count("xTicks = xTickCount;"), 1)
        self.assertEqual(
            from_isr_body.count("xReturn = xTickCount;"),
            1,
        )
        for token in (
            "portTICK_TYPE_ENTER_CRITICAL();",
            "portTICK_TYPE_EXIT_CRITICAL();",
        ):
            self.assertIn(token, task_body)
        for token in (
            "portTICK_TYPE_SET_INTERRUPT_MASK_FROM_ISR();",
            "portTICK_TYPE_CLEAR_INTERRUPT_MASK_FROM_ISR(",
        ):
            self.assertIn(token, from_isr_body)

    def test_official_leaves_share_the_recovered_tick_word(self) -> None:
        package = OFFICIAL.read_bytes()
        self.assertEqual(len(package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        application = package[32:]

        expected = (
            (
                TASK_START,
                TASK_END,
                "dff8ac0800687047",
                "6dbb234e35fb86f883529c083fed0e1c"
                "abdca99d6647a95568ed1a5522310ac0",
                0x8AC,
                0,
            ),
            (
                FROM_ISR_START,
                FROM_ISR_END,
                "0020dff8a00800687047",
                "8fe0a4f494b20b340d1126b2da725919"
                "f86c53cc3c1cabf5031fffc03f6de63a",
                0x8A0,
                2,
            ),
        )
        for start, end, raw, digest, immediate, literal_offset in expected:
            with self.subTest(start=f"0x{start:08X}"):
                body = self.span(application, start, end)
                self.assertEqual(len(body), end - start)
                self.assertEqual(body.hex(), raw)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
                first, second = struct.unpack_from(
                    "<HH",
                    body,
                    literal_offset,
                )
                self.assertEqual(first, 0xF8DF)
                self.assertEqual(second >> 12, 0)
                self.assertEqual(second & 0x0FFF, immediate)
                pc = (start + literal_offset + 4) & ~3
                self.assertEqual(pc + immediate, TICK_COUNT_LITERAL)
                self.assertEqual(
                    body[literal_offset + 4:],
                    bytes.fromhex("00687047"),
                )
        self.assertEqual(
            self.span(
                application,
                FROM_ISR_START,
                FROM_ISR_START + 2,
            ),
            bytes.fromhex("0020"),
        )

        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(
                    application,
                    TICK_COUNT_LITERAL,
                    TICK_COUNT_LITERAL + 4,
                ),
            )[0],
            TICK_COUNT_WORD,
        )
    def test_task_getter_returns_all_u32_edges_with_one_read(self) -> None:
        for ticks in U32_EDGE_VALUES:
            with self.subTest(ticks=f"0x{ticks:08X}"):
                self.set_ticks(ticks)
                self.assertEqual(self.get_task(), ticks)
                self.assertEqual(self.get_reads(), 1)

    def test_isr_getter_returns_all_u32_edges_with_one_read(self) -> None:
        for ticks in U32_EDGE_VALUES:
            with self.subTest(ticks=f"0x{ticks:08X}"):
                self.set_ticks(ticks)
                self.assertEqual(self.get_from_isr(), ticks)
                self.assertEqual(self.get_reads(), 1)

    def test_public_leaves_do_not_cache_or_share_a_read(self) -> None:
        self.set_ticks(0xFFFFFFFF)
        self.assertEqual(self.get_task(), 0xFFFFFFFF)
        self.assertEqual(self.get_reads(), 1)
        self.assertEqual(self.get_from_isr(), 0xFFFFFFFF)
        self.assertEqual(self.get_reads(), 2)
        self.assertEqual(self.get_provider(), 0xFFFFFFFF)
        self.assertEqual(self.get_reads(), 3)

    def test_each_target_leaf_has_a_pinned_extractable_abi(self) -> None:
        for leaf_name, expected in LEAVES.items():
            with self.subTest(leaf=leaf_name):
                data, sections = self.apollo_overlay.parse_elf32(
                    self.target_objects[leaf_name]
                )
                symbol_table = self.apollo_overlay.section_named(
                    sections,
                    ".symtab",
                )
                string_table = sections[int(symbol_table["link"])]
                strings = data[
                    int(string_table["offset"]):
                    int(string_table["offset"])
                    + int(string_table["size"])
                ]
                symbols = []
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
                    symbols.append((name, fields))

                function = next(
                    fields
                    for name, fields in symbols
                    if name == expected["symbol"]
                )
                function_section = sections[int(function[5])]
                self.assertEqual(
                    function_section["name"],
                    f".text.{expected['symbol']}",
                )
                self.assertEqual(int(function_section["flags"]), 0x6)
                self.assertEqual(int(function_section["alignment"]), 4)
                self.assertEqual(
                    (int(function[1]), int(function[2])),
                    (1, expected["size"]),
                )
                self.assertEqual(function[3] & 0x0F, 2)

                raw = data[
                    int(function_section["offset"]):
                    int(function_section["offset"])
                    + int(function_section["size"])
                ]
                self.assertEqual(len(raw), expected["size"])
                self.assertEqual(raw.hex(), expected["bytes"])
                self.assertEqual(
                    hashlib.sha256(raw).hexdigest(),
                    expected["sha256"],
                )

                defined_functions = {
                    name
                    for name, fields in symbols
                    if name
                    and fields[3] & 0x0F == 2
                    and fields[5] != 0
                }
                undefined = {
                    name
                    for name, fields in symbols
                    if name and fields[5] == 0
                }
                self.assertEqual(
                    defined_functions,
                    {expected["symbol"]},
                )
                self.assertEqual(undefined, expected["undefined"])

                relocations = []
                for section in sections:
                    if (
                        int(section["type"]) == 9
                        and int(section["info"])
                        == int(function_section["index"])
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
                                    symbols[information >> 8][0],
                                )
                            )
                self.assertEqual(
                    relocations,
                    expected["relocations"],
                )

                for prefix in (".data", ".bss", ".rodata"):
                    self.assertFalse(
                        any(
                            section["name"].startswith(prefix)
                            and int(section["size"]) != 0
                            for section in sections
                        ),
                        (leaf_name, prefix),
                    )

    def test_source_boundary_is_pinned_and_has_no_hidden_state(
        self,
    ) -> None:
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(sha256(HOST_FIXTURE), HOST_FIXTURE_SHA256)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "xTaskGetTickCount()",
            "xTaskGetTickCountFromISR()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "portTICK_TYPE_IS_ATOMIC == 1",
            "[0x00454EFE, 0x00454F06)",
            "[0x00454F06, 0x00454F10)",
            "0x20074A34",
            "return OPEN_CFW_FREERTOS_TICK_COUNT_WORD",
            "ticks = OPEN_CFW_FREERTOS_TICK_COUNT_READ()",
        ):
            self.assertIn(token, source)
        for token in (
            "typedef __UINT32_TYPE__ open_cfw_freertos_tick_type",
            "OPEN_CFW_FREERTOS_TICK_COUNT_ADDRESS = 0x20074A34U",
            "volatile open_cfw_freertos_tick_type",
            "open_cfw_freertos_tick_count_read(void)",
        ):
            self.assertIn(token, header)
        for disallowed in (
            "static volatile",
            "static open_cfw_freertos_tick_type",
            "const char",
            "struct ",
        ):
            self.assertNotIn(disallowed, source)

    def test_leaf_selection_fails_closed(self) -> None:
        base_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            *TARGET_COMMON_FLAGS,
            "-DOPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF",
            "-fsyntax-only",
            str(SOURCE),
        ]
        no_leaf = subprocess.run(
            base_command,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(no_leaf.returncode, 0)
        self.assertIn(
            "select exactly one FreeRTOS tick-count leaf",
            no_leaf.stderr,
        )

        two_leaves = subprocess.run(
            [
                *base_command[:-2],
                "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_TASK",
                "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_PROVIDER",
                *base_command[-2:],
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(two_leaves.returncode, 0)
        self.assertIn(
            "select exactly one FreeRTOS tick-count leaf",
            two_leaves.stderr,
        )

    @_APPLE_ONLY
    def test_production_config_report_redirects_and_artifacts_are_exact(
        self,
    ) -> None:
        functions = (
            "open_cfw_freertos_tick_count_read",
            "open_cfw_freertos_task_get_tick_count",
            "open_cfw_freertos_task_get_tick_count_from_isr",
        )
        leaves = [
            leaf
            for leaf in self.overlay_config["relocated_leaves"]
            if leaf["function"] in functions
        ]
        self.assertEqual(
            [leaf["function"] for leaf in leaves],
            list(functions),
        )
        expected_function_order = [
            *functions,
            "open_cfw_tinyframe_cksum_add",
            "open_cfw_transport_crc32_update",
            "open_cfw_crc16_ccitt_xmodem",
            "open_cfw_crc16_ccitt",
            "open_cfw_freertos_task_missed_yield",
            "open_cfw_freertos_task_reset_event_item_value",
            "open_cfw_freertos_task_increment_mutex_held_count",
        ]
        self.assertEqual(
            [
                function
                for function in self.overlay_config["functions"]
                if function in set(expected_function_order)
            ],
            expected_function_order,
        )

        expected_leaves = {
            functions[0]: {
                "offset": 115_320,
                "size": 12,
                "sha256": (
                    "cfebf8fa4a718de0d3d1b954cad1c9a2"
                    "1dad627dfe62e3810da7d9e6e0423416"
                ),
                "unrelocated_sha256": (
                    "cfebf8fa4a718de0d3d1b954cad1c9a2"
                    "1dad627dfe62e3810da7d9e6e0423416"
                ),
                "selector": (
                    "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_PROVIDER"
                ),
                "relocations": [],
                "bytes": "44f63420c2f2070000687047",
            },
            functions[1]: {
                "offset": 115_332,
                "size": 4,
                "sha256": (
                    "f52f0e05236261aa72331dfeceb18c21"
                    "e2682694afdff01ed96046c5dda3c2ed"
                ),
                "unrelocated_sha256": (
                    "90a54a1f68a806a1795bd04485690823"
                    "5426b3c0f67be605fb94d3d5344a747f"
                ),
                "selector": (
                    "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_TASK"
                ),
                "relocations": [
                    {
                        "offset": 0,
                        "type": "R_ARM_THM_JUMP24",
                        "symbol": functions[0],
                        "target_function": functions[0],
                    }
                ],
                "bytes": "fff7f8bf",
            },
            functions[2]: {
                "offset": 115_336,
                "size": 4,
                "sha256": (
                    "cdcdfc75bb08504fce75a95fac5acf2c"
                    "8f9502c9eecc7c886198f721cf321b0b"
                ),
                "unrelocated_sha256": (
                    "90a54a1f68a806a1795bd04485690823"
                    "5426b3c0f67be605fb94d3d5344a747f"
                ),
                "selector": (
                    "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_FROM_ISR"
                ),
                "relocations": [
                    {
                        "offset": 0,
                        "type": "R_ARM_THM_JUMP24",
                        "symbol": functions[0],
                        "target_function": functions[0],
                    }
                ],
                "bytes": "fff7f6bf",
            },
        }
        for leaf in leaves:
            function = leaf["function"]
            expected = expected_leaves[function]
            self.assertEqual(
                leaf["source"],
                {
                    **leaf["source"],
                    "path": (
                        "components/shared/freertos/"
                        "runtime_freertos_tick_count.c"
                    ),
                    "size": 3_412,
                    "sha256": SOURCE_SHA256,
                    "license": "MIT",
                    "upstream_commit": (
                        "def7d2df2b0506d3d249334974f51e427c17a41c"
                    ),
                },
            )
            self.assertIn(
                "-DOPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF",
                leaf["toolchain"]["flags"],
            )
            self.assertIn(
                expected["selector"],
                leaf["toolchain"]["flags"],
            )
            self.assertEqual(
                leaf["expected"],
                {
                    "size": expected["size"],
                    "sha256": expected["sha256"],
                    "alignment": 4,
                    "offset": expected["offset"],
                    "unrelocated_sha256": (
                        expected["unrelocated_sha256"]
                    ),
                },
            )
            self.assertEqual(
                leaf["relocations"],
                expected["relocations"],
            )

        report_leaves = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.production["relocated_leaves"]
            if leaf["extraction"]["function"] in functions
        }
        self.assertEqual(set(report_leaves), set(functions))
        overlay_path = ROOT / self.production["overlay"]["artifact"]
        overlay = overlay_path.read_bytes()
        for function, expected in expected_leaves.items():
            report = report_leaves[function]
            extraction = report["extraction"]
            placement = report["placement"]
            self.assertEqual(
                (
                    placement["offset"],
                    placement["size"],
                    placement["alignment"],
                    placement["runtime_address"],
                ),
                (
                    expected["offset"],
                    expected["size"],
                    4,
                    0x00794324 + expected["offset"],
                ),
            )
            self.assertEqual(
                (
                    extraction["size"],
                    extraction["sha256"],
                    extraction["unrelocated_sha256"],
                    extraction["relocation_count"],
                ),
                (
                    expected["size"],
                    expected["sha256"],
                    expected["unrelocated_sha256"],
                    len(expected["relocations"]),
                ),
            )
            self.assertEqual(
                overlay[
                    expected["offset"]:
                    expected["offset"] + expected["size"]
                ].hex(),
                expected["bytes"],
            )
            self.assertEqual(
                self.production["overlay"]["functions"][function],
                {
                    "offset": expected["offset"],
                    "size": expected["size"],
                },
            )

        patch_expectations = {
            "replace_freertos_task_get_tick_count": {
                "address": TASK_START,
                "size": 8,
                "sha256": (
                    "6dbb234e35fb86f883529c083fed0e1c"
                    "abdca99d6647a95568ed1a5522310ac0"
                ),
                "target": functions[1],
                "replacement": "5bf353bb00bf00bf",
            },
            "replace_freertos_task_get_tick_count_from_isr": {
                "address": FROM_ISR_START,
                "size": 10,
                "sha256": (
                    "8fe0a4f494b20b340d1126b2da725919"
                    "f86c53cc3c1cabf5031fffc03f6de63a"
                ),
                "target": functions[2],
                "replacement": "5bf351bb00bf00bf00bf",
            },
        }
        patches = {
            patch["name"]: patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["name"] in patch_expectations
        }
        self.assertEqual(set(patches), set(patch_expectations))
        component = (
            ROOT / self.production["component"]["artifact"]
        ).read_bytes()
        official = OFFICIAL.read_bytes()
        for name, expected in patch_expectations.items():
            patch = patches[name]
            self.assertEqual(patch["runtime_address"], expected["address"])
            self.assertEqual(patch["expected_size"], expected["size"])
            self.assertEqual(patch["expected_sha256"], expected["sha256"])
            self.assertEqual(patch["target_function"], expected["target"])
            self.assertEqual(
                patch["replacement_hex"],
                expected["replacement"],
            )
            replacement = bytes.fromhex(expected["replacement"])
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    expected["address"],
                    replacement[:4],
                    link=False,
                ),
                patch["target_address"],
            )
            self.assertEqual(
                replacement[4:],
                b"\x00\xbf" * ((expected["size"] - 4) // 2),
            )
            offset = patch["payload_offset"]
            self.assertEqual(
                component[offset:offset + expected["size"]],
                replacement,
            )
            self.assertEqual(
                official[offset:offset + expected["size"]],
                self.span(
                    official[32:],
                    expected["address"],
                    expected["address"] + expected["size"],
                ),
            )

        self.assertEqual(
            (
                self.production["overlay"]["size"],
                self.production["overlay"]["sha256"],
                self.production["component"]["size"],
                self.production["component"]["sha256"],
            ),
            (
                165_412,
                "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada",
                3_688_808,
                "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c",
            ),
        )
        self.assertEqual(
            {
                key: self.production["component"][key]
                for key in (
                    "opaque_base_bytes",
                    "source_owned_bytes",
                    "source_owned_in_place_bytes",
                    "generated_wrapper_bytes",
                    "generated_patch_site_bytes",
                    "replaced_stock_function_bytes",
                )
            },
            {
                "opaque_base_bytes": 3_401_688,
                "source_owned_bytes": 165_594,
                "source_owned_in_place_bytes": 182,
                "generated_wrapper_bytes": 32,
                "generated_patch_site_bytes": 121_494,
                "replaced_stock_function_bytes": 121_672,
            },
        )

    @_APPLE_ONLY
    def test_production_config_relocations_and_rollback_are_exact(
        self,
    ) -> None:
        provider = "open_cfw_freertos_tick_count_read"
        contracts = {
            provider: {
                "macro": (
                    "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_PROVIDER"
                ),
                "origin": (
                    "bounded provider for the recovered G2 FreeRTOS "
                    "xTickCount compatibility word"
                ),
                "offset": 115_320,
                "address": 0x007B059C,
                "size": 12,
                "padding": 2,
                "sha256": (
                    "cfebf8fa4a718de0d3d1b954cad1c9a2"
                    "1dad627dfe62e3810da7d9e6e0423416"
                ),
                "unrelocated": (
                    "cfebf8fa4a718de0d3d1b954cad1c9a2"
                    "1dad627dfe62e3810da7d9e6e0423416"
                ),
                "relocations": [],
            },
            "open_cfw_freertos_task_get_tick_count": {
                "macro": "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_TASK",
                "origin": (
                    "source-equivalent adaptation of authenticated "
                    "FreeRTOS-Kernel V10.5.1 xTaskGetTickCount using "
                    "the recovered G2 atomic tick seam"
                ),
                "offset": 115_332,
                "address": 0x007B05A8,
                "size": 4,
                "padding": 0,
                "sha256": (
                    "f52f0e05236261aa72331dfeceb18c21"
                    "e2682694afdff01ed96046c5dda3c2ed"
                ),
                "unrelocated": (
                    "90a54a1f68a806a1795bd04485690823"
                    "5426b3c0f67be605fb94d3d5344a747f"
                ),
                "relocations": [
                    {
                        "offset": 0,
                        "type": "R_ARM_THM_JUMP24",
                        "symbol": provider,
                        "target_function": provider,
                    }
                ],
            },
            "open_cfw_freertos_task_get_tick_count_from_isr": {
                "macro": (
                    "-DOPEN_CFW_FREERTOS_TICK_COUNT_LEAF_FROM_ISR"
                ),
                "origin": (
                    "source-equivalent adaptation of authenticated "
                    "FreeRTOS-Kernel V10.5.1 "
                    "xTaskGetTickCountFromISR using the recovered G2 "
                    "atomic tick seam"
                ),
                "offset": 115_336,
                "address": 0x007B05AC,
                "size": 4,
                "padding": 0,
                "sha256": (
                    "cdcdfc75bb08504fce75a95fac5acf2c"
                    "8f9502c9eecc7c886198f721cf321b0b"
                ),
                "unrelocated": (
                    "90a54a1f68a806a1795bd04485690823"
                    "5426b3c0f67be605fb94d3d5344a747f"
                ),
                "relocations": [
                    {
                        "offset": 0,
                        "type": "R_ARM_THM_JUMP24",
                        "symbol": provider,
                        "target_function": provider,
                    }
                ],
            },
        }
        upstream_commit = (
            "def7d2df2b0506d3d249334974f51e427c17a41c"
        )
        upstream = (
            "https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/"
            f"{upstream_commit}/tasks.c"
        )
        common_flags = [
            *TARGET_COMMON_FLAGS[1:],
            "-DOPEN_CFW_FREERTOS_TICK_COUNT_BUILD_LEAF",
        ]
        configured = {
            leaf["function"]: leaf
            for leaf in self.overlay_config["relocated_leaves"]
            if leaf["function"] in contracts
        }
        reported = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.production["relocated_leaves"]
            if leaf["extraction"]["function"] in contracts
        }
        self.assertEqual(set(configured), set(contracts))
        self.assertEqual(set(reported), set(contracts))

        for function, expected in contracts.items():
            with self.subTest(function=function):
                config_leaf = configured[function]
                expected_source = {
                    "path": (
                        "components/shared/freertos/"
                        "runtime_freertos_tick_count.c"
                    ),
                    "size": 3_412,
                    "sha256": SOURCE_SHA256,
                    "license": "MIT",
                    "origin": expected["origin"],
                    "upstream": upstream,
                    "upstream_commit": upstream_commit,
                    "evidence": (
                        "docs/research/"
                        "freertos-task-count-source-boundary-audit.md"
                    ),
                }
                expected_toolchain = {
                    "target": "thumbv7em-none-eabi",
                    "reviewed_version_prefix": (
                        "Apple clang version 21.0.0"
                    ),
                    "flags": [*common_flags, expected["macro"]],
                }
                self.assertEqual(
                    config_leaf["source"],
                    expected_source,
                )
                self.assertEqual(
                    config_leaf["toolchain"],
                    expected_toolchain,
                )
                self.assertEqual(
                    config_leaf["expected"],
                    {
                        "size": expected["size"],
                        "sha256": expected["sha256"],
                        "alignment": 4,
                        "offset": expected["offset"],
                        "unrelocated_sha256": (
                            expected["unrelocated"]
                        ),
                    },
                )
                self.assertEqual(
                    config_leaf["relocations"],
                    expected["relocations"],
                )

                report_leaf = reported[function]
                self.assertEqual(
                    report_leaf["source"],
                    expected_source,
                )
                self.assertEqual(
                    {
                        "target": report_leaf["toolchain"]["target"],
                        "flags": report_leaf["toolchain"]["flags"],
                    },
                    {
                        "target": expected_toolchain["target"],
                        "flags": expected_toolchain["flags"],
                    },
                )
                self.assertTrue(
                    report_leaf["toolchain"]["version"].startswith(
                        expected_toolchain[
                            "reviewed_version_prefix"
                        ]
                    )
                )
                self.assertEqual(
                    report_leaf["placement"],
                    {
                        "alignment": 4,
                        "offset": expected["offset"],
                        "padding_before": expected["padding"],
                        "runtime_address": expected["address"],
                        "runtime_address_hex": (
                            f"0x{expected['address']:08X}"
                        ),
                        "size": expected["size"],
                    },
                )
                extraction = report_leaf["extraction"]
                self.assertEqual(
                    {
                        key: extraction[key]
                        for key in (
                            "alignment",
                            "function",
                            "relocation_count",
                            "runtime_address",
                            "runtime_address_hex",
                            "section",
                            "sha256",
                            "size",
                            "unrelocated_sha256",
                        )
                    },
                    {
                        "alignment": 4,
                        "function": function,
                        "relocation_count": len(
                            expected["relocations"]
                        ),
                        "runtime_address": expected["address"],
                        "runtime_address_hex": (
                            f"0x{expected['address']:08X}"
                        ),
                        "section": f".text.{function}",
                        "sha256": expected["sha256"],
                        "size": expected["size"],
                        "unrelocated_sha256": (
                            expected["unrelocated"]
                        ),
                    },
                )
                self.assertEqual(
                    [
                        {
                            key: relocation[key]
                            for key in (
                                "offset",
                                "runtime_address",
                                "symbol",
                                "target_address",
                                "target_function",
                                "type",
                                "type_id",
                            )
                        }
                        for relocation in extraction["relocations"]
                    ],
                    [
                        {
                            "offset": relocation["offset"],
                            "runtime_address": (
                                expected["address"]
                                + relocation["offset"]
                            ),
                            "symbol": relocation["symbol"],
                            "target_address": contracts[provider][
                                "address"
                            ],
                            "target_function": provider,
                            "type": relocation["type"],
                            "type_id": 30,
                        }
                        for relocation in expected["relocations"]
                    ],
                )

        self.assertEqual(
            self.overlay_config["expected"],
            {
                "overlay_size": 165_412,
                "overlay_sha256": (
                    "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada"
                ),
                "component_size": 3_688_808,
                "component_sha256": (
                    "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c"
                ),
            },
        )

        expected_patches = {
            "replace_freertos_task_get_tick_count": {
                "runtime_address": TASK_START,
                "expected_size": 8,
                "expected_sha256": (
                    "6dbb234e35fb86f883529c083fed0e1c"
                    "abdca99d6647a95568ed1a5522310ac0"
                ),
                "branch": "b_w",
                "target_function": (
                    "open_cfw_freertos_task_get_tick_count"
                ),
                "payload_offset": 118_558,
                "replacement": "5bf353bb00bf00bf",
                "stock": "dff8ac0800687047",
            },
            "replace_freertos_task_get_tick_count_from_isr": {
                "runtime_address": FROM_ISR_START,
                "expected_size": 10,
                "expected_sha256": (
                    "8fe0a4f494b20b340d1126b2da725919"
                    "f86c53cc3c1cabf5031fffc03f6de63a"
                ),
                "branch": "b_w",
                "target_function": (
                    "open_cfw_freertos_task_get_tick_count_from_isr"
                ),
                "payload_offset": 118_566,
                "replacement": "5bf351bb00bf00bf00bf",
                "stock": "0020dff8a00800687047",
            },
        }
        configured_patches = {
            patch["name"]: patch
            for patch in self.overlay_config["patch_sites"]
            if patch["name"] in expected_patches
        }
        report_patches = {
            patch["name"]: patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["name"] in expected_patches
        }
        self.assertEqual(set(configured_patches), set(expected_patches))
        self.assertEqual(set(report_patches), set(expected_patches))

        rebuilt_overlay = (
            ROOT / self.production["overlay"]["artifact"]
        ).read_bytes()
        rebuilt_component = (
            ROOT / self.production["component"]["artifact"]
        ).read_bytes()
        official = OFFICIAL.read_bytes()
        restored = bytearray(rebuilt_component)
        for name, expected in expected_patches.items():
            with self.subTest(patch=name):
                self.assertEqual(
                    configured_patches[name],
                    {
                        key: expected[key]
                        for key in (
                            "runtime_address",
                            "expected_size",
                            "expected_sha256",
                            "branch",
                            "target_function",
                        )
                    }
                    | {"name": name},
                )
                patch = report_patches[name]
                replacement = bytes.fromhex(expected["replacement"])
                stock = bytes.fromhex(expected["stock"])
                offset = expected["payload_offset"]
                self.assertEqual(
                    {
                        key: patch[key]
                        for key in (
                            "name",
                            "runtime_address",
                            "expected_size",
                            "expected_sha256",
                            "branch",
                            "target_function",
                            "payload_offset",
                            "replacement_hex",
                        )
                    },
                    {
                        "name": name,
                        "runtime_address": expected["runtime_address"],
                        "expected_size": expected["expected_size"],
                        "expected_sha256": expected["expected_sha256"],
                        "branch": "b_w",
                        "target_function": expected["target_function"],
                        "payload_offset": offset,
                        "replacement_hex": expected["replacement"],
                    },
                )
                self.assertEqual(
                    hashlib.sha256(stock).hexdigest(),
                    expected["expected_sha256"],
                )
                self.assertEqual(
                    official[offset:offset + len(stock)],
                    stock,
                )
                self.assertEqual(
                    rebuilt_component[
                        offset:offset + len(replacement)
                    ],
                    replacement,
                )
                target = contracts[expected["target_function"]][
                    "address"
                ]
                self.assertEqual(patch["target_address"], target)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        expected["runtime_address"],
                        replacement[:4],
                        link=False,
                    ),
                    target,
                )
                self.assertEqual(
                    replacement[4:],
                    b"\x00\xbf" * ((len(replacement) - 4) // 2),
                )
                restored[offset:offset + len(stock)] = stock

        self.assertEqual(
            (
                len(rebuilt_overlay),
                hashlib.sha256(rebuilt_overlay).hexdigest(),
                len(rebuilt_component),
                hashlib.sha256(rebuilt_component).hexdigest(),
            ),
            (
                165_412,
                "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada",
                3_688_808,
                "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c",
            ),
        )
        reset_unordered_tail_size = 388
        semaphore_take_tail_size = 624
        timeout_tail_size = 138
        next_closure_tail_size = 492
        lz4_tail_size = 1_758
        scheduler_tail_size = 782
        easylogger_tail_size = 2_094
        bq27427_tail_size = 4_634
        util_error_tail_size = 254
        task_get_info_tail_size = 122
        pre_task_get_info_overlay = rebuilt_overlay[:-task_get_info_tail_size]
        pre_util_error_overlay = pre_task_get_info_overlay[:-util_error_tail_size]
        pre_bq27427_overlay = pre_util_error_overlay[:-bq27427_tail_size]
        self.assertEqual(
            (
                len(pre_bq27427_overlay),
                hashlib.sha256(pre_bq27427_overlay).hexdigest(),
            ),
            (
                159_902,
                "094aa2f3bb6fc0484db27df117802801ce5483d74b36b9f6834e8bdf06f798b7",
            ),
        )
        pre_reset_unordered_overlay = pre_bq27427_overlay[
            :-reset_unordered_tail_size
        ]
        self.assertEqual(
            (
                len(pre_reset_unordered_overlay),
                hashlib.sha256(pre_reset_unordered_overlay).hexdigest(),
            ),
            (
                159_514,
                "cf7a05089cfee32a0593a976f7166033a2cc305a6a98f478e09e0b4b3d8173c3",
            ),
        )
        pre_semaphore_take_overlay = pre_reset_unordered_overlay[
            :-semaphore_take_tail_size
        ]
        self.assertEqual(
            (
                len(pre_semaphore_take_overlay),
                hashlib.sha256(pre_semaphore_take_overlay).hexdigest(),
            ),
            (
                158_890,
                "f4215dbd41d718c638deb51ba4c0f30c13a5311479d7ffe9c2054a8fcc502de8",
            ),
        )
        pre_easylogger_overlay = pre_semaphore_take_overlay[
            :-easylogger_tail_size
        ]
        self.assertEqual(
            (
                len(pre_easylogger_overlay),
                hashlib.sha256(pre_easylogger_overlay).hexdigest(),
            ),
            (
                156_796,
                "92d99a6eefc9ca8dc228d0fbc51b9dcd684f7b6cbf1dd1892875c64e939b462e",
            ),
        )
        pre_timeout_overlay = pre_easylogger_overlay[:-timeout_tail_size]
        self.assertEqual(
            (len(pre_timeout_overlay), hashlib.sha256(pre_timeout_overlay).hexdigest()),
            (
                156_658,
                "a0b36a6c7a860c06039add7eefe15b83807b2bb76f7f89954064184c0c39ac45",
            ),
        )
        lz4_overlay = pre_timeout_overlay[:-next_closure_tail_size]
        self.assertEqual(
            (len(lz4_overlay), hashlib.sha256(lz4_overlay).hexdigest()),
            (
                156_166,
                "a40010dea68b80dc378322e312c0e7685e3025b899465571b77b6b3eb48e5909",
            ),
        )
        scheduler_overlay = lz4_overlay[:-lz4_tail_size]
        self.assertEqual(
            (len(scheduler_overlay), hashlib.sha256(scheduler_overlay).hexdigest()),
            (
                154_408,
                "d3accbdc0e6de2143d8fa7d6d16f0705cefd8e2a5c3f607a30c98961017a1b2f",
            ),
        )
        historical_overlay = scheduler_overlay[:-scheduler_tail_size]
        self.assertEqual(len(historical_overlay) - 115_318, 38_308)
        self.assertEqual(
            hashlib.sha256(historical_overlay[:115_318]).hexdigest(),
            "8a2f88b627148f820d5cc2d6ed8e4336"
            "e86cdbecb957a4c81e6d633dc4268552",
        )

        for offset, size in (
            (38_198, 180),
            (119_964, 218),
            (21_908, 1_026),
            (68_974, 132),
            (76_448, 24),
            (41_180, 20),
            (41_200, 24),
            (41_224, 44),
            (40_036, 354),
            (39_522, 200),
            (118_252, 306),
            (118_892, 338),
            (119_696, 246),
            (120_982, 38),
            (120_896, 22),
            (120_198, 128),
        ):
            restored[offset:offset + size] = official[offset:offset + size]
        # BQ27427 fuel-gauge 32-redirect cluster admitted after the
        # historical extent below; restore its stock spans before trimming.
        for offset, size in (
            (1_061_162, 86),
            (1_061_248, 86),
            (1_061_334, 90),
            (1_061_424, 88),
            (1_061_512, 112),
            (1_061_624, 10),
            (1_061_634, 10),
            (1_061_644, 10),
            (1_061_654, 10),
            (1_061_664, 92),
            (1_061_756, 92),
            (1_061_848, 10),
            (1_061_858, 10),
            (1_061_868, 10),
            (1_061_878, 10),
            (1_061_888, 10),
            (1_061_898, 10),
            (1_061_908, 100),
            (1_062_008, 202),
            (1_062_210, 126),
            (1_062_336, 336),
            (1_062_672, 458),
            (1_063_302, 88),
            (1_063_390, 88),
            (1_063_478, 28),
            (1_063_506, 312),
            (1_063_852, 334),
            (1_064_236, 382),
            (1_064_660, 354),
            (1_065_028, 176),
            (1_065_236, 10),
            (1_065_246, 198),
        ):
            restored[offset:offset + size] = official[offset:offset + size]
        for offset, replacement_hex in (
            (
                691_244,
                "b6f2ecbb00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
            ),
            (
                1_143_640,
                "48f266b800bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf",
            ),
        ):
            replacement = bytes.fromhex(replacement_hex)
            restored[offset:offset + len(replacement)] = replacement
        restored[858_984:859_162] = official[858_984:859_162]
        del restored[-(
            reset_unordered_tail_size
            + semaphore_take_tail_size
            + easylogger_tail_size
            + timeout_tail_size
            + next_closure_tail_size
            + lz4_tail_size
            + scheduler_tail_size
            + bq27427_tail_size
            + util_error_tail_size
            + task_get_info_tail_size
        ):]
        restored[118_172:118_184] = official[118_172:118_184]
        restored[120_182:120_198] = official[120_182:120_198]
        restored[120_326:120_336] = official[120_326:120_336]
        restored[121_578:121_600] = official[121_578:121_600]
        restored[121_600:121_622] = official[121_600:121_622]
        restored[120_648:120_776] = official[120_648:120_776]
        del restored[-1_713:]
        first_word = struct.unpack_from("<I", restored, 0)[0]
        struct.pack_into(
            "<I",
            restored,
            0,
            (first_word & 0xFF000000) | len(restored),
        )
        struct.pack_into(
            "<I",
            restored,
            4,
            zlib.crc32(restored[8:]) & 0xFFFFFFFF,
        )
        self.assertEqual(len(restored), 3_675_309)
        self.assertEqual(
            hashlib.sha256(restored).hexdigest(),
            "8a57e59b6b3cb08437dd9e2005060d8a5040c403ff5eef11e28087915f875e7e",
        )

    @_APPLE_ONLY
    def test_manifest_tail_package_and_rebuild_are_byte_exact(
        self,
    ) -> None:
        raw_manifest = json.loads(
            CORE_SOURCE_MANIFEST.read_text(encoding="utf-8")
        )
        self.assertEqual(
            raw_manifest["package"],
            {
                "output_name": (
                    "g2-openCFW-s200_v2.2.6.10-core-source."
                    "evenota.bin"
                ),
                "expected_size": 4_467_302,
                "expected_sha256": (
                    "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f"
                ),
                "profiles": {
                    "linux-clang": {
                        "expected_size": 4_447_070,
                        "expected_sha256": (
                            "be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25"
                        ),
                    },
                },
            },
        )
        main_override = raw_manifest["component_overrides"][
            "apollo_main"
        ]
        self.assertEqual(
            main_override["provider"],
            {
                "kind": "source_build",
                "path": (
                    "components/apollo_main/core_overlay/build/"
                    "ota_s200_firmware_ota.bin"
                ),
                "size": 3_688_808,
                "sha256": (
                    "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c"
                ),
                "profiles": {
                    "linux-clang": {
                        "size": 3_668_576,
                        "sha256": (
                            "292f55478951dc8d41a8bc5e4cc01f80ae88f9c44350d8fec89958c939a4fac5"
                        ),
                    },
                },
            },
        )
        regions = main_override["regions"]
        self.assertEqual(len(regions), 1745)
        self.assertEqual(regions[0]["file_offset"], 0)
        for earlier, later in zip(regions, regions[1:]):
            self.assertEqual(
                earlier["file_offset"] + earlier["size"],
                later["file_offset"],
                (earlier["name"], later["name"]),
            )
        self.assertEqual(
            regions[-1]["file_offset"] + regions[-1]["size"],
            3_688_808,
        )

        timeout_regions = {
            region["name"]: {
                key: region[key]
                for key in (
                    "file_offset",
                    "size",
                    "target_address",
                    "address_status",
                )
            }
            for region in regions
            if region["name"] in {
                "freertos_task_check_for_timeout_source_replacement",
                "apollo_freertos_task_check_for_timeout_source_leaf_alignment",
                "apollo_freertos_task_check_for_timeout_source_leaf",
            }
        }
        self.assertEqual(
            timeout_regions,
            {
                "freertos_task_check_for_timeout_source_replacement": {
                    "file_offset": 120_198,
                    "size": 128,
                    "target_address": 0x0045_5566,
                    "address_status": "generated_source_entry_replacement",
                },
                "apollo_freertos_task_check_for_timeout_source_leaf_alignment": {
                    "file_offset": 3_641_870,
                    "size": 2,
                    "target_address": 0x007B_11EE,
                    "address_status": "generated_alignment",
                },
                "apollo_freertos_task_check_for_timeout_source_leaf": {
                    "file_offset": 3_641_872,
                    "size": 136,
                    "target_address": 0x007B_11F0,
                    "address_status": "source_compiled",
                },
            },
        )

        split_names = {
            "freertos_task_priority_set_source_replacement",
            "opaque_between_freertos_task_priority_set_and_task_suspend_all",
            "freertos_task_suspend_all_source_replacement",
            "opaque_between_freertos_task_suspend_all_and_resume_all",
            "freertos_task_resume_all_source_replacement",
            "freertos_task_get_tick_count_source_replacement",
            "freertos_task_get_tick_count_from_isr_source_replacement",
            "freertos_task_count_source_replacement",
        }
        split = [region for region in regions if region["name"] in split_names]
        self.assertEqual(
            [
                (
                    region["name"],
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                    region["address_status"],
                )
                for region in split
            ],
            [
                (
                    "freertos_task_priority_set_source_replacement",
                    117_810,
                    218,
                    0x00454C12,
                    "generated_source_entry_replacement",
                ),
                (
                    "opaque_between_freertos_task_priority_set_and_"
                    "task_suspend_all",
                    118_028,
                    144,
                    0x00454CEC,
                    "official_blob",
                ),
                (
                    "freertos_task_suspend_all_source_replacement",
                    118_172,
                    12,
                    0x00454D7C,
                    "generated_source_entry_replacement",
                ),
                (
                    "opaque_between_freertos_task_suspend_all_and_"
                    "resume_all",
                    118_184,
                    68,
                    0x00454D88,
                    "official_blob",
                ),
                (
                    "freertos_task_resume_all_source_replacement",
                    118_252,
                    306,
                    0x00454DCC,
                    "generated_source_entry_replacement",
                ),
                (
                    "freertos_task_get_tick_count_source_replacement",
                    118_558,
                    8,
                    TASK_START,
                    "generated_source_entry_replacement",
                ),
                (
                    "freertos_task_get_tick_count_from_isr_"
                    "source_replacement",
                    118_566,
                    10,
                    FROM_ISR_START,
                    "generated_source_entry_replacement",
                ),
                (
                    "freertos_task_count_source_replacement",
                    118_576,
                    6,
                    0x00454F10,
                    "generated_source_entry_replacement",
                ),
            ],
        )

        expected_tail = [
            (
                "apollo_freertos_tick_count_provider_source_leaf_"
                "alignment",
                3_638_714,
                2,
                0x007B059A,
                "generated_alignment",
                "0000",
            ),
            (
                "apollo_freertos_tick_count_provider_source_leaf",
                3_638_716,
                12,
                0x007B059C,
                "source_compiled",
                "44f63420c2f2070000687047",
            ),
            (
                "apollo_freertos_task_get_tick_count_source_leaf",
                3_638_728,
                4,
                0x007B05A8,
                "source_compiled",
                "fff7f8bf",
            ),
            (
                "apollo_freertos_task_get_tick_count_from_isr_"
                "source_leaf",
                3_638_732,
                4,
                0x007B05AC,
                "source_compiled",
                "fff7f6bf",
            ),
            (
                "apollo_freertos_task_missed_yield_source_leaf",
                3_638_736,
                14,
                0x007B05B0,
                "source_compiled",
                "44f64420c2f20700012101607047",
            ),
            (
                "apollo_freertos_task_reset_event_item_value_"
                "source_leaf_alignment",
                3_638_750,
                2,
                0x007B05BE,
                "generated_alignment",
                "0000",
            ),
            (
                "apollo_freertos_task_reset_event_item_value_"
                "source_leaf",
                3_638_752,
                26,
                0x007B05C0,
                "source_compiled",
                (
                    "44f62021c2f20701086880690a680968"
                    "c96ac1f1380191617047"
                ),
            ),
            (
                "apollo_freertos_task_increment_mutex_held_count_"
                "source_leaf_alignment",
                3_638_778,
                2,
                0x007B05DA,
                "generated_alignment",
                "0000",
            ),
            (
                "apollo_freertos_task_increment_mutex_held_count_"
                "source_leaf",
                3_638_780,
                24,
                0x007B05DC,
                "source_compiled",
                (
                    "44f62020c2f20700016819b101684a6e"
                    "01324a6600687047"
                ),
            ),
            (
                "apollo_freertos_task_suspend_all_source_leaf",
                3_638_804,
                16,
                0x007B05F4,
                "source_compiled",
                "44f65820c2f207000168013101607047",
            ),
            (
                "apollo_freertos_task_internal_set_timeout_state_"
                "source_leaf",
                3_638_820,
                18,
                0x007B0604,
                "source_compiled",
                "44f63421c2f207014a690260096841607047",
            ),
        ]
        current_component = CURRENT_COMPONENT.read_bytes()
        expected_tail_names = {item[0] for item in expected_tail}
        historical_tail = [
            region for region in regions
            if region["name"] in expected_tail_names
        ]
        self.assertEqual(
            [
                (
                    region["name"],
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                    region["address_status"],
                )
                for region in historical_tail
            ],
            [item[:5] for item in expected_tail],
        )
        for region, expected in zip(historical_tail, expected_tail):
            start = region["file_offset"]
            end = start + region["size"]
            self.assertEqual(
                current_component[start:end].hex(),
                expected[5],
            )
        self.assertEqual(
            sum(
                region["size"]
                for region in historical_tail
                if region["address_status"] == "source_compiled"
            ),
            118,
        )
        self.assertEqual(
            sum(
                region["size"]
                for region in historical_tail
                if region["address_status"] == "generated_alignment"
            ),
            6,
        )

        current_report = json.loads(
            CURRENT_OVERLAY_REPORT.read_text(encoding="utf-8")
        )
        expected_accounting = {
            "generated_patch_site_bytes": 121_494,
            "generated_wrapper_bytes": 32,
            "opaque_base_bytes": 3_401_688,
            "replaced_stock_function_bytes": 121_672,
            "source_owned_bytes": 165_594,
            "source_owned_in_place_bytes": 182,
        }
        self.assertEqual(
            {
                key: current_report["component"][key]
                for key in expected_accounting
            },
            expected_accounting,
        )
        self.assertEqual(
            sum(
                expected_accounting[key]
                for key in (
                    "generated_patch_site_bytes",
                    "generated_wrapper_bytes",
                    "opaque_base_bytes",
                    "source_owned_bytes",
                )
            ),
            3_688_808,
        )
        link = current_report["overlay"]["link"]
        self.assertEqual(
            {
                key: link[key]
                for key in (
                    "text_size",
                    "rodata_size",
                    "isolated_text_size",
                    "isolated_padding_size",
                    "relocated_text_size",
                    "relocated_rodata_size",
                    "relocated_padding_size",
                    "resolved_relocation_count",
                )
            },
            {
                "text_size": 109_592,
                "rodata_size": 3_996,
                "isolated_text_size": 140,
                "isolated_padding_size": 4,
                "relocated_text_size": 47_558,
                "relocated_rodata_size": 3_260,
                "relocated_padding_size": 358,
                "resolved_relocation_count": 906,
            },
        )
        self.assertEqual(
            sum(
                link[key]
                for key in (
                    "text_size",
                    "rodata_size",
                    "isolated_text_size",
                    "isolated_padding_size",
                    "relocated_text_size",
                    "relocated_rodata_size",
                    "relocated_padding_size",
                    "relocated_closure_padding_size",
                )
            ),
            165_412,
        )
        self.assertEqual(
            (
                len(current_report["overlay"]["functions"]),
                len(current_report["overlay"]["patched_sites"]),
            ),
            (943, 882),
        )

        current_overlay = CURRENT_OVERLAY.read_bytes()
        rebuilt_overlay = (
            ROOT / self.production["overlay"]["artifact"]
        ).read_bytes()
        rebuilt_component = (
            ROOT / self.production["component"]["artifact"]
        ).read_bytes()
        self.assertEqual(current_overlay, rebuilt_overlay)
        self.assertEqual(current_component, rebuilt_component)
        self.assertEqual(
            (
                len(current_overlay),
                hashlib.sha256(current_overlay).hexdigest(),
                len(current_component),
                hashlib.sha256(current_component).hexdigest(),
            ),
            (
                165_412,
                "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada",
                3_688_808,
                "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c",
            ),
        )

        package_report = json.loads(
            CORE_SOURCE_REPORT.read_text(encoding="utf-8")
        )
        package = CORE_SOURCE_PACKAGE.read_bytes()
        self.assertEqual(
            package_report["package"],
            {
                "artifact": (
                    "package/g2-openCFW-s200_v2.2.6.10-"
                    "core-source.evenota.bin"
                ),
                "size": 4_467_302,
                "sha256": (
                    "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f"
                ),
                "reference_sha256": (
                    "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f"
                ),
                "byte_identical_to_reference": True,
            },
        )
        self.assertEqual(
            (
                len(package),
                hashlib.sha256(package).hexdigest(),
            ),
            (
                4_467_302,
                "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f",
            ),
        )

        payloads = dict(self.package_payloads)
        payloads["apollo_main"] = rebuilt_component
        rebuilt_package, entries = self.open_cfw.assemble_evenota(
            self.package_manifest,
            payloads,
        )
        self.assertEqual(rebuilt_package, package)
        main_entry = next(
            entry
            for entry in entries
            if entry.filename == "ota/s200_firmware_ota.bin"
        )
        self.assertEqual(main_entry.payload_size, 3_688_808)
        self.assertEqual(main_entry.checksum, 0x1897DF9E)


if __name__ == "__main__":
    unittest.main()
