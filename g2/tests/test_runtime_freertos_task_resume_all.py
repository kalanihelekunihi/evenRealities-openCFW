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
    ROOT / "components" / "shared" / "freertos"
    / "runtime_freertos_task_resume_all.c"
)
HEADER = SOURCE.with_suffix(".h")
CANDIDATE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_task_resume_all_host.c"
)
ORACLE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_task_resume_all_upstream_oracle_host.c"
)
TICK_ORACLE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_task_increment_tick_upstream_oracle_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_VERIFIER = ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
FREERTOS_INCLUDE = ROOT / "third_party" / "freertos-kernel" / "include"
FREERTOS_PORT = (
    ROOT / "third_party" / "freertos-kernel" / "portable" / "IAR"
    / "ARM_CM55_NTZ" / "non_secure"
)
FREERTOS_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "candidates"
    / "cmsis_freertos_constructors"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
CORE_SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

SOURCE_SIZE = 6_262
SOURCE_SHA256 = "455b29e4eaec27451ad5ed24953583291659201b7fbd2da5c330f6e9da081dd5"
HEADER_SIZE = 10_625
HEADER_SHA256 = "9eaadd2e390b7300e90140a1e114481eaac2135c9830d320a2a8653f213c1045"
CANDIDATE_FIXTURE_SIZE = 20_218
CANDIDATE_FIXTURE_SHA256 = "783030ea1fe57d39609511e4c27dda1dad4c83599ba52af0f081a121c30cf89e"
ORACLE_FIXTURE_SIZE = 6_366
ORACLE_FIXTURE_SHA256 = "ac3d0f00ed2ae54c4cf2726651b881758661037ffa8aff7b083386fc74ad2ff4"
TICK_ORACLE_FIXTURE_SHA256 = "432ad24d7bb999cdd4f785ad0ac90b2720717171475a6cd4f86fe6e4b0b30cdf"
UPSTREAM_TASKS_SHA256 = "14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463"

BASE = 0x00438000
START = 0x00454DCC
END = 0x00454EFE
STOCK_SHA256 = "548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09"
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

RAM_LITERALS = {
    0x00455468: 0x20074A58,
    0x004551A0: 0x20074A30,
    0x004551AC: 0x20074A38,
    0x004551B0: 0x2006A49C,
    0x004551A4: 0x20074A20,
    0x004557A8: 0x20073D24,
    0x00455A18: 0x20074A40,
    0x00455A14: 0x20074A44,
}
OUTGOING_CALLS = [
    (0x00454DDC, 0x005FA0A4),
    (0x00454DEA, 0x004420D0),
    (0x00454EBE, 0x00455876),
    (0x00454ECC, 0x0045504C),
    (0x00454EF2, 0x004420BC),
    (0x00454EF6, 0x004420E8),
]
CALLERS = [
    (0x004418D8, "13f078fa"),
    (0x00441936, "13f049fa"),
    (0x0044194A, "13f03ffa"),
    (0x00441B76, "13f029f9"),
    (0x00441BEC, "13f0eef8"),
    (0x00441C32, "13f0cbf8"),
    (0x00441CA2, "13f093f8"),
    (0x00441D2E, "13f04df8"),
    (0x00441D78, "13f028f8"),
    (0x00454B7A, "00f027f9"),
    (0x00454FCE, "fff7fdfe"),
    (0x00455600, "fff7e4fb"),
    (0x00455786, "fff721fb"),
    (0x004561E8, "fef7f0fd"),
    (0x0045627A, "fef7a7fd"),
    (0x0047E8AC, "d6f78efa"),
    (0x0047E8DE, "d6f775fa"),
    (0x0047E8EC, "d6f76efa"),
    (0x0047ECBE, "d6f785f8"),
    (0x0047EE14, "d5f7daff"),
    (0x0057E216, "d6f6d9fd"),
]
CALLER_ADDRESS_SHA256 = "0376e19f832cae16a06c7f82772d8447c7b0ba259829731b5f2d9fd459bbcbbf"
CALLER_RECORD_SHA256 = "b6a64bf2fc5277484f9ec220ae171f77a520adb1bcf03c9b57f56360a9a769f2"
RAW_POINTER_HIT_SHA256 = "3bbc8c32bcc73d9275d5a486a5f909a19718991b19f668ff857ee80e49e280a8"

