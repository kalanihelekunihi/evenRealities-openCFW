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
LINUX_EXACT_ROOT = Path("/Users/kalani/Repo/SybilSightABCD/openCFW")
LINUX_EXACT_CLANG = Path("/home/linuxbrew/.linuxbrew/bin/clang")
FREERTOS = ROOT / "components" / "shared" / "freertos"
SOURCE = FREERTOS / "runtime_freertos_queue_semaphore_take_upstream_candidate.c"
HEADER = SOURCE.with_suffix(".h")
HELPER_SOURCE = (
    FREERTOS
    / "runtime_freertos_queue_get_disinherit_priority_after_timeout.c"
)
HELPER_HEADER = HELPER_SOURCE.with_suffix(".h")
CANDIDATE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_queue_semaphore_take_upstream_candidate_host.c"
)
ORACLE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_queue_semaphore_take_upstream_oracle_host.c"
)
UPSTREAM_QUEUE = ROOT / "third_party" / "freertos-kernel" / "queue.c"
UPSTREAM_VERIFIER = ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
UPSTREAM_PROVENANCE = ROOT / "third_party" / "freertos-kernel" / "PROVENANCE.json"
FREERTOS_INCLUDE = ROOT / "third_party" / "freertos-kernel" / "include"
FREERTOS_PORT = (
    ROOT / "third_party" / "freertos-kernel" / "portable" / "IAR"
    / "ARM_CM55_NTZ" / "non_secure"
)
ORACLE_CONFIG_DIR = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "candidates"
    / "cmsis_freertos_constructors"
)
ORACLE_CONFIG = ORACLE_CONFIG_DIR / "FreeRTOSConfig.h"
ORACLE_PORT = ORACLE_CONFIG_DIR / "portmacro.h"
ORACLE_STRING = ORACLE_CONFIG_DIR / "string.h"
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
PRODUCTION_QUEUE = (
    ROOT / "components" / "apollo_main" / "core_overlay"
    / "runtime_freertos_queue.c"
)
CORE_SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

FILE_PINS = {
    SOURCE: (
        5_867,
        "7bc1adb794188c36fe0693ef4dcf0e45b83cb32ba523142ecb72e703d65979e2",
    ),
    HEADER: (
        10_052,
        "e570c374e46115987810cd958773292bc80a8ef98b5cb9503a51327ef15328fd",
    ),
    CANDIDATE_FIXTURE: (
        12_124,
        "f9d965e6a5a41f80ccfc68e447fb11d280244ee909d6034e0ee9afce7fc4ee1d",
    ),
    ORACLE_FIXTURE: (
        10_734,
        "a8cffb7a592b07ebe6e6aa931dd7e28dfc5497a5a6362450fcf254bed160a3ac",
    ),
    HELPER_SOURCE: (
        2_620,
        "37a4ea5a258befb3b607bf5b0c3e6f28b60ed11279b98e13910e0a125519db3a",
    ),
    HELPER_HEADER: (
        4_456,
        "cd97393461faefa962b91b286977226e1e7c3f1e3dc5a5167c415d5e33c5bd1f",
    ),
}
BOUNDARY_PINS = {
    UPSTREAM_QUEUE: (
        125_614,
        "5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894",
    ),
    UPSTREAM_VERIFIER: (
        19_109,
        "a140aca673c0516e2dd2d948bd9cdb673445729b7593c5e79a0f70e50dd04b1b",
    ),
    UPSTREAM_PROVENANCE: (
        13_785,
        "810d28df622a96646dd70d56311355c3531393fcf0fac1feac585f9cd799f99a",
    ),
    ORACLE_CONFIG: (
        5_184,
        "537e12cd879b06d7748f9b0e177f6ad0e17cd176405945771580e6d9c8312889",
    ),
    ORACLE_PORT: (
        910,
        "6e1ac1013191a6bd3e4924656a03a1515a1d5f06df83b8fbb9073a489961e675",
    ),
    ORACLE_STRING: (
        513,
        "1612795defaff20b3a0ad57b0106a1906a973d94557b2ac7c35d8d5307771f1d",
    ),
}

BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
APPLICATION_SHA256 = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
START = 0x0044_1C44
END = 0x0044_1DA6
STOCK_SHA256 = "4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c"
PREDECESSOR_START = 0x0044_1B0A
PREDECESSOR_SHA256 = "f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560"
SUCCESSOR_END = 0x0044_1E66
SUCCESSOR_SHA256 = "cd084580c8e0eededc50eef8fa544290e2c09df64d3ec1e1bf1bbe13bdeb25c4"
HELPER_START = 0x0044_1EC4
HELPER_END = 0x0044_1ED8
HELPER_STOCK_SHA256 = "21721e8f80852df9a1d4f0f23db76d3144a4c8c04a81606dccee5b3ff132819c"

