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
    / "runtime_freertos_reset_event_item_value.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_reset_event_item_value_host.c"
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
CORE_SOURCE_MANIFEST = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)

SOURCE_SIZE = 2_468
SOURCE_SHA256 = (
    "4a34efbad2b321bb0cd04fb4378a83c50"
    "7c546beb858b3533eb7a0134cace7db"
)
HEADER_SIZE = 2_074
HEADER_SHA256 = (
    "7cbacbed8fba97f13abb0f9bfd19fc285"
    "fd27413ace3122ddf1dab0e2ca9da67"
)
HOST_FIXTURE_SIZE = 2_526
HOST_FIXTURE_SHA256 = (
    "9451c62a9831e382f3c8555d58bcbe5b"
    "5d696f91a193439d063e131f879533df"
)

BASE = 0x00438000
START = 0x00455ACA
END = 0x00455AE0
STOCK_BYTES = "dff89015086880690a680968c96ad1f1380191617047"
STOCK_SHA256 = (
    "76463ec53fbc06884c159bf5b7d01708"
    "c06e404e9b51bdcaab307b219179c049"
)
CURRENT_TCB_LITERAL = 0x0045605C
CURRENT_TCB_WORD = 0x20074A20
EVENT_ITEM_VALUE_OFFSET = 0x18
PRIORITY_OFFSET = 0x2C
MAX_PRIORITIES = 56
CALLERS = [(0x0047ECCE, "d6f7fcfe")]
CALLER_DIGEST = (
    "13157b371b412ca87ad1f51cb2694c5c7"
    "062132d784310e135fa58ff5d0e2116"
)

