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
    / "apollo_main"
    / "core_overlay"
    / "runtime_cmsis_message_queue_new.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_cmsis_message_queue_new_host.c"
)
CMSIS_ROOT = ROOT / "third_party" / "cmsis-freertos"
UPSTREAM = (
    CMSIS_ROOT
    / "CMSIS-FreeRTOS"
    / "CMSIS"
    / "RTOS2"
    / "FreeRTOS"
    / "Source"
    / "cmsis_os2.c"
)
UPSTREAM_VERIFIER = CMSIS_ROOT / "verify_snapshot.py"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
PRODUCTION_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)

APPLICATION_BASE = 0x0043_8000
STOCK_START = 0x0044_9A32
STOCK_END = 0x0044_9ABE
STOCK_SHA256 = (
    "52d0abf097914cc84b2cdfe7f628dc61"
    "f9efb40bac880112062315d2b1bfba47"
)
STOCK_BYTES = bytes.fromhex(
    "f8b504000d0016000027fff7e7fa00283ad1002c38d0002d36d05ff0ff31"
    "002e1dd0b06800280cd0f068502809d33069002806d0706905fb04f2904201"
    "d301210ee0b06800280bd1f068002808d13069002805d17069002802d100210"
    "0e00021012909d100200090b368326929002000f7f792fd070007e0002905d1"
    "002229002000f7f7bffd07003800f2bd"
)
CALLERS = [
    (0x0044_4746, "05f074f9"),
    (0x0045_D1FC, "ecf719fc"),
    (0x0045_E9A0, "ebf747f8"),
    (0x0047_3A0A, "d6f712f8"),
    (0x0047_5316, "d4f78cfb"),
    (0x0047_64F4, "d3f79dfa"),
    (0x0048_E1DA, "bbf72afc"),
    (0x0048_EE36, "baf7fcfd"),
    (0x0049_1442, "b8f7f6fa"),
    (0x004A_66FA, "a3f79af9"),
    (0x004C_4D72, "84f75efe"),
    (0x004C_634C, "83f771fb"),
    (0x0051_2D72, "36f75efe"),
    (0x0053_836A, "11f762fb"),
    (0x0053_C3FA, "0df71afb"),
]
CALLER_SHA256 = (
    "7974f375f4b38120a6df7ce5416cef9f"
    "a65031d5768226b8785d2916d0f96f18"
)
OUTGOING = [
    (0x0044_9A3C, "fff7e7fa", 0x0044_900E),
    (0x0044_9AA2, "f7f792fd", 0x0044_15CA),
    (0x0044_9AB4, "f7f7bffd", 0x0044_1636),
]

SOURCE_SHA256 = (
    "8897019aa7a2beca32a88dc60808fb1f"
    "99b1538933b8ab4fbd9ed4fed38d433c"
)
UPSTREAM_SHA256 = (
    "8a0d60b56ad30c4f7957f64fa5811580"
    "17b6812ec94b832d974c773ae4f2bc36"
)
UPSTREAM_FUNCTION_SIZE = 1531
UPSTREAM_FUNCTION_SHA256 = (
    "096ed95a146b99b65c77a8a63b474b69"
    "57eec64f9764b134ceb34f8426eb18f2"
)
TARGET_FUNCTION = "open_cfw_cmsis_message_queue_new"
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
TARGET_BYTES = bytes.fromhex(
    "70b582b01446eff3058232bb0e460546fff7feff024631462846012a16d10028"
    "18bf002919d01cb3a368e268c3b1502a13d322698ab1666901fb00f5ae420cd3"
    "00260096fff7feff02b070bdeff310821ab9eff31182002ae1d0002002b070bd"
    "002afad12269002af7d16269002af4d1002202b0bde87040fff7febf"
)
TARGET_SHA256 = (
    "543fb1ef418aeadd05e2f3b3e60c3f48"
    "c0f3521dfa995a3079a86b86ccc58eee"
)
RELOCATED_SHA256 = (
    "afbba4f9f08b2df17a4350d7a7e83d99"
    "b8439283ee40c1a1604bd879dff75f04"
)
PRODUCTION_OVERLAY_SIZE = 167_426
PRODUCTION_OVERLAY_SHA256 = (
    "800245ad7f4ba1044f01888fc0141f9f3304bc531773847ba9c0c29e62245491"
)
PRODUCTION_COMPONENT_SIZE = 3_690_822
PRODUCTION_COMPONENT_SHA256 = (
    "9ed3e77e10dd911ae34e9ba17f691f6988c592723b52a9676b8d414554a21459"
)
PRODUCTION_OFFSET = 113_808
PRODUCTION_ADDRESS = 0x007A_FFB4
TARGET_RELOCATIONS = [
    (
        0x10,
        10,
        "open_cfw_freertos_task_get_scheduler_state",
    ),
    (
        0x44,
        10,
        "open_cfw_freertos_queue_generic_create_static",
    ),
    (
        0x78,
        30,
        "open_cfw_freertos_queue_generic_create",
    ),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_upstream_function(source: str) -> bytes:
    marker = "osMessageQueueId_t osMessageQueueNew ("
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1].encode()
    raise AssertionError("unterminated upstream osMessageQueueNew")


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


class RuntimeCmsisMessageQueueNewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_cmsis_message_queue_new.dylib"
            if sys.platform == "darwin"
            else "runtime_cmsis_message_queue_new.so"
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
        cls.host_compile = subprocess.run(
            host_command,
            check=False,
            capture_output=True,
            text=True,
        )
        if cls.host_compile.returncode:
            raise AssertionError(
                cls.host_compile.stderr or cls.host_compile.stdout
            )
        cls.loaded = ctypes.CDLL(str(library))

        cls.reset = cls.loaded.open_cfw_test_cmsis_message_queue_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.call = cls.loaded.open_cfw_test_cmsis_message_queue_call
        cls.call.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        cls.call.restype = ctypes.c_void_p
        for name in ("control", "storage", "dynamic"):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_cmsis_{name}_pointer",
            )
            function.argtypes = []
            function.restype = ctypes.c_void_p
            setattr(cls, f"{name}_pointer", function)

        cls.target_object = temporary / "runtime_cmsis_message_queue_new.o"
        cls.target_compile = subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if cls.target_compile.returncode:
            raise AssertionError(
                cls.target_compile.stderr or cls.target_compile.stdout
            )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.elf, cls.sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        cls.symbols = apollo_overlay.parse_elf32_symbols(
            cls.elf,
            cls.sections,
        )
        cls.sections_by_name = {
            str(section["name"]): section for section in cls.sections
        }
        text = cls.sections_by_name[f".text.{TARGET_FUNCTION}"]
        cls.target_text = cls.elf[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]

        production_output = temporary / "production"
        cls.production_report = apollo_overlay.build(
            root=ROOT,
            config_path=PRODUCTION_CONFIG,
            output_dir=production_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.production_overlay = (
            production_output / "apollo_core_overlay.bin"
        ).read_bytes()
        cls.production_component = (
            production_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def get_uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def set_uint(self, name: str, value: int) -> None:
        ctypes.c_uint.in_dll(self.loaded, name).value = value

    def set_int(self, name: str, value: int) -> None:
        ctypes.c_int.in_dll(self.loaded, name).value = value

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def test_authenticated_upstream_and_production_source(self) -> None:
        self.assertEqual(UPSTREAM.stat().st_size, 70_106)
        self.assertEqual(sha256(UPSTREAM.read_bytes()), UPSTREAM_SHA256)
        block = extract_upstream_function(UPSTREAM.read_text())
        self.assertEqual(len(block), UPSTREAM_FUNCTION_SIZE)
        self.assertEqual(sha256(block), UPSTREAM_FUNCTION_SHA256)

        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CMSIS-FreeRTOS v10.5.1", verifier.stdout)
        self.assertIn("Git blobs", verifier.stdout)

        source = SOURCE.read_text()
        self.assertEqual(sha256(source.encode()), SOURCE_SHA256)
        self.assertIn("SPDX-License-Identifier: Apache-2.0", source)
        self.assertIn(
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            source,
        )
        for marker in (
            "#define configSUPPORT_STATIC_ALLOCATION 1",
            "#define configSUPPORT_DYNAMIC_ALLOCATION 1",
            "#define configQUEUE_REGISTRY_SIZE 0",
            "sizeof(open_cfw_cmsis_static_queue) == 0x50U",
            "(attr->mq_size >= (msg_count * msg_size))",
            "#define xTaskGetSchedulerState",
            "#define xQueueGenericCreateStatic",
            "#define xQueueGenericCreate",
        ):
            self.assertIn(marker, source)

    def test_stock_body_boundaries_calls_and_reference_topology(self) -> None:
        body = self.span(STOCK_START, STOCK_END)
        self.assertEqual(body, STOCK_BYTES)
        self.assertEqual(len(body), 140)
        self.assertEqual(sha256(body), STOCK_SHA256)
        self.assertEqual(self.span(STOCK_START - 2, STOCK_START).hex(), "10bd")
        self.assertEqual(self.span(STOCK_END, STOCK_END + 2).hex(), "f8b5")

        direct_bl: list[tuple[int, str]] = []
        direct_bw: list[tuple[int, str]] = []
        external_interior: list[tuple[int, int, str]] = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, destination in (
                (True, direct_bl),
                (False, direct_bw),
            ):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target == STOCK_START and not (
                    STOCK_START <= address < STOCK_END
                ):
                    destination.append((address, encoded.hex()))
                if STOCK_START < target < STOCK_END and not (
                    STOCK_START <= address < STOCK_END
                ):
                    external_interior.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(direct_bl, CALLERS)
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(
            sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoding in direct_bl
                )
            ),
            CALLER_SHA256,
        )

        narrow: list[tuple[int, int]] = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in narrow_branch_targets(address, halfword):
                if STOCK_START <= target < STOCK_END and not (
                    STOCK_START <= address < STOCK_END
                ):
                    narrow.append((address, target))
        self.assertEqual(narrow, [])

        stored: list[tuple[int, int]] = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if STOCK_START <= (value & ~1) < STOCK_END:
                stored.append((APPLICATION_BASE + offset, value))
        self.assertEqual(stored, [])

        outgoing: list[tuple[int, str, int]] = []
        for address in range(STOCK_START, STOCK_END - 3, 2):
            encoded = self.span(address, address + 4)
            try:
                target = self.apollo_overlay.decode_thumb_branch(
                    address,
                    encoded,
                    link=True,
                )
            except self.apollo_overlay.BuildError:
                continue
            if not STOCK_START <= target < STOCK_END:
                outgoing.append((address, encoded.hex(), target))
        self.assertEqual(outgoing, OUTGOING)

    @_APPLE_ONLY
    def test_target_text_alignment_relocations_and_symbol_closure(self) -> None:
        self.assertEqual(self.target_compile.stderr, "")
        self.assertEqual(len(self.target_text), 124)
        self.assertEqual(self.target_text, TARGET_BYTES)
        self.assertEqual(sha256(self.target_text), TARGET_SHA256)

        text = self.sections_by_name[f".text.{TARGET_FUNCTION}"]
        self.assertEqual(int(text["alignment"]), 4)
        self.assertEqual(int(text["flags"]) & 7, 6)

        symbols_by_name = {
            str(symbol["name"]): symbol for symbol in self.symbols
        }
        function = symbols_by_name[TARGET_FUNCTION]
        self.assertEqual(int(function["binding"]), 1)
        self.assertEqual(int(function["type"]), 2)
        self.assertEqual(int(function["section_index"]), int(text["index"]))
        self.assertEqual(int(function["value"]) & ~1, 0)
        self.assertEqual(int(function["size"]), 124)

        relocation_section = self.sections_by_name[
            f".rel.text.{TARGET_FUNCTION}"
        ]
        relocations = []
        for entry in range(
            int(relocation_section["offset"]),
            int(relocation_section["offset"]) +
            int(relocation_section["size"]),
            8,
        ):
            offset, information = struct.unpack_from(
                "<II",
                self.elf,
                entry,
            )
            relocations.append(
                (
                    offset,
                    information & 0xFF,
                    str(self.symbols[information >> 8]["name"]),
                )
            )
        self.assertEqual(relocations, TARGET_RELOCATIONS)
        self.assertEqual(
            {
                name
                for _offset, _kind, name in relocations
                if int(symbols_by_name[name]["section_index"]) == 0
            },
            {item[2] for item in TARGET_RELOCATIONS},
        )

    @_APPLE_ONLY
    def test_eventual_extraction_retains_no_unrelated_allocatable_data(
        self,
    ) -> None:
        allocatable = [
            {
                "name": str(section["name"]),
                "size": int(section["size"]),
                "flags": int(section["flags"]),
            }
            for section in self.sections
            if int(section["flags"]) & 2 and int(section["size"])
        ]
        self.assertEqual(
            allocatable,
            [
                {
                    "name": f".text.{TARGET_FUNCTION}",
                    "size": 124,
                    "flags": 6,
                },
                {
                    "name": f".ARM.exidx.text.{TARGET_FUNCTION}",
                    "size": 8,
                    "flags": 130,
                },
            ],
        )

        runtime_address = 0x0070_0000
        relocation_config = [
            {
                "offset": offset,
                "type": (
                    "R_ARM_THM_CALL" if kind == 10
                    else "R_ARM_THM_JUMP24"
                ),
                "symbol": symbol,
                "target_address": target,
            }
            for (offset, kind, symbol), target in zip(
                TARGET_RELOCATIONS,
                (0x0070_1000, 0x0070_2000, 0x0070_3000),
            )
        ]
        extracted, report = (
            self.apollo_overlay.extract_in_place_function_section(
                self.target_object,
                TARGET_FUNCTION,
                runtime_address=runtime_address,
                relocation_configs=relocation_config,
            )
        )
        self.assertEqual(len(extracted), 124)
        self.assertEqual(report["unrelocated_sha256"], TARGET_SHA256)
        self.assertEqual(report["relocation_count"], 3)
        self.assertEqual(report["discarded_alloc_section_count"], 1)
        self.assertEqual(report["discarded_alloc_section_bytes"], 8)
        self.assertEqual(
            report["discarded_alloc_sections"],
            [
                {
                    "name": f".ARM.exidx.text.{TARGET_FUNCTION}",
                    "size": 8,
                    "flags": 130,
                }
            ],
        )

    @_APPLE_ONLY
    def test_production_config_report_redirect_and_artifacts_are_exact(
        self,
    ) -> None:
        config = json.loads(PRODUCTION_CONFIG.read_text(encoding="utf-8"))
        leaves = [
            leaf
            for leaf in config["relocated_leaves"]
            if leaf["function"] == TARGET_FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertEqual(
            leaf["source"],
            {
                "path": (
                    "components/apollo_main/core_overlay/"
                    "runtime_cmsis_message_queue_new.c"
                ),
                "size": SOURCE.stat().st_size,
                "sha256": SOURCE_SHA256,
                "license": "Apache-2.0",
                "origin": (
                    "bounded freestanding port of the exact authenticated "
                    "CMSIS-FreeRTOS v10.5.1 osMessageQueueNew algorithm "
                    "using the recovered G2 allocation and IRQ policy"
                ),
                "upstream": (
                    "https://github.com/ARM-software/CMSIS-FreeRTOS/blob/"
                    "d213f261b5be6bb29a7cce8b84071706b72f4d53/"
                    "CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c"
                ),
                "upstream_commit": (
                    "d213f261b5be6bb29a7cce8b84071706b72f4d53"
                ),
                "evidence": (
                    "docs/research/"
                    "upstream-library-source-reuse-audit.md"
                ),
            },
        )
        self.assertEqual(
            leaf["expected"],
            {
                "size": len(TARGET_BYTES),
                "sha256": RELOCATED_SHA256,
                "alignment": 4,
                "offset": PRODUCTION_OFFSET,
                "unrelocated_sha256": TARGET_SHA256,
            },
        )
        self.assertEqual(
            leaf["relocations"],
            [
                {
                    "offset": offset,
                    "type": (
                        "R_ARM_THM_CALL"
                        if kind == 10
                        else "R_ARM_THM_JUMP24"
                    ),
                    "symbol": symbol,
                    "target_function": symbol,
                }
                for offset, kind, symbol in TARGET_RELOCATIONS
            ],
        )
        patches = [
            patch
            for patch in config["patch_sites"]
            if patch["name"] == "replace_cmsis_message_queue_new"
        ]
        self.assertEqual(
            patches,
            [
                {
                    "name": "replace_cmsis_message_queue_new",
                    "runtime_address": STOCK_START,
                    "expected_size": len(STOCK_BYTES),
                    "expected_sha256": STOCK_SHA256,
                    "branch": "b_w",
                    "target_function": TARGET_FUNCTION,
                }
            ],
        )
        self.assertEqual(
            config["expected"],
            {
                "overlay_size": PRODUCTION_OVERLAY_SIZE,
                "overlay_sha256": PRODUCTION_OVERLAY_SHA256,
                "component_size": PRODUCTION_COMPONENT_SIZE,
                "component_sha256": PRODUCTION_COMPONENT_SHA256,
            },
        )

        report = self.production_report
        self.assertEqual(
            (
                len(self.production_overlay),
                sha256(self.production_overlay),
            ),
            (PRODUCTION_OVERLAY_SIZE, PRODUCTION_OVERLAY_SHA256),
        )
        self.assertEqual(
            (
                len(self.production_component),
                sha256(self.production_component),
            ),
            (PRODUCTION_COMPONENT_SIZE, PRODUCTION_COMPONENT_SHA256),
        )
        leaf_reports = [
            item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] == TARGET_FUNCTION
        ]
        self.assertEqual(len(leaf_reports), 1)
        leaf_report = leaf_reports[0]
        self.assertEqual(
            leaf_report["placement"],
            {
                "offset": PRODUCTION_OFFSET,
                "size": len(TARGET_BYTES),
                "alignment": 4,
                "padding_before": 2,
                "runtime_address": PRODUCTION_ADDRESS,
                "runtime_address_hex": "0x007AFFB4",
            },
        )
        self.assertEqual(
            (
                leaf_report["extraction"]["sha256"],
                leaf_report["extraction"]["unrelocated_sha256"],
                leaf_report["extraction"]["relocation_count"],
            ),
            (RELOCATED_SHA256, TARGET_SHA256, 3),
        )
        relocated_body = self.production_overlay[
            PRODUCTION_OFFSET:PRODUCTION_OFFSET + len(TARGET_BYTES)
        ]
        self.assertEqual(sha256(relocated_body), RELOCATED_SHA256)
        self.assertNotEqual(relocated_body, TARGET_BYTES)
        expected_targets = (
            (
                "open_cfw_freertos_task_get_scheduler_state",
                0x007A_EAAC,
                True,
            ),
            (
                "open_cfw_freertos_queue_generic_create_static",
                0x007A_EB14,
                True,
            ),
            (
                "open_cfw_freertos_queue_generic_create",
                0x007A_EBC0,
                False,
            ),
        )
        for relocation, (symbol, target, link) in zip(
            leaf_report["extraction"]["relocations"],
            expected_targets,
        ):
            self.assertEqual(relocation["symbol"], symbol)
            self.assertEqual(relocation["target_function"], symbol)
            self.assertEqual(relocation["target_address"], target)
            offset = int(relocation["offset"])
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    PRODUCTION_ADDRESS + offset,
                    relocated_body[offset:offset + 4],
                    link=link,
                ),
                target,
            )
        patch_reports = [
            patch
            for patch in report["overlay"]["patched_sites"]
            if patch["name"] == "replace_cmsis_message_queue_new"
        ]
        self.assertEqual(len(patch_reports), 1)
        patch = patch_reports[0]
        self.assertEqual(
            (
                patch["runtime_address"],
                patch["target_address"],
                patch["payload_offset"],
                patch["expected_size"],
                patch["expected_sha256"],
            ),
            (
                STOCK_START,
                PRODUCTION_ADDRESS,
                STOCK_START - APPLICATION_BASE + 32,
                len(STOCK_BYTES),
                STOCK_SHA256,
            ),
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                STOCK_START,
                replacement[:4],
                link=False,
            ),
            PRODUCTION_ADDRESS,
        )
        self.assertEqual(
            replacement[4:],
            b"\x00\xbf" * ((len(STOCK_BYTES) - 4) // 2),
        )
        patch_offset = int(patch["payload_offset"])
        self.assertEqual(
            self.production_component[
                patch_offset:patch_offset + len(replacement)
            ],
            replacement,
        )
        self.assertEqual(
            {
                key: report["component"][key]
                for key in (
                    "generated_patch_site_bytes",
                    "generated_wrapper_bytes",
                    "opaque_base_bytes",
                    "replaced_stock_function_bytes",
                    "source_owned_bytes",
                    "source_owned_in_place_bytes",
                )
            },
            {
                "generated_patch_site_bytes": 121_634,
                "generated_wrapper_bytes": 32,
                "opaque_base_bytes": 3_401_548,
                "replaced_stock_function_bytes": 121_812,
                "source_owned_bytes": 165_622,
                "source_owned_in_place_bytes": 182,
            },
        )
        self.assertEqual(len(report["overlay"]["functions"]), 945)
        self.assertEqual(len(report["overlay"]["patched_sites"]), 884)

        historical_overlay = self.production_overlay[:113_970]
        self.assertEqual(
            (
                len(historical_overlay),
                sha256(historical_overlay),
            ),
            (
                113_970,
                "dba3b91264a8437ea5f44d872b41a712"
                "3d6dd70e7816bdab7d6bff82d2c93ca9",
            ),
        )
        official = OFFICIAL.read_bytes()
        historical_component = bytearray(self.production_component)
        historical_component[71_484:71_638] = official[71_484:71_638]
        # Undo the later watchdog source milestone for this older checkpoint.
        historical_component[1_012_480:1_012_544] = official[
            1_012_480:1_012_544
        ]
        historical_component[1_012_544:1_012_620] = official[
            1_012_544:1_012_620
        ]
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
            (123_184, 256),
            (123_440, 112),
            (123_552, 90),
            (123_642, 94),
            (40_642, 34),
            (71_866, 180),
            (22_940, 106),
            (23_056, 26),
            (23_082, 26),
            (79_496, 162),
            (118_172, 12),
            (118_252, 306),
            (118_558, 8),
            (118_566, 10),
            (118_892, 338),
            (39_522, 200),
            (119_696, 246),
            (120_182, 16),
            (120_198, 128),
            (120_326, 10),
            # Scheduler-start closure admitted after this historical root.
            (41_474, 46),
            (118_028, 144),
            (119_252, 206),
            (120_896, 22),
            (120_982, 38),
            (121_578, 22),
            (121_600, 22),
            # Charger-common eleven-body production cluster.
            (479_132, 240),
            (479_372, 94),
            (479_466, 464),
            (479_930, 450),
            (480_380, 226),
            (480_606, 276),
            (480_882, 372),
            (481_276, 142),
            (481_440, 122),
            (481_562, 6),
            (481_568, 8),
            (858_984, 178),
        ):
            historical_component[offset:offset + size] = official[
                offset:offset + size
            ]
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
            historical_component[offset:offset + len(replacement)] = (
                replacement
            )
        del historical_component[3_637_366:]
        first_word = struct.unpack_from("<I", historical_component, 0)[0]
        struct.pack_into(
            "<I",
            historical_component,
            0,
            (first_word & 0xFF000000) | len(historical_component),
        )
        struct.pack_into(
            "<I",
            historical_component,
            4,
            zlib.crc32(historical_component[8:]) & 0xFFFFFFFF,
        )
        self.assertEqual(
            (
                len(historical_component),
                sha256(bytes(historical_component)),
            ),
            (
                3_637_366,
                "340120823caa5d95dc9c75199edb8f9915849d8ccc3ffe58e5474bc2d3324cd6",
            ),
        )

    def test_host_layout_and_null_attribute_dynamic_path(self) -> None:
        self.assertEqual(self.host_compile.stderr, "")
        size = self.loaded.open_cfw_test_cmsis_static_queue_size
        size.argtypes = []
        size.restype = ctypes.c_uint
        self.assertEqual(size(), 0x50)

        self.reset()
        result = self.call(7, 3, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(result, self.dynamic_pointer())
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_dynamic_calls"), 1)
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_dynamic_count"), 7)
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_dynamic_size"), 3)
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_dynamic_type"), 0)
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_static_calls"), 0)

    def test_irq_and_scheduler_policy_matrix(self) -> None:
        cases = [
            # ipsr, scheduler, primask, basepri, allow, scheduler reads,
            # primask reads, basepri reads
            (1, 1, 0, 0, False, 0, 0, 0),
            (3, 2, 1, 1, False, 0, 0, 0),
            (0, 1, 1, 1, True, 1, 0, 0),
            (0, 2, 1, 0, False, 1, 1, 0),
            (0, 2, 0, 1, False, 1, 1, 1),
            (0, 2, 0, 0, True, 1, 1, 1),
            (0, 0, 0, 0, True, 1, 1, 1),
            (0, 0, 0, 7, False, 1, 1, 1),
        ]
        for (
            ipsr,
            scheduler,
            primask,
            basepri,
            allow,
            scheduler_reads,
            primask_reads,
            basepri_reads,
        ) in cases:
            with self.subTest(
                ipsr=ipsr,
                scheduler=scheduler,
                primask=primask,
                basepri=basepri,
            ):
                self.reset()
                self.set_uint("open_cfw_test_cmsis_ipsr", ipsr)
                self.set_int(
                    "open_cfw_test_cmsis_scheduler_state",
                    scheduler,
                )
                self.set_uint("open_cfw_test_cmsis_primask", primask)
                self.set_uint("open_cfw_test_cmsis_basepri", basepri)
                result = self.call(1, 1, 0, 0, 0, 0, 0, 0, 0)
                self.assertEqual(result, self.dynamic_pointer() if allow else None)
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_ipsr_reads"),
                    1,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_scheduler_calls"),
                    scheduler_reads,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_primask_reads"),
                    primask_reads,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_basepri_reads"),
                    basepri_reads,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_dynamic_calls"),
                    1 if allow else 0,
                )

    def test_invalid_dimensions_and_creator_failures_return_null(self) -> None:
        for count, size in ((0, 1), (1, 0), (0, 0)):
            with self.subTest(count=count, size=size):
                self.reset()
                self.assertIsNone(
                    self.call(count, size, 0, 0, 0, 0, 0, 0, 0)
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_ipsr_reads"),
                    1,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_scheduler_calls"),
                    1,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_dynamic_calls"),
                    0,
                )

        self.reset()
        self.set_uint("open_cfw_test_cmsis_dynamic_success", 0)
        self.assertIsNone(self.call(1, 1, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_dynamic_calls"), 1)

        self.reset()
        self.set_uint("open_cfw_test_cmsis_static_success", 0)
        self.assertIsNone(self.call(1, 1, 1, 1, 80, 1, 1, 0, 0))
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_static_calls"), 1)

    def test_exhaustive_attribute_validation_and_static_forwarding(self) -> None:
        for provide_cb in (0, 1):
            for cb_size in (0, 79, 80, 81):
                for provide_mq in (0, 1):
                    for mq_size in (0, 11, 12, 13):
                        with self.subTest(
                            provide_cb=provide_cb,
                            cb_size=cb_size,
                            provide_mq=provide_mq,
                            mq_size=mq_size,
                        ):
                            self.reset()
                            result = self.call(
                                3,
                                4,
                                1,
                                provide_cb,
                                cb_size,
                                provide_mq,
                                mq_size,
                                0xFFFF_FFFF,
                                1,
                            )
                            static = (
                                provide_cb == 1
                                and cb_size >= 80
                                and provide_mq == 1
                                and mq_size >= 12
                            )
                            dynamic = (
                                provide_cb == 0
                                and cb_size == 0
                                and provide_mq == 0
                                and mq_size == 0
                            )
                            if static:
                                self.assertEqual(result, self.control_pointer())
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_static_calls"
                                    ),
                                    1,
                                )
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_static_count"
                                    ),
                                    3,
                                )
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_static_size"
                                    ),
                                    4,
                                )
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_static_type"
                                    ),
                                    0,
                                )
                                static_storage = ctypes.c_void_p.in_dll(
                                    self.loaded,
                                    "open_cfw_test_cmsis_static_storage",
                                ).value
                                static_control = ctypes.c_void_p.in_dll(
                                    self.loaded,
                                    "open_cfw_test_cmsis_static_control",
                                ).value
                                self.assertEqual(
                                    static_storage,
                                    self.storage_pointer(),
                                )
                                self.assertEqual(
                                    static_control,
                                    self.control_pointer(),
                                )
                            elif dynamic:
                                self.assertEqual(result, self.dynamic_pointer())
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_dynamic_calls"
                                    ),
                                    1,
                                )
                            else:
                                self.assertIsNone(result)
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_static_calls"
                                    ),
                                    0,
                                )
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_dynamic_calls"
                                    ),
                                    0,
                                )

    def test_unsigned_multiplication_wrap_and_ignored_attributes(self) -> None:
        self.reset()
        result = self.call(
            0x8000_0000,
            2,
            1,
            1,
            80,
            1,
            0,
            0xA5A5_5A5A,
            1,
        )
        self.assertEqual(result, self.control_pointer())
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_static_calls"), 1)
        self.assertEqual(
            self.get_uint("open_cfw_test_cmsis_static_count"),
            0x8000_0000,
        )
        self.assertEqual(self.get_uint("open_cfw_test_cmsis_static_size"), 2)


if __name__ == "__main__":
    unittest.main()