CALLERS = [
    (0x0044_1780, "00f060fa"),
    (0x0044_9802, "f8f71ffa"),
    (0x0044_999E, "f8f751f9"),
    (0x0044_9DA0, "f7f750ff"),
    (0x0047_3842, "cef7fff9"),
    (0x0048_4196, "bdf755fd"),
    (0x0048_41F0, "bdf728fd"),
    (0x0048_4246, "bdf7fdfc"),
    (0x0048_42AE, "bdf7c9fc"),
    (0x0051_4014, "2df716fe"),
]
CALLER_ADDRESS_SHA256 = "f713585a87faff9b034d775b62f3e98cf2cc6f292bd6fa556731a37588effb91"
CALLER_RECORD_SHA256 = "d2fd8eb3089d8db9783c09630b6ed9505b361be17da450fdc3bda5c2b38e8e1b"
OUTGOING = [
    (0x0044_1C52, 0x005F_A0A4),
    (0x0044_1C66, 0x005F_A0A4),
    (0x0044_1C74, 0x0045_58A4),
    (0x0044_1C8E, 0x005F_A0A4),
    (0x0044_1C9E, 0x0044_1F88),
    (0x0044_1CA2, 0x0045_4DCC),
    (0x0044_1CA6, 0x0044_20D0),
    (0x0044_1CBC, 0x0045_5556),
    (0x0044_1CC2, 0x0044_20E8),
    (0x0044_1CC6, 0x0045_4D7C),
    (0x0044_1CCA, 0x0044_20D0),
    (0x0044_1CEE, 0x0044_20E8),
    (0x0044_1CF6, 0x0045_5566),
    (0x0044_1D00, 0x0044_1FF6),
    (0x0044_1D0E, 0x0044_20D0),
    (0x0044_1D14, 0x0045_58CC),
    (0x0044_1D1A, 0x0044_20E8),
    (0x0044_1D24, 0x0045_5282),
    (0x0044_1D2A, 0x0044_1F88),
    (0x0044_1D2E, 0x0045_4DCC),
    (0x0044_1D36, 0x0044_20BC),
    (0x0044_1D46, 0x0045_5AE0),
    (0x0044_1D56, 0x0045_5370),
    (0x0044_1D5E, 0x0044_20BC),
    (0x0044_1D62, 0x0044_20E8),
    (0x0044_1D6A, 0x0044_20E8),
    (0x0044_1D74, 0x0044_1F88),
    (0x0044_1D78, 0x0045_4DCC),
    (0x0044_1D7E, 0x0044_1FF6),
    (0x0044_1D8A, 0x0044_20D0),
    (0x0044_1D90, 0x0044_1EC4),
    (0x0044_1D98, 0x0045_5A1C),
    (0x0044_1D9C, 0x0044_20E8),
]
RAW_POINTER_HITS = [(0x005A_9FB5, 0x0044_1D43)]
RAW_POINTER_SHA256 = "55fca9e006b9d8ada8e1f9a1b64d3efadc2cc88e75ab9d40fbd875a8c7eb726c"
FALSE_POSITIVE_START = 0x005A_9F98
FALSE_POSITIVE_END = 0x005A_9FCA
FALSE_POSITIVE_SHA256 = "7c65189b672effd1b500b23b8d5b423bb446c504f2efdc269279959fdac332be"
FALSE_POSITIVE_FUNCTION_CALLERS = [
    (0x005A_6574, "03f010fd"),
    (0x005A_8C20, "01f0baf9"),
    (0x005A_A41E, "fff7bbfd"),
]