FUNCTION = "open_cfw_freertos_task_reset_event_item_value"
TARGET_BYTES = (
    "44f62021c2f20701086880690a680968"
    "c96ac1f1380191617047"
)
TARGET_SHA256 = (
    "04fee613f7c2fb46a3e6f5832f7ea618"
    "75543a30160757ffd63579b58f0c45c6"
)
APPLE_OFFSET = 115_356
LINUX_OFFSET = 117_188
APPLE_RUNTIME_ADDRESS = 0x007B_05C0
LINUX_RUNTIME_ADDRESS = 0x007B_0CE8
APPLE_REPLACEMENT = "5af379bd" + "00bf" * 9
APPLE_REPLACEMENT_SHA256 = (
    "d59138d081a6517f67a45c79ec67665a"
    "0db477023669ecc510de77d10ab7c01e"
)
LINUX_REPLACEMENT = "5bf30db9" + "00bf" * 9
LINUX_REPLACEMENT_SHA256 = (
    "c418595a739029c5c6f993d9b0a79bab"
    "54ec26c95eeb62cccbb2e36a7b084e18"
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


class RuntimeFreeRTOSResetEventItemValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        library = temporary / library_name(
            "runtime_freertos_reset_event_item_value"
        )
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
        cls.configure = (
            cls.loaded.open_cfw_test_freertos_reset_event_item_configure
        )
        cls.configure.argtypes = [ctypes.c_uint32] * 9
        cls.configure.restype = None
        cls.invoke = (
            cls.loaded.open_cfw_test_freertos_reset_event_item_invoke
        )
        cls.invoke.argtypes = []
        cls.invoke.restype = ctypes.c_uint32
        cls.event = cls.loaded.open_cfw_test_freertos_reset_event_item_event
        cls.event.argtypes = [ctypes.c_uint32]
        cls.event.restype = ctypes.c_uint32
        cls.priority = (
            cls.loaded.open_cfw_test_freertos_reset_event_item_priority
        )
        cls.priority.argtypes = [ctypes.c_uint32]
        cls.priority.restype = ctypes.c_uint32
        cls.loads = cls.loaded.open_cfw_test_freertos_reset_event_item_loads
        cls.loads.argtypes = []
        cls.loads.restype = ctypes.c_uint32

        cls.target_object = temporary / (
            "runtime_freertos_reset_event_item_value.o"
        )
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

    def test_authenticated_upstream_source_and_local_inputs_are_pinned(
        self,
    ) -> None:
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            sha256(UPSTREAM_TASKS),
            "14020d617b96dd2814e1211f6e3b645bc"
            "f5e2bd3179c23fe7dd16bc666fe9463",
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
            """TickType_t uxTaskResetEventItemValue( void )
{
    TickType_t uxReturn;

    uxReturn = listGET_LIST_ITEM_VALUE( &( pxCurrentTCB->xEventListItem ) );""",
            upstream,
        )
        self.assertIn(
            """listSET_LIST_ITEM_VALUE( &( pxCurrentTCB->xEventListItem ), ( ( TickType_t ) configMAX_PRIORITIES - ( TickType_t ) pxCurrentTCB->uxPriority ) );""",
            upstream,
        )
        self.assertIn("return uxReturn;", upstream)

        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(HEADER.stat().st_size, HEADER_SIZE)
        self.assertEqual(HOST_FIXTURE.stat().st_size, HOST_FIXTURE_SIZE)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(sha256(HOST_FIXTURE), HOST_FIXTURE_SHA256)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "uxTaskResetEventItemValue()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00455ACA, 0x00455AE0)",
            "configMAX_PRIORITIES - uxPriority",
            "0x20074A20",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_CURRENT_TCB_ADDRESS = 0x20074A20U",
            "OPEN_CFW_FREERTOS_EVENT_ITEM_VALUE_OFFSET = 0x18U",
            "OPEN_CFW_FREERTOS_PRIORITY_OFFSET = 0x2CU",
            "OPEN_CFW_FREERTOS_MAX_PRIORITIES = 56U",
            "struct open_cfw_freertos_event_tcb",
            "volatile open_cfw_freertos_tick_type event_item_value",
            "volatile open_cfw_freertos_ubase_type priority",
        ):
            self.assertIn(token, header)

    def test_official_body_hash_layout_and_state_seam_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        body = self.span(START, END)
        self.assertEqual(len(body), 22)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)

        first, second = struct.unpack_from("<HH", body, 0)
        self.assertEqual(first, 0xF8DF)
        self.assertEqual(second >> 12, 1)
        self.assertEqual(second & 0x0FFF, 0x590)
        pc = (START + 4) & ~3
        self.assertEqual(pc + (second & 0x0FFF), CURRENT_TCB_LITERAL)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(CURRENT_TCB_LITERAL, CURRENT_TCB_LITERAL + 4),
            )[0],
            CURRENT_TCB_WORD,
        )

        self.assertEqual(body[4:8].hex(), "08688069")
        self.assertEqual(body[8:12].hex(), "0a680968")
        self.assertEqual(body[12:16].hex(), "c96ad1f1")
        self.assertEqual(body[-6:].hex(), "380191617047")
        self.assertEqual(self.span(START - 4, START).hex(), "295070bd")
        self.assertEqual(self.span(END, END + 4).hex(), "dff87815")

    def test_official_topology_has_one_caller_and_no_bypass(
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
            CALLER_DIGEST,
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

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            normalized = value & ~1 if value & 1 else value
            if START <= normalized < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

    def test_host_preserves_three_independent_current_tcb_evaluations(
        self,
    ) -> None:
        cases = (
            (
                (0x11111111, 7, 0x22222222, 19, 0x33333333, 55),
                (0, 1, 2),
            ),
            (
                (0x89ABCDEF, 0, 0x76543210, 56, 0xDEADBEEF, 1),
                (2, 0, 1),
            ),
            (
                (0xFFFFFFFF, 0xFFFFFFFF, 0, 0x80000000, 1, 57),
                (1, 2, 0),
            ),
        )
        for values, snapshots in cases:
            with self.subTest(values=values, snapshots=snapshots):
                self.configure(*values, *snapshots)
                initial_events = [values[index * 2] for index in range(3)]
                priorities = [values[index * 2 + 1] for index in range(3)]

                result = self.invoke()

                read_index, write_index, priority_index = snapshots
                self.assertEqual(result, initial_events[read_index])
                self.assertEqual(self.loads(), 3)
                expected_events = list(initial_events)
                expected_events[write_index] = (
                    MAX_PRIORITIES - priorities[priority_index]
                ) & 0xFFFFFFFF
                self.assertEqual(
                    [self.event(index) for index in range(3)],
                    expected_events,
                )
                self.assertEqual(
                    [self.priority(index) for index in range(3)],
                    priorities,
                )

    def test_host_same_snapshot_matches_released_single_tcb_semantics(
        self,
    ) -> None:
        for index in range(3):
            for priority in (0, 1, 55, 56, 57, 0xFFFFFFFF):
                with self.subTest(index=index, priority=priority):
                    values = [
                        0x10203040,
                        3,
                        0x50607080,
                        9,
                        0x90ABCDEF,
                        17,
                    ]
                    values[index * 2 + 1] = priority
                    original = values[index * 2]
                    self.configure(*values, index, index, index)

                    self.assertEqual(self.invoke(), original)
                    self.assertEqual(self.loads(), 3)
                    self.assertEqual(
                        self.event(index),
                        (MAX_PRIORITIES - priority) & 0xFFFFFFFF,
                    )

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
        self.assertEqual((int(function[1]), int(function[2])), (1, 26))
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

    def test_dual_profile_configuration_filtering_and_redirects_are_exact(
        self,
    ) -> None:
        leaf = next(
            leaf
            for leaf in self.config["relocated_leaves"]
            if leaf["function"] == FUNCTION
        )
        self.assertNotIn("profiles", leaf)
        self.assertEqual(
            leaf["source"],
            {
                "path": (
                    "components/shared/freertos/"
                    "runtime_freertos_reset_event_item_value.c"
                ),
                "size": SOURCE_SIZE,
                "sha256": SOURCE_SHA256,
                "license": "MIT",
                "origin": (
                    "source-equivalent adaptation of authenticated "
                    "FreeRTOS-Kernel V10.5.1 "
                    "uxTaskResetEventItemValue using the recovered G2 "
                    "TCB and pxCurrentTCB seams"
                ),
                "upstream": (
                    "https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/"
                    "def7d2df2b0506d3d249334974f51e427c17a41c/"
                    "tasks.c"
                ),
                "upstream_commit": (
                    "def7d2df2b0506d3d249334974f51e427c17a41c"
                ),
                "evidence": (
                    "docs/research/"
                    "freertos-reset-event-item-value-source-boundary-"
                    "audit.md"
                ),
            },
        )
        expected = {
            "size": 26,
            "sha256": TARGET_SHA256,
            "alignment": 4,
            "offset": APPLE_OFFSET,
            "unrelocated_sha256": TARGET_SHA256,
        }
        self.assertEqual(leaf["expected"], expected)
        self.assertEqual(leaf["relocations"], [])
        self.assertEqual(
            leaf["toolchain_profiles"]["linux-clang"],
            {
                "reviewed_version_prefix": (
                    "Homebrew clang version 22.1.8"
                ),
                "expected": {
                    **expected,
                    "offset": LINUX_OFFSET,
                },
                "relocations": [],
            },
        )

        apple_config = self.apollo_overlay.filter_config_for_profile(
            copy.deepcopy(self.config),
            "apple-clang",
        )
        linux_config = self.apollo_overlay.filter_config_for_profile(
            copy.deepcopy(self.config),
            "linux-clang",
        )
        for filtered in (apple_config, linux_config):
            expected_functions = {
                "open_cfw_freertos_task_missed_yield",
                FUNCTION,
                "open_cfw_freertos_task_increment_mutex_held_count",
            }
            self.assertEqual(
                [
                    item["function"]
                    for item in filtered["relocated_leaves"]
                    if item["function"] in expected_functions
                ],
                [
                    "open_cfw_freertos_task_missed_yield",
                    FUNCTION,
                    (
                        "open_cfw_freertos_task_"
                        "increment_mutex_held_count"
                    ),
                ],
            )
        self.assertEqual(
            self.apollo_overlay.resolve_leaf_profile(
                leaf,
                "linux-clang",
            )["expected"]["offset"],
            LINUX_OFFSET,
        )

        patch = next(
            patch
            for patch in self.config["patch_sites"]
            if patch["target_function"] == FUNCTION
        )
        self.assertEqual(
            patch,
            {
                "name": (
                    "replace_freertos_task_reset_event_item_value"
                ),
                "runtime_address": START,
                "expected_size": END - START,
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            },
        )
        self.assertNotIn("profiles", patch)
        for target, replacement_hex, replacement_sha256 in (
            (
                APPLE_RUNTIME_ADDRESS,
                APPLE_REPLACEMENT,
                APPLE_REPLACEMENT_SHA256,
            ),
            (
                LINUX_RUNTIME_ADDRESS,
                LINUX_REPLACEMENT,
                LINUX_REPLACEMENT_SHA256,
            ),
        ):
            replacement = (
                self.apollo_overlay.encode_thumb_branch(
                    START,
                    target,
                    link=False,
                )
                + b"\x00\xbf" * 9
            )
            self.assertEqual(replacement.hex(), replacement_hex)
            self.assertEqual(
                hashlib.sha256(replacement).hexdigest(),
                replacement_sha256,
            )

    @_APPLE_ONLY
    def test_production_apple_placement_redirect_and_aggregate_are_exact(
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
                "padding_before": 2,
                "runtime_address": APPLE_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007B05C0",
                "size": 26,
            },
        )
        self.assertEqual(report_leaf["extraction"]["sha256"], TARGET_SHA256)
        self.assertEqual(
            report_leaf["extraction"]["unrelocated_sha256"],
            TARGET_SHA256,
        )
        self.assertEqual(report_leaf["extraction"]["relocation_count"], 0)

        overlay = (
            ROOT / self.production["overlay"]["artifact"]
        ).read_bytes()
        self.assertEqual(overlay[115_354:115_356], b"\x00\x00")
        self.assertEqual(
            overlay[APPLE_OFFSET:APPLE_OFFSET + 26].hex(),
            TARGET_BYTES,
        )
        patch = next(
            patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["target_function"] == FUNCTION
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(patch["payload_offset"], 121_578)
        self.assertEqual(patch["target_address"], APPLE_RUNTIME_ADDRESS)
        self.assertEqual(replacement.hex(), APPLE_REPLACEMENT)
        self.assertEqual(
            hashlib.sha256(replacement).hexdigest(),
            APPLE_REPLACEMENT_SHA256,
        )

        self.assertEqual(
            (
                self.production["overlay"]["size"],
                self.production["overlay"]["sha256"],
                len(self.production["overlay"]["functions"]),
                len(self.production["overlay"]["patched_sites"]),
            ),
            (
                143_227,
                (
                    "200b0b3385c26dbe93cfab37503d21f45d3a6a32ee2dd32451c1ce8c63308b10"
                ),
                786,
                727,
            ),
        )
        self.assertEqual(
            (
                self.production["component"]["size"],
                self.production["component"]["sha256"],
                self.production["component"][
                    "generated_patch_site_bytes"
                ],
                self.production["component"][
                    "replaced_stock_function_bytes"
                ],
                self.production["component"]["source_owned_bytes"],
                self.production["component"]["opaque_base_bytes"],
            ),
            (
                3_666_623,
                (
                    "ad895f785a66f249a9c4d45ea353b559acebf57ad8f82fedf43af2361e79e83b"
                ),
                99_192,
                99_370,
                143_409,
                3_423_990,
            ),
        )

    def test_manifest_split_appended_leaves_and_package_are_exact(
        self,
    ) -> None:
        manifest = json.loads(
            CORE_SOURCE_MANIFEST.read_text(encoding="utf-8")
        )
        self.assertEqual(
            {
                key: manifest["package"][key]
                for key in (
                    "expected_size",
                    "expected_sha256",
                    "profiles",
                )
            },
            {
                "expected_size": 4_445_117,
                "expected_sha256": (
                    "62569df0c68123922de03f482f0affae3975114186581dd30adce650d45f28f6"
                ),
                "profiles": {
                    "linux-clang": {
                        "expected_size": 4_446_156,
                        "expected_sha256": (
                            "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3"
                        ),
                    },
                },
            },
        )
        regions = manifest["component_overrides"]["apollo_main"][
            "regions"
        ]
        selected_names = {
            (
                "opaque_between_freertos_scheduler_state_and_"
                "task_priority_disinherit"
            ),
            "freertos_task_priority_disinherit_source_replacement",
            (
                "opaque_between_freertos_task_priority_disinherit_and_"
                "reset_event_item"
            ),
            "freertos_task_reset_event_item_value_source_replacement",
            (
                "freertos_task_increment_mutex_held_count_"
                "source_replacement"
            ),
            (
                "opaque_between_freertos_increment_mutex_held_count_"
                "and_task_notify_wait"
            ),
            "freertos_task_notify_wait_source_replacement",
            "freertos_task_notify_source_replacement",
            "opaque_between_freertos_task_notify_variants",
            "freertos_task_notify_from_isr_source_replacement",
            (
                "opaque_between_freertos_task_notify_from_isr_and_"
                "add_current_to_delayed_list"
            ),
            "freertos_task_add_current_to_delayed_list_source_replacement",
            (
                "opaque_between_freertos_add_current_to_delayed_list_"
                "and_list_initialise"
            ),
            (
                "apollo_freertos_task_reset_event_item_value_"
                "source_leaf_alignment"
            ),
            "apollo_freertos_task_reset_event_item_value_source_leaf",
            (
                "apollo_freertos_task_increment_mutex_held_count_"
                "source_leaf_alignment"
            ),
            (
                "apollo_freertos_task_increment_mutex_held_count_"
                "source_leaf"
            ),
        }
        selected = {
            region["name"]: (
                region["file_offset"],
                region["size"],
                region["target_address"],
                region["address_status"],
            )
            for region in regions
            if region["name"] in selected_names
        }
        self.assertEqual(
            selected,
            {
                (
                    "opaque_between_freertos_scheduler_state_and_"
                    "task_priority_disinherit"
                ): (121_060, 170, 0x0045_58C4, "official_blob"),
                "freertos_task_priority_disinherit_source_replacement": (
                    121_230,
                    164,
                    0x0045_596E,
                    "generated_source_entry_replacement",
                ),
                (
                    "opaque_between_freertos_task_priority_disinherit_"
                    "and_reset_event_item"
                ): (121_394, 184, 0x0045_5A12, "official_blob"),
                (
                    "freertos_task_reset_event_item_value_"
                    "source_replacement"
                ): (
                    121_578,
                    22,
                    START,
                    "generated_source_entry_replacement",
                ),
                (
                    "freertos_task_increment_mutex_held_count_"
                    "source_replacement"
                ): (
                    121_600,
                    22,
                    END,
                    "generated_source_entry_replacement",
                ),
                (
                    "opaque_between_freertos_increment_mutex_held_count_"
                    "and_task_notify_wait"
                ): (121_622, 142, 0x0045_5AF6, "official_blob"),
                "freertos_task_notify_wait_source_replacement": (
                    121_764,
                    196,
                    0x0045_5B84,
                    "generated_source_entry_replacement",
                ),
                "freertos_task_notify_source_replacement": (
                    121_960,
                    368,
                    0x0045_5C48,
                    "generated_source_entry_replacement",
                ),
                "opaque_between_freertos_task_notify_variants": (
                    122_328,
                    8,
                    0x0045_5DB8,
                    "official_blob",
                ),
                "freertos_task_notify_from_isr_source_replacement": (
                    122_336,
                    412,
                    0x0045_5DC0,
                    "generated_source_entry_replacement",
                ),
                (
                    "opaque_between_freertos_task_notify_from_isr_and_"
                    "add_current_to_delayed_list"
                ): (122_748, 76, 0x0045_5F5C, "official_blob"),
                (
                    "freertos_task_add_current_to_delayed_list_"
                    "source_replacement"
                ): (
                    122_824,
                    118,
                    0x0045_5FA8,
                    "generated_source_entry_replacement",
                ),
                (
                    "opaque_between_freertos_add_current_to_delayed_"
                    "list_and_list_initialise"
                ): (122_942, 94, 0x0045_601E, "official_blob"),
                (
                    "apollo_freertos_task_reset_event_item_value_"
                    "source_leaf_alignment"
                ): (3_638_750, 2, 0x007B_05BE, "generated_alignment"),
                (
                    "apollo_freertos_task_reset_event_item_value_"
                    "source_leaf"
                ): (3_638_752, 26, APPLE_RUNTIME_ADDRESS, "source_compiled"),
                (
                    "apollo_freertos_task_increment_mutex_held_count_"
                    "source_leaf_alignment"
                ): (3_638_778, 2, 0x007B_05DA, "generated_alignment"),
                (
                    "apollo_freertos_task_increment_mutex_held_count_"
                    "source_leaf"
                ): (3_638_780, 24, 0x007B_05DC, "source_compiled"),
            },
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
