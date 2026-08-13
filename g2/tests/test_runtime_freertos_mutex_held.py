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
    / "runtime_freertos_mutex_held.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_mutex_held_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_QUEUE = ROOT / "third_party" / "freertos-kernel" / "queue.c"
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
    "eeb844aa15cdee6d110c61b8cce59cff"
    "48a947605bffd72c035bf9c1dc06a55a"
)
HEADER_SHA256 = (
    "d0594f514a5617925b76266380328793"
    "29187491ebe2aa91f7a76e2694624a6c"
)
HOST_FIXTURE_SHA256 = (
    "556506e76c5a1d74406feb5ceb0fa3a9"
    "c68db643358df43c51ed14040561628b"
)

BASE = 0x00438000
START = 0x00455AE0
END = 0x00455AF6
STOCK_BYTES = "dff878150868002803d00868426e521c426608687047"
STOCK_SHA256 = (
    "3cca7b821687976e59eccd737dc20b206"
    "4b86d66195c6f60f6a7cc2353f40d2f"
)
CURRENT_TCB_LITERAL = 0x0045605C
CURRENT_TCB_WORD = 0x20074A20
MUTEXES_HELD_OFFSET = 0x64
CALLERS = [(0x00441D46, "13f0cbfe")]
CALLER_START = 0x00441C44
CALLER_END = 0x00441DA6

