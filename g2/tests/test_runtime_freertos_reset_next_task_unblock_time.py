from __future__ import annotations

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
    / "runtime_freertos_reset_next_task_unblock_time.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_reset_next_task_unblock_time_host.c"
)
AUDIT = (
    ROOT
    / "docs"
    / "research"
    / "freertos-reset-next-task-unblock-time-source-boundary-audit.md"
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

SOURCE_SIZE = 2_544
SOURCE_SHA256 = (
    "afaf50d27bf7fc9a106e15b9318d36f0"
    "afa6ff6ba35619269297f41e3ce867b8"
)
HEADER_SIZE = 4_721
HEADER_SHA256 = (
    "33d825bc20a59592935908a88a061062"
    "707fc5e81590f077a7adb2324ef07073"
)
HOST_FIXTURE_SIZE = 7_792
HOST_FIXTURE_SHA256 = (
    "c9ae51f8a9be9850dc8e00ebe3b23ffc"
    "fe0aaea0292aef23e77936b3be061d47"
)

BASE = 0x00438000
START = 0x00455876
END = 0x0045589C
STOCK_BYTES = (
    "dff8d81708680068002805d15ff0ff30"
    "dff8d817086005e00868c0680068dff8"
    "c81708607047"
)
STOCK_SHA256 = (
    "a789916ee424c824c5c5f2302e62e4a"
    "861f0fa1289917d9c0e095947bce82598"
)
DELAYED_LIST_LITERAL = 0x00456050
DELAYED_LIST_WORD = 0x20074A24
NEXT_UNBLOCK_LITERAL = 0x00456060
NEXT_UNBLOCK_WORD = 0x20074A50

CALLERS = [
    (0x00454B0A, "00f0b4fe"),
    (0x00454EBE, "00f0dafc"),
    (0x0045509A, "00f0ecfb"),
    (0x00455420, "00f029fa"),
    (0x004554D0, "00f0d1f9"),
    (0x00455D9A, "fff76cfd"),
]
CALLER_ADDRESS_SHA256 = (
    "e849e824765de1654a2c5cca71758a37"
    "bce2729459dc5f3b7cb71b9854082c56"
)
CALLER_RECORD_SHA256 = (
    "012189a12f316609470b8801612f6365"
    "db31ce8510ec46a218c3044a02a86fd3"
)
CALLER_SPANS = {
    (0x00454AAE, 0x00454B4C): (
        158,
        "fed4eb28935bf7034f3f1893518e7de0"
        "56995a5083d42863ab007e9e74de2597",
    ),
    (0x00454DCC, 0x00454EFE): (
        306,
        "548e05e1f8a2f498372dd1f4eb7c6536"
        "e093dbbfdb82fbe8f9b54231cedc8a09",
    ),
    (0x0045504C, 0x0045519E): (
        338,
        "438ad4e9e1a7b439671463b2bbfd13616"
        "ebb6de32bd2aad53b802d31f11cc050",
    ),
    (0x00455370, 0x00455466): (
        246,
        "1a5d4850f0799e97548f23ee1617fc1d"
        "e362f8d2a674301baa6facd579d13de4",
    ),
    (0x0045547C, 0x00455556): (
        218,
        "aa14475cf28218296c4fd829c02080fc0"
        "17a5fe137f476de47e747f1e920e33b",
    ),
    (0x00455C48, 0x00455DB8): (
        368,
        "fbcc2f27349099a2dc37ef103fc959730"
        "f14c6e0ef387507cbcba22fd3fc0a63",
    ),
}

FUNCTION = "open_cfw_freertos_task_reset_next_task_unblock_time"
TARGET_BYTES = (
    "44f62420c2f207000168096821b10168"
    "c9680968c16270474ff0ff31c1627047"
)
TARGET_SHA256 = (
    "249e6dafc8adc7286fbf5b96db744f90"
    "2a04c7a38709a4344f766e01ec264a5f"
)
TARGET_PROFILES = {
    "apple-clang": {
        "version_prefix": "Apple clang version 21.0.0",
        "bytes": TARGET_BYTES,
        "sha256": TARGET_SHA256,
        "relocations": [],
    },
    "linux-clang": {
        "version_prefix": "Homebrew clang version 22.1.8",
        "bytes": TARGET_BYTES,
        "sha256": TARGET_SHA256,
        "relocations": [],
    },
}
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

EVENT_LIST_LOAD = 1
EVENT_COUNT_READ = 2
EVENT_HEAD_VALUE_READ = 3
EVENT_TIME_STORE = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


class RuntimeFreeRTOSResetNextTaskUnblockTimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.profile_name = os.environ.get(
            "OPENCFW_TOOLCHAIN_PROFILE",
            "apple-clang",
        )
        if cls.profile_name not in TARGET_PROFILES:
            raise AssertionError(
                f"unreviewed toolchain profile {cls.profile_name!r}"
            )
        cls.profile = TARGET_PROFILES[cls.profile_name]
        version = subprocess.run(
            [clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if not version.startswith(str(cls.profile["version_prefix"])):
            raise AssertionError(
                f"compiler does not match {cls.profile_name}: {version!r}"
            )

        library = temporary / library_name("runtime_freertos_reset_unblock")
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
        cls.configure = cls.loaded.open_cfw_test_reset_unblock_configure
        cls.configure.argtypes = [ctypes.c_uint32] * 9
        cls.configure.restype = None
        cls.invoke = cls.loaded.open_cfw_test_reset_unblock_invoke
        cls.invoke.argtypes = []
        cls.invoke.restype = None
        cls.time = cls.loaded.open_cfw_test_reset_unblock_time
        cls.time.argtypes = []
        cls.time.restype = ctypes.c_uint32
        cls.load_count = cls.loaded.open_cfw_test_reset_unblock_load_count
        cls.load_count.argtypes = []
        cls.load_count.restype = ctypes.c_uint32
        cls.event_count = cls.loaded.open_cfw_test_reset_unblock_event_count
        cls.event_count.argtypes = []
        cls.event_count.restype = ctypes.c_uint32
        cls.event_kind = cls.loaded.open_cfw_test_reset_unblock_event_kind
        cls.event_kind.argtypes = [ctypes.c_uint32]
        cls.event_kind.restype = ctypes.c_uint32
        cls.event_subject = (
            cls.loaded.open_cfw_test_reset_unblock_event_subject
        )
        cls.event_subject.argtypes = [ctypes.c_uint32]
        cls.event_subject.restype = ctypes.c_uint32
        cls.event_value = cls.loaded.open_cfw_test_reset_unblock_event_value
        cls.event_value.argtypes = [ctypes.c_uint32]
        cls.event_value.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_freertos_reset_unblock.o"
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

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[32:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    @classmethod
    def events(cls) -> list[tuple[int, int, int]]:
        return [
            (
                cls.event_kind(index),
                cls.event_subject(index),
                cls.event_value(index),
            )
            for index in range(cls.event_count())
        ]

    def test_authenticated_upstream_and_candidate_files_are_pinned(
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
            """static void prvResetNextTaskUnblockTime( void )
{
    if( listLIST_IS_EMPTY( pxDelayedTaskList ) != pdFALSE )
    {
        /* The new current delayed list is empty.  Set xNextTaskUnblockTime to
         * the maximum possible value so it is  extremely unlikely that the
         * if( xTickCount >= xNextTaskUnblockTime ) test will pass until
         * there is an item in the delayed list. */
        xNextTaskUnblockTime = portMAX_DELAY;
    }
    else
    {
        /* The new current delayed list is not empty, get the value of
         * the item at the head of the delayed list.  This is the time at
         * which the task at the head of the delayed list should be removed
         * from the Blocked state. */
        xNextTaskUnblockTime = listGET_ITEM_VALUE_OF_HEAD_ENTRY( pxDelayedTaskList );
    }
}""",
            upstream,
        )
        self.assertIn(
            "static List_t * volatile pxDelayedTaskList;",
            upstream,
        )
        self.assertIn(
            "static volatile TickType_t xNextTaskUnblockTime",
            upstream,
        )
        unordered_start = upstream.index(
            "void vTaskRemoveFromUnorderedEventList("
        )
        public_timeout_start = upstream.index(
            "void vTaskSetTimeOutState("
        )
        unordered_source = upstream[
            unordered_start:public_timeout_start
        ]
        self.assertIn("prvResetNextTaskUnblockTime();", unordered_source)
        self.assertIn(
            "listSET_LIST_ITEM_VALUE( pxEventListItem, "
            "xItemValue | taskEVENT_LIST_ITEM_VALUE_IN_USE );",
            unordered_source,
        )

        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE)), (
            SOURCE_SIZE,
            SOURCE_SHA256,
        ))
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER)), (
            HEADER_SIZE,
            HEADER_SHA256,
        ))
        self.assertEqual(
            (HOST_FIXTURE.stat().st_size, sha256(HOST_FIXTURE)),
            (HOST_FIXTURE_SIZE, HOST_FIXTURE_SHA256),
        )
        self.assertTrue(AUDIT.is_file())

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "prvResetNextTaskUnblockTime()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00455876, 0x0045589C)",
            "OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_LOAD()",
            "OPEN_CFW_FREERTOS_DELAYED_LIST_COUNT_READ(delayed_list)",
            "OPEN_CFW_FREERTOS_DELAYED_LIST_HEAD_VALUE_READ(delayed_list)",
            "OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_STORE",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_DELAYED_TASK_LIST_ADDRESS = 0x20074A24U",
            "OPEN_CFW_FREERTOS_NEXT_TASK_UNBLOCK_TIME_ADDRESS = 0x20074A50U",
            "OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_ITEM_SIZE = 0x14U",
            "OPEN_CFW_FREERTOS_RESET_UNBLOCK_MINI_ITEM_SIZE = 0x0CU",
            "OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_SIZE = 0x14U",
            "OPEN_CFW_FREERTOS_RESET_UNBLOCK_LIST_END_NEXT_OFFSET = 0x0CU",
        ):
            self.assertIn(token, header)

    def test_official_body_globals_list_abi_and_neighbors_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(
            hashlib.sha256(self.application).hexdigest(),
            "19044a72bdfeb04c6b1b104d87da7b98"
            "e13cc18928528d84d999b6bcc0ba9701",
        )
        body = self.span(START, END)
        self.assertEqual((len(body), body.hex()), (38, STOCK_BYTES))
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)

        def literal_target(address: int, encoded: bytes) -> tuple[int, int]:
            first, second = struct.unpack("<HH", encoded)
            self.assertEqual(first, 0xF8DF)
            return (
                second >> 12,
                ((address + 4) & ~3) + (second & 0x0FFF),
            )

        self.assertEqual(
            literal_target(START, body[0:4]),
            (1, DELAYED_LIST_LITERAL),
        )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(DELAYED_LIST_LITERAL, DELAYED_LIST_LITERAL + 4),
            )[0],
            DELAYED_LIST_WORD,
        )
        for address, encoded in (
            (START + 0x10, body[0x10:0x14]),
            (START + 0x1E, body[0x1E:0x22]),
        ):
            self.assertEqual(
                literal_target(address, encoded),
                (1, NEXT_UNBLOCK_LITERAL),
            )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(NEXT_UNBLOCK_LITERAL, NEXT_UNBLOCK_LITERAL + 4),
            )[0],
            NEXT_UNBLOCK_WORD,
        )

        self.assertEqual(body[4:10].hex(), "086800680028")
        self.assertEqual(body[24:30].hex(), "0868c0680068")
        self.assertEqual(body[-4:].hex(), "08607047")
        self.assertEqual(
            (
                len(self.span(0x00455836, START)),
                hashlib.sha256(
                    self.span(0x00455836, START)
                ).hexdigest(),
            ),
            (
                64,
                "86f7fc5725fe0fbbe85c07f68669981b"
                "ad154cd58163427a6ead8106538e2a12",
            ),
        )
        following = self.span(END, 0x004558A4)
        self.assertEqual(following.hex(), "dff8bc0700687047")
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "c7437c4b802c4991fe9a7bda7e790a1"
            "e252276812c72d57ef2b0db2cc18ac661",
        )

    def test_empty_list_reads_once_and_writes_port_max_delay(self) -> None:
        self.configure(
            0,
            0x11111111,
            7,
            0x22222222,
            9,
            0x33333333,
            0,
            1,
            0x13579BDF,
        )
        self.invoke()
        self.assertEqual(self.time(), 0xFFFFFFFF)
        self.assertEqual(self.load_count(), 1)
        self.assertEqual(
            self.events(),
            [
                (EVENT_LIST_LOAD, 0, 0),
                (EVENT_COUNT_READ, 0, 0),
                (EVENT_TIME_STORE, 0xFFFFFFFF, 0xFFFFFFFF),
            ],
        )

    def test_nonempty_list_reloads_pointer_before_head_value(self) -> None:
        self.configure(
            1,
            0x11111111,
            0,
            0x89ABCDEF,
            3,
            0x33333333,
            0,
            1,
            0x13579BDF,
        )
        self.invoke()
        self.assertEqual(self.time(), 0x89ABCDEF)
        self.assertEqual(self.load_count(), 2)
        self.assertEqual(
            self.events(),
            [
                (EVENT_LIST_LOAD, 0, 0),
                (EVENT_COUNT_READ, 0, 1),
                (EVENT_LIST_LOAD, 1, 1),
                (EVENT_HEAD_VALUE_READ, 1, 0x89ABCDEF),
                (EVENT_TIME_STORE, 0xFFFFFFFF, 0x89ABCDEF),
            ],
        )

    def test_nonzero_count_and_full_tick_range_are_preserved(self) -> None:
        for count, value in (
            (0xFFFFFFFF, 0),
            (2, 0x7FFFFFFF),
            (1, 0xFFFFFFFF),
        ):
            with self.subTest(count=count, value=value):
                self.configure(
                    count,
                    value,
                    count,
                    value,
                    count,
                    value,
                    2,
                    2,
                    value ^ 0xFFFFFFFF,
                )
                self.invoke()
                self.assertEqual(self.time(), value)
                self.assertEqual(self.load_count(), 2)

    def test_target_profiles_emit_one_relocation_free_32_byte_leaf(
        self,
    ) -> None:
        leaf, report = self.apollo_overlay.extract_isolated_function_section(
            self.target_object,
            FUNCTION,
        )
        self.assertEqual(report, {
            "function": FUNCTION,
            "section": f".text.{FUNCTION}",
            "size": 32,
            "sha256": str(self.profile["sha256"]),
            "alignment": 4,
            "relocation_count": 0,
            "discarded_alloc_section_count": 1,
            "discarded_alloc_section_bytes": 8,
            "discarded_alloc_sections": [
                {
                    "name": f".ARM.exidx.text.{FUNCTION}",
                    "size": 8,
                    "flags": 130,
                }
            ],
        })
        self.assertEqual(leaf.hex(), self.profile["bytes"])
        self.assertEqual(hashlib.sha256(leaf).hexdigest(), TARGET_SHA256)
        self.assertEqual(self.profile["relocations"], [])

        data, sections = self.apollo_overlay.parse_elf32(self.target_object)
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        self.assertEqual(
            {
                symbol["name"]
                for symbol in symbols
                if (
                    symbol["name"]
                    and int(symbol["type"]) == 2
                    and int(symbol["section_index"]) != 0
                )
            },
            {FUNCTION},
        )
        self.assertEqual(
            {
                symbol["name"]
                for symbol in symbols
                if symbol["name"] and int(symbol["section_index"]) == 0
            },
            set(),
        )
        writable = [
            section["name"]
            for section in sections
            if (
                int(section["flags"]) & 0x3 == 0x3
                and int(section["size"]) != 0
            )
        ]
        self.assertEqual(writable, [])

    def test_official_topology_has_six_callers_and_no_bypass(self) -> None:
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
        self.assertEqual(
            [call for call in calls if call[0] == 0x004554D0],
            [(0x004554D0, "00f0d1f9")],
        )
        unordered_event_remove = self.span(0x0045547C, 0x00455556)
        self.assertEqual(len(unordered_event_remove), 218)
        self.assertEqual(
            hashlib.sha256(unordered_event_remove).hexdigest(),
            "aa14475cf28218296c4fd829c02080fc0"
            "17a5fe137f476de47e747f1e920e33b",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(exterior_interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in calls
                )
            ).hexdigest(),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address) + bytes.fromhex(encoded)
                    for address, encoded in calls
                )
            ).hexdigest(),
            CALLER_RECORD_SHA256,
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

        for (start, end), (size, digest) in CALLER_SPANS.items():
            caller = self.span(start, end)
            self.assertEqual(len(caller), size)
            self.assertEqual(hashlib.sha256(caller).hexdigest(), digest)

    def test_source_is_registered_in_production_inputs(self) -> None:
        overlay = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        manifest = json.loads(
            CORE_SOURCE_MANIFEST.read_text(encoding="utf-8")
        )
        overlay_text = json.dumps(overlay, sort_keys=True)
        manifest_text = json.dumps(manifest, sort_keys=True)
        for token in (FUNCTION, SOURCE.name):
            self.assertIn(token, overlay_text)
        for token in (
            "freertos_task_reset_next_task_unblock_time_source_replacement",
            "apollo_freertos_task_reset_next_task_unblock_time_source_leaf",
        ):
            self.assertIn(token, manifest_text)

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