FUNCTION = "open_cfw_freertos_task_resume_all"
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]
TARGET_PROFILES = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0",
        "sha256": "8b8a8bde3a875d1b4f6b28d3aa0e4bedf2c80f80d0c0c380614e3e1a8c4216a3",
        "bytes": (
            "2de9f04381b044f65824c2f20704206868b1fff7feff206801382060206870b1"
            "0024fff7feff204601b0bde8f083fff7feff4ff0ff300021016000bffee754f8"
            "280c0028ecd043f62458c2f20708d8f8001000294dd04af29c494ff0000ec2f2"
            "06094ff0010c00bfd8f80c10cb68996adf6948681d6a03f11806b042bd606f60"
            "08bf4d60c3f828e00868013808605d6998686f68de68191d8f428660706008bf"
            "6e60286801382860dd6a54f8200c854284bf44f8205cdd6a05eb850009eb8006"
            "77685e61ba689f60da605160b96059f82010013149f8201054f8380cc06a8542"
            "28bf44f814ccd8f800000028bcd1fff7feff54f8185c65b1012600bffff7feff"
            "002818bf44f8146c013df7d1002044f8180c54f8140c00283ff482affff7feff"
            "01247ee7"
        ),
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "sha256": "7fb0e6bab36ed324d800362e1d1f85e29b8b7924e6cbe994600ebe998fe025a6",
        "bytes": (
            "2de9f04381b044f65824c2f20704206868b1fff7feff206801382060206870b1"
            "0024fff7feff204601b0bde8f083fff7feff4ff0ff300021016000bffee754f8"
            "280c0028ecd043f62458c2f20708d8f8001000294dd04af29c494ff0000ec2f2"
            "06094ff0010c00bfd8f80c10cb68996ad3e907054f6803f11806b74285606860"
            "08bf4d60c3f828e00868013808605d69d3e902766868191d8842be60776008bf"
            "6e60286801382860dd6a54f8200c854284bf44f8205cdd6a05eb850009eb8006"
            "77685e61ba68c3e902725160b96059f82010013149f8201054f8380cc06a8542"
            "28bf44f814ccd8f800000028bcd1fff7feff54f8185c65b1012600bffff7feff"
            "002818bf44f8146c013df7d1002044f8180c54f8140c00283ff482affff7feff"
            "01247ee7"
        ),
    },
}
TARGET_RELOCATIONS = [
    (0x12, 10, "open_cfw_freertos_port_enter_critical"),
    (0x22, 10, "open_cfw_freertos_port_exit_critical"),
    (0x2E, 10, "ulSetInterruptMask"),
    (0xEE, 10, "open_cfw_freertos_task_reset_next_task_unblock_time"),
    (0xFC, 10, "open_cfw_freertos_task_increment_tick"),
    (0x11C, 10, "open_cfw_freertos_port_yield"),
]

NULL = 0xFFFFFFFF
READY = 0x100
BLOCKED = 0x200
PENDING = 0x300
SENTINEL = 0xFFFFFFFE
ASSERTED = ctypes.c_int32(0x80000000).value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