FUNCTION = "open_cfw_freertos_queue_semaphore_take_upstream_candidate"
FUNCTION_SECTION = ".text." + FUNCTION
HELPER_FUNCTION = "open_cfw_freertos_queue_get_disinherit_priority_after_timeout"
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]
TARGETS = {
    "apple-clang": {
        "size": 602,
        "alignment": 4,
        "section_sha256": "c5b343d383bd3fa14d706f23ae1b7b46114583f2310e1ad77cad53635bd4276b",
        "object_size": 1_732,
        "object_sha256": "826991c27dc3cf1cd674fac5fad81d94225e94d38ab15775ee7caa6eb2bfcb5a",
        "helper_object_size": 960,
        "helper_object_sha256": "6d95d3125054521d3366839e9c5011a215b6c36cfe2c89ea18542f1f396a1360",
        "helper_call_offset": 0x244,
    },
    "linux-clang": {
        "size": 600,
        "alignment": 4,
        "section_sha256": "e5021439d803107fff7701c5c335ca9d70297cedf3d4dfc2a88f1445c46ea619",
        "object_size": 1_708,
        "object_sha256": "97a32188abc9977e40a403d709679351c70ec5e895488ccf3f94b39fb76d2f54",
        "helper_object_size": 940,
        "helper_object_sha256": "f48b96a42912c1cb07aed3097fce5eb0f79b065400212bb988ffeee89f1a1e50",
        "helper_call_offset": 0x242,
    },
}
HELPER_SECTION_SIZE = 18
HELPER_SECTION_SHA256 = "fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519"


def sha256(data: bytes | Path) -> str:
    if isinstance(data, Path):
        data = data.read_bytes()
    return hashlib.sha256(data).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def thumb_wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | (imm10 << 12) | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0x0F) < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    return ()


def thumb_wide_conditional_branch_target(
    address: int, first: int, second: int
) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    condition = (first >> 6) & 0x0F
    if condition >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        (sign << 20) | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18) | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 21
    return (address + 4 + immediate) & 0xFFFF_FFFF


