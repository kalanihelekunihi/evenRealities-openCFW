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
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_cmsis_mutex_new.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_cmsis_mutex_new_host.c"
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
UPSTREAM_HEADER = (
    CMSIS_ROOT
    / "CMSIS_5"
    / "CMSIS"
    / "RTOS2"
    / "Include"
    / "cmsis_os2.h"
)
UPSTREAM_VERIFIER = CMSIS_ROOT / "verify_snapshot.py"
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
CURRENT_BUILD_REPORT = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "build"
    / "build-report.json"
)
CURRENT_OVERLAY = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "build"
    / "apollo_core_overlay.bin"
)
CURRENT_COMPONENT = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "build"
    / "ota_s200_firmware_ota.bin"
)
CURRENT_MANIFEST = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)
CURRENT_PACKAGE = (
    ROOT
    / "build"
    / "source"
    / "package"
    / "g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
)
CURRENT_FLASH_PLAN = ROOT / "build" / "source" / "flash-plan.json"

APPLICATION_BASE = 0x0043_8000
STOCK_START = 0x0044_971C
STOCK_END = 0x0044_97B6
STOCK_SHA256 = (
    "09f88d8a6a64730936a52aa0c2f90d9"
    "bcb0152f6e2439919f6409110148999ec"
)
STOCK_BYTES = bytes.fromhex(
    "70b505000026fff774fc002843d1002d01d0686800e00020c10701d5012400e0"
    "0024000737d45ff0ff31002d0fd0a868002804d0e868502801d3012108e0a868"
    "002805d1e868002802d1002100e0002101290dd1002c05d0a9680420f7f7baff"
    "060012e0a9680120f7f7b4ff06000ce000290ad1002c04d00420f7f79eff0600"
    "03e00120f7f799ff0600002e03d0002c01d056f00106300070bd"
)
CALLERS = [
    (0x0044_47E6, "04f099ff"),
    (0x0044_AA38, "fef770fe"),
    (0x0045_BA56, "edf761fe"),
    (0x0045_C074, "edf752fb"),
    (0x0046_0186, "e9f7c9fa"),
    (0x0046_802C, "e1f776fb"),
    (0x0046_F556, "daf7e1f8"),
    (0x0047_4DA2, "d4f7bbfc"),
    (0x0047_4DAC, "d4f7b6fc"),
    (0x0047_65B8, "d3f7b0f8"),
    (0x0049_13D8, "b8f7a0f9"),
    (0x0049_72D0, "b2f724fa"),
    (0x0049_C0A8, "adf738fb"),
    (0x004A_CFC6, "9cf7a9fb"),
    (0x004B_897E, "90f7cdfe"),
    (0x004D_9B42, "6ff7ebfd"),
    (0x004E_1F8A, "67f7c7fb"),
    (0x004F_FA7C, "49f74efe"),
    (0x004F_FBE4, "49f79afd"),
    (0x0050_42E0, "45f71cfa"),
    (0x0054_1094, "08f742fb"),
    (0x0054_17DE, "07f79dff"),
    (0x0055_2B72, "f6f6d3fd"),
    (0x0058_4BEC, "c4f696fd"),
    (0x0058_5CB2, "c3f633fd"),
    (0x0058_99B4, "bff6b2fe"),
    (0x0058_B224, "bef67afa"),
    (0x0059_EA74, "aaf652fe"),
    (0x005B_0130, "99f6f4fa"),
    (0x005E_4336, "65f6f1f9"),
]
CALLER_SHA256 = (
    "14d18197e409351bfa6ded1310c61c1f"
    "27246ebd93ecf86452d19ac0bdadbfd0"
)
OUTGOING = [
    (0x0044_9722, "fff774fc", 0x0044_900E),
    (0x0044_9778, "f7f7baff", 0x0044_16F0),
    (0x0044_9784, "f7f7b4ff", 0x0044_16F0),
    (0x0044_9796, "f7f79eff", 0x0044_16D6),
    (0x0044_97A0, "f7f799ff", 0x0044_16D6),
]

