from __future__ import annotations

import copy
import ctypes
import hashlib
import json
import os
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
    / "shared"
    / "freertos"
    / "runtime_freertos_missed_yield.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_missed_yield_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
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

SOURCE_SHA256 = (
    "1f7ec93d00e35dcc4cf156d455992449"
    "3e46f6cc89c30de1ed7e53442177013c"
)
HEADER_SHA256 = (
    "0008f68d1196ea92a33a8cfa7bee3397"
    "33354ccf8d64b96279acf6a43a1a21af"
)
HOST_FIXTURE_SHA256 = (
    "828ca596ce5980b03478fa115c661ff4"
    "ba90d808ef0db97effb5b2e2868f9a07"
)

BASE = 0x00438000
START = 0x004555E6
END = 0x004555F0
STOCK_BYTES = "0120dff8581608607047"
STOCK_SHA256 = (
    "8cada1af8ad4973f2ad647d45c8a0ac9"
    "c56fdf2d8b270607844b7940eb7d5d2d"
)
YIELD_PENDING_LITERAL = 0x00455C44
YIELD_PENDING_WORD = 0x20074A44
CALLERS = [
    (0x00441FA2, "13f020fb"),
    (0x00441FD8, "13f005fb"),
]

FUNCTION = "open_cfw_freertos_task_missed_yield"
TARGET_BYTES = "44f64420c2f20700012101607047"
TARGET_SHA256 = (
    "2b028e0c4aa84ce41bfe4b4164a397ae"
    "4d5ba9f177900cefb3b71c5d5d339ba9"
)
APPLE_OFFSET = 175_188
LINUX_OFFSET = 117_172
APPLE_RUNTIME_ADDRESS = 0x007BEF78

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

_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang")
    == "apple-clang",
    "production byte-exact build uses the reviewed Apple-clang profile",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


class RuntimeFreeRTOSMissedYieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        library = temporary / library_name("runtime_freertos_missed_yield")
        host_command = [
            clang,
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
        cls.reset = cls.loaded.open_cfw_test_freertos_missed_yield_reset
        cls.reset.argtypes = [ctypes.c_int32]
        cls.reset.restype = None
        cls.invoke = cls.loaded.open_cfw_test_freertos_missed_yield_invoke
        cls.invoke.argtypes = []
        cls.invoke.restype = None
        cls.value = cls.loaded.open_cfw_test_freertos_missed_yield_value
        cls.value.argtypes = []
        cls.value.restype = ctypes.c_int32
        cls.stores = cls.loaded.open_cfw_test_freertos_missed_yield_stores
        cls.stores.argtypes = []
        cls.stores.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_freertos_missed_yield.o"
        subprocess.run(
            [
                clang,
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
        cls.config = json.loads(
            OVERLAY_CONFIG.read_text(encoding="utf-8")
        )
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[32:]

        cls.production = None
        if (
            os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang"
        ) == "apple-clang":
            # The parent integration step intentionally records the final
            # overlay/component pins only after this isolated leaf is proven.
            # Build the otherwise-identical production graph with only those
            # two aggregate pins omitted.
            build_config = copy.deepcopy(cls.config)
            build_config["expected"] = {}
            unpinned_config = temporary / "overlay-unpinned-final.json"
            unpinned_config.write_text(
                json.dumps(build_config, indent=2) + "\n",
                encoding="utf-8",
            )
            cls.production = apollo_overlay.build(
                root=ROOT,
                config_path=unpinned_config,
                output_dir=temporary / "production",
                clang=clang,
                toolchain_profile="apple-clang",
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    def test_authenticated_upstream_source_and_license_are_pinned(
        self,
    ) -> None:
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            sha256(UPSTREAM_TASKS),
            "14020d617b96dd2814e1211f6e3b645b"
            "cf5e2bd3179c23fe7dd16bc666fe9463",
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)
        upstream = UPSTREAM_TASKS.read_text(encoding="utf-8")
        self.assertIn(
            """void vTaskMissedYield( void )
{
    xYieldPending = pdTRUE;
}""",
            upstream,
        )
        self.assertIn(
            "PRIVILEGED_DATA static volatile BaseType_t "
            "xYieldPending = pdFALSE;",
            upstream,
        )

        self.assertEqual(SOURCE.stat().st_size, 1_749)
        self.assertEqual(HEADER.stat().st_size, 1_055)
        self.assertEqual(HOST_FIXTURE.stat().st_size, 1_150)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(sha256(HOST_FIXTURE), HOST_FIXTURE_SHA256)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "vTaskMissedYield()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x004555E6, 0x004555F0)",
            "xYieldPending",
            "0x20074A44",
            "OPEN_CFW_FREERTOS_YIELD_PENDING_STORE("
            "OPEN_CFW_FREERTOS_TRUE)",
        ):
            self.assertIn(token, source)
        for token in (
            "typedef __INT32_TYPE__ open_cfw_freertos_base_type",
            "OPEN_CFW_FREERTOS_YIELD_PENDING_ADDRESS = 0x20074A44U",
            "OPEN_CFW_FREERTOS_TRUE = 1",
            "volatile open_cfw_freertos_base_type",
        ):
            self.assertIn(token, header)
        for disallowed in ("struct ", "typedef void (*", "malloc(", "free("):
            self.assertNotIn(disallowed, source)

    def test_official_body_hash_bounds_and_state_seam_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        body = self.span(START, END)
        self.assertEqual(len(body), END - START)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(body[:2], bytes.fromhex("0120"))
        self.assertEqual(body[6:], bytes.fromhex("08607047"))

        first, second = struct.unpack_from("<HH", body, 2)
        self.assertEqual(first, 0xF8DF)
        self.assertEqual(second >> 12, 1)
        self.assertEqual(second & 0x0FFF, 0x658)
        pc = ((START + 2) + 4) & ~3
        self.assertEqual(pc + (second & 0x0FFF), YIELD_PENDING_LITERAL)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(
                    YIELD_PENDING_LITERAL,
                    YIELD_PENDING_LITERAL + 4,
                ),
            )[0],
            YIELD_PENDING_WORD,
        )
        self.assertEqual(
            self.span(START - 4, START).hex(),
            "280032bd",
        )
        self.assertEqual(
            self.span(END, END + 4).hex(),
            "80b507e0",
        )

    def test_official_topology_has_only_two_direct_callers_and_no_bypass(
        self,
    ) -> None:
        calls = []
        jumps = []
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, calls), (False, jumps)):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
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
        self.assertEqual(calls, CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in calls
                )
            ).hexdigest(),
            "2832a5fd455af7146bcb2f014bec58042"
            "2f81265fb61028293947397b34a359d",
        )

        narrow = []
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
                    narrow.append((address, target, halfword))
        self.assertEqual(narrow, [])

        stale_pointers = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            normalized = value & ~1 if value & 1 else value
            if START <= normalized < END:
                stale_pointers.append((BASE + offset, value))
        self.assertEqual(stale_pointers, [])

    def test_host_adapter_performs_exactly_one_volatile_true_store(
        self,
    ) -> None:
        for initial in (
            -0x80000000,
            -1,
            0,
            1,
            0x7FFFFFFF,
        ):
            with self.subTest(initial=initial):
                self.reset(initial)
                self.assertEqual(self.value(), initial)
                self.assertEqual(self.stores(), 0)
                self.invoke()
                self.assertEqual(self.value(), 1)
                self.assertEqual(self.stores(), 1)
        self.invoke()
        self.assertEqual(self.value(), 1)
        self.assertEqual(self.stores(), 2)

    def test_apple_target_object_is_one_relocation_free_leaf(
        self,
    ) -> None:
        data, sections = self.apollo_overlay.parse_elf32(
            self.target_object
        )
        symbol_table = self.apollo_overlay.section_named(
            sections,
            ".symtab",
        )
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            symbols.append(
                (
                    self.apollo_overlay.elf_string(
                        strings,
                        fields[0],
                        "symbol",
                    ),
                    fields,
                )
            )
        function = next(
            fields for name, fields in symbols if name == FUNCTION
        )
        function_section = sections[int(function[5])]
        self.assertEqual(
            function_section["name"],
            f".text.{FUNCTION}",
        )
        self.assertEqual(int(function_section["flags"]), 0x6)
        self.assertEqual(int(function_section["alignment"]), 4)
        self.assertEqual((int(function[1]), int(function[2])), (1, 14))
        self.assertEqual(function[3] & 0x0F, 2)
        leaf = data[
            int(function_section["offset"]):
            int(function_section["offset"]) + int(function_section["size"])
        ]
        self.assertEqual(leaf.hex(), TARGET_BYTES)
        self.assertEqual(hashlib.sha256(leaf).hexdigest(), TARGET_SHA256)

        self.assertEqual(
            {
                name
                for name, fields in symbols
                if name and fields[3] & 0x0F == 2 and fields[5] != 0
            },
            {FUNCTION},
        )
        self.assertEqual(
            {
                name
                for name, fields in symbols
                if name and fields[5] == 0
            },
            set(),
        )
        relocations = [
            section
            for section in sections
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(function_section["index"])
                and int(section["size"]) != 0
            )
        ]
        self.assertEqual(relocations, [])
        for prefix in (".data", ".bss", ".rodata"):
            self.assertFalse(
                any(
                    section["name"].startswith(prefix)
                    and int(section["size"]) != 0
                    for section in sections
                )
            )

    def test_dual_profile_configuration_and_filtering_are_exact(
        self,
    ) -> None:
        configured = [
            leaf
            for leaf in self.config["relocated_leaves"]
            if leaf["function"] == FUNCTION
        ]
        self.assertEqual(len(configured), 1)
        leaf = configured[0]
        self.assertIn(leaf, self.config["relocated_leaves"])
        self.assertIn(FUNCTION, self.config["functions"])
        self.assertNotIn("profiles", leaf)
        self.assertEqual(
            leaf["source"],
            {
                "path": (
                    "components/shared/freertos/"
                    "runtime_freertos_missed_yield.c"
                ),
                "size": 1_749,
                "sha256": SOURCE_SHA256,
                "license": "MIT",
                "origin": (
                    "source-equivalent adaptation of authenticated "
                    "FreeRTOS-Kernel V10.5.1 vTaskMissedYield using "
                    "the recovered G2 xYieldPending seam"
                ),
                "upstream": (
                    "https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/"
                    "def7d2df2b0506d3d249334974f51e427c17a41c/tasks.c"
                ),
                "upstream_commit": (
                    "def7d2df2b0506d3d249334974f51e427c17a41c"
                ),
                "evidence": (
                    "docs/research/"
                    "freertos-missed-yield-source-boundary-audit.md"
                ),
            },
        )
        self.assertEqual(
            leaf["expected"],
            {
                "size": 14,
                "sha256": TARGET_SHA256,
                "alignment": 4,
                "offset": APPLE_OFFSET,
                "unrelocated_sha256": TARGET_SHA256,
            },
        )
        self.assertEqual(leaf["relocations"], [])
        linux = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            linux["reviewed_version_prefix"],
            "Homebrew clang version 22.1.8",
        )
        self.assertEqual(
            linux["expected"],
            {
                "size": 14,
                "sha256": TARGET_SHA256,
                "alignment": 4,
                "offset": LINUX_OFFSET,
                "unrelocated_sha256": TARGET_SHA256,
            },
        )
        self.assertEqual(linux["relocations"], [])

        apple_config = self.apollo_overlay.filter_config_for_profile(
            copy.deepcopy(self.config),
            "apple-clang",
        )
        linux_config = self.apollo_overlay.filter_config_for_profile(
            copy.deepcopy(self.config),
            "linux-clang",
        )
        apple_leaf_names = [
            item["function"] for item in apple_config["relocated_leaves"]
        ]
        linux_leaf_names = [
            item["function"] for item in linux_config["relocated_leaves"]
        ]
        self.assertIn(FUNCTION, apple_leaf_names)
        self.assertEqual(
            [
                item["function"]
                for item in apple_config["relocated_leaves"]
                if item["function"] in {
                    "open_cfw_freertos_task_reset_event_item_value",
                    "open_cfw_freertos_task_increment_mutex_held_count",
                }
            ],
            [
                "open_cfw_freertos_task_reset_event_item_value",
                "open_cfw_freertos_task_increment_mutex_held_count",
            ],
        )
        self.assertIn(FUNCTION, linux_leaf_names)
        self.assertEqual(
            [
                item["function"]
                for item in linux_config["relocated_leaves"]
                if item["function"] in {
                    "open_cfw_freertos_task_reset_event_item_value",
                    "open_cfw_freertos_task_increment_mutex_held_count",
                }
            ],
            [
                "open_cfw_freertos_task_reset_event_item_value",
                "open_cfw_freertos_task_increment_mutex_held_count",
            ],
        )
        resolved_linux = self.apollo_overlay.resolve_leaf_profile(
            leaf,
            "linux-clang",
        )
        self.assertEqual(
            resolved_linux["toolchain"]["reviewed_version_prefix"],
            "Homebrew clang version 22.1.8",
        )
        self.assertEqual(resolved_linux["expected"]["offset"], LINUX_OFFSET)

        patches = [
            patch
            for patch in self.config["patch_sites"]
            if patch["target_function"] == FUNCTION
        ]
        self.assertEqual(
            patches,
            [
                {
                    "name": "replace_freertos_task_missed_yield",
                    "runtime_address": START,
                    "expected_size": 10,
                    "expected_sha256": STOCK_SHA256,
                    "branch": "b_w",
                    "target_function": FUNCTION,
                }
            ],
        )
        self.assertNotIn("profiles", patches[0])
        self.assertEqual(
            [
                patch["name"]
                for patch in apple_config["patch_sites"]
                if patch["target_function"] == FUNCTION
            ],
            ["replace_freertos_task_missed_yield"],
        )
        self.assertEqual(
            [
                patch["name"]
                for patch in linux_config["patch_sites"]
                if patch["target_function"] == FUNCTION
            ],
            ["replace_freertos_task_missed_yield"],
        )

    @_APPLE_ONLY
    def test_production_apple_leaf_and_redirect_are_byte_exact(
        self,
    ) -> None:
        self.assertIsNotNone(self.production)
        report_leaf = next(
            leaf
            for leaf in self.production["relocated_leaves"]
            if leaf["extraction"]["function"] == FUNCTION
        )
        self.assertEqual(
            report_leaf["placement"],
            {
                "alignment": 4,
                "offset": APPLE_OFFSET,
                "padding_before": 0,
                "runtime_address": APPLE_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007BEF78",
                "size": 14,
            },
        )
        self.assertEqual(
            {
                key: report_leaf["extraction"][key]
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
                "function": FUNCTION,
                "relocation_count": 0,
                "runtime_address": APPLE_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007BEF78",
                "section": f".text.{FUNCTION}",
                "sha256": TARGET_SHA256,
                "size": 14,
                "unrelocated_sha256": TARGET_SHA256,
            },
        )
        overlay = (
            ROOT / self.production["overlay"]["artifact"]
        ).read_bytes()
        self.assertEqual(
            overlay[APPLE_OFFSET:APPLE_OFFSET + 14].hex(),
            TARGET_BYTES,
        )
        self.assertEqual(
            self.production["overlay"]["functions"][FUNCTION],
            {"offset": APPLE_OFFSET, "size": 14},
        )

        patch = next(
            patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["name"] == "replace_freertos_task_missed_yield"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(
            patch["expected_sha256"],
            STOCK_SHA256,
        )
        self.assertEqual(patch["runtime_address"], START)
        self.assertEqual(patch["expected_size"], END - START)
        self.assertEqual(patch["target_function"], FUNCTION)
        self.assertEqual(patch["target_address"], APPLE_RUNTIME_ADDRESS)
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                START,
                replacement[:4],
                link=False,
            ),
            APPLE_RUNTIME_ADDRESS,
        )
        self.assertEqual(replacement[4:], b"\x00\xbf" * 3)
        self.assertEqual(
            replacement.hex(),
            "5af3e3bf00bf00bf00bf",
        )
        component = (
            ROOT / self.production["component"]["artifact"]
        ).read_bytes()
        offset = patch["payload_offset"]
        self.assertEqual(component[offset:offset + 10], replacement)
        self.assertEqual(self.package[offset:offset + 10].hex(), STOCK_BYTES)
        self.assertEqual(
            (
                self.production["overlay"]["size"],
                self.production["overlay"]["sha256"],
                len(self.production["overlay"]["functions"]),
                len(self.production["overlay"]["patched_sites"]),
                self.production["component"]["size"],
                self.production["component"]["sha256"],
                self.production["component"]["source_owned_bytes"],
                self.production["component"]["opaque_base_bytes"],
            ),
            (
                429_058,
                (
                    "0e3a5f42548a24be9c6be90f9d6a60031af69b6570e7d212815f6671bb6d7bcd"
                ),
                2_631,
                2_374,
                3_952_454,
                (
                    "d72288b5831087acaff95fc3aaadb9e178b755ee8ce3b64a17be24af1bfd3dcb"
                ),
                431_334,
                3_111_914,
            ),
        )

    @staticmethod
    def narrow_branch_targets(
        address: int,
        halfword: int,
    ) -> tuple[int, ...]:
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
                ((halfword >> 9) & 1) << 6
                | ((halfword >> 3) & 0x1F) << 1
            )
            return (address + 4 + immediate,)
        return ()


if __name__ == "__main__":
    unittest.main()
