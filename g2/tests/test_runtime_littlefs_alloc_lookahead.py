from __future__ import annotations

import os

import ctypes
import hashlib
import importlib.util
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
    / "runtime_littlefs_alloc_lookahead.c"
)
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_alloc_lookahead_host.c"
)
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_alloc_lookahead_upstream_oracle_host.c"
)
LITTLEFS_SOURCE = ROOT / "third_party" / "littlefs" / "lfs.c"
LITTLEFS_HEADER = ROOT / "third_party" / "littlefs" / "lfs.h"
LITTLEFS_UTIL_SOURCE = ROOT / "third_party" / "littlefs" / "lfs_util.c"
LITTLEFS_PROVENANCE = ROOT / "third_party" / "littlefs" / "PROVENANCE.json"
LITTLEFS_VERIFIER = ROOT / "third_party" / "littlefs" / "verify_snapshot.py"
MAIN_PACKAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BOOT_IMAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_bootloader.bin"
)
MAIN_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"

FUNCTION = "open_cfw_littlefs_alloc_lookahead"
SOURCE_SIZE = 5_445
SOURCE_SHA256 = (
    "44ab9037747a4cb209404423d52cf817"
    "b035cbab5177a8c0cb05090df4b68491"
)
HOST_FIXTURE_SHA256 = (
    "02362ba83e9aa30e942a1bc0db648303"
    "c22ed6fd701b44e66d4b064862653b6c"
)
ORACLE_FIXTURE_SHA256 = (
    "a2093662073194cc26c0de5c057c5fa"
    "64d9fd009d8986addecf1fe6fad98e8c6"
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_TREE = "06dd0162169d3cb550cd24a3e34d0e4d02983ad3"
UPSTREAM_LFS_C_SHA256 = (
    "81a209e8551754d13b24fc0a2b6707f"
    "b3b2475e14feba00bf0df722b98a31398"
)
UPSTREAM_LFS_H_SHA256 = (
    "ee44e99d6b19119b3e577b969b80c9d"
    "5e6f96410c9593794afddf6d4b314c486"
)
UPSTREAM_LFS_UTIL_SHA256 = (
    "f2fbde533670560434bd9f5a547174cc"
    "7c5a4670a02c47b4bd85180dced8b2ec"
)

MAIN_BASE = 0x0043_8000
MAIN_START = 0x004C_B0F6
MAIN_END = 0x004C_B12E
MAIN_CALLBACK_POINTER = (0x004C_BED8, 0x004C_B0F7)
BOOT_BASE = 0x0041_0000
BOOT_START = 0x0041_0DFE
BOOT_END = 0x0041_0E36
BOOT_CALLBACK_POINTER = (0x0041_1BE0, 0x0041_0DFF)

MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
MAIN_PAYLOAD_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
BOOT_SHA256 = (
    "f89a4c4657537cec6bfc572bdb831886"
    "6309b90a5d180c4307680d39824167b5"
)
STOCK_BYTES = bytes.fromhex(
    "10b4426d891ac26e5118c26eb1fbf2f302fb1311826d91420bd2"
    "426e0b00db08d35c012411f0070294402343406ec90843540020"
    "10bc7047"
)
STOCK_SHA256 = (
    "58285c138461a673be0bed2c5376f8d7"
    "39e40e2aea753ad05d5061bfbc9265cf"
)
PREDECESSOR_SHA256 = (
    "55b7d516bb75d425ebbc077729c8c03a"
    "ef31b93897d422450084cfed8a771f66"
)
SUCCESSOR_SHA256 = (
    "4598d43d64f64b3c9adb472aeea8671f"
    "c58d7d26cd8c562c63ae2875b77a8f46"
)
CLUSTER_SHA256 = (
    "27e70f4e5b4194be066ab2fb762b76f7"
    "09f516e614594d09b7c4a8a781648043"
)

COMMON_FLAGS = [
    "-mthumb",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-Wall",
    "-Wextra",
    "-Werror",
]
TARGETS = {
    "main": {
        "target": "thumbv7em-none-eabi",
        "flags": ["-O2", *COMMON_FLAGS],
        "size": 50,
        "alignment": 4,
        "sha256": (
            "ff36aeaff70307ae466d9f7fafacad678"
            "c706db1551b18d98d7fe68bf3dc5eef"
        ),
        "bytes": bytes.fromhex(
            "426dc36e891a1944b1fbf3f2d0f858c002fb131161450ad2"
            "406e01f00702c9084ff0010c435c0cfa02f21a43425400207047"
        ),
    },
    "boot": {
        "target": "arm-none-eabi",
        "flags": ["-mcpu=cortex-m55", "-Oz", *COMMON_FLAGS],
        "size": 48,
        "alignment": 2,
        "sha256": (
            "bd8e7c926d98a940f215cd41a2fb593"
            "2bfbf1abcf7378839dcadd537ae55324d"
        ),
        "bytes": bytes.fromhex(
            "10b5426dc46e836d891a2144b1fbf4f202fb1411994209d2"
            "406e01f007020123c90803fa02f2435c1a434254002010bd"
        ),
    },
}
PRODUCTION = {
    "main": {
        "config": MAIN_CONFIG,
        "overlay_name": "apollo_core_overlay.bin",
        "component_name": "ota_s200_firmware_ota.bin",
        "overlay_size": 360_578,
        "overlay_sha256": (
            "6f1f38ff89e350a1e104f09fd9278056ac6b8884d0bc21c8357c845ba82035a7"
        ),
        "component_size": 3_883_974,
        "component_sha256": (
            "71d4e2b8011cc1e7503bdbe9e7251963f04b0092a80934d00e5a5ad181c651eb"
        ),
        "leaf_offset": 113_756,
        "leaf_address": 0x007A_FF80,
        "padding_before": 2,
        "patch_address": MAIN_START,
        "patch_offset_key": "payload_offset",
        "patch_offset": MAIN_START - MAIN_BASE + 32,
        "accounting": {
            "generated_patch_site_bytes": 397_446,
            "generated_wrapper_bytes": 32,
            "opaque_base_bytes": 3_123_534,
            "replaced_stock_function_bytes": 397_626,
            "source_owned_bytes": 362_962,
            "source_owned_in_place_bytes": 184,
        },
    },
    "boot": {
        "config": BOOT_CONFIG,
        "overlay_name": "bootloader_core_overlay.bin",
        "component_name": "ota_s200_bootloader.bin",
        "overlay_size": 15_240,
        "overlay_sha256": (
            "d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314"
        ),
        "component_size": 163_840,
        "component_sha256": (
            "f570bbf749b16043c8ccfc6eeae66fafaabf4146d5cc55f63d5fab729775ccad"
        ),
        "leaf_offset": 302,
        "leaf_address": 0x0043_45A6,
        "padding_before": 0,
        "patch_address": BOOT_START,
        "patch_offset_key": "file_offset",
        "patch_offset": BOOT_START - BOOT_BASE,
        "accounting": {
            "generated_alignment_bytes": 16,
            "generated_isolated_alignment_bytes": 0,
            "generated_patch_site_bytes": 16_474,
            "generated_relocated_alignment_bytes": 15,
            "generated_stock_to_overlay_alignment_bytes": 1,
            "opaque_base_bytes": 119_425,
            "source_owned_bytes": 27_925,
        },
    },
}

UINT32_MASK = 0xFFFF_FFFF
BUFFER_BYTES = 512
ORACLE_CASES = 20_000


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class LittlefsCache32(ctypes.Structure):
    _fields_ = [
        ("block", ctypes.c_uint32),
        ("offset", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("buffer", ctypes.c_uint32),
    ]


class LittlefsGstate32(ctypes.Structure):
    _fields_ = [
        ("tag", ctypes.c_uint32),
        ("pair", ctypes.c_uint32 * 2),
    ]


class LittlefsLookahead32(ctypes.Structure):
    _fields_ = [
        ("start", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("next", ctypes.c_uint32),
        ("checkpoint", ctypes.c_uint32),
        ("buffer", ctypes.c_uint32),
    ]


class Littlefs32(ctypes.Structure):
    _fields_ = [
        ("read_cache", LittlefsCache32),
        ("program_cache", LittlefsCache32),
        ("root", ctypes.c_uint32 * 2),
        ("open_list", ctypes.c_uint32),
        ("seed", ctypes.c_uint32),
        ("global_state", LittlefsGstate32),
        ("disk_state", LittlefsGstate32),
        ("delta_state", LittlefsGstate32),
        ("lookahead", LittlefsLookahead32),
        ("configuration", ctypes.c_uint32),
        ("block_count", ctypes.c_uint32),
        ("name_max", ctypes.c_uint32),
        ("file_max", ctypes.c_uint32),
        ("attribute_max", ctypes.c_uint32),
        ("inline_max", ctypes.c_uint32),
    ]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def span(image: bytes, base: int, start: int, end: int) -> bytes:
    return image[start - base:end - base]


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def compile_host(source: Path, output: Path) -> ctypes.CDLL:
    command = [
        os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        str(source),
    ]
    if sys.platform == "darwin":
        command.extend(["-dynamiclib", "-o", str(output)])
    else:
        command.extend(["-shared", "-fPIC", "-o", str(output)])
    subprocess.run(command, check=True, capture_output=True, text=True)
    return ctypes.CDLL(str(output))


def bind_host_api(library: ctypes.CDLL, prefix: str) -> dict[str, object]:
    api: dict[str, object] = {}
    api["reset"] = getattr(library, prefix + "reset")
    api["reset"].argtypes = [
        ctypes.c_uint8,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
    ]
    api["reset"].restype = None
    api["call"] = getattr(library, prefix + "call")
    api["call"].argtypes = [ctypes.c_uint32]
    api["call"].restype = ctypes.c_int
    api["buffer_get"] = getattr(library, prefix + "buffer_get")
    api["buffer_get"].argtypes = [ctypes.c_size_t]
    api["buffer_get"].restype = ctypes.c_uint8
    api["buffer_checksum"] = getattr(library, prefix + "buffer_checksum")
    api["buffer_checksum"].argtypes = []
    api["buffer_checksum"].restype = ctypes.c_uint32
    for name in ("start", "size", "block_count"):
        api[name] = getattr(library, prefix + name)
        api[name].argtypes = []
        api[name].restype = ctypes.c_uint32
    for name in (
        "lfs_size",
        "start_offset",
        "size_offset",
        "buffer_offset",
        "block_count_offset",
    ):
        api[name] = getattr(library, prefix + name)
        api[name].argtypes = []
        api[name].restype = ctypes.c_size_t
    return api


def expected_buffer_checksum(
    pattern: int,
    changed_index: int | None,
    changed_value: int,
) -> int:
    checksum = 2166136261
    for index in range(BUFFER_BYTES):
        value = changed_value if index == changed_index else pattern
        checksum ^= value
        checksum = (checksum * 16777619) & UINT32_MASK
    return checksum


class RuntimeLittlefsAllocLookaheadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)

        cls.candidate = compile_host(
            HOST_FIXTURE,
            temporary / library_name("littlefs_alloc_lookahead_candidate"),
        )
        cls.oracle = compile_host(
            ORACLE_FIXTURE,
            temporary / library_name("littlefs_alloc_lookahead_oracle"),
        )
        cls.candidate_api = bind_host_api(
            cls.candidate,
            "open_cfw_test_littlefs_alloc_lookahead_",
        )
        cls.oracle_api = bind_host_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_alloc_lookahead_",
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.target_records: dict[str, dict[str, object]] = {}
        for name, specification in TARGETS.items():
            object_path = temporary / f"{name}.o"
            command = [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                f"--target={specification['target']}",
                *specification["flags"],
                "-c",
                str(SOURCE),
                "-o",
                str(object_path),
            ]
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            data, sections = apollo_overlay.parse_elf32(object_path)
            symbols = apollo_overlay.parse_elf32_symbols(data, sections)
            symbol = next(
                item for item in symbols if item["name"] == FUNCTION
            )
            section = sections[int(symbol["section_index"])]
            function_offset = (
                int(section["offset"])
                + (int(symbol["value"]) & ~1)
                - int(section["address"])
            )
            body = data[
                function_offset:function_offset + int(symbol["size"])
            ]
            relocations: list[tuple[int, int, str]] = []
            for relocation_section in sections:
                if (
                    int(relocation_section["type"]) != 9
                    or int(relocation_section["info"]) != int(section["index"])
                ):
                    continue
                for index in range(int(relocation_section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(relocation_section["offset"]) + index * 8,
                    )
                    relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            str(symbols[information >> 8]["name"]),
                        )
                    )
            undefined = sorted(
                str(item["name"])
                for item in symbols
                if (
                    int(item["section_index"]) == 0
                    and int(item["binding"]) != 0
                    and item["name"]
                )
            )
            cls.target_records[name] = {
                "command": command,
                "stderr": completed.stderr,
                "body": body,
                "symbol": symbol,
                "section": section,
                "relocations": relocations,
                "undefined": undefined,
                "allocated": [
                    (
                        str(item["name"]),
                        int(item["size"]),
                        int(item["alignment"]),
                        bool(int(item["flags"]) & 1),
                    )
                    for item in sections
                    if int(item["flags"]) & 2 and int(item["size"])
                ],
            }

        cls.production_builds: dict[str, dict[str, object]] = {}
        stage_config = json.loads(MAIN_CONFIG.read_text(encoding="utf-8"))
        stage_config["expected"] = stage_config["core_stage_expected"]
        for profile in stage_config.get("toolchain_profiles", {}).values():
            if "core_stage_expected" in profile:
                profile["expected"] = profile["core_stage_expected"]
        stage_config_path = temporary / "main-stage-overlay.json"
        stage_config_path.write_text(
            json.dumps(stage_config, indent=2) + "\n",
            encoding="utf-8",
        )
        main_output = temporary / "main-build"
        cls.production_builds["main"] = apollo_overlay.build(
            root=ROOT,
            config_path=stage_config_path,
            output_dir=main_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        boot_spec = importlib.util.spec_from_file_location(
            "open_cfw_test_littlefs_alloc_boot_builder",
            ROOT
            / "components"
            / "bootloader"
            / "core_overlay"
            / "build_component.py",
        )
        if boot_spec is None or boot_spec.loader is None:
            raise RuntimeError("cannot load bootloader overlay builder")
        boot_builder = importlib.util.module_from_spec(boot_spec)
        boot_spec.loader.exec_module(boot_builder)
        boot_output = temporary / "boot-build"
        cls.production_builds["boot"] = boot_builder.build(
            root=ROOT,
            config_path=BOOT_CONFIG,
            output_dir=boot_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        for name, specification in PRODUCTION.items():
            output = temporary / f"{name}-build"
            cls.production_builds[name]["overlay_bytes"] = (
                output / str(specification["overlay_name"])
            ).read_bytes()
            cls.production_builds[name]["component_bytes"] = (
                output / str(specification["component_name"])
            ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset_both(
        self,
        pattern: int,
        start: int,
        size: int,
        block_count: int,
    ) -> None:
        self.candidate_api["reset"](pattern, start, size, block_count)
        self.oracle_api["reset"](pattern, start, size, block_count)

    def test_source_and_pristine_upstream_are_authenticated(self) -> None:
        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        self.assertEqual(
            sha256(HOST_FIXTURE.read_bytes()),
            HOST_FIXTURE_SHA256,
        )
        self.assertEqual(
            sha256(ORACLE_FIXTURE.read_bytes()),
            ORACLE_FIXTURE_SHA256,
        )
        self.assertEqual(
            sha256(LITTLEFS_SOURCE.read_bytes()),
            UPSTREAM_LFS_C_SHA256,
        )
        self.assertEqual(
            sha256(LITTLEFS_HEADER.read_bytes()),
            UPSTREAM_LFS_H_SHA256,
        )
        self.assertEqual(
            sha256(LITTLEFS_UTIL_SOURCE.read_bytes()),
            UPSTREAM_LFS_UTIL_SHA256,
        )
        verifier = subprocess.run(
            [sys.executable, str(LITTLEFS_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("littlefs v2.10.1", verifier.stdout)

        provenance = LITTLEFS_PROVENANCE.read_text(encoding="utf-8")
        self.assertIn(f'"selected_commit": "{UPSTREAM_COMMIT}"', provenance)
        self.assertIn(f'"selected_tree": "{UPSTREAM_TREE}"', provenance)
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_alloc_lookahead()",
            UPSTREAM_COMMIT,
            UPSTREAM_TREE,
            "Apollo-main [0x004CB0F6, 0x004CB12E)",
            "bootloader\n * [0x00410DFE, 0x00410E36)",
            "lookahead\n    ) == 0x54U",
            "start\n        ) == 0x54U",
            "size\n        ) == 0x58U",
            "buffer\n        ) == 0x64U",
            "block_count\n    ) == 0x6CU",
            "((block - lfs->lookahead.start) + lfs->block_count) %",
            "lfs->lookahead.buffer[off / 8U] |=",
        ):
            self.assertIn(token, source)
        oracle = ORACLE_FIXTURE.read_text(encoding="utf-8")
        self.assertIn("../../third_party/littlefs/lfs.c", oracle)
        self.assertIn("return lfs_alloc_lookahead(", oracle)

    def test_recovered_target_and_host_layouts_are_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(LittlefsCache32), 0x10)
        self.assertEqual(ctypes.sizeof(LittlefsGstate32), 0x0C)
        self.assertEqual(ctypes.sizeof(LittlefsLookahead32), 0x14)
        self.assertEqual(ctypes.sizeof(Littlefs32), 0x80)
        self.assertEqual(Littlefs32.lookahead.offset, 0x54)
        self.assertEqual(
            Littlefs32.lookahead.offset + LittlefsLookahead32.start.offset,
            0x54,
        )
        self.assertEqual(
            Littlefs32.lookahead.offset + LittlefsLookahead32.size.offset,
            0x58,
        )
        self.assertEqual(
            Littlefs32.lookahead.offset + LittlefsLookahead32.buffer.offset,
            0x64,
        )
        self.assertEqual(Littlefs32.block_count.offset, 0x6C)

        for name in (
            "lfs_size",
            "start_offset",
            "size_offset",
            "buffer_offset",
            "block_count_offset",
        ):
            self.assertEqual(
                self.candidate_api[name](),
                self.oracle_api[name](),
            )

    def test_twenty_thousand_cases_match_upstream_and_independent_oracle(
        self,
    ) -> None:
        rng = random.Random(0x02_10_01_A110C)
        in_range = 0
        out_of_range = 0
        actual_changes = 0

        for index in range(ORACLE_CASES):
            pattern = rng.randrange(0x100)
            if index < ORACLE_CASES // 2:
                block_count = rng.randrange(1, 4097)
                size = rng.randrange(1, min(block_count, 4096) + 1)
                expected_off = rng.randrange(size)
                start = rng.randrange(0, UINT32_MASK - expected_off + 1)
                block = start + expected_off
            else:
                block_count = rng.randrange(1, UINT32_MASK + 1)
                size = rng.randrange(0, min(block_count, 4096) + 1)
                start = rng.randrange(0, UINT32_MASK + 1)
                block = rng.randrange(0, UINT32_MASK + 1)

            delta = (block - start) & UINT32_MASK
            off = ((delta + block_count) & UINT32_MASK) % block_count
            changed_index: int | None = None
            changed_value = pattern
            if off < size:
                in_range += 1
                changed_index = off // 8
                changed_value = pattern | (1 << (off % 8))
                if changed_value != pattern:
                    actual_changes += 1
            else:
                out_of_range += 1

            self.reset_both(pattern, start, size, block_count)
            self.assertEqual(self.candidate_api["call"](block), 0)
            self.assertEqual(self.oracle_api["call"](block), 0)

            expected_checksum = expected_buffer_checksum(
                pattern,
                changed_index,
                changed_value,
            )
            self.assertEqual(
                self.candidate_api["buffer_checksum"](),
                expected_checksum,
            )
            self.assertEqual(
                self.oracle_api["buffer_checksum"](),
                expected_checksum,
            )
            probe = changed_index if changed_index is not None else 0
            expected_probe = (
                changed_value if changed_index is not None else pattern
            )
            self.assertEqual(
                self.candidate_api["buffer_get"](probe),
                expected_probe,
            )
            self.assertEqual(
                self.oracle_api["buffer_get"](probe),
                expected_probe,
            )
            for name, expected in (
                ("start", start),
                ("size", size),
                ("block_count", block_count),
            ):
                self.assertEqual(self.candidate_api[name](), expected)
                self.assertEqual(self.oracle_api[name](), expected)

        self.assertGreaterEqual(in_range, ORACLE_CASES // 2)
        self.assertGreater(out_of_range, 1000)
        self.assertGreater(actual_changes, 4000)

    def test_official_images_stock_bodies_and_neighbors_are_exact(self) -> None:
        self.assertEqual(len(self.main_package), 3_523_396)
        self.assertEqual(sha256(self.main_package), MAIN_PACKAGE_SHA256)
        self.assertEqual(len(self.main), 3_523_364)
        self.assertEqual(sha256(self.main), MAIN_PAYLOAD_SHA256)
        self.assertEqual(len(self.boot), 148_599)
        self.assertEqual(sha256(self.boot), BOOT_SHA256)

        cases = (
            (self.main, MAIN_BASE, MAIN_START, MAIN_END),
            (self.boot, BOOT_BASE, BOOT_START, BOOT_END),
        )
        for image, base, start, end in cases:
            with self.subTest(start=f"{start:#010x}"):
                body = span(image, base, start, end)
                self.assertEqual(body, STOCK_BYTES)
                self.assertEqual(len(body), 56)
                self.assertEqual(sha256(body), STOCK_SHA256)
                self.assertEqual(
                    sha256(span(image, base, start - 16, start)),
                    PREDECESSOR_SHA256,
                )
                self.assertEqual(
                    sha256(span(image, base, end, end + 16)),
                    SUCCESSOR_SHA256,
                )
                self.assertEqual(
                    sha256(span(image, base, start - 22, end + 16)),
                    CLUSTER_SHA256,
                )
        self.assertEqual(
            span(self.main, MAIN_BASE, MAIN_START - 22, MAIN_END + 16),
            span(self.boot, BOOT_BASE, BOOT_START - 22, BOOT_END + 16),
        )

    def test_dual_image_callback_and_no_interior_topology_is_exact(self) -> None:
        cases = (
            (
                self.main,
                MAIN_BASE,
                MAIN_START,
                MAIN_END,
                MAIN_CALLBACK_POINTER,
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_START,
                BOOT_END,
                BOOT_CALLBACK_POINTER,
            ),
        )
        for image, base, start, end, callback in cases:
            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(
                    self.scan_topology(image, base, start, end),
                    {
                        "callers": [],
                        "wide_jumps": [],
                        "narrow": [],
                        "stored": [callback],
                        "interior": [],
                    },
                )
                pointer_address, pointer_value = callback
                self.assertEqual(
                    struct.unpack(
                        "<I",
                        span(
                            image,
                            base,
                            pointer_address,
                            pointer_address + 4,
                        ),
                    )[0],
                    pointer_value,
                )
                self.assertEqual(pointer_value, start | 1)

    @_APPLE_ONLY
    def test_main_and_boot_target_profiles_are_exact_and_closed(self) -> None:
        for name, specification in TARGETS.items():
            with self.subTest(name=name):
                record = self.target_records[name]
                body = record["body"]
                symbol = record["symbol"]
                section = record["section"]
                self.assertEqual(record["stderr"], "")
                self.assertEqual(body, specification["bytes"])
                self.assertEqual(len(body), specification["size"])
                self.assertEqual(sha256(body), specification["sha256"])
                self.assertEqual(
                    int(section["alignment"]),
                    specification["alignment"],
                )
                self.assertEqual(int(symbol["size"]), specification["size"])
                self.assertEqual(int(symbol["value"]) & ~1, 0)
                self.assertEqual(int(symbol["type"]), 2)
                self.assertNotEqual(int(symbol["section_index"]), 0)
                self.assertEqual(record["relocations"], [])
                self.assertEqual(record["undefined"], [])
                self.assertEqual(
                    record["allocated"],
                    [
                        (
                            f".text.{FUNCTION}",
                            specification["size"],
                            specification["alignment"],
                            False,
                        ),
                        (
                            f".ARM.exidx.text.{FUNCTION}",
                            8,
                            4,
                            False,
                        ),
                    ],
                )

    @_APPLE_ONLY
    def test_production_configs_reports_redirects_and_artifacts_are_exact(
        self,
    ) -> None:
        for name, specification in PRODUCTION.items():
            with self.subTest(name=name):
                config = json.loads(
                    Path(specification["config"]).read_text(encoding="utf-8")
                )
                leaves = [
                    item
                    for item in config["relocated_leaves"]
                    if item["function"] == FUNCTION
                ]
                self.assertEqual(len(leaves), 1)
                leaf_config = leaves[0]
                target = TARGETS[name]
                self.assertEqual(
                    leaf_config["source"]["path"],
                    SOURCE.relative_to(ROOT).as_posix(),
                )
                self.assertEqual(
                    (
                        leaf_config["source"]["size"],
                        leaf_config["source"]["sha256"],
                        leaf_config["source"]["license"],
                        leaf_config["source"]["upstream_commit"],
                    ),
                    (
                        SOURCE_SIZE,
                        SOURCE_SHA256,
                        "BSD-3-Clause",
                        UPSTREAM_COMMIT,
                    ),
                )
                self.assertEqual(leaf_config["relocations"], [])
                self.assertEqual(
                    leaf_config["expected"],
                    {
                        "size": target["size"],
                        "sha256": target["sha256"],
                        "alignment": target["alignment"],
                        "offset": specification["leaf_offset"],
                        "unrelocated_sha256": target["sha256"],
                    },
                )
                patches = [
                    item
                    for item in config["patch_sites"]
                    if item["name"] == "replace_littlefs_alloc_lookahead"
                ]
                self.assertEqual(len(patches), 1)
                self.assertEqual(
                    patches[0],
                    {
                        "name": "replace_littlefs_alloc_lookahead",
                        "runtime_address": specification["patch_address"],
                        "expected_size": len(STOCK_BYTES),
                        "expected_sha256": STOCK_SHA256,
                        "branch": "b_w",
                        "target_function": FUNCTION,
                    },
                )

                report = self.production_builds[name]
                overlay = report["overlay_bytes"]
                component = report["component_bytes"]
                self.assertEqual(
                    (len(overlay), sha256(overlay)),
                    (
                        specification["overlay_size"],
                        specification["overlay_sha256"],
                    ),
                )
                self.assertEqual(
                    (len(component), sha256(component)),
                    (
                        specification["component_size"],
                        specification["component_sha256"],
                    ),
                )
                leaf_reports = [
                    item
                    for item in report["relocated_leaves"]
                    if item["extraction"]["function"] == FUNCTION
                ]
                self.assertEqual(len(leaf_reports), 1)
                leaf_report = leaf_reports[0]
                self.assertEqual(
                    leaf_report["placement"],
                    {
                        "offset": specification["leaf_offset"],
                        "size": target["size"],
                        "alignment": target["alignment"],
                        "padding_before": specification["padding_before"],
                        "runtime_address": specification["leaf_address"],
                        "runtime_address_hex": (
                            f"0x{specification['leaf_address']:08X}"
                        ),
                    },
                )
                self.assertEqual(
                    leaf_report["extraction"]["relocation_count"],
                    0,
                )
                self.assertEqual(
                    leaf_report["extraction"]["relocations"],
                    [],
                )
                self.assertEqual(
                    overlay[
                        specification["leaf_offset"]:
                        specification["leaf_offset"] + target["size"]
                    ],
                    target["bytes"],
                )

                patch_reports = [
                    item
                    for item in report["overlay"]["patched_sites"]
                    if item["name"] == "replace_littlefs_alloc_lookahead"
                ]
                self.assertEqual(len(patch_reports), 1)
                patch = patch_reports[0]
                self.assertEqual(
                    patch[specification["patch_offset_key"]],
                    specification["patch_offset"],
                )
                self.assertEqual(
                    (
                        patch["runtime_address"],
                        patch["target_address"],
                        patch["expected_size"],
                        patch["expected_sha256"],
                    ),
                    (
                        specification["patch_address"],
                        specification["leaf_address"],
                        len(STOCK_BYTES),
                        STOCK_SHA256,
                    ),
                )
                replacement = bytes.fromhex(patch["replacement_hex"])
                self.assertEqual(len(replacement), len(STOCK_BYTES))
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        specification["patch_address"],
                        replacement[:4],
                        link=False,
                    ),
                    specification["leaf_address"],
                )
                self.assertEqual(
                    replacement[4:],
                    b"\x00\xbf" * ((len(STOCK_BYTES) - 4) // 2),
                )
                patch_offset = specification["patch_offset"]
                self.assertEqual(
                    component[
                        patch_offset:patch_offset + len(replacement)
                    ],
                    replacement,
                )
                for key, expected in specification["accounting"].items():
                    self.assertEqual(report["component"][key], expected)

    @staticmethod
    def scan_topology(
        image: bytes,
        base: int,
        start: int,
        end: int,
    ) -> dict[str, list[object]]:
        import apollo_overlay

        callers: list[object] = []
        wide_jumps: list[object] = []
        narrow: list[object] = []
        stored: list[object] = []
        interior: list[object] = []

        for offset in range(0, len(image) - 3, 2):
            address = base + offset
            encoded = image[offset:offset + 4]
            for link, observed in (
                (True, callers),
                (False, wide_jumps),
            ):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == start:
                    observed.append((address, encoded.hex()))
                if (
                    start < target < end
                    and not start <= address < end
                ):
                    interior.append(
                        (address, target, link, encoded.hex())
                    )

        for offset in range(0, len(image) - 1, 2):
            address = base + offset
            halfword = struct.unpack_from("<H", image, offset)[0]
            for target in RuntimeLittlefsAllocLookaheadTests.narrow_targets(
                address,
                halfword,
            ):
                if (
                    start <= target < end
                    and not start <= address < end
                ):
                    narrow.append((address, target, halfword))

        for offset in range(0, len(image) - 3):
            value = struct.unpack_from("<I", image, offset)[0]
            canonical = value & ~1 if value & 1 else value
            if start <= canonical < end:
                stored.append((base + offset, value))

        return {
            "callers": callers,
            "wide_jumps": wide_jumps,
            "narrow": narrow,
            "stored": stored,
            "interior": interior,
        }

    @staticmethod
    def narrow_targets(address: int, halfword: int) -> list[int]:
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
                (((halfword >> 9) & 1) << 5)
                | ((halfword >> 3) & 0x1F)
            )
            return [address + 4 + immediate * 2]
        return []


if __name__ == "__main__":
    unittest.main()
