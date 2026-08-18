from __future__ import annotations

import os

import ctypes
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_RELATIVE = (
    "components/apollo_main/core_overlay/"
    "runtime_littlefs_disk_version_parts.c"
)
SOURCE = ROOT / SOURCE_RELATIVE
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_disk_version_parts_host.c"
)
LITTLEFS_SOURCE = ROOT / "third_party" / "littlefs" / "lfs.c"
LITTLEFS_PROVENANCE = ROOT / "third_party" / "littlefs" / "PROVENANCE.json"
MAIN_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
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

SOURCE_SIZE = 1734
SOURCE_SHA256 = (
    "920d03e80c9d16a1d0b4299f8151eefe"
    "4d9f3ac1ba89c2d40bcc5830335eb5a7"
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_URL = (
    "https://github.com/littlefs-project/littlefs/blob/"
    f"{UPSTREAM_COMMIT}/lfs.c"
)
UPSTREAM_SOURCE_SHA256 = (
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398"
)
UPSTREAM_PARTS_SHA256 = (
    "d868fc549322d6e98a23e7b1c3a7c76"
    "f26496a4731235ea190a515058052a313"
)
UPSTREAM_PROVIDER_AND_PARTS_SHA256 = (
    "c9aaa8e5099e70ee44197a48cbe54123"
    "13c54e6a6d184a980c532bc66268c3cc"
)

MAIN_BASE = 0x00438000
BOOT_BASE = 0x00410000
MAIN_CONFIG_ADDRESS = 0x006E83A4
BOOT_CONFIG_ADDRESS = 0x00431070
MAIN_CONFIG_BYTES = bytes.fromhex(
    "00000000b9634700f163470029644700dd644700100000000001000000100000"
    "c00b0000f401000000100000000100000000000000000000000000000000000"
    "00000000000000000000000000000000000000000"
)
BOOT_CONFIG_BYTES = bytes.fromhex(
    "00000000d91242001113420049134200d5134200100000000001000000100000"
    "c00b0000f401000000100000000100000000000000000000000000000000000"
    "00000000000000000000000000000000000000000"
)

STOCK_PROVIDER = bytes.fromhex("dff89c087047")
STOCK_MAJOR = bytes.fromhex("80b5fff7faff000c80b202bd")
STOCK_MINOR = bytes.fromhex("80b5fff7f4ff80b202bd")
STOCK_SUCCESSOR = bytes.fromhex("c16e01667047")

RAW_MAJOR = bytes.fromhex("80b5fff7feff000c80bd")
RAW_MINOR = bytes.fromhex("80b5fff7feff80b280bd")
RAW_MAJOR_SHA256 = (
    "ebb72edfdb508cbf5b617452eb60cbceb"
    "58bfdfc879dcece076544efa75c092f"
)
RAW_MINOR_SHA256 = (
    "da349b05b3a26d6a22ba3f707c4c21e"
    "1591915aeb8451e21f7509905926a4b9d"
)

COMMON_FLAGS = [
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
BOOT_FLAGS = [
    "-mcpu=cortex-m55",
    "-mthumb",
    "-Oz",
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

FUNCTIONS = (
    "open_cfw_littlefs_disk_version_major",
    "open_cfw_littlefs_disk_version_minor",
)
PROVIDER = "open_cfw_littlefs_disk_version"

PROFILES = {
    "main": {
        "config": MAIN_CONFIG,
        "target": "thumbv7em-none-eabi",
        "flags": COMMON_FLAGS,
        "alignment": 4,
        "overlay_name": "apollo_core_overlay.bin",
        "component_name": "ota_s200_firmware_ota.bin",
        "overlay_size": 143227,
        "overlay_sha256": (
            "200b0b3385c26dbe93cfab37503d21f45d3a6a32ee2dd32451c1ce8c63308b10"
        ),
        "component_size": 3666623,
        "component_sha256": (
            "ad895f785a66f249a9c4d45ea353b559acebf57ad8f82fedf43af2361e79e83b"
        ),
        "overlay_base": 0x00794324,
        "provider_offset": 108456,
        "provider_address": 0x007AEACC,
        "provider_bytes": bytes.fromhex("0120c0f202007047"),
        "old_overlay_size": 114324,
        "old_overlay_sha256": (
            "00318de9ff51e19f77d889fa691a3a2a"
            "54e035b1287843bda857f944af58e065"
        ),
        "current_prefix_sha256": (
            "feb002f33602609a99286d6483043204"
            "0c6beb398990f44338e7a400ee144bf8"
        ),
        "old_component_sha256": (
            "f0da043e234dc38481059459755e09162"
            "2d689313cd12e5c8d5155c7b4ba3202"
        ),
        "current_layout_rollback_sha256": (
            "9aa6c62720bdd08f90d196c9e5c4e444406737de2d2171fd5b801ef1b45f3b8c"
        ),
        "historical_tail_size": 22,
        "historical_tail_offset": 113732,
        "later_lookahead_patch": {
            "offset": 602390,
            "size": 56,
        },
        "later_easylogger_patches": (
            {"offset": 21908, "size": 1026},
            {"offset": 22940, "size": 106},
            {"offset": 23056, "size": 26},
            {"offset": 23082, "size": 26},
            {"offset": 68974, "size": 132},
            {"offset": 76448, "size": 24},
            {"offset": 79496, "size": 162},
        ),
        "later_tick_patches": (
            {"offset": 118558, "size": 8},
            {"offset": 118566, "size": 10},
        ),
        "later_cmsis_patch": {
            "offset": 72274,
            "size": 140,
        },
        "later_pc_task_patch": {
            "offset": 118582,
            "size": 34,
        },
        "later_mutex_patch": {
            "offset": 71484,
            "size": 154,
        },
        "later_heap_malloc_patch": {
            "offset": 123184,
            "size": 256,
        },
        "later_heap_free_patch": {
            "offset": 123440,
            "size": 112,
        },
        "later_heap_init_patch": {
            "offset": 123552,
            "size": 90,
        },
        "later_heap_insert_patch": {
            "offset": 123642,
            "size": 94,
        },
        "later_queue_delete_patch": {
            "offset": 40642,
            "size": 34,
        },
        "later_queue_reset_patch": {
            "offset": 38198,
            "size": 180,
        },
        "later_unordered_event_patch": {
            "offset": 119964,
            "size": 218,
        },
        "later_semaphore_patch": {
            "offset": 71866,
            "size": 180,
        },
        "later_missed_yield_patch": {
            "offset": 120326,
            "size": 10,
        },
        "later_check_for_timeout_patch": {
            "offset": 120198,
            "size": 128,
        },
        "later_suspend_all_patch": {
            "offset": 118172,
            "size": 12,
        },
        "later_timeout_state_patch": {
            "offset": 120182,
            "size": 16,
        },
        "later_reset_event_item_value_patch": {
            "offset": 121578,
            "size": 22,
        },
        "later_mutex_held_patch": {
            "offset": 121600,
            "size": 22,
        },
        "later_scheduler_patches": (
            {"offset": 41180, "size": 20},
            {"offset": 41200, "size": 24},
            {"offset": 41224, "size": 44},
            {"offset": 118252, "size": 306},
            {"offset": 118892, "size": 338},
            {"offset": 120982, "size": 38},
        ),
        "major": {
            "offset": 113732,
            "address": 0x007AFF68,
            "sha256": (
                "cffc852c2243f51e8a52543b4f2410b1"
                "92e2365c25f161cfd12f69cae8544122"
            ),
            "bytes": bytes.fromhex("80b5fef7affd000c80bd"),
            "padding_before": 0,
        },
        "minor": {
            "offset": 113744,
            "address": 0x007AFF74,
            "sha256": (
                "e0494044bcf077ed5b67a33cf3eb526b"
                "b9b8b6f31dcfefb5ce347a197b100012"
            ),
            "bytes": bytes.fromhex("80b5fef7a9fd80b280bd"),
            "padding_before": 2,
        },
        "patches": {
            "provider": {
                "offset": 602340,
                "address": 0x004CB0C4,
                "replacement": bytes.fromhex("e3f202bd00bf"),
            },
            "major": {
                "offset": 602346,
                "address": 0x004CB0CA,
                "replacement": bytes.fromhex(
                    "e4f24dbf00bf00bf00bf00bf"
                ),
            },
            "minor": {
                "offset": 602358,
                "address": 0x004CB0D6,
                "replacement": bytes.fromhex("e4f24dbf00bf00bf00bf"),
            },
            "successor": {
                "offset": 602368,
                "address": 0x004CB0E0,
                "replacement": bytes.fromhex("e3f2cebc00bf"),
            },
        },
        "accounting": {
            "generated_patch_site_bytes": 99192,
            "generated_wrapper_bytes": 32,
            "opaque_base_bytes": 3423990,
            "replaced_stock_function_bytes": 99370,
            "source_owned_bytes": 143409,
            "source_owned_in_place_bytes": 182,
        },
    },
    "boot": {
        "config": BOOT_CONFIG,
        "target": "arm-none-eabi",
        "flags": BOOT_FLAGS,
        "alignment": 2,
        "overlay_name": "bootloader_core_overlay.bin",
        "component_name": "ota_s200_bootloader.bin",
        "overlay_size": 662,
        "overlay_sha256": (
            "7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b"
        ),
        "component_size": 149262,
        "component_sha256": (
            "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267"
        ),
        "overlay_base": 0x00434478,
        "provider_offset": 24,
        "provider_address": 0x00434490,
        "provider_bytes": bytes.fromhex("0048704701000200"),
        "old_overlay_size": 282,
        "old_overlay_sha256": (
            "b934dbea7624660c3c774eb0f4edd5e7"
            "3a738fc59023fc69cfac96417dfe2fee"
        ),
        "old_component_sha256": (
            "1aa7920a16ed2857a2743394c0f62395"
            "a2f2477f95c965da47d1e29c4d2d8247"
        ),
        "current_layout_rollback_sha256": (
            "83660259f4bf9f5cb2aa12957f5b97048ae19402d81fba5f5ff07f77a39778c1"
        ),
        "historical_tail_size": 20,
        "later_lookahead_patch": {
            "offset": 3582,
            "size": 56,
        },
        "later_easylogger_patches": (
            {"offset": 31444, "size": 106},
            {"offset": 31560, "size": 26},
            {"offset": 31586, "size": 26},
            {"offset": 45400, "size": 162},
        ),
        "major": {
            "offset": 282,
            "address": 0x00434592,
            "sha256": (
                "15251b134de5617995984b9d8140d6fb"
                "88dca904ef8ef72e480b99f3c0250b2a"
            ),
            "bytes": bytes.fromhex("80b5fff77cff000c80bd"),
            "padding_before": 0,
        },
        "minor": {
            "offset": 292,
            "address": 0x0043459C,
            "sha256": (
                "685d7f3e70053272d9a3920aaf7867d0"
                "a84e8adb402bbccd4ef3afc76195b2b7"
            ),
            "bytes": bytes.fromhex("80b5fff777ff80b280bd"),
            "padding_before": 0,
        },
        "patches": {
            "provider": {
                "offset": 3532,
                "address": 0x00410DCC,
                "replacement": bytes.fromhex("23f060bb00bf"),
            },
            "major": {
                "offset": 3538,
                "address": 0x00410DD2,
                "replacement": bytes.fromhex(
                    "23f0debb00bf00bf00bf00bf"
                ),
            },
            "minor": {
                "offset": 3550,
                "address": 0x00410DDE,
                "replacement": bytes.fromhex("23f0ddbb00bf00bf00bf"),
            },
            "successor": {
                "offset": 3560,
                "address": 0x00410DE8,
                "replacement": bytes.fromhex("23f048bb00bf"),
            },
        },
        "accounting": {
            "generated_alignment_bytes": 3,
            "generated_isolated_alignment_bytes": 0,
            "generated_patch_site_bytes": 860,
            "generated_relocated_alignment_bytes": 2,
            "generated_stock_to_overlay_alignment_bytes": 1,
            "opaque_base_bytes": 147739,
            "source_owned_bytes": 660,
        },
    },
}

STOCK_CASES = {
    "main": {
        "image_base": MAIN_BASE,
        "provider": 0x004CB0C4,
        "major": 0x004CB0CA,
        "minor": 0x004CB0D6,
        "successor": 0x004CB0E0,
        "major_callers": (
            (0x004CF03A, "fcf746f8"),
            (0x004CF06C, "fcf72df8"),
            (0x004CF130, "fbf7cbff"),
        ),
        "minor_callers": (
            (0x004CF046, "fcf746f8"),
            (0x004CF056, "fcf73ef8"),
            (0x004CF064, "fcf737f8"),
            (0x004CF128, "fbf7d5ff"),
        ),
        "major_address_sha256": (
            "7b51f3769f44fc88574db1e9bc59f7b"
            "9b0cfb9ebd4828aefff900ac41362b8e6"
        ),
        "major_call_sha256": (
            "b1f8555d4d8eb20e0a0a898bbfe883b"
            "80368ae9377546e18cf26f12199394b8d"
        ),
        "minor_address_sha256": (
            "2f5995119cd1d3a878599ae4700360a1"
            "54ffeef59ffe001065ebee67db470eec"
        ),
        "minor_call_sha256": (
            "814d436d436d9c2d64eda05fa3f6e059"
            "ebde8a66a981a614866342b8b35c5029"
        ),
    },
    "boot": {
        "image_base": BOOT_BASE,
        "provider": 0x00410DCC,
        "major": 0x00410DD2,
        "minor": 0x00410DDE,
        "successor": 0x00410DE8,
        "major_callers": (
            (0x00414712, "fcf75efb"),
            (0x00414744, "fcf745fb"),
            (0x00414808, "fcf7e3fa"),
        ),
        "minor_callers": (
            (0x0041471E, "fcf75efb"),
            (0x0041472E, "fcf756fb"),
            (0x0041473C, "fcf74ffb"),
            (0x00414800, "fcf7edfa"),
        ),
        "major_address_sha256": (
            "100a325439b572d704b51d5e6d1655d7"
            "cdd1e1b8e1dfafdb490b9202d68f447b"
        ),
        "major_call_sha256": (
            "83276cd45e30e95552935784ffb10530"
            "b1dd4442a61a40dc91c4c10ef2710525"
        ),
        "minor_address_sha256": (
            "9ecabb917e880f8328063075d3805590d"
            "e83912a3d24e88070e6191ef6749f11"
        ),
        "minor_call_sha256": (
            "375d3dfef878923f2646ffd704b95f204"
            "97c08f6c4ae4ba0af0fab3ca6c3a692"
        ),
    },
}


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeLittlefsDiskVersionPartsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()

        library = temporary / (
            "runtime_littlefs_disk_version_parts"
            + (".dylib" if sys.platform == "darwin" else ".so")
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.host = ctypes.CDLL(str(library))
        for name in (
            "set",
            "major",
            "minor",
            "provider_calls",
            "lfs_forwarded",
        ):
            function = getattr(
                cls.host,
                "open_cfw_test_littlefs_disk_version_parts_" + name,
            )
            if name == "set":
                function.argtypes = [ctypes.c_uint32]
                function.restype = None
            else:
                function.argtypes = []
                function.restype = (
                    ctypes.c_uint16
                    if name in ("major", "minor")
                    else ctypes.c_uint
                )
        for name in ("major", "minor"):
            function = getattr(
                cls.host,
                "open_cfw_oracle_littlefs_disk_version_parts_" + name,
            )
            function.argtypes = []
            function.restype = ctypes.c_uint16

        cls.objects = {}
        for profile_name, profile in PROFILES.items():
            object_path = temporary / f"{profile_name}-parts.o"
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    f"--target={profile['target']}",
                    *profile["flags"],
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(object_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.objects[profile_name] = object_path

        cls.builds = {}
        cls.builds["main"] = apollo_overlay.build(
            root=ROOT,
            config_path=MAIN_CONFIG,
            output_dir=temporary / "main-build",
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        boot_spec = importlib.util.spec_from_file_location(
            "open_cfw_test_bootloader_overlay_builder",
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
        cls.builds["boot"] = boot_builder.build(
            root=ROOT,
            config_path=BOOT_CONFIG,
            output_dir=temporary / "boot-build",
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        for name, profile in PROFILES.items():
            output = temporary / f"{name}-build"
            cls.builds[name]["overlay_bytes"] = (
                output / profile["overlay_name"]
            ).read_bytes()
            cls.builds[name]["component_bytes"] = (
                output / profile["component_name"]
            ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def span(data: bytes, base: int, start: int, end: int) -> bytes:
        return data[start - base:end - base]

    @staticmethod
    def expected_source(origin: str) -> dict[str, object]:
        return {
            "path": SOURCE_RELATIVE,
            "size": SOURCE_SIZE,
            "sha256": SOURCE_SHA256,
            "license": "BSD-3-Clause",
            "origin": origin,
            "upstream": UPSTREAM_URL,
            "upstream_commit": UPSTREAM_COMMIT,
            "evidence": "docs/research/littlefs-next-closed-leaves-audit.md",
        }

    def test_source_license_and_exact_upstream_lines_are_authenticated(
        self,
    ) -> None:
        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(self.digest(SOURCE.read_bytes()), SOURCE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "SPDX-License-Identifier: BSD-3-Clause",
            "v2.10.1 lfs.c at commit",
            UPSTREAM_COMMIT,
            "open_cfw_littlefs_disk_version(lfs) >> 16",
            "open_cfw_littlefs_disk_version(lfs) >> 0",
        ):
            self.assertIn(token, source)

        upstream = LITTLEFS_SOURCE.read_bytes()
        self.assertEqual(self.digest(upstream), UPSTREAM_SOURCE_SHA256)
        lines = upstream.splitlines(keepends=True)
        expected_parts = (
            b"static uint16_t lfs_fs_disk_version_major(lfs_t *lfs) {\n"
            b"    return 0xffff & (lfs_fs_disk_version(lfs) >> 16);\n"
            b"\n"
            b"}\n"
            b"\n"
            b"static uint16_t lfs_fs_disk_version_minor(lfs_t *lfs) {\n"
            b"    return 0xffff & (lfs_fs_disk_version(lfs) >> 0);\n"
            b"}\n"
            b"\n"
        )
        self.assertEqual(b"".join(lines[548:557]), expected_parts)
        self.assertEqual(self.digest(expected_parts), UPSTREAM_PARTS_SHA256)
        self.assertEqual(
            self.digest(b"".join(lines[536:557])),
            UPSTREAM_PROVIDER_AND_PARTS_SHA256,
        )
        provenance = json.loads(
            LITTLEFS_PROVENANCE.read_text(encoding="utf-8")
        )
        self.assertEqual(provenance["upstream"]["selected_tag"], "v2.10.1")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertFalse(
            provenance["recovered_g2_configuration"]["build_options"][
                "LFS_MULTIVERSION"
            ]
        )

    def test_non_multiversion_config_seams_are_exact_84_byte_objects(
        self,
    ) -> None:
        cases = (
            (
                self.main,
                MAIN_BASE,
                MAIN_CONFIG_ADDRESS,
                MAIN_CONFIG_BYTES,
                "f38bd899e180d29ee60609a2452d25c2"
                "d2d6c6fef4eb455064e23a6ca7c6e813",
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_CONFIG_ADDRESS,
                BOOT_CONFIG_BYTES,
                "724c351d2136e3c2f10b59ad84d547da"
                "4632739ea1f20eb839e9af2cfbd5b6e8",
            ),
        )
        for image, base, address, expected, expected_hash in cases:
            observed = self.span(image, base, address, address + 84)
            self.assertEqual(observed, expected)
            self.assertEqual(len(observed), 84)
            self.assertEqual(self.digest(observed), expected_hash)
            words = struct.unpack("<21I", observed)
            self.assertEqual(
                words[5:12],
                (16, 256, 4096, 3008, 500, 4096, 256),
            )
            self.assertEqual(words[12:], (0,) * 9)
            self.assertEqual(len(observed), 0x54)

    def test_host_semantics_match_independent_oracle_for_u32_domain_samples(
        self,
    ) -> None:
        set_version = (
            self.host.open_cfw_test_littlefs_disk_version_parts_set
        )
        candidate_major = (
            self.host.open_cfw_test_littlefs_disk_version_parts_major
        )
        candidate_minor = (
            self.host.open_cfw_test_littlefs_disk_version_parts_minor
        )
        oracle_major = (
            self.host.open_cfw_oracle_littlefs_disk_version_parts_major
        )
        oracle_minor = (
            self.host.open_cfw_oracle_littlefs_disk_version_parts_minor
        )
        provider_calls = (
            self.host.open_cfw_test_littlefs_disk_version_parts_provider_calls
        )
        forwarded = (
            self.host.open_cfw_test_littlefs_disk_version_parts_lfs_forwarded
        )
        values = [
            0,
            1,
            0xFFFF,
            0x10000,
            0x00020001,
            0x12345678,
            0x7FFFFFFF,
            0x80000000,
            0xFFFF0000,
            0xFFFFFFFF,
        ]
        state = 0xC001D00D
        for _ in range(256):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            values.append(state)
        for value in values:
            set_version(value)
            self.assertEqual(candidate_major(), oracle_major())
            self.assertEqual(provider_calls(), 1)
            self.assertEqual(forwarded(), 1)
            self.assertEqual(candidate_minor(), oracle_minor())
            self.assertEqual(provider_calls(), 2)
            self.assertEqual(forwarded(), 1)
            self.assertEqual(candidate_major(), (value >> 16) & 0xFFFF)
            self.assertEqual(candidate_minor(), value & 0xFFFF)

    def test_stock_dual_image_bodies_neighbors_and_caller_topology(
        self,
    ) -> None:
        images = {"main": self.main, "boot": self.boot}
        identical_segments = []
        for name, case in STOCK_CASES.items():
            image = images[name]
            base = case["image_base"]
            segment = self.span(
                image,
                base,
                case["provider"],
                case["successor"] + len(STOCK_SUCCESSOR),
            )
            self.assertEqual(
                segment,
                STOCK_PROVIDER + STOCK_MAJOR + STOCK_MINOR + STOCK_SUCCESSOR,
            )
            identical_segments.append(segment)
            self.assertEqual(
                self.digest(STOCK_PROVIDER),
                "1ff8f5ac86a29e52674a91191c4ed763"
                "fe635aed200e701063e8224aa15c3870",
            )
            self.assertEqual(
                self.digest(STOCK_MAJOR),
                "c9ab0025e9e77a75e9240efbd5b15da2"
                "2807bdaa9f9deaf2cb425d4850f3bf08",
            )
            self.assertEqual(
                self.digest(STOCK_MINOR),
                "c03343d554dbdd887485eff548d1f2852"
                "a1e2f1fe86e662759d478f1d28c7253",
            )
            self.assertEqual(
                struct.unpack("<H", STOCK_PROVIDER[-2:])[0],
                0x4770,
            )
            self.assertEqual(
                struct.unpack("<H", STOCK_MAJOR[-2:])[0],
                0xBD02,
            )
            self.assertEqual(
                struct.unpack("<H", STOCK_MINOR[-2:])[0],
                0xBD02,
            )

            for part in ("major", "minor"):
                start = case[part]
                end = start + len(
                    STOCK_MAJOR if part == "major" else STOCK_MINOR
                )
                callers = case[f"{part}_callers"]
                topology = self.scan_topology(image, base, start, end)
                self.assertEqual(
                    topology,
                    {
                        "callers": list(callers),
                        "wide_jumps": [],
                        "narrow": [],
                        "stored": [],
                        "interior": [],
                    },
                )
                addresses = b"".join(
                    struct.pack("<I", address) for address, _ in callers
                )
                calls = b"".join(
                    self.span(image, base, address, address + 4)
                    for address, _ in callers
                )
                self.assertEqual(
                    self.digest(addresses),
                    case[f"{part}_address_sha256"],
                )
                self.assertEqual(
                    self.digest(calls),
                    case[f"{part}_call_sha256"],
                )
        self.assertEqual(identical_segments[0], identical_segments[1])

    def test_separately_compiled_objects_are_exact_closed_relocated_leaves(
        self,
    ) -> None:
        expected_bodies = {
            FUNCTIONS[0]: (RAW_MAJOR, RAW_MAJOR_SHA256),
            FUNCTIONS[1]: (RAW_MINOR, RAW_MINOR_SHA256),
        }
        for profile_name, object_path in self.objects.items():
            profile = PROFILES[profile_name]
            data, sections = self.apollo_overlay.parse_elf32(object_path)
            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            undefined_globals = sorted(
                str(symbol["name"])
                for symbol in symbols
                if int(symbol["binding"]) == 1
                and int(symbol["section_index"]) == 0
                and symbol["name"]
            )
            self.assertEqual(undefined_globals, [PROVIDER])
            defined_functions = {
                str(symbol["name"])
                for symbol in symbols
                if int(symbol["binding"]) == 1
                and int(symbol["type"]) == 2
                and int(symbol["section_index"]) != 0
            }
            self.assertEqual(defined_functions, set(FUNCTIONS))

            for function, (expected_body, expected_hash) in (
                expected_bodies.items()
            ):
                section = self.apollo_overlay.section_named(
                    sections,
                    f".text.{function}",
                )
                start = int(section["offset"])
                body = data[start:start + int(section["size"])]
                self.assertEqual(int(section["type"]), 1)
                self.assertEqual(int(section["flags"]), 6)
                self.assertEqual(
                    int(section["alignment"]),
                    profile["alignment"],
                )
                self.assertEqual(body, expected_body)
                self.assertEqual(len(body), 10)
                self.assertEqual(self.digest(body), expected_hash)

                symbol = next(
                    item for item in symbols if item["name"] == function
                )
                self.assertEqual(int(symbol["binding"]), 1)
                self.assertEqual(int(symbol["type"]), 2)
                self.assertEqual(int(symbol["visibility"]), 0)
                self.assertEqual(int(symbol["section_index"]), section["index"])
                self.assertEqual(int(symbol["value"]), 1)
                self.assertEqual(int(symbol["size"]), 10)

                relocations = self.relocations_for(
                    data,
                    sections,
                    int(section["index"]),
                    symbols,
                )
                self.assertEqual(relocations, [(2, 10, PROVIDER)])
                exidx = self.apollo_overlay.section_named(
                    sections,
                    f".ARM.exidx.text.{function}",
                )
                self.assertEqual(
                    (
                        int(exidx["type"]),
                        int(exidx["flags"]),
                        int(exidx["size"]),
                    ),
                    (0x70000001, 130, 8),
                )

    def test_production_configs_pin_source_toolchain_relocations_and_finals(
        self,
    ) -> None:
        for profile_name, profile in PROFILES.items():
            config = json.loads(profile["config"].read_text(encoding="utf-8"))
            leaves = [
                leaf
                for leaf in config["relocated_leaves"]
                if leaf["function"] in FUNCTIONS
            ]
            self.assertEqual(
                [leaf["function"] for leaf in leaves],
                list(FUNCTIONS),
            )
            for index, leaf in enumerate(leaves):
                function = FUNCTIONS[index]
                short = "major" if function.endswith("major") else "minor"
                origin_prefix = (
                    "bounded freestanding port"
                    if profile_name == "main"
                    else "shared bounded freestanding port"
                )
                origin = (
                    f"{origin_prefix} of exact littlefs v2.10.1 "
                    f"lfs_fs_disk_version_{short} closed over the existing "
                    "source-owned disk-version provider"
                )
                self.assertEqual(
                    leaf["source"],
                    self.expected_source(origin),
                )
                self.assertEqual(
                    leaf["toolchain"],
                    {
                        "target": profile["target"],
                        "reviewed_version_prefix": (
                            "Apple clang version 21.0.0"
                        ),
                        "flags": profile["flags"],
                    },
                )
                self.assertEqual(
                    leaf["expected"],
                    {
                        "size": 10,
                        "sha256": profile[short]["sha256"],
                        "alignment": profile["alignment"],
                        "offset": profile[short]["offset"],
                        "unrelocated_sha256": (
                            RAW_MAJOR_SHA256
                            if short == "major"
                            else RAW_MINOR_SHA256
                        ),
                    },
                )
                self.assertEqual(
                    leaf["relocations"],
                    [
                        {
                            "offset": 2,
                            "type": "R_ARM_THM_CALL",
                            "symbol": PROVIDER,
                            "target_function": PROVIDER,
                        }
                    ],
                )
            self.assertEqual(
                config["expected"],
                {
                    "overlay_size": profile["overlay_size"],
                    "overlay_sha256": profile["overlay_sha256"],
                    "component_size": profile["component_size"],
                    "component_sha256": profile["component_sha256"],
                },
            )

    @_APPLE_ONLY
    def test_production_reports_link_exact_calls_and_discard_siblings(
        self,
    ) -> None:
        for profile_name, profile in PROFILES.items():
            report = self.builds[profile_name]
            overlay = report["overlay_bytes"]
            component = report["component_bytes"]
            self.assertEqual(len(overlay), profile["overlay_size"])
            self.assertEqual(self.digest(overlay), profile["overlay_sha256"])
            self.assertEqual(len(component), profile["component_size"])
            self.assertEqual(
                self.digest(component),
                profile["component_sha256"],
            )
            self.assertEqual(
                overlay[
                    profile["provider_offset"]:
                    profile["provider_offset"] + len(profile["provider_bytes"])
                ],
                profile["provider_bytes"],
            )
            self.assertEqual(
                report["toolchain"]["target"],
                json.loads(
                    profile["config"].read_text(encoding="utf-8")
                )["toolchain"]["target"],
            )

            leaves = [
                leaf
                for leaf in report["relocated_leaves"]
                if leaf["extraction"]["function"] in FUNCTIONS
            ]
            self.assertEqual(
                [leaf["extraction"]["function"] for leaf in leaves],
                list(FUNCTIONS),
            )
            for index, leaf in enumerate(leaves):
                short = "major" if index == 0 else "minor"
                expected = profile[short]
                placement = leaf["placement"]
                extraction = leaf["extraction"]
                self.assertEqual(
                    placement,
                    {
                        "offset": expected["offset"],
                        "size": 10,
                        "alignment": profile["alignment"],
                        "padding_before": expected["padding_before"],
                        "runtime_address": expected["address"],
                        "runtime_address_hex": (
                            f"0x{expected['address']:08X}"
                        ),
                    },
                )
                linked = overlay[
                    expected["offset"]:expected["offset"] + 10
                ]
                self.assertEqual(linked, expected["bytes"])
                self.assertEqual(self.digest(linked), expected["sha256"])
                self.assertEqual(extraction["size"], 10)
                self.assertEqual(extraction["sha256"], expected["sha256"])
                self.assertEqual(
                    extraction["unrelocated_sha256"],
                    RAW_MAJOR_SHA256
                    if short == "major"
                    else RAW_MINOR_SHA256,
                )
                self.assertEqual(extraction["alignment"], profile["alignment"])
                relocation = extraction["relocations"]
                self.assertEqual(len(relocation), 1)
                self.assertEqual(
                    {
                        "offset": relocation[0]["offset"],
                        "type": relocation[0]["type"],
                        "type_id": relocation[0]["type_id"],
                        "symbol": relocation[0]["symbol"],
                        "target_function": relocation[0]["target_function"],
                        "target_address": relocation[0]["target_address"],
                    },
                    {
                        "offset": 2,
                        "type": "R_ARM_THM_CALL",
                        "type_id": 10,
                        "symbol": PROVIDER,
                        "target_function": PROVIDER,
                        "target_address": profile["provider_address"],
                    },
                )
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        expected["address"] + 2,
                        linked[2:6],
                        link=True,
                    ),
                    profile["provider_address"],
                )
                sibling = FUNCTIONS[1 - index]
                self.assertEqual(
                    extraction["discarded_alloc_sections"],
                    [
                        *(
                            [
                                {
                                    "name": (
                                        f".ARM.exidx.text.{FUNCTIONS[0]}"
                                    ),
                                    "size": 8,
                                    "flags": 130,
                                }
                            ]
                            if index == 0
                            else [
                                {
                                    "name": f".text.{sibling}",
                                    "size": 10,
                                    "flags": 6,
                                },
                                {
                                    "name": (
                                        f".ARM.exidx.text.{FUNCTIONS[0]}"
                                    ),
                                    "size": 8,
                                    "flags": 130,
                                },
                            ]
                        ),
                        *(
                            [
                                {
                                    "name": f".text.{sibling}",
                                    "size": 10,
                                    "flags": 6,
                                },
                                {
                                    "name": (
                                        f".ARM.exidx.text.{FUNCTIONS[1]}"
                                    ),
                                    "size": 8,
                                    "flags": 130,
                                },
                            ]
                            if index == 0
                            else [
                                {
                                    "name": (
                                        f".ARM.exidx.text.{FUNCTIONS[1]}"
                                    ),
                                    "size": 8,
                                    "flags": 130,
                                }
                            ]
                        ),
                    ],
                )
                self.assertEqual(
                    (
                        extraction["discarded_alloc_section_count"],
                        extraction["discarded_alloc_section_bytes"],
                    ),
                    (3, 26),
                )
                self.assertEqual(
                    leaf["toolchain"]["flags"],
                    profile["flags"],
                )

            old_size = profile["old_overlay_size"]
            self.assertEqual(
                self.digest(overlay[:old_size]),
                profile.get(
                    "current_prefix_sha256",
                    profile["old_overlay_sha256"],
                ),
            )
            tail_offset = profile.get("historical_tail_offset", old_size)
            tail = overlay[
                tail_offset:
                tail_offset + profile["historical_tail_size"]
            ]
            self.assertEqual(
                tail,
                (
                    profile["major"]["bytes"]
                    + (b"\0\0" if profile_name == "main" else b"")
                    + profile["minor"]["bytes"]
                ),
            )

    @_APPLE_ONLY
    def test_redirects_neighbors_and_component_mutation_accounting_are_exact(
        self,
    ) -> None:
        stock_images = {
            "main": self.main_package,
            "boot": self.boot,
        }
        stock_offsets = {
            "main": {
                "major": PROFILES["main"]["patches"]["major"]["offset"],
                "minor": PROFILES["main"]["patches"]["minor"]["offset"],
            },
            "boot": {
                "major": PROFILES["boot"]["patches"]["major"]["offset"],
                "minor": PROFILES["boot"]["patches"]["minor"]["offset"],
            },
        }
        for profile_name, profile in PROFILES.items():
            report = self.builds[profile_name]
            component = report["component_bytes"]
            patches = {
                patch["name"].removeprefix("replace_littlefs_"): patch
                for patch in report["overlay"]["patched_sites"]
                if patch["name"] in (
                    "replace_littlefs_disk_version",
                    "replace_littlefs_disk_version_major",
                    "replace_littlefs_disk_version_minor",
                    "replace_littlefs_alloc_ckpoint",
                )
            }
            mapped = {
                "disk_version": "provider",
                "disk_version_major": "major",
                "disk_version_minor": "minor",
                "alloc_ckpoint": "successor",
            }
            for report_name, short in mapped.items():
                expected = profile["patches"][short]
                observed = patches[report_name]
                self.assertEqual(observed["branch"], "b_w")
                self.assertEqual(observed["runtime_address"], expected["address"])
                offset_key = (
                    "payload_offset"
                    if profile_name == "main"
                    else "file_offset"
                )
                self.assertEqual(observed[offset_key], expected["offset"])
                replacement = bytes.fromhex(observed["replacement_hex"])
                self.assertEqual(replacement, expected["replacement"])
                self.assertEqual(replacement[4:], b"\x00\xbf" * (
                    (len(replacement) - 4) // 2
                ))
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        expected["address"],
                        replacement[:4],
                        link=False,
                    ),
                    observed["target_address"],
                )
                start = expected["offset"]
                self.assertEqual(
                    component[start:start + len(replacement)],
                    replacement,
                )

            provider = profile["patches"]["provider"]
            successor = profile["patches"]["successor"]
            cluster = component[
                provider["offset"]:
                successor["offset"] + len(successor["replacement"])
            ]
            self.assertEqual(
                cluster,
                provider["replacement"]
                + profile["patches"]["major"]["replacement"]
                + profile["patches"]["minor"]["replacement"]
                + successor["replacement"],
            )

            component_report = report["component"]
            for key, value in profile["accounting"].items():
                self.assertEqual(component_report[key], value)
            self.assertEqual(
                sum(
                    component_report[key]
                    for key in (
                        (
                            "opaque_base_bytes",
                            "generated_patch_site_bytes",
                            "generated_wrapper_bytes",
                            "source_owned_bytes",
                        )
                        if profile_name == "main"
                        else (
                            "opaque_base_bytes",
                            "generated_patch_site_bytes",
                            "generated_alignment_bytes",
                            "source_owned_bytes",
                        )
                    )
                ),
                len(component),
            )

            restored = bytearray(component)
            stock = stock_images[profile_name]
            for short, stock_body in (
                ("major", STOCK_MAJOR),
                ("minor", STOCK_MINOR),
            ):
                offset = stock_offsets[profile_name][short]
                self.assertEqual(
                    stock[offset:offset + len(stock_body)],
                    stock_body,
                )
                restored[offset:offset + len(stock_body)] = stock_body
            later = profile["later_lookahead_patch"]
            later_offset = later["offset"]
            later_size = later["size"]
            restored[later_offset:later_offset + later_size] = stock[
                later_offset:later_offset + later_size
            ]
            for later_patch in profile["later_easylogger_patches"]:
                patch_offset = later_patch["offset"]
                patch_size = later_patch["size"]
                restored[
                    patch_offset:patch_offset + patch_size
                ] = stock[patch_offset:patch_offset + patch_size]
            if profile_name == "main":
                for later_patch in profile["later_tick_patches"]:
                    patch_offset = later_patch["offset"]
                    patch_size = later_patch["size"]
                    restored[
                        patch_offset:patch_offset + patch_size
                    ] = stock[patch_offset:patch_offset + patch_size]
                for key in (
                    "later_queue_reset_patch",
                    "later_unordered_event_patch",
                    "later_cmsis_patch",
                    "later_pc_task_patch",
                    "later_mutex_patch",
                    "later_heap_malloc_patch",
                    "later_heap_free_patch",
                    "later_heap_init_patch",
                    "later_heap_insert_patch",
                    "later_queue_delete_patch",
                    "later_semaphore_patch",
                    "later_missed_yield_patch",
                    "later_check_for_timeout_patch",
                    "later_suspend_all_patch",
                    "later_timeout_state_patch",
                    "later_reset_event_item_value_patch",
                    "later_mutex_held_patch",
                ):
                    later_patch = profile[key]
                    patch_offset = later_patch["offset"]
                    patch_size = later_patch["size"]
                    restored[
                        patch_offset:patch_offset + patch_size
                    ] = stock[patch_offset:patch_offset + patch_size]
                for later_patch in profile["later_scheduler_patches"]:
                    patch_offset = later_patch["offset"]
                    patch_size = later_patch["size"]
                    restored[
                        patch_offset:patch_offset + patch_size
                    ] = stock[patch_offset:patch_offset + patch_size]
                for patch_offset, patch_size in (
                    (39_522, 200),
                    (119_696, 246),
                    (120_896, 22),
                ):
                    restored[
                        patch_offset:patch_offset + patch_size
                    ] = stock[patch_offset:patch_offset + patch_size]
                for patch_offset, replacement_hex in (
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
                    restored[
                        patch_offset:patch_offset + len(replacement)
                    ] = replacement
            appended_bytes = (
                profile["overlay_size"] - profile["old_overlay_size"]
            )
            del restored[-appended_bytes:]
            if profile_name == "main":
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
            self.assertEqual(
                self.digest(restored),
                profile.get(
                    "current_layout_rollback_sha256",
                    profile["old_component_sha256"],
                ),
            )

    @classmethod
    def relocations_for(
        cls,
        data: bytes,
        sections: list[dict[str, int | str]],
        section_index: int,
        symbols: list[dict[str, int | str]],
    ) -> list[tuple[int, int, str]]:
        records = []
        for section in sections:
            if (
                int(section["type"]) != 9
                or int(section["info"]) != section_index
            ):
                continue
            self_entry_size = int(section["entry_size"])
            for index in range(int(section["size"]) // self_entry_size):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + index * self_entry_size,
                )
                records.append(
                    (
                        offset,
                        information & 0xFF,
                        str(symbols[information >> 8]["name"]),
                    )
                )
        return records

    @classmethod
    def scan_topology(
        cls,
        image: bytes,
        base: int,
        start: int,
        end: int,
    ) -> dict[str, list[object]]:
        callers: list[object] = []
        wide_jumps: list[object] = []
        narrow: list[object] = []
        stored: list[object] = []
        interior: list[object] = []

        for offset in range(0, len(image) - 3, 2):
            address = base + offset
            encoded = image[offset:offset + 4]
            for link, observed in ((True, callers), (False, wide_jumps)):
                try:
                    target = cls.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except cls.apollo_overlay.BuildError:
                    continue
                if target == start:
                    observed.append((address, encoded.hex()))
                if (
                    start < target < end
                    and not start <= address < end
                ):
                    interior.append((address, target, link, encoded.hex()))

        for offset in range(0, len(image) - 1, 2):
            address = base + offset
            halfword = struct.unpack_from("<H", image, offset)[0]
            for target in cls.narrow_branch_targets(address, halfword):
                if (
                    start <= target < end
                    and not start <= address < end
                ):
                    narrow.append((address, target, halfword))

        target_words = {
            address | thumb
            for address in range(start, end, 2)
            for thumb in (0, 1)
        }
        for offset in range(0, len(image) - 3):
            value = struct.unpack_from("<I", image, offset)[0]
            if value in target_words:
                stored.append((base + offset, value))
        return {
            "callers": callers,
            "wide_jumps": wide_jumps,
            "narrow": narrow,
            "stored": stored,
            "interior": interior,
        }

    @staticmethod
    def narrow_branch_targets(address: int, halfword: int) -> list[int]:
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