class FreeRTOSQueueSemaphoreTakeUpstreamCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.compiler_version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout
        if cls.compiler_version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif cls.compiler_version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
            if Path(cls.clang) != LINUX_EXACT_CLANG:
                raise AssertionError(
                    f"Linux pins require {LINUX_EXACT_CLANG}, got {cls.clang}"
                )
            if ROOT != LINUX_EXACT_ROOT:
                raise AssertionError(
                    f"Linux pins require exact root {LINUX_EXACT_ROOT}, got {ROOT}"
                )
        else:
            raise AssertionError(f"unreviewed target compiler: {cls.compiler_version!r}")
        requested = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        if requested is not None and requested != cls.profile:
            raise AssertionError(f"profile/compiler mismatch: {requested!r} != {cls.profile!r}")

        cls.candidate = cls.compile_host(
            temporary / library_name("take-candidate"), CANDIDATE_FIXTURE, []
        )
        cls.oracle = cls.compile_host(
            temporary / library_name("take-oracle"),
            ORACLE_FIXTURE,
            [
                "-ffreestanding", "-fno-builtin", "-I", str(ORACLE_CONFIG_DIR),
                "-I", str(FREERTOS_INCLUDE), "-I", str(FREERTOS_PORT),
            ],
        )
        for library in (cls.candidate, cls.oracle):
            cls.bind_host(library)

        cls.target_objects = [temporary / "take-1.o", temporary / "take-2.o"]
        cls.helper_objects = [temporary / "helper-1.o", temporary / "helper-2.o"]
        for output in cls.target_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                check=True, capture_output=True, text=True,
            )
        for output in cls.helper_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(HELPER_SOURCE), "-o", str(output)],
                check=True, capture_output=True, text=True,
            )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def compile_host(cls, output: Path, source: Path, extra: list[str]):
        command = [
            cls.clang, "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra",
            "-Werror", *extra, str(source),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(output)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(output))

    @staticmethod
    def bind_host(library) -> None:
        library.open_cfw_take_reset.argtypes = [ctypes.c_uint32] * 5
        library.open_cfw_take_configure.argtypes = [ctypes.c_uint32] * 7
        library.open_cfw_take_execute.argtypes = [ctypes.c_uint32]
        library.open_cfw_take_execute.restype = ctypes.c_int32
        for name in (
            "messages", "send_waiters", "receive_waiters", "check_calls",
            "disinherit_priority", "event_count",
        ):
            getattr(library, f"open_cfw_take_get_{name}").restype = ctypes.c_uint32
        for name in ("holder", "disinherit_holder"):
            getattr(library, f"open_cfw_take_get_{name}").restype = ctypes.c_size_t
        for name in ("receive_lock", "transmit_lock"):
            getattr(library, f"open_cfw_take_get_{name}").restype = ctypes.c_int32
        for name in ("event", "event_argument"):
            function = getattr(library, f"open_cfw_take_get_{name}")
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32

    @classmethod
    def run_case(cls, library, reset, configure, ticks):
        library.open_cfw_take_reset(*reset)
        library.open_cfw_take_configure(*configure)
        result = int(library.open_cfw_take_execute(ticks))
        count = int(library.open_cfw_take_get_event_count())
        return {
            "result": result,
            "messages": int(library.open_cfw_take_get_messages()),
            "send_waiters": int(library.open_cfw_take_get_send_waiters()),
            "receive_waiters": int(library.open_cfw_take_get_receive_waiters()),
            "holder": int(library.open_cfw_take_get_holder()),
            "receive_lock": int(library.open_cfw_take_get_receive_lock()),
            "transmit_lock": int(library.open_cfw_take_get_transmit_lock()),
            "check_calls": int(library.open_cfw_take_get_check_calls()),
            "disinherit_holder": int(library.open_cfw_take_get_disinherit_holder()),
            "disinherit_priority": int(library.open_cfw_take_get_disinherit_priority()),
            "events": [
                (
                    int(library.open_cfw_take_get_event(index)),
                    int(library.open_cfw_take_get_event_argument(index)),
                )
                for index in range(count)
            ],
        }

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    def test_authenticated_inputs_and_recovered_configuration_are_pinned(self) -> None:
        for path, (size, digest) in {**FILE_PINS, **BOUNDARY_PINS}.items():
            self.assertEqual(path.stat().st_size, size, path)
            self.assertEqual(sha256(path), digest, path)
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True, capture_output=True, text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)

        upstream = UPSTREAM_QUEUE.read_text(encoding="utf-8")
        for token in (
            "BaseType_t xQueueSemaphoreTake( QueueHandle_t xQueue,",
            "#define uxQueueType               pcHead",
            "#define queueQUEUE_IS_MUTEX       NULL",
            "xInheritanceOccurred = xTaskPriorityInherit",
            "uxHighestWaitingPriority = prvGetDisinheritPriorityAfterTimeout",
            "vTaskPriorityDisinheritAfterTimeout",
        ):
            self.assertIn(token, upstream)
        config = ORACLE_CONFIG.read_text(encoding="utf-8")
        for name, value in (
            ("configUSE_PREEMPTION", "1"),
            ("configUSE_MUTEXES", "1"),
            ("configUSE_TIMERS", "1"),
            ("configUSE_QUEUE_SETS", "0"),
            ("configMAX_PRIORITIES", "56"),
            ("INCLUDE_xTaskGetSchedulerState", "1"),
        ):
            self.assertRegex(
                config,
                rf"(?m)^#define\s+{name}\s+{value}\s*$",
            )

    def test_pristine_upstream_oracle_matches_all_semaphore_paths(self) -> None:
        cases = [
            ((2, 0, 2, 0, 0), (1, 2, 1, 2, 1, 1, 0), 0),
            ((1, 1, 0, 0, 0), (1, 1, 1, 1, 1, 0, 0), 0),
            ((0, 0, 0, 0, 0), (1, 0, 1, 0, 1, 0, 0), 0),
            ((0, 0, 0, 0, 0), (1, 0, 1, 0, 1, 0, 0), 11),
            ((0, 0, 0, 0, 0), (0, 2, 1, 2, 1, 0, 0), 13),
            ((0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0, 0), 23),
            ((0, 1, 0, 1, 6), (0, 0, 1, 0, 1, 0, 1), 29),
        ]
        for reset, configure, ticks in cases:
            with self.subTest(reset=reset, configure=configure, ticks=ticks):
                candidate = self.run_case(self.candidate, reset, configure, ticks)
                oracle = self.run_case(self.oracle, reset, configure, ticks)
                self.assertEqual(candidate, oracle)

        timeout = self.run_case(
            self.candidate,
            (0, 1, 0, 1, 6),
            (0, 0, 1, 0, 1, 0, 1),
            29,
        )
        self.assertEqual(timeout["result"], 0)
        self.assertEqual(timeout["check_calls"], 2)
        self.assertEqual(timeout["disinherit_holder"], 0x22222222)
        self.assertEqual(timeout["disinherit_priority"], 6)
        self.assertIn((12, 1), timeout["events"])
        self.assertIn((13, 6), timeout["events"])

    def test_official_body_neighbors_and_outgoing_call_topology_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(len(stock), 354)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        self.assertEqual(sha256(self.span(PREDECESSOR_START, START)), PREDECESSOR_SHA256)
        self.assertEqual(sha256(self.span(END, SUCCESSOR_END)), SUCCESSOR_SHA256)
        self.assertEqual(sha256(self.span(HELPER_START, HELPER_END)), HELPER_STOCK_SHA256)

        outgoing = []
        for offset in range(0, len(stock) - 3, 2):
            address = START + offset
            first, second = struct.unpack_from("<HH", stock, offset)
            target = thumb_wide_branch_target(address, first, second, link=True)
            if target is not None and not START <= target < END:
                outgoing.append((address, target))
        self.assertEqual(outgoing, OUTGOING)
        self.assertIn((0x0044_1D90, HELPER_START), outgoing)

    def test_all_entry_callers_and_external_interior_branches_are_closed(self) -> None:
        observed_callers = []
        entry_bw = []
        external_interior = []
        wide_conditional = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            encoded = self.application[offset:offset + 4].hex()
            for link in (True, False):
                target = thumb_wide_branch_target(address, first, second, link=link)
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    (observed_callers if link else entry_bw).append((address, encoded))
                elif not START <= address < END:
                    external_interior.append((address, target, encoded))
            target = thumb_wide_conditional_branch_target(address, first, second)
            if target is not None and START <= target < END and not START <= address < END:
                wide_conditional.append((address, target, encoded))
        external_narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if START <= target < END and not START <= address < END:
                    external_narrow.append((address, target, halfword))
        self.assertEqual(observed_callers, CALLERS)
        self.assertEqual(entry_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(wide_conditional, [])
        self.assertEqual(external_narrow, [])
        self.assertEqual(
            sha256(b"".join(struct.pack("<I", address) for address, _ in CALLERS)),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            sha256(b"".join(
                struct.pack("<I", address) + bytes.fromhex(encoded)
                for address, encoded in CALLERS
            )),
            CALLER_RECORD_SHA256,
        )

    def test_unaligned_raw_collision_is_pinned_executable_code_not_pointer_data(self) -> None:
        raw_hits = []
        halfword_hits = []
        word_hits = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                raw_hits.append((BASE + offset, value))
                if offset % 2 == 0:
                    halfword_hits.append((BASE + offset, value))
                if offset % 4 == 0:
                    word_hits.append((BASE + offset, value))
        self.assertEqual(raw_hits, RAW_POINTER_HITS)
        self.assertEqual(halfword_hits, [])
        self.assertEqual(word_hits, [])
        self.assertEqual(
            sha256(b"".join(struct.pack("<II", *record) for record in raw_hits)),
            RAW_POINTER_SHA256,
        )
        context = self.span(FALSE_POSITIVE_START, FALSE_POSITIVE_END)
        self.assertEqual(len(context), 50)
        self.assertEqual(sha256(context), FALSE_POSITIVE_SHA256)
        self.assertEqual(self.span(0x005A_9FB4, 0x005A_9FB6).hex(), "4543")
        self.assertEqual(self.span(0x005A_9FB6, 0x005A_9FB8).hex(), "1d44")
        self.assertEqual(self.span(0x005A_9FB8, 0x005A_9FBA).hex(), "0029")
        self.assertEqual(
            struct.unpack_from("<I", self.application, 0x005A_9FB5 - BASE)[0],
            0x0044_1D43,
        )
        executable_callers = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            if thumb_wide_branch_target(
                address, first, second, link=True
            ) == FALSE_POSITIVE_START:
                executable_callers.append((
                    address,
                    self.application[offset:offset + 4].hex(),
                ))
        self.assertEqual(executable_callers, FALSE_POSITIVE_FUNCTION_CALLERS)

    def test_target_objects_pin_both_profiles_and_close_with_helper(self) -> None:
        expected = TARGETS[self.profile]
        self.assertEqual(self.target_objects[0].read_bytes(), self.target_objects[1].read_bytes())
        self.assertEqual(self.helper_objects[0].read_bytes(), self.helper_objects[1].read_bytes())
        for output in self.target_objects:
            self.assertEqual(output.stat().st_size, expected["object_size"])
            self.assertEqual(sha256(output), expected["object_sha256"])
            data, sections = self.apollo_overlay.parse_elf32(output)
            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            symbol = next(item for item in symbols if item["name"] == FUNCTION)
            section = sections[int(symbol["section_index"])]
            body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            self.assertEqual((int(symbol["value"]), int(symbol["size"])), (1, expected["size"]))
            self.assertEqual(int(section["alignment"]), expected["alignment"])
            self.assertEqual(sha256(body), expected["section_sha256"])
            parsed_symbols, relocations = self.parse_symbols_and_relocations(data, sections)
            self.assertEqual(
                [name for name, fields in parsed_symbols if name and fields[5] == 0],
                [HELPER_FUNCTION],
            )
            text_relocations = [item for item in relocations if item[0] == FUNCTION_SECTION]
            self.assertEqual(
                text_relocations,
                [(FUNCTION_SECTION, expected["helper_call_offset"], 10, HELPER_FUNCTION)],
            )
        for output in self.helper_objects:
            self.assertEqual(output.stat().st_size, expected["helper_object_size"])
            self.assertEqual(sha256(output), expected["helper_object_sha256"])
            data, sections = self.apollo_overlay.parse_elf32(output)
            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            symbol = next(item for item in symbols if item["name"] == HELPER_FUNCTION)
            section = sections[int(symbol["section_index"])]
            body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            self.assertEqual(int(symbol["size"]), HELPER_SECTION_SIZE)
            self.assertEqual(sha256(body), HELPER_SECTION_SHA256)
            parsed_symbols, relocations = self.parse_symbols_and_relocations(data, sections)
            self.assertEqual([name for name, fields in parsed_symbols if name and fields[5] == 0], [])
            self.assertFalse(any(item[0].startswith(".text") for item in relocations))

    def parse_symbols_and_relocations(self, data, sections):
        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symbol_table["offset"]) + index * 16
            )
            parsed_symbols.append((
                self.apollo_overlay.elf_string(strings, fields[0], "symbol"),
                fields,
            ))
        relocations = []
        for relocation_section in sections:
            if int(relocation_section["type"]) != 9:
                continue
            relocated = sections[int(relocation_section["info"])]
            for index in range(int(relocation_section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II", data,
                    int(relocation_section["offset"]) + index * 8,
                )
                relocations.append((
                    str(relocated["name"]), offset, information & 0xFF,
                    parsed_symbols[information >> 8][0],
                ))
        return parsed_symbols, relocations

    def test_qualified_pair_is_atomically_registered_for_production(self) -> None:
        config_text = OVERLAY_CONFIG.read_text(encoding="utf-8")
        relative_source = SOURCE.relative_to(ROOT).as_posix()
        config = json.loads(config_text)
        self.assertIn(FUNCTION, config["functions"])
        self.assertIn(HELPER_FUNCTION, config["functions"])
        self.assertNotIn(
            "open_cfw_freertos_queue_semaphore_take",
            config["functions"],
        )
        leaves = config["relocated_leaves"]
        helper_index = next(
            index for index, item in enumerate(leaves)
            if item["function"] == HELPER_FUNCTION
        )
        take_index = next(
            index for index, item in enumerate(leaves)
            if item["function"] == FUNCTION
        )
        self.assertLess(helper_index, take_index)
        self.assertEqual(leaves[take_index]["source"]["path"], relative_source)
        effective_take = leaves[take_index]
        if self.profile == "linux-clang":
            effective_take = {
                **effective_take,
                **effective_take["toolchain_profiles"][self.profile],
            }
        self.assertEqual(
            effective_take["relocations"],
            [{
                "offset": TARGETS[self.profile]["helper_call_offset"],
                "type": "R_ARM_THM_CALL",
                "symbol": HELPER_FUNCTION,
                "symbol_type": "STT_NOTYPE",
                "target_function": HELPER_FUNCTION,
            }],
        )
        patch = next(
            item for item in config["patch_sites"]
            if item["name"] == "replace_freertos_queue_semaphore_take"
        )
        self.assertEqual(patch["runtime_address"], START)
        self.assertEqual(patch["target_function"], FUNCTION)
        production = PRODUCTION_QUEUE.read_text(encoding="utf-8")
        self.assertIn(
            "#if defined(OPEN_CFW_FREERTOS_QUEUE_INCLUDE_LEGACY_SEMAPHORE_TAKE)",
            production,
        )
        self.assertIn("(__UINTPTR_TYPE__)0x00441C45U", production)
        manifest = json.loads(CORE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
        provider = manifest["component_overrides"]["apollo_main"]["provider"]
        self.assertEqual(provider["size"], 3_665_974)
        self.assertEqual(
            provider["sha256"],
            "5cef32ba7350e7f6476336fa6a087010"
            "e6143e3e692205215c271430aa110d22",
        )
        region = next(
            item for item in manifest["component_overrides"]["apollo_main"]["regions"]
            if item["name"] == "freertos_queue_semaphore_take_source_replacement"
        )
        self.assertEqual(region["target_address"], START)
        self.assertEqual(region["size"], END - START)


if __name__ == "__main__":
    unittest.main()