SOURCE_SIZE = 9_798
SOURCE_SHA256 = (
    "28081734a384c089635681014ed028414"
    "b75d375c22f0a52a64f53e22842cf2d"
)
UPSTREAM_SHA256 = (
    "8a0d60b56ad30c4f7957f64fa5811580"
    "17b6812ec94b832d974c773ae4f2bc36"
)
UPSTREAM_FUNCTION_SIZE = 2_169
UPSTREAM_FUNCTION_SHA256 = (
    "c928d16d21e4c016836b54f3a3780609"
    "c567e6484adcb297bc1b9f733ed47b15"
)

TARGET_FUNCTION = "open_cfw_cmsis_mutex_new"
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
    "10b5eff3058109b1002010bd0446fff7feff01280fd1dcb160680107f4d4a168"
    "e26889b1502aefd3c00716d10120bde81040fff7febfeff310800028e4d1eff3"
    "11800028e0d1e6e7002addd1c00708d10120bde81040fff7febf0420fff7feff"
    "02e00420fff7feff00281cbf40f0010010bdc9e7"
)
TARGET_SHA256 = (
    "59e1d787a4beaa36b01d932672e438933"
    "31fc5d22a46e2371cc111ec4dacb192"
)
TARGET_RELOCATIONS = [
    (
        0x0E,
        10,
        "open_cfw_freertos_task_get_scheduler_state",
    ),
    (
        0x32,
        30,
        "open_cfw_freertos_queue_create_mutex_static",
    ),
    (
        0x56,
        30,
        "open_cfw_freertos_queue_create_mutex",
    ),
    (
        0x5C,
        10,
        "open_cfw_freertos_queue_create_mutex_static",
    ),
    (
        0x64,
        10,
        "open_cfw_freertos_queue_create_mutex",
    ),
]
DEPENDENCY_ADDRESSES = {
    "open_cfw_freertos_task_get_scheduler_state": 0x007A_EAAC,
    "open_cfw_freertos_queue_create_mutex": 0x007A_E100,
    "open_cfw_freertos_queue_create_mutex_static": 0x007A_EC6C,
}
PRODUCTION_OFFSET = 113_972
PRODUCTION_RUNTIME_ADDRESS = 0x007B_0058
PRODUCTION_FINAL_SHA256 = (
    "b3d601be84edaa82345cd814f173010b"
    "39e1e0772d76f5763881fe5e845fe3c4"
)
PRODUCTION_OVERLAY_SHA256 = (
    "3d5c9fe87fd46cbc40bb5670653f45d3"
            "d61f9d777168aa47b70fb10712698ab4"
)
PRODUCTION_COMPONENT_SHA256 = (
    "5cef32ba7350e7f6476336fa6a087010"
            "e6143e3e692205215c271430aa110d22"
)
PRODUCTION_PACKAGE_SHA256 = (
    "e6472064c2536c055fb9a47efe49c9d9"
            "b553ce15ed1bc308115730454e3b94bc"
)
PRODUCTION_FLASH_PLAN_SHA256 = (
    "97230c89e27b9fea1db1d0cc9c2ca6bed"
    "5449ece6d35ea98cf101d7a219b1d9e"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_upstream_function(source: str) -> bytes:
    marker = "osMutexId_t osMutexNew ("
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
    raise AssertionError("unterminated upstream osMutexNew")


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


def expected_route(
    provide_attr: bool,
    attr_bits: int,
    provide_cb: bool,
    cb_size: int,
) -> tuple[str, int, bool]:
    if not provide_attr:
        return ("dynamic", 1, False)
    if attr_bits & 0x8:
        return ("none", 0, False)
    recursive = bool(attr_bits & 0x1)
    queue_type = 4 if recursive else 1
    if provide_cb and cb_size >= 80:
        return ("static", queue_type, recursive)
    if not provide_cb and cb_size == 0:
        return ("dynamic", queue_type, recursive)
    return ("none", queue_type, recursive)


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeCmsisMutexNewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = OFFICIAL.read_bytes()
        cls.application = package[32:]
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_cmsis_mutex_new.dylib"
            if sys.platform == "darwin"
            else "runtime_cmsis_mutex_new.so"
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
        cls.reset = cls.loaded.open_cfw_test_cmsis_mutex_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.call = cls.loaded.open_cfw_test_cmsis_mutex_call
        cls.call.argtypes = [
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        cls.call.restype = ctypes.c_size_t
        for name in ("control", "dynamic"):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_cmsis_mutex_{name}_pointer",
            )
            function.argtypes = []
            function.restype = ctypes.c_size_t
            setattr(cls, f"{name}_pointer", function)

        cls.target_object = temporary / "runtime_cmsis_mutex_new.o"
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

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
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

        current_output = temporary / "current-overlay"
        cls.current_report = apollo_overlay.build(
            root=ROOT,
            config_path=CURRENT_CONFIG,
            output_dir=current_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.current_overlay = (
            current_output / "apollo_core_overlay.bin"
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

    def test_authenticated_upstream_and_bounded_source_are_exact(self) -> None:
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

        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
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
            "#define configUSE_RECURSIVE_MUTEXES 1",
            "#define configQUEUE_REGISTRY_SIZE 0",
            "sizeof(open_cfw_cmsis_static_semaphore) == 0x50U",
            "sizeof(open_cfw_cmsis_mutex_attr) == 0x10U",
            "#define osMutexRecursive",
            "#define osMutexPrioInherit",
            "#define osMutexRobust",
            "#define xTaskGetSchedulerState",
            "#define xQueueCreateMutexStatic",
            "#define xQueueCreateMutex",
        ):
            self.assertIn(marker, source)

        header = UPSTREAM_HEADER.read_text()
        for marker in (
            "#define osMutexRecursive      0x00000001U",
            "#define osMutexPrioInherit    0x00000002U",
            "#define osMutexRobust         0x00000008U",
            "} osMutexAttr_t;",
        ):
            self.assertIn(marker, header)

    def test_stock_body_boundaries_calls_and_reference_topology(self) -> None:
        body = self.span(STOCK_START, STOCK_END)
        self.assertEqual(body, STOCK_BYTES)
        self.assertEqual(len(body), 154)
        self.assertEqual(sha256(body), STOCK_SHA256)
        self.assertEqual(
            self.span(STOCK_START - 8, STOCK_START).hex(),
            "01e07ff00200f2bd",
        )
        self.assertEqual(
            self.span(STOCK_END, STOCK_END + 8).hex(),
            "f8b506000c007508",
        )

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
        self.assertEqual(self.target_text, TARGET_BYTES)
        self.assertEqual(len(self.target_text), 116)
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
        self.assertEqual(int(function["size"]), 116)

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
            set(DEPENDENCY_ADDRESSES),
        )

    @_APPLE_ONLY
    def test_extraction_discards_only_unreached_ehabi_metadata(self) -> None:
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
                    "size": 116,
                    "flags": 6,
                },
                {
                    "name": f".ARM.exidx.text.{TARGET_FUNCTION}",
                    "size": 8,
                    "flags": 130,
                },
            ],
        )

        runtime_address = (
            int(self.current_report["overlay"]["overlay_runtime_address"])
            + len(self.current_overlay)
        )
        runtime_address = (runtime_address + 3) & ~3
        relocation_config = [
            {
                "offset": offset,
                "type": (
                    "R_ARM_THM_CALL"
                    if kind == 10
                    else "R_ARM_THM_JUMP24"
                ),
                "symbol": symbol,
                "target_address": DEPENDENCY_ADDRESSES[symbol],
            }
            for offset, kind, symbol in TARGET_RELOCATIONS
        ]
        extracted, report = (
            self.apollo_overlay.extract_in_place_function_section(
                self.target_object,
                TARGET_FUNCTION,
                runtime_address=runtime_address,
                relocation_configs=relocation_config,
            )
        )
        self.assertEqual(len(extracted), 116)
        self.assertEqual(report["unrelocated_sha256"], TARGET_SHA256)
        self.assertEqual(report["relocation_count"], 5)
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
        for relocation in report["relocations"]:
            offset = int(relocation["offset"])
            link = relocation["type"] == "R_ARM_THM_CALL"
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    runtime_address + offset,
                    extracted[offset:offset + 4],
                    link=link,
                ),
                DEPENDENCY_ADDRESSES[relocation["symbol"]],
            )

        replacement = (
            self.apollo_overlay.encode_thumb_branch(
                STOCK_START,
                runtime_address,
                link=False,
            )
            + b"\x00\xbf" * ((len(STOCK_BYTES) - 4) // 2)
        )
        self.assertEqual(len(replacement), len(STOCK_BYTES))
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                STOCK_START,
                replacement[:4],
                link=False,
            ),
            runtime_address,
        )

    @_APPLE_ONLY
    def test_production_config_report_redirect_and_artifacts_are_exact(
        self,
    ) -> None:
        config = json.loads(CURRENT_CONFIG.read_text())
        leaves = [
            item
            for item in config["relocated_leaves"]
            if item["function"] == TARGET_FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertEqual(leaf["function"], TARGET_FUNCTION)
        self.assertEqual(
            leaf["source"],
            {
                "path": (
                    "components/apollo_main/core_overlay/"
                    "runtime_cmsis_mutex_new.c"
                ),
                "size": SOURCE_SIZE,
                "sha256": SOURCE_SHA256,
                "license": "Apache-2.0",
                "origin": (
                    "bounded freestanding port of the exact authenticated "
                    "CMSIS-FreeRTOS v10.5.1 osMutexNew algorithm using the "
                    "recovered G2 allocation, recursive-handle, and IRQ "
                    "policies"
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
                    "docs/research/upstream-library-source-reuse-audit.md"
                ),
            },
        )
        self.assertEqual(
            leaf["expected"],
            {
                "size": 116,
                "sha256": PRODUCTION_FINAL_SHA256,
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
        self.assertEqual(
            config["functions"].count(TARGET_FUNCTION),
            1,
        )
        config_patches = [
            item
            for item in config["patch_sites"]
            if item["name"] == "replace_cmsis_mutex_new"
        ]
        self.assertEqual(len(config_patches), 1)
        self.assertEqual(
            config_patches[0],
            {
                "name": "replace_cmsis_mutex_new",
                "runtime_address": STOCK_START,
                "expected_size": len(STOCK_BYTES),
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": TARGET_FUNCTION,
            },
        )
        self.assertEqual(
            config["expected"],
            {
                "overlay_size": 142_578,
                "overlay_sha256": PRODUCTION_OVERLAY_SHA256,
                "component_size": 3_665_974,
                "component_sha256": PRODUCTION_COMPONENT_SHA256,
            },
        )

        report = json.loads(CURRENT_BUILD_REPORT.read_text())
        self.assertEqual(
            report["overlay"]["functions"][TARGET_FUNCTION],
            {"offset": PRODUCTION_OFFSET, "size": 116},
        )
        productions = [
            item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] == TARGET_FUNCTION
        ]
        self.assertEqual(len(productions), 1)
        production = productions[0]
        self.assertEqual(
            production["placement"],
            {
                "offset": PRODUCTION_OFFSET,
                "size": 116,
                "alignment": 4,
                "padding_before": 2,
                "runtime_address": PRODUCTION_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007B0058",
            },
        )
        self.assertEqual(
            production["extraction"]["sha256"],
            PRODUCTION_FINAL_SHA256,
        )
        self.assertEqual(
            production["extraction"]["unrelocated_sha256"],
            TARGET_SHA256,
        )
        self.assertEqual(
            [
                (
                    relocation["offset"],
                    relocation["type"],
                    relocation["symbol"],
                    relocation["target_address"],
                )
                for relocation in production["extraction"]["relocations"]
            ],
            [
                (
                    offset,
                    (
                        "R_ARM_THM_CALL"
                        if kind == 10
                        else "R_ARM_THM_JUMP24"
                    ),
                    symbol,
                    DEPENDENCY_ADDRESSES[symbol],
                )
                for offset, kind, symbol in TARGET_RELOCATIONS
            ],
        )
        component_report = report["component"]
        self.assertEqual(component_report["size"], 3_665_974)
        self.assertEqual(
            component_report["sha256"],
            PRODUCTION_COMPONENT_SHA256,
        )
        self.assertEqual(
            component_report["replaced_stock_function_bytes"],
            98_580,
        )
        self.assertEqual(
            component_report["generated_patch_site_bytes"],
            98_402,
        )
        self.assertEqual(component_report["generated_wrapper_bytes"], 32)
        self.assertEqual(
            component_report["source_owned_in_place_bytes"],
            182,
        )
        self.assertEqual(component_report["source_owned_bytes"], 142_760)
        self.assertEqual(component_report["opaque_base_bytes"], 3_424_780)

        overlay = CURRENT_OVERLAY.read_bytes()
        component = CURRENT_COMPONENT.read_bytes()
        package = CURRENT_PACKAGE.read_bytes()
        self.assertEqual(len(overlay), 142_578)
        self.assertEqual(sha256(overlay), PRODUCTION_OVERLAY_SHA256)
        self.assertEqual(len(component), 3_665_974)
        self.assertEqual(sha256(component), PRODUCTION_COMPONENT_SHA256)
        self.assertEqual(len(package), 4_444_468)
        self.assertEqual(sha256(package), PRODUCTION_PACKAGE_SHA256)
        self.assertEqual(
            overlay[PRODUCTION_OFFSET:PRODUCTION_OFFSET + 116],
            component[
                len(component) - len(overlay) + PRODUCTION_OFFSET:
                len(component) - len(overlay) + PRODUCTION_OFFSET + 116
            ],
        )

        patches = [
            item
            for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_cmsis_mutex_new"
        ]
        self.assertEqual(len(patches), 1)
        patch = patches[0]
        self.assertEqual(patch["name"], "replace_cmsis_mutex_new")
        self.assertEqual(patch["payload_offset"], 71_484)
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                STOCK_START,
                bytes.fromhex(patch["replacement_hex"][:8]),
                link=False,
            ),
            PRODUCTION_RUNTIME_ADDRESS,
        )
        self.assertEqual(
            component[71_484:71_484 + len(STOCK_BYTES)],
            bytes.fromhex(patch["replacement_hex"]),
        )

        manifest = json.loads(CURRENT_MANIFEST.read_text())
        self.assertEqual(
            manifest["package"],
            {
                "output_name": (
                    "g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
                ),
                "expected_size": 4_444_468,
                "expected_sha256": PRODUCTION_PACKAGE_SHA256,
                "profiles": {
                    "linux-clang": {
                        "expected_size": 4_446_156,
                        "expected_sha256": (
                            "2cca0fbac8da01ede95a3cecd55dd070"
            "6f6dad3a8437605f8a68949cee3c6bc3"
                        ),
                    },
                },
            },
        )
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual(
            main["provider"],
            {
                "kind": "source_build",
                "path": (
                    "components/apollo_main/core_overlay/build/"
                    "ota_s200_firmware_ota.bin"
                ),
                "size": 3_665_974,
                "sha256": PRODUCTION_COMPONENT_SHA256,
                "profiles": {
                    "linux-clang": {
                        "size": 3_667_662,
                        "sha256": (
                            "686ea217db2837bffd8a190485f0a6f7"
            "19242e927fba17281c6f54aa066767f6"
                        ),
                    },
                },
            },
        )
        regions = {region["name"]: region for region in main["regions"]}
        self.assertEqual(
            (
                regions["cmsis_mutex_new_source_replacement"]["file_offset"],
                regions["cmsis_mutex_new_source_replacement"]["size"],
                regions["cmsis_mutex_new_source_replacement"][
                    "target_address"
                ],
                regions["cmsis_mutex_new_source_replacement"][
                    "address_status"
                ],
            ),
            (
                71_484,
                154,
                STOCK_START,
                "generated_source_entry_replacement",
            ),
        )
        self.assertEqual(
            (
                regions[
                    "apollo_cmsis_mutex_new_source_leaf_alignment"
                ]["file_offset"],
                regions[
                    "apollo_cmsis_mutex_new_source_leaf_alignment"
                ]["size"],
                regions[
                    "apollo_cmsis_mutex_new_source_leaf_alignment"
                ]["target_address"],
                regions["apollo_cmsis_mutex_new_source_leaf"]["file_offset"],
                regions["apollo_cmsis_mutex_new_source_leaf"]["size"],
                regions["apollo_cmsis_mutex_new_source_leaf"][
                    "target_address"
                ],
            ),
            (
                3_637_366,
                2,
                0x007B_0056,
                3_637_368,
                116,
                PRODUCTION_RUNTIME_ADDRESS,
            ),
        )

        flash_plan = CURRENT_FLASH_PLAN.read_bytes()
        self.assertEqual(len(flash_plan), 946_460)
        self.assertEqual(
            sha256(flash_plan),
            PRODUCTION_FLASH_PLAN_SHA256,
        )
        parsed_plan = json.loads(flash_plan)
        self.assertEqual(len(parsed_plan["flash_regions"]), 1328)
        self.assertEqual(
            len(parsed_plan["unresolved_flash_regions"]),
            2,
        )

    @_APPLE_ONLY
    def test_current_dependencies_are_source_owned_and_abi_compatible(
        self,
    ) -> None:
        functions = self.current_report["overlay"]["functions"]
        observed = {
            name: (
                int(functions[name]["offset"]),
                int(functions[name]["size"]),
            )
            for name in DEPENDENCY_ADDRESSES
        }
        self.assertEqual(
            observed,
            {
                "open_cfw_freertos_task_get_scheduler_state": (
                    108_424,
                    32,
                ),
                "open_cfw_freertos_queue_create_mutex": (
                    105_948,
                    30,
                ),
                "open_cfw_freertos_queue_create_mutex_static": (
                    108_872,
                    38,
                ),
            },
        )
        config = json.loads(CURRENT_CONFIG.read_text())
        base = int(
            self.current_report["overlay"]["overlay_runtime_address"]
        )
        self.assertEqual(
            {
                name: base + offset
                for name, (offset, _size) in observed.items()
            },
            DEPENDENCY_ADDRESSES,
        )

        abi = set(config["functions"])
        self.assertTrue(set(DEPENDENCY_ADDRESSES).issubset(abi))
        patches = {
            patch["name"]: (
                patch["runtime_address"],
                patch["target_function"],
            )
            for patch in config["patch_sites"]
        }
        self.assertEqual(
            patches["replace_freertos_queue_create_mutex"],
            (
                0x0044_16D6,
                "open_cfw_freertos_queue_create_mutex",
            ),
        )
        self.assertEqual(
            patches["replace_freertos_queue_create_mutex_static"],
            (
                0x0044_16F0,
                "open_cfw_freertos_queue_create_mutex_static",
            ),
        )

    def test_host_layout_and_default_dynamic_path(self) -> None:
        self.assertEqual(self.host_compile.stderr, "")
        for name, expected in (
            ("static_semaphore_size", 80),
            ("attr_size", 32 if ctypes.sizeof(ctypes.c_void_p) == 8 else 16),
            ("attr_offset_name", 0),
            (
                "attr_offset_attr_bits",
                8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 4,
            ),
            (
                "attr_offset_cb_mem",
                16 if ctypes.sizeof(ctypes.c_void_p) == 8 else 8,
            ),
            (
                "attr_offset_cb_size",
                24 if ctypes.sizeof(ctypes.c_void_p) == 8 else 12,
            ),
        ):
            function = getattr(
                self.loaded,
                f"open_cfw_test_cmsis_mutex_{name}",
            )
            function.argtypes = []
            function.restype = ctypes.c_uint
            self.assertEqual(function(), expected)

        self.reset()
        result = self.call(0, 0, 0, 0, 0)
        self.assertEqual(result, self.dynamic_pointer())
        self.assertEqual(
            self.get_uint("open_cfw_test_cmsis_mutex_dynamic_calls"),
            1,
        )
        self.assertEqual(
            self.get_uint("open_cfw_test_cmsis_mutex_dynamic_type"),
            1,
        )
        self.assertEqual(
            self.get_uint("open_cfw_test_cmsis_mutex_static_calls"),
            0,
        )

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
                self.set_uint("open_cfw_test_cmsis_mutex_ipsr", ipsr)
                self.set_int(
                    "open_cfw_test_cmsis_mutex_scheduler_state",
                    scheduler,
                )
                self.set_uint("open_cfw_test_cmsis_mutex_primask", primask)
                self.set_uint("open_cfw_test_cmsis_mutex_basepri", basepri)
                result = self.call(0, 0, 0, 0, 0)
                self.assertEqual(
                    result,
                    self.dynamic_pointer() if allow else 0,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_mutex_ipsr_reads"),
                    1,
                )
                self.assertEqual(
                    self.get_uint(
                        "open_cfw_test_cmsis_mutex_scheduler_calls"
                    ),
                    scheduler_reads,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_mutex_primask_reads"),
                    primask_reads,
                )
                self.assertEqual(
                    self.get_uint("open_cfw_test_cmsis_mutex_basepri_reads"),
                    basepri_reads,
                )
                self.assertEqual(
                    self.get_uint(
                        "open_cfw_test_cmsis_mutex_dynamic_calls"
                    ),
                    1 if allow else 0,
                )

    def test_exhaustive_attributes_match_independent_oracle(self) -> None:
        control = self.control_pointer()
        dynamic = self.dynamic_pointer()
        self.assertEqual(control & 1, 0)
        self.assertEqual(dynamic & 1, 0)

        for provide_attr in (False, True):
            for attr_bits in range(32):
                for provide_cb in (False, True):
                    for cb_size in (0, 79, 80, 81):
                        with self.subTest(
                            provide_attr=provide_attr,
                            attr_bits=attr_bits,
                            provide_cb=provide_cb,
                            cb_size=cb_size,
                        ):
                            self.reset()
                            result = self.call(
                                int(provide_attr),
                                attr_bits,
                                int(provide_cb),
                                cb_size,
                                1,
                            )
                            route, queue_type, recursive = expected_route(
                                provide_attr,
                                attr_bits,
                                provide_cb,
                                cb_size,
                            )
                            expected_pointer = {
                                "static": control,
                                "dynamic": dynamic,
                                "none": 0,
                            }[route]
                            if expected_pointer and recursive:
                                expected_pointer |= 1
                            self.assertEqual(result, expected_pointer)
                            self.assertEqual(
                                self.get_uint(
                                    "open_cfw_test_cmsis_mutex_static_calls"
                                ),
                                1 if route == "static" else 0,
                            )
                            self.assertEqual(
                                self.get_uint(
                                    "open_cfw_test_cmsis_mutex_dynamic_calls"
                                ),
                                1 if route == "dynamic" else 0,
                            )
                            if route == "static":
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_mutex_"
                                        "static_type"
                                    ),
                                    queue_type,
                                )
                                static_control = ctypes.c_void_p.in_dll(
                                    self.loaded,
                                    "open_cfw_test_cmsis_mutex_"
                                    "static_control",
                                ).value
                                self.assertEqual(static_control, control)
                            if route == "dynamic":
                                self.assertEqual(
                                    self.get_uint(
                                        "open_cfw_test_cmsis_mutex_"
                                        "dynamic_type"
                                    ),
                                    queue_type,
                                )

    def test_creator_failures_do_not_create_or_tag_handles(self) -> None:
        for attr_bits in (0, 1, 2, 3):
            with self.subTest(route="dynamic", attr_bits=attr_bits):
                self.reset()
                self.set_uint(
                    "open_cfw_test_cmsis_mutex_dynamic_success",
                    0,
                )
                self.assertEqual(
                    self.call(1, attr_bits, 0, 0, 1),
                    0,
                )
                self.assertEqual(
                    self.get_uint(
                        "open_cfw_test_cmsis_mutex_dynamic_calls"
                    ),
                    1,
                )

            with self.subTest(route="static", attr_bits=attr_bits):
                self.reset()
                self.set_uint(
                    "open_cfw_test_cmsis_mutex_static_success",
                    0,
                )
                self.assertEqual(
                    self.call(1, attr_bits, 1, 80, 1),
                    0,
                )
                self.assertEqual(
                    self.get_uint(
                        "open_cfw_test_cmsis_mutex_static_calls"
                    ),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