FUNCTION = "open_cfw_freertos_task_increment_mutex_held_count"
TARGET_BYTES = "44f62020c2f20700016819b101684a6e01324a6600687047"
TARGET_SHA256 = (
    "494b41afb48389988e2678920ae7e179"
    "6b41a3d568e5c01c35c12c48bf7b57bf"
)
APPLE_OFFSET = 115_384
LINUX_OFFSET = 117_216
APPLE_RUNTIME_ADDRESS = 0x007B_05DC
LINUX_RUNTIME_ADDRESS = 0x007B_0D04
APPLE_REPLACEMENT = "5af37cbd" + "00bf" * 9
APPLE_REPLACEMENT_SHA256 = (
    "43481c385f5503febe82250a58b59e03"
    "44cfe8dda7eea05cb7b345d259c792c6"
)
LINUX_REPLACEMENT = "5bf310b9" + "00bf" * 9
LINUX_REPLACEMENT_SHA256 = (
    "62769495c0b1a1e09ba7e8fb6d6ac67"
    "0bce001c5ca5c8a5b46923a72ad686597"
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


class RuntimeFreeRTOSMutexHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        library = temporary / library_name("runtime_freertos_mutex_held")
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

        size_type = ctypes.c_size_t
        cls.reset = cls.loaded.open_cfw_test_mutex_held_reset
        cls.reset.argtypes = [size_type, size_type, size_type]
        cls.reset.restype = None
        cls.set_count = cls.loaded.open_cfw_test_mutex_held_set
        cls.set_count.argtypes = [size_type, ctypes.c_uint32]
        cls.set_count.restype = None
        cls.invoke = cls.loaded.open_cfw_test_mutex_held_invoke
        cls.invoke.argtypes = []
        cls.invoke.restype = size_type
        cls.get_count = cls.loaded.open_cfw_test_mutex_held_get
        cls.get_count.argtypes = [size_type]
        cls.get_count.restype = ctypes.c_uint32

        for name in (
            "current_reads",
            "count_reads",
            "count_writes",
            "increments",
            "invalid_identities",
        ):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_mutex_held_{name}",
            )
            function.argtypes = []
            function.restype = ctypes.c_uint32
            setattr(cls, name, function)
        cls.owner = cls.loaded.open_cfw_test_mutex_held_owner
        cls.owner.argtypes = []
        cls.owner.restype = size_type

        cls.target_object = temporary / "runtime_freertos_mutex_held.o"
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

    def test_authenticated_upstream_source_and_local_files_are_pinned(
        self,
    ) -> None:
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            sha256(UPSTREAM_TASKS),
            "14020d617b96dd2814e1211f6e3b645b"
            "cf5e2bd3179c23fe7dd16bc666fe9463",
        )
        self.assertEqual(
            sha256(UPSTREAM_QUEUE),
            "5cdf4fa35fe059446effff5bf20deaf83"
            "ddffb08921bc198fda106b1d17dd894",
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
            """#if ( configUSE_MUTEXES == 1 )

    TaskHandle_t pvTaskIncrementMutexHeldCount( void )
    {
        /* If xSemaphoreCreateMutex() is called before any tasks have been created
         * then pxCurrentTCB will be NULL. */
        if( pxCurrentTCB != NULL )
        {
            ( pxCurrentTCB->uxMutexesHeld )++;
        }

        return pxCurrentTCB;
    }

#endif /* configUSE_MUTEXES */""",
            upstream,
        )
        queue = UPSTREAM_QUEUE.read_text(encoding="utf-8")
        self.assertIn(
            "pxQueue->u.xSemaphore.xMutexHolder = "
            "pvTaskIncrementMutexHeldCount();",
            queue,
        )

        self.assertEqual(SOURCE.stat().st_size, 2_342)
        self.assertEqual(HEADER.stat().st_size, 1_709)
        self.assertEqual(HOST_FIXTURE.stat().st_size, 4_878)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(sha256(HOST_FIXTURE), HOST_FIXTURE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "pvTaskIncrementMutexHeldCount()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00455AE0, 0x00455AF6)",
            "configUSE_MUTEXES=1",
            "OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_READ()",
            "OPEN_CFW_FREERTOS_MUTEX_HELD_INCREMENT(current_tcb)",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_MUTEX_HELD_CURRENT_TCB_ADDRESS = "
            "0x20074A20U",
            "OPEN_CFW_FREERTOS_MUTEX_HELD_COUNT_OFFSET = 0x64U",
            "OPEN_CFW_FREERTOS_MUTEX_HELD_CONFIG_USE_MUTEXES = 1",
            "volatile open_cfw_freertos_mutex_held_uintptr",
            "OPEN_CFW_FREERTOS_MUTEX_HELD_COUNT(tcb)++",
        ):
            self.assertIn(token, header)

    def test_official_body_neighbors_and_ram_seam_are_exact(self) -> None:
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
        self.assertEqual(
            hashlib.sha256(self.span(0x00455ACA, START)).hexdigest(),
            "76463ec53fbc06884c159bf5b7d01708"
            "c06e404e9b51bdcaab307b219179c049",
        )
        self.assertEqual(self.span(END, END + 2), b"\x00\x00")

        first, second = struct.unpack_from("<HH", body)
        self.assertEqual(first, 0xF8DF)
        self.assertEqual(second >> 12, 1)
        self.assertEqual(second & 0x0FFF, 0x578)
        pc = (START + 4) & ~3
        self.assertEqual(pc + (second & 0x0FFF), CURRENT_TCB_LITERAL)
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(CURRENT_TCB_LITERAL, CURRENT_TCB_LITERAL + 4),
            )[0],
            CURRENT_TCB_WORD,
        )
        self.assertEqual(
            body[4:].hex(),
            "0868002803d00868426e521c426608687047",
        )

    def test_host_null_path_reads_current_twice_without_tcb_access(
        self,
    ) -> None:
        returned = 0x20002000
        unused = 0x20003000
        self.reset(0, returned, unused)
        self.set_count(returned, 0x12345678)

        self.assertEqual(self.invoke(), returned)
        self.assertEqual(self.current_reads(), 2)
        self.assertEqual(self.count_reads(), 0)
        self.assertEqual(self.count_writes(), 0)
        self.assertEqual(self.increments(), 0)
        self.assertEqual(self.owner(), 0)
        self.assertEqual(self.get_count(returned), 0x12345678)
        self.assertEqual(self.invalid_identities(), 0)

    def test_host_nonnull_path_uses_second_owner_and_returns_third(
        self,
    ) -> None:
        decision_owner = 0x20001000
        increment_owner = 0x20002000
        returned_owner = 0x20003000
        self.reset(decision_owner, increment_owner, returned_owner)
        self.set_count(decision_owner, 7)
        self.set_count(increment_owner, 0xFFFFFFFF)
        self.set_count(returned_owner, 19)

        self.assertEqual(self.invoke(), returned_owner)
        self.assertEqual(self.current_reads(), 3)
        self.assertEqual(self.count_reads(), 1)
        self.assertEqual(self.count_writes(), 1)
        self.assertEqual(self.increments(), 1)
        self.assertEqual(self.owner(), increment_owner)
        self.assertEqual(self.get_count(decision_owner), 7)
        self.assertEqual(self.get_count(increment_owner), 0)
        self.assertEqual(self.get_count(returned_owner), 19)
        self.assertEqual(self.invalid_identities(), 0)

    def test_target_object_is_one_relocation_free_24_byte_leaf(self) -> None:
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
        self.assertEqual((int(function[1]), int(function[2])), (1, 24))
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
        self.assertEqual(
            [
                section["name"]
                for section in sections
                if (
                    int(section["type"]) == 9
                    and int(section["info"]) == int(function_section["index"])
                    and int(section["size"]) != 0
                )
            ],
            [],
        )
        for prefix in (".data", ".bss", ".rodata"):
            self.assertFalse(
                any(
                    section["name"].startswith(prefix)
                    and int(section["size"]) != 0
                    for section in sections
                )
            )

    def test_official_topology_has_one_queue_caller_and_no_bypass(
        self,
    ) -> None:
        calls = []
        jumps = []
        exterior_interior = []
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
                    exterior_interior.append(
                        (address, target, link, encoded.hex())
                    )
        self.assertEqual(calls, CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(exterior_interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in calls
                )
            ).hexdigest(),
            "42d0fa34f41d5e3fa202edaef73496d2"
            "5b6eb8e3d918bc2fc091a1ccf1c2a1a7",
        )

        narrow_exterior = []
        narrow_internal = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in self.narrow_branch_targets(address, halfword):
                if START <= target < END:
                    observed = (address, target, halfword)
                    if START <= address < END:
                        narrow_internal.append(observed)
                    else:
                        narrow_exterior.append(observed)
        self.assertEqual(narrow_exterior, [])
        self.assertEqual(
            narrow_internal,
            [(0x00455AE8, 0x00455AF2, 0xD003)],
        )

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            normalized = value & ~1 if value & 1 else value
            if START <= normalized < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        caller = self.span(CALLER_START, CALLER_END)
        self.assertEqual(len(caller), 354)
        self.assertEqual(
            hashlib.sha256(caller).hexdigest(),
            "4d112cee107085a6606d4704c6f9edb4"
            "83264086cc9f954991ac76818c08b34c",
        )
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                CALLERS[0][0],
                bytes.fromhex(CALLERS[0][1]),
                link=True,
            ),
            START,
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
                    "runtime_freertos_mutex_held.c"
                ),
                "size": 2_342,
                "sha256": SOURCE_SHA256,
                "license": "MIT",
                "origin": (
                    "source-equivalent adaptation of authenticated "
                    "FreeRTOS-Kernel V10.5.1 "
                    "pvTaskIncrementMutexHeldCount using the recovered "
                    "G2 TCB and pxCurrentTCB seams"
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
                    "freertos-mutex-held-source-boundary-audit.md"
                ),
            },
        )
        expected = {
            "size": 24,
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
            self.assertEqual(
                [
                    item["function"]
                    for item in filtered["relocated_leaves"]
                    if item["function"] in {
                        "open_cfw_freertos_task_missed_yield",
                        "open_cfw_freertos_task_reset_event_item_value",
                        "open_cfw_freertos_task_increment_mutex_held_count",
                    }
                ],
                [
                    "open_cfw_freertos_task_missed_yield",
                    (
                        "open_cfw_freertos_task_"
                        "reset_event_item_value"
                    ),
                    FUNCTION,
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
                    "replace_freertos_task_"
                    "increment_mutex_held_count"
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
                "runtime_address_hex": "0x007B05DC",
                "size": 24,
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
        self.assertEqual(overlay[115_382:115_384], b"\x00\x00")
        self.assertEqual(
            overlay[APPLE_OFFSET:APPLE_OFFSET + 24].hex(),
            TARGET_BYTES,
        )
        patch = next(
            patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["target_function"] == FUNCTION
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(patch["payload_offset"], 121_600)
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
                self.production["component"]["size"],
                self.production["component"]["sha256"],
            ),
            (
                142_578,
                (
                    "3d5c9fe87fd46cbc40bb5670653f45d3"
            "d61f9d777168aa47b70fb10712698ab4"
                ),
                615,
                578,
                3_665_974,
                (
                    "5cef32ba7350e7f6476336fa6a087010"
            "e6143e3e692205215c271430aa110d22"
                ),
            ),
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