class RuntimeFreeRTOSTaskResumeAllTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        parent = ROOT / "build"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=parent)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.profile_name = os.environ.get(
            "OPENCFW_TOOLCHAIN_PROFILE",
            "apple-clang" if sys.platform == "darwin" else "linux-clang",
        )
        cls.profile = TARGET_PROFILES[cls.profile_name]
        version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout
        if not version.startswith(str(cls.profile["version"])):
            raise AssertionError(f"compiler/profile mismatch: {version!r}")

        cls.candidate = cls.compile_host(
            temporary / library_name("resume_candidate"), CANDIDATE_FIXTURE, []
        )
        cls.oracle = cls.compile_host(
            temporary / library_name("resume_oracle"),
            ORACLE_FIXTURE,
            [
                "-ffreestanding", "-fno-builtin", "-I", str(FREERTOS_CONFIG),
                "-I", str(FREERTOS_INCLUDE), "-I", str(FREERTOS_PORT),
            ],
        )
        cls.bind_candidate()
        cls.bind_oracle()

        cls.target_objects = [temporary / "resume_1.o", temporary / "resume_2.o"]
        for target in cls.target_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(target)],
                check=True, capture_output=True, text=True,
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
    def compile_host(cls, output: Path, source: Path, extra: list[str]):
        # FreeRTOS intentionally views the MiniListItem_t sentinel through the
        # common ListItem_t prefix.  Disable host strict-alias optimization so
        # the 64-bit differential harness preserves that upstream contract.
        command = [
            cls.clang, "-O2", "-fno-strict-aliasing",
            "-Wall", "-Wextra", "-Werror", *extra, str(source),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(output)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(output))

    @classmethod
    def bind_candidate(cls) -> None:
        prefix = "open_cfw_resume_host_"
        cls.candidate_reset = getattr(cls.candidate, prefix + "reset")
        cls.candidate_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        for name in ("set_task", "set_list_index"):
            getattr(cls.candidate, prefix + name).argtypes = [ctypes.c_uint32] * 2
        for name in ("insert_ready", "insert_pending"):
            getattr(cls.candidate, prefix + name).argtypes = [ctypes.c_uint32]
        cls.candidate_execute = getattr(cls.candidate, prefix + "execute")
        cls.candidate_execute.restype = ctypes.c_int32
        for name in (
            "suspended", "pended", "yield_pending", "top", "tick_calls",
            "enter_calls", "exit_calls", "yield_calls", "reset_calls",
            "assert_calls", "pending_count", "blocked_count", "event_count",
        ):
            getattr(cls.candidate, prefix + "get_" + name).restype = ctypes.c_uint32
        for name in ("ready_count", "state_container", "event_container",
                     "event_kind", "event_value", "list_index"):
            function = getattr(cls.candidate, prefix + "get_" + name)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32
        cls.candidate_list_owner = getattr(cls.candidate, prefix + "get_list_owner")
        cls.candidate_list_owner.argtypes = [ctypes.c_uint32] * 2
        cls.candidate_list_owner.restype = ctypes.c_uint32

    @classmethod
    def bind_oracle(cls) -> None:
        prefix = "open_cfw_oracle_freertos_task_resume_all_"
        cls.oracle_reset = getattr(cls.oracle, prefix + "reset")
        cls.oracle_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32,
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        getattr(cls.oracle, prefix + "set_task").argtypes = [ctypes.c_uint32] * 2
        getattr(cls.oracle, prefix + "set_list_index").argtypes = [ctypes.c_uint32] * 2
        for name in ("insert_ready", "insert_pending"):
            getattr(cls.oracle, prefix + name).argtypes = [ctypes.c_uint32]
        cls.oracle_execute = getattr(cls.oracle, prefix + "execute")
        cls.oracle_execute.restype = ctypes.c_int32
        for name in ("suspended", "pended", "yield_pending", "top",
                     "pending_count", "blocked_count"):
            getattr(cls.oracle, prefix + "get_" + name).restype = ctypes.c_uint32
        for name in ("ready_count", "state_container", "event_container",
                     "list_index"):
            function = getattr(cls.oracle, prefix + "get_" + name)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32
        cls.oracle_list_owner = getattr(cls.oracle, prefix + "get_list_owner")
        cls.oracle_list_owner.argtypes = [ctypes.c_uint32] * 2
        cls.oracle_list_owner.restype = ctypes.c_uint32
        cls.oracle_tick = getattr(
            cls.oracle,
            "open_cfw_oracle_freertos_task_increment_tick_get_tick",
        )
        cls.oracle_tick.restype = ctypes.c_uint32

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    @classmethod
    def configure_pair(
        cls, suspended: int, current_tasks: int, pended: int,
        yield_pending: int, top: int, current: int, tick_results: int = 0,
    ) -> None:
        cls.candidate_reset(
            suspended, current_tasks, pended, yield_pending, top, current,
            tick_results,
        )
        cls.oracle_reset(suspended, current_tasks, pended, yield_pending, top, current)

    @classmethod
    def operate_pair(cls, name: str, *arguments: int) -> None:
        getattr(cls.candidate, "open_cfw_resume_host_" + name)(*arguments)
        getattr(cls.oracle, "open_cfw_oracle_freertos_task_resume_all_" + name)(*arguments)

    @classmethod
    def snapshot(cls, library, prefix: str) -> dict:
        getter = lambda name: getattr(library, prefix + "get_" + name)
        ready_priorities = (*range(6), 55)
        list_kinds = (PENDING, BLOCKED, *(READY + p for p in ready_priorities))
        return {
            "suspended": getter("suspended")(),
            "pended": getter("pended")(),
            "yield": ctypes.c_int32(getter("yield_pending")()).value,
            "top": getter("top")(),
            "pending": getter("pending_count")(),
            "blocked": getter("blocked_count")(),
            "ready": [getter("ready_count")(priority) for priority in ready_priorities],
            "state": [getter("state_container")(task) for task in range(4)],
            "event": [getter("event_container")(task) for task in range(4)],
            "index": [getter("list_index")(kind) for kind in list_kinds],
            "order": [
                [getter("list_owner")(kind, position) for position in range(4)]
                for kind in list_kinds
            ],
        }

    def pair_snapshot(self) -> tuple[dict, dict]:
        return (
            self.snapshot(self.candidate, "open_cfw_resume_host_"),
            self.snapshot(
                self.oracle, "open_cfw_oracle_freertos_task_resume_all_"
            ),
        )

    def test_candidate_matches_pristine_upstream_graph_scenarios(self) -> None:
        scenarios = [
            # Nested resume does not drain pending work or pended ticks.
            (2, 2, 3, 0, 1, 0, 0, 0, 0, 0, [("set_task", 0, 1),
                                     ("insert_ready", 0),
                                     ("set_task", 1, 3),
                                     ("insert_pending", 1)]),
            # Outermost resume with zero registered tasks performs no drain.
            (1, 0, 2, 1, 0, 0, 0, 0, 0, 0, [("set_task", 0, 0)]),
            # Higher priority pending task migrates and all pended ticks drain.
            (1, 2, 3, 0, 1, 0, 0, 3, 1, 1, [("set_task", 0, 1),
                                     ("insert_ready", 0),
                                     ("set_task", 1, 3),
                                     ("insert_pending", 1)]),
            # Lower priority migration does not request a yield.
            (1, 2, 0, 0, 4, 0, 0, 0, 1, 0, [("set_task", 0, 4),
                                     ("insert_ready", 0),
                                     ("set_task", 1, 2),
                                     ("insert_pending", 1)]),
            # Time slicing: pristine tick and the explicit tick seam both yield.
            (1, 2, 1, 0, 2, 0, 1, 1, 0, 1, [("set_task", 0, 2),
                                     ("insert_ready", 0),
                                     ("set_task", 1, 2),
                                     ("insert_ready", 1)]),
            # Two pending tasks exercise index repair and priority 55 insertion.
            (1, 4, 0, 0, 55, 0, 0, 0, 1, 1, [("set_task", 0, 2),
                                     ("insert_ready", 0),
                                     ("set_task", 1, 55),
                                     ("insert_ready", 1),
                                     ("set_task", 2, 55),
                                     ("insert_pending", 2),
                                     ("set_task", 3, 54),
                                     ("insert_pending", 3),
                                     ("set_list_index", PENDING, 2),
                                     ("set_list_index", BLOCKED, 3),
                                     ("set_list_index", READY + 55, 1)]),
        ]
        for scenario in scenarios:
            (
                suspended, tasks, pended, pending, top, current, ticks,
                expected_ticks, expected_resets, expected_yields, operations,
            ) = scenario
            with self.subTest(scenario=scenario[:7]):
                self.configure_pair(suspended, tasks, pended, pending, top, current, ticks)
                for operation in operations:
                    self.operate_pair(operation[0], *operation[1:])
                candidate_result = self.candidate_execute()
                oracle_result = self.oracle_execute()
                self.assertEqual(candidate_result, oracle_result)
                self.assertEqual(*self.pair_snapshot())
                self.assertEqual(
                    self.candidate.open_cfw_resume_host_get_tick_calls(),
                    expected_ticks,
                )
                self.assertEqual(self.oracle_tick(), expected_ticks)
                self.assertEqual(
                    self.candidate.open_cfw_resume_host_get_reset_calls(),
                    expected_resets,
                )
                self.assertEqual(
                    self.candidate.open_cfw_resume_host_get_yield_calls(),
                    expected_yields,
                )
                self.assertEqual(candidate_result != 0, expected_yields != 0)

        # The final scenario must repair both source-list indices while keeping
        # the non-sentinel destination index and inserting immediately before it.
        self.assertEqual(self.candidate.open_cfw_resume_host_get_list_index(PENDING), SENTINEL)
        self.assertEqual(self.candidate.open_cfw_resume_host_get_list_index(BLOCKED), SENTINEL)
        self.assertEqual(self.candidate.open_cfw_resume_host_get_list_index(READY + 55), 1)
        self.assertEqual(
            [self.candidate_list_owner(READY + 55, position) for position in range(3)],
            [2, 1, NULL],
        )
        self.assertEqual(self.candidate.open_cfw_resume_host_get_ready_count(54), 1)

    def test_complete_outer_resume_seam_order_is_explicit(self) -> None:
        self.candidate_reset(1, 3, 3, 0, 1, 0, 0b010)
        for operation in (
            ("set_task", 0, 1), ("insert_ready", 0),
            ("set_task", 1, 3), ("insert_pending", 1),
            ("set_task", 2, 2), ("insert_pending", 2),
        ):
            getattr(self.candidate, "open_cfw_resume_host_" + operation[0])(
                *operation[1:]
            )
        self.assertEqual(self.candidate_execute(), 1)
        count = self.candidate.open_cfw_resume_host_get_event_count()
        self.assertEqual(
            [self.candidate.open_cfw_resume_host_get_event_kind(i) for i in range(count)],
            [
                1, 2, 1, 3, 1, 4,
                5, 6, 7, 8, 9,
                5, 6, 8, 9,
                10, 11,
                12, 12, 9, 12,
                13, 14, 15, 16,
            ],
        )
        self.assertEqual(
            [self.candidate.open_cfw_resume_host_get_event_value(i) for i in range(count)],
            [
                1, 0, 1, 0, 0, 3,
                0, 1, 3, 0, 1,
                0, 3, 0, 1,
                0, 3,
                0, 1, 1, 0,
                0, 1, 0, 0,
            ],
        )

    def test_assert_and_volatile_critical_order_are_explicit(self) -> None:
        self.candidate_reset(0, 1, 0, 0, 0, 0, 0)
        self.assertEqual(self.candidate_execute(), ASSERTED)
        self.assertEqual(self.candidate.open_cfw_resume_host_get_assert_calls(), 1)
        count = self.candidate.open_cfw_resume_host_get_event_count()
        self.assertEqual(
            [self.candidate.open_cfw_resume_host_get_event_kind(i) for i in range(count)],
            [1, 17],
        )

        self.candidate_reset(2, 1, 0, 0, 0, 0, 0)
        self.assertEqual(self.candidate_execute(), 0)
        count = self.candidate.open_cfw_resume_host_get_event_count()
        self.assertEqual(
            [self.candidate.open_cfw_resume_host_get_event_kind(i) for i in range(count)],
            [1, 2, 1, 3, 1, 16],
        )
        self.assertEqual(
            [self.candidate.open_cfw_resume_host_get_event_value(i) for i in range(count)],
            [2, 0, 2, 1, 1, 0],
        )

    def test_source_and_authenticated_upstream_inputs_are_pinned(self) -> None:
        for path, size, digest in (
            (SOURCE, SOURCE_SIZE, SOURCE_SHA256),
            (HEADER, HEADER_SIZE, HEADER_SHA256),
            (CANDIDATE_FIXTURE, CANDIDATE_FIXTURE_SIZE, CANDIDATE_FIXTURE_SHA256),
            (ORACLE_FIXTURE, ORACLE_FIXTURE_SIZE, ORACLE_FIXTURE_SHA256),
        ):
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        self.assertEqual(sha256(UPSTREAM_TASKS), UPSTREAM_TASKS_SHA256)
        self.assertEqual(sha256(TICK_ORACLE_FIXTURE), TICK_ORACLE_FIXTURE_SHA256)
        subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

        source = SOURCE.read_text()
        header = HEADER.read_text()
        upstream = UPSTREAM_TASKS.read_text()
        for token in (
            "BaseType_t xTaskResumeAll( void )",
            "--uxSchedulerSuspended;",
            "while( listLIST_IS_EMPTY( &xPendingReadyList ) == pdFALSE )",
            "TickType_t xPendedCounts = xPendedTicks",
            "taskYIELD_IF_USING_PREEMPTION();",
        ):
            self.assertIn(token, upstream)
        for token in (
            "configMAX_PRIORITIES=56", "preemption enabled",
            "OPEN_CFW_FREERTOS_RESUME_MEMORY_BARRIER()",
            "OPEN_CFW_FREERTOS_RESUME_INCREMENT_TICK()",
            "OPEN_CFW_FREERTOS_RESUME_RESET_NEXT_UNBLOCK_TIME()",
        ):
            self.assertIn(token, source)
        for token in (
            "0x20073D24U", "0x20074A58U", "0x20074A30U",
            "0x20074A40U", "0x20074A44U", "0x2006A49CU",
            "OPEN_CFW_FREERTOS_RESUME_TCB_EVENT_ITEM_OFFSET = 0x18U",
            "OPEN_CFW_FREERTOS_RESUME_TCB_PRIORITY_OFFSET = 0x2CU",
        ):
            self.assertIn(token, header)

    def test_official_body_literals_calls_and_direct_entry_topology(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(hashlib.sha256(self.package).hexdigest(), PACKAGE_SHA256)
        body = self.span(START, END)
        self.assertEqual(len(body), 306)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(body[:10].hex(), "70b500240025dff89466")
        self.assertEqual(body[-8:].hex(), "edf7f7f8280070bd")
        for literal, word in RAM_LITERALS.items():
            self.assertEqual(struct.unpack("<I", self.span(literal, literal + 4))[0], word)

        outgoing = []
        callers = []
        jumps = []
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            first, second = struct.unpack("<HH", encoded)
            if first & 0xF800 != 0xF000 or second & 0x8000 == 0:
                continue
            for link in (True, False):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(address, encoded, link=link)
                except self.apollo_overlay.BuildError:
                    continue
                if START <= address < END and link:
                    outgoing.append((address, target))
                if target == START:
                    (callers if link else jumps).append((address, encoded.hex()))
                if START < target < END and not START <= address < END:
                    interior.append((address, target, link, encoded.hex()))
        self.assertEqual(outgoing, OUTGOING_CALLS)
        self.assertEqual(callers, CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            hashlib.sha256(b"".join(struct.pack("<I", a) for a, _ in CALLERS)).hexdigest(),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(b"".join(struct.pack("<I", a) + bytes.fromhex(e)
                                    for a, e in CALLERS)).hexdigest(),
            CALLER_RECORD_SHA256,
        )

        narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in self.narrow_branch_targets(address, halfword):
                if START <= target < END and not START <= address < END:
                    narrow.append((address, target, halfword))
        self.assertEqual(narrow, [])

        wide_conditional = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            target = self.wide_conditional_branch_target(address, encoded)
            if (
                target is not None and
                START <= target < END and
                not START <= address < END
            ):
                wide_conditional.append((address, target, encoded.hex()))
        self.assertEqual(wide_conditional, [])

        raw_hits = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                raw_hits.append((BASE + offset, value))
        self.assertNotIn(START, {value & ~1 for _, value in raw_hits})
        self.assertEqual(
            hashlib.sha256(b"".join(struct.pack("<II", *hit) for hit in raw_hits)).hexdigest(),
            RAW_POINTER_HIT_SHA256,
        )

    def test_target_profiles_are_deterministic_and_close_over_six_calls(self) -> None:
        observed = []
        for target in self.target_objects:
            data, sections = self.apollo_overlay.parse_elf32(target)
            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            function = next(s for s in symbols if s["name"] == FUNCTION)
            section = sections[int(function["section_index"])]
            body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            self.assertEqual(int(section["alignment"]), 4)
            self.assertEqual((int(function["value"]), int(function["size"])), (1, 292))
            self.assertEqual(body.hex(), self.profile["bytes"])
            self.assertEqual(hashlib.sha256(body).hexdigest(), self.profile["sha256"])
            self.assertEqual(self.parse_relocations(data, sections), TARGET_RELOCATIONS)
            undefined = {
                s["name"] for s in symbols
                if s["name"] and int(s["section_index"]) == 0
            }
            self.assertEqual(undefined, {name for _, _, name in TARGET_RELOCATIONS})
            observed.append(body)
        self.assertEqual(observed[0], observed[1])

    def test_source_is_registered_in_production_inputs(self) -> None:
        overlay = OVERLAY_CONFIG.read_text()
        manifest = CORE_SOURCE_MANIFEST.read_text()
        for token in (SOURCE.name, FUNCTION):
            self.assertIn(token, overlay)
        self.assertIn(
            "freertos_task_resume_all_source_replacement",
            manifest,
        )
        self.assertIn(
            "apollo_freertos_task_resume_all_source_leaf",
            manifest,
        )
        json.loads(overlay)
        json.loads(manifest)

    @staticmethod
    def parse_relocations(data: bytes, sections: list[dict]) -> list[tuple[int, int, str]]:
        import apollo_overlay
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symbol_table["offset"]) + index * 16
            )
            symbols.append((apollo_overlay.elf_string(strings, fields[0], "symbol"), fields))
        records = []
        target_name = f".text.{FUNCTION}"
        for section in sections:
            if int(section["type"]) != 9:
                continue
            if str(sections[int(section["info"])]["name"]) != target_name:
                continue
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II", data, int(section["offset"]) + index * 8
                )
                records.append((offset, information & 0xFF, symbols[information >> 8][0]))
        return records

    @staticmethod
    def narrow_branch_targets(address: int, halfword: int) -> list[int]:
        if halfword & 0xF800 == 0xE000:
            immediate = halfword & 0x07FF
            if immediate & 0x0400:
                immediate -= 0x0800
            return [address + 4 + immediate * 2]
        if halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0x0F) < 0x0E:
            immediate = halfword & 0xFF
            if immediate & 0x80:
                immediate -= 0x100
            return [address + 4 + immediate * 2]
        if halfword & 0xF500 == 0xB100:
            immediate = (((halfword >> 9) & 1) << 6) | (((halfword >> 3) & 0x1F) << 1)
            return [address + 4 + immediate]
        return []

    @staticmethod
    def wide_conditional_branch_target(address: int, encoded: bytes) -> int | None:
        first, second = struct.unpack("<HH", encoded)
        # Thumb-2 B<c>.W T3: 11110 S cond imm6 / 10 J1 0 J2 imm11.
        if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
            return None
        condition = (first >> 6) & 0x0F
        if condition >= 0x0E:
            return None
        immediate = (
            (((first >> 10) & 1) << 20)
            | (((second >> 11) & 1) << 19)
            | (((second >> 13) & 1) << 18)
            | ((first & 0x3F) << 12)
            | ((second & 0x07FF) << 1)
        )
        if immediate & (1 << 20):
            immediate -= 1 << 21
        return address + 4 + immediate


if __name__ == "__main__":
    unittest.main()
