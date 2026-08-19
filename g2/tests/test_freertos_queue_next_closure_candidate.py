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
    / "runtime_freertos_queue_next_closure.c"
)
HEADER = SOURCE.with_suffix(".h")
CANDIDATE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_queue_next_closure_host.c"
)
ORACLE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_queue_next_closure_upstream_oracle_host.c"
)
UPSTREAM_QUEUE = ROOT / "third_party" / "freertos-kernel" / "queue.c"
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

SOURCE_SIZE = 7_277
SOURCE_SHA256 = "b13a24bf4538016109194500c9ff7d9bfe5feac0b9f2c9708b390b028aad6f61"
HEADER_SIZE = 14_564
HEADER_SHA256 = "84592af1b7beed6201f927d59e18fcf52a4edaf2b58360c96efce276770a5239"
CANDIDATE_FIXTURE_SIZE = 19_665
CANDIDATE_FIXTURE_SHA256 = "d9bd4035555771b0449b51a7562c77c8f7c6a83c77ce29f7713bc8eddab62cd8"
ORACLE_FIXTURE_SIZE = 8_323
ORACLE_FIXTURE_SHA256 = "e7c43c0babd5578631c68bf8a003cb7ec02eef329caaf768b6ab9f208c3c25d3"
UPSTREAM_QUEUE_SHA256 = "5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894"
UPSTREAM_TASKS_SHA256 = "14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463"

BASE = 0x00438000
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
STOCK = {
    "give": (
        0x00441A42,
        0x00441B0A,
        "c56510d6607b980330894348b4f10affb4b1c90c256c497814803a72a7f71e9e",
    ),
    "remove": (
        0x00455370,
        0x00455466,
        "1a5d4850f0799e97548f23ee1617fc1de362f8d2a674301baa6facd579d13de4",
    ),
}
CLOSURE_SHA256 = "c676fb469cfb041aaa6ca082198f25191089d06f67619289dec172ce578f2e4b"
CALLERS = {
    "give": [
        (0x004499D8, "f8f733f8"),
        (0x00449E48, "f7f7fbfd"),
        (0x00473894, "cef7d5f8"),
        (0x00513F6C, "2df769fd"),
    ],
    "remove": [
        (0x0044158E, "13f0effe"),
        (0x00441900, "13f036fd"),
        (0x004419F4, "13f0bcfc"),
        (0x00441AC0, "13f056fc"),
        (0x00441C10, "13f0aefb"),
        (0x00441D56, "13f00bfb"),
        (0x00441E18, "13f0aafa"),
        (0x00441F9A, "13f0e9f9"),
        (0x00441FD0, "13f0cef9"),
    ],
}
CALLER_ADDRESS_SHA256 = {
    "give": "2f14fa17758a7633ba914c8f78a65d9168840abce36e1754c872896e898675cf",
    "remove": "a70b7dc8096a87718913eab967349886456a22c8ee3c85da0d0a77a66d91a501",
}
CALLER_RECORD_SHA256 = {
    "give": "00f9ffadf5e2d69859f61d9934f545ab637ca74166018fa4427df2e7796f0e34",
    "remove": "c3121cb346781b1abc1b10beb14f8c2f2a6b436f65da228c531cad71c5c8f5d7",
}
OUTGOING = {
    "give": [
        (0x00441A4C, 0x005FA0A4),
        (0x00441A60, 0x005FA0A4),
        (0x00441A86, 0x005FA0A4),
        (0x00441A94, 0x005FA0A4),
        (0x00441AC0, 0x00455370),
        (0x00441AD2, 0x00454F10),
        (0x00441AE6, 0x005FA0A4),
        (0x00441B02, 0x005FA0BA),
    ],
    "remove": [
        (0x0045537A, 0x005FA0A4),
        (0x00455420, 0x00455876),
    ],
}
RAW_POINTER_HIT_SHA256 = {
    "give": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "remove": "0a3e7dd8b2b2f17bde133e4ea7448b42c3843217855790cd4d7cf2ad8537c24e",
}
STOCK_RAM_LITERALS = {
    0x004551A0: 0x20074A30,
    0x00455468: 0x20074A58,
    0x004557A8: 0x20073D24,
    0x00455C34: 0x20074A20,
    0x00455C40: 0x20074A38,
    0x00455C44: 0x20074A44,
    0x00455DBC: 0x2006A49C,
}
HEADER_FIXED_ADDRESSES = {
    "OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TCB_ADDRESS": 0x20074A20,
    "OPEN_CFW_FREERTOS_QUEUE_NEXT_CURRENT_TASK_COUNT_ADDRESS": 0x20074A30,
    "OPEN_CFW_FREERTOS_QUEUE_NEXT_TOP_READY_PRIORITY_ADDRESS": 0x20074A38,
    "OPEN_CFW_FREERTOS_QUEUE_NEXT_YIELD_PENDING_ADDRESS": 0x20074A44,
    "OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_ADDRESS": 0x20074A58,
    "OPEN_CFW_FREERTOS_QUEUE_NEXT_READY_LISTS_ADDRESS": 0x2006A49C,
    "OPEN_CFW_FREERTOS_QUEUE_NEXT_PENDING_READY_LIST_ADDRESS": 0x20073D24,
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]
TARGET_FUNCTIONS_BY_PROFILE = {
    "apple-clang": {
        "open_cfw_freertos_task_remove_from_event_list": (
            216,
            "ee7695d521943e9e85f026f000f8b9bf25517ffd96cf85a6e263ba129217a94e",
        ),
        "open_cfw_freertos_queue_give_from_isr": (
            212,
            "a96ce1e9c86adad777fc709a3cead4e943f8c35bb9118ba9922bac393e45a5ba",
        ),
    },
    "linux-clang": {
        "open_cfw_freertos_task_remove_from_event_list": (
            216,
            "1e2768a9ba0c5008c152ef2718c08c93876445cdd9105ad346925609523e761a",
        ),
        "open_cfw_freertos_queue_give_from_isr": (
            212,
            "a96ce1e9c86adad777fc709a3cead4e943f8c35bb9118ba9922bac393e45a5ba",
        ),
    },
}
TARGET_TEXT_RELOCATIONS = [
    (
        ".text.open_cfw_freertos_queue_give_from_isr",
        0x9A,
        10,
        "open_cfw_freertos_task_remove_from_event_list",
    ),
]
PRODUCTION_ORDER = [
    "open_cfw_freertos_task_remove_from_event_list",
    "open_cfw_freertos_queue_give_from_isr",
    "open_cfw_freertos_task_check_free_stack_space",
]
PRODUCTION_PINS = {
    "apple-clang": {
        "open_cfw_freertos_task_remove_from_event_list": {
            "size": 216,
            "sha256": "ee7695d521943e9e85f026f000f8b9bf25517ffd96cf85a6e263ba129217a94e",
            "alignment": 4,
            "offset": 117_984,
            "unrelocated_sha256": "ee7695d521943e9e85f026f000f8b9bf25517ffd96cf85a6e263ba129217a94e",
        },
        "open_cfw_freertos_queue_give_from_isr": {
            "size": 212,
            "sha256": "1dab465785d5495fa530b4e6ff4494bc57f31287fbf558cebe491bdb18206054",
            "alignment": 4,
            "offset": 118_200,
            "unrelocated_sha256": "a96ce1e9c86adad777fc709a3cead4e943f8c35bb9118ba9922bac393e45a5ba",
        },
    },
    "linux-clang": {
        "open_cfw_freertos_task_remove_from_event_list": {
            "size": 216,
            "sha256": "1e2768a9ba0c5008c152ef2718c08c93876445cdd9105ad346925609523e761a",
            "alignment": 4,
            "offset": 119_844,
            "unrelocated_sha256": "1e2768a9ba0c5008c152ef2718c08c93876445cdd9105ad346925609523e761a",
        },
        "open_cfw_freertos_queue_give_from_isr": {
            "size": 212,
            "sha256": "1dab465785d5495fa530b4e6ff4494bc57f31287fbf558cebe491bdb18206054",
            "alignment": 4,
            "offset": 120_060,
            "unrelocated_sha256": "a96ce1e9c86adad777fc709a3cead4e943f8c35bb9118ba9922bac393e45a5ba",
        },
    },
}
PRODUCTION_RELOCATION = {
    "offset": 154,
    "type": "R_ARM_THM_CALL",
    "symbol": "open_cfw_freertos_task_remove_from_event_list",
    "target_function": "open_cfw_freertos_task_remove_from_event_list",
}
PRODUCTION_AGGREGATES = {
    "apple-clang": {
        "overlay_size": 147_021,
        "overlay_sha256": "02c48ddcf4fa682ec14c3520ccac159c98a357aff4d18bd7e8ad01817e3bc2cd",
        "component_size": 3_670_417,
        "component_sha256": "eee145e7f687e622447bc33fc9dc45b3ab5eb1f1ad49717029196d589799aa4c",
    },
    "linux-clang": {
        "overlay_size": 144_266,
        "overlay_sha256": "4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9",
        "component_size": 3_667_662,
        "component_sha256": "686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6",
    },
}

ASSERTED = ctypes.c_int32(0x80000000).value
NONE = 0
BLOCKED = 1
RECEIVE = 2
PENDING = 3
READY = 0x100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


class FreeRTOSQueueNextClosureCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        parent = ROOT / "build"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=parent)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout
        if version.startswith("Apple clang version 21.0.0"):
            cls.toolchain_profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            cls.toolchain_profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed target compiler: {version!r}")
        cls.target_functions = TARGET_FUNCTIONS_BY_PROFILE[
            cls.toolchain_profile
        ]

        cls.candidate = cls.compile_host(
            temporary / library_name("queue_next_candidate"),
            CANDIDATE_FIXTURE,
            [],
        )
        cls.oracle = cls.compile_host(
            temporary / library_name("queue_next_oracle"),
            ORACLE_FIXTURE,
            [
                "-ffreestanding", "-fno-builtin", "-I", str(FREERTOS_CONFIG),
                "-I", str(FREERTOS_INCLUDE), "-I", str(FREERTOS_PORT),
            ],
        )
        cls.bind(cls.candidate, "open_cfw_queue_next_host_", candidate=True)
        cls.bind(cls.oracle, "open_cfw_oracle_queue_next_", candidate=False)

        cls.target_objects = [temporary / "candidate-1.o", temporary / "candidate-2.o"]
        for output in cls.target_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                check=True, capture_output=True, text=True,
            )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[32:]

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
    def bind(library, prefix: str, candidate: bool) -> None:
        getattr(library, prefix + "reset").argtypes = [ctypes.c_uint32] * 4
        getattr(library, prefix + "configure_queue").argtypes = (
            [ctypes.c_uint32] * 4 + [ctypes.c_int32]
        )
        getattr(library, prefix + "configure_mutex_alias").argtypes = (
            [ctypes.c_uint32] * 2
        )
        getattr(library, prefix + "insert_waiter").argtypes = [ctypes.c_uint32]
        getattr(library, prefix + "seed_ready").argtypes = [ctypes.c_uint32]
        getattr(library, prefix + "set_ready_index").argtypes = (
            [ctypes.c_uint32] * 2
        )
        execute = getattr(library, prefix + "execute")
        execute.argtypes = [ctypes.c_uint32, ctypes.c_int32]
        execute.restype = ctypes.c_int32
        for name in ("transmit_lock", "flag", "yield_pending"):
            getattr(library, prefix + "get_" + name).restype = ctypes.c_int32
        for name in (
            "messages", "top_ready_priority", "receive_count", "blocked_count",
            "pending_count", "waiter_state_container", "waiter_event_container",
        ):
            getattr(library, prefix + "get_" + name).restype = ctypes.c_uint32
        ready = getattr(library, prefix + "get_ready_count")
        ready.argtypes = [ctypes.c_uint32]
        ready.restype = ctypes.c_uint32
        for name in (
            "ready_head_owner", "ready_tail_owner", "ready_index_owner",
        ):
            getter = getattr(library, prefix + "get_" + name)
            getter.argtypes = [ctypes.c_uint32]
            getter.restype = ctypes.c_uint32
        if candidate:
            for name in (
                "execute_null_queue", "execute_ownerless_remove",
            ):
                getattr(library, prefix + name).restype = ctypes.c_int32
            for name in (
                "set_mask_calls", "clear_mask_calls", "clear_mask_argument",
                "task_count_loads", "reset_unblock_calls", "validate_calls",
                "reset_after_ready", "trace_send_calls", "trace_failed_calls",
                "assert_calls",
            ):
                getattr(library, prefix + "get_" + name).restype = ctypes.c_uint32
        else:
            getattr(library, prefix + "get_next_unblock_time").restype = ctypes.c_uint32

    @classmethod
    def configure_pair(
        cls, suspended: int, current: int, top: int, tasks: int,
        length: int, messages: int, item_size: int, mutex: int, lock: int,
        waiter: int | None,
    ) -> None:
        for library, prefix in (
            (cls.candidate, "open_cfw_queue_next_host_"),
            (cls.oracle, "open_cfw_oracle_queue_next_"),
        ):
            getattr(library, prefix + "reset")(suspended, current, top, tasks)
            getattr(library, prefix + "configure_queue")(
                length, messages, item_size, mutex, lock
            )
            if waiter is not None:
                getattr(library, prefix + "insert_waiter")(waiter)

    @staticmethod
    def snapshot(library, prefix: str, priorities: tuple[int, ...]) -> dict:
        get = lambda name: getattr(library, prefix + "get_" + name)
        return {
            "messages": get("messages")(),
            "lock": get("transmit_lock")(),
            "flag": get("flag")(),
            "yield": get("yield_pending")(),
            "top": get("top_ready_priority")(),
            "receive": get("receive_count")(),
            "blocked": get("blocked_count")(),
            "pending": get("pending_count")(),
            "state_container": get("waiter_state_container")(),
            "event_container": get("waiter_event_container")(),
            "ready": [get("ready_count")(priority) for priority in priorities],
        }

    def pair_snapshot(self, priorities: tuple[int, ...]) -> tuple[dict, dict]:
        return (
            self.snapshot(self.candidate, "open_cfw_queue_next_host_", priorities),
            self.snapshot(self.oracle, "open_cfw_oracle_queue_next_", priorities),
        )

    def test_candidate_matches_pristine_upstream_queue_and_task_graphs(self) -> None:
        scenarios = [
            # no waiter; ordinary unlocked semaphore increment
            (0, 2, 2, 4, 5, 1, 0, 0, -1, None, 1, 7, 1, 0),
            # lower-priority waiter moves to ready without a wake flag
            (0, 4, 4, 4, 5, 1, 0, 0, -1, 2, 1, 7, 1, 1),
            # equal-priority waiter moves to ready without yielding
            (0, 3, 3, 4, 5, 1, 0, 0, -1, 3, 1, 6, 1, 1),
            # higher-priority waiter updates top/yield/output flag
            (0, 2, 2, 4, 5, 1, 0, 0, -1, 3, 1, 0, 1, 1),
            # nullable wake pointer still leaves xYieldPending latched
            (0, 2, 2, 4, 5, 1, 0, 0, -1, 3, 0, 9, 1, 1),
            # suspended scheduler moves only the event item to pending-ready
            (1, 2, 2, 4, 5, 1, 0, 0, -1, 3, 1, 0, 1, 0),
            # locked queue increments cTxLock and leaves the waiter blocked
            (0, 2, 2, 4, 5, 1, 0, 0, 0, 3, 1, 0, 1, 0),
            # saturation at task count leaves cTxLock unchanged
            (0, 2, 2, 4, 5, 1, 0, 0, 4, 3, 1, 0, 1, 0),
            # full queue fails without waking or incrementing
            (0, 2, 2, 4, 5, 5, 0, 0, -1, 3, 1, 6, 0, 0),
        ]
        for scenario in scenarios:
            (
                suspended, current, top, tasks, length, messages, item_size,
                mutex, lock, waiter, use_flag, initial_flag, expected_result,
                expected_reset,
            ) = scenario
            with self.subTest(scenario=scenario):
                self.configure_pair(
                    suspended, current, top, tasks, length, messages, item_size,
                    mutex, lock, waiter,
                )
                candidate_result = self.candidate.open_cfw_queue_next_host_execute(
                    use_flag, initial_flag
                )
                oracle_result = self.oracle.open_cfw_oracle_queue_next_execute(
                    use_flag, initial_flag
                )
                self.assertEqual(candidate_result, oracle_result)
                self.assertEqual(candidate_result, expected_result)
                priorities = tuple(sorted({0, current, top, waiter or 0, 55}))
                self.assertEqual(*self.pair_snapshot(priorities))
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_reset_unblock_calls(),
                    expected_reset,
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_validate_calls(), 1
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_set_mask_calls(), 1
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_clear_mask_calls(), 1
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_clear_mask_argument(),
                    0x35,
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_trace_send_calls(),
                    expected_result,
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_trace_failed_calls(),
                    1 - expected_result,
                )
                if expected_reset != 0:
                    self.assertEqual(
                        self.candidate
                            .open_cfw_queue_next_host_get_reset_after_ready(),
                        1,
                    )
                    self.assertEqual(
                        self.oracle.open_cfw_oracle_queue_next_get_next_unblock_time(),
                        0xFFFFFFFF,
                    )
                else:
                    self.assertEqual(
                        self.candidate
                            .open_cfw_queue_next_host_get_reset_after_ready(),
                        0,
                    )

    def test_locked_queue_model_covers_signed_and_population_edges(self) -> None:
        for lock in (-128, -2, 0, 1, 3, 63, 126):
            for tasks in (0, 1, 2, 4, 64, 127):
                with self.subTest(lock=lock, tasks=tasks):
                    self.configure_pair(
                        0, 2, 2, tasks, 10, 2, 0, 0, lock, None
                    )
                    candidate_result = (
                        self.candidate.open_cfw_queue_next_host_execute(1, 11)
                    )
                    oracle_result = (
                        self.oracle.open_cfw_oracle_queue_next_execute(1, 11)
                    )
                    self.assertEqual(candidate_result, oracle_result)
                    self.assertEqual(candidate_result, 1)
                    expected_lock = (
                        lock + 1
                        if ctypes.c_uint32(lock).value < tasks else lock
                    )
                    self.assertEqual(*self.pair_snapshot((0, 2, 55)))
                    self.assertEqual(
                        self.candidate.open_cfw_queue_next_host_get_transmit_lock(),
                        expected_lock,
                    )
                    self.assertEqual(
                        self.candidate.open_cfw_queue_next_host_get_task_count_loads(),
                        1,
                    )

    def test_mutex_discriminator_is_independent_of_union_holder_word(self) -> None:
        for head_is_null, holder_is_nonnull in ((0, 0), (0, 1), (1, 0)):
            with self.subTest(
                head_is_null=head_is_null,
                holder_is_nonnull=holder_is_nonnull,
            ):
                self.configure_pair(0, 2, 2, 4, 4, 0, 0, 0, -1, None)
                for library, prefix in (
                    (self.candidate, "open_cfw_queue_next_host_"),
                    (self.oracle, "open_cfw_oracle_queue_next_"),
                ):
                    getattr(library, prefix + "configure_mutex_alias")(
                        head_is_null, holder_is_nonnull
                    )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_execute(1, 19),
                    self.oracle.open_cfw_oracle_queue_next_execute(1, 19),
                )
                self.assertEqual(*self.pair_snapshot((0, 2, 55)))

    def test_ready_insertion_obeys_existing_list_index(self) -> None:
        priority = 4
        for use_seed_as_index, expected_head, expected_tail in (
            (0, 2, 1),
            (1, 1, 2),
        ):
            with self.subTest(use_seed_as_index=use_seed_as_index):
                self.configure_pair(
                    0, 2, priority, 4, 5, 1, 0, 0, -1, priority
                )
                for library, prefix in (
                    (self.candidate, "open_cfw_queue_next_host_"),
                    (self.oracle, "open_cfw_oracle_queue_next_"),
                ):
                    getattr(library, prefix + "seed_ready")(priority)
                    getattr(library, prefix + "set_ready_index")(
                        priority, use_seed_as_index
                    )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_execute(1, 0),
                    self.oracle.open_cfw_oracle_queue_next_execute(1, 0),
                )
                self.assertEqual(*self.pair_snapshot((priority,)))
                expected_index = 2 if use_seed_as_index else 0xFFFFFFFE
                for library, prefix in (
                    (self.candidate, "open_cfw_queue_next_host_"),
                    (self.oracle, "open_cfw_oracle_queue_next_"),
                ):
                    self.assertEqual(
                        getattr(library, prefix + "get_ready_head_owner")(
                            priority
                        ),
                        expected_head,
                    )
                    self.assertEqual(
                        getattr(library, prefix + "get_ready_tail_owner")(
                            priority
                        ),
                        expected_tail,
                    )
                    self.assertEqual(
                        getattr(library, prefix + "get_ready_index_owner")(
                            priority
                        ),
                        expected_index,
                    )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_reset_after_ready(),
                    1,
                )

    def test_assert_mutex_and_optional_flag_paths_are_explicit(self) -> None:
        self.candidate.open_cfw_queue_next_host_reset(0, 2, 2, 4)
        self.assertEqual(
            self.candidate.open_cfw_queue_next_host_execute_null_queue(), ASSERTED
        )
        self.assertEqual(self.candidate.open_cfw_queue_next_host_get_assert_calls(), 1)
        self.assertEqual(self.candidate.open_cfw_queue_next_host_get_set_mask_calls(), 1)

        for item_size, mutex in ((1, 0), (0, 1)):
            with self.subTest(item_size=item_size, mutex=mutex):
                self.candidate.open_cfw_queue_next_host_reset(0, 2, 2, 4)
                self.candidate.open_cfw_queue_next_host_configure_queue(
                    4, 0, item_size, mutex, -1
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_execute(0, 19), ASSERTED
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_assert_calls(), 1
                )
                self.assertEqual(
                    self.candidate.open_cfw_queue_next_host_get_clear_mask_calls(), 0
                )

        self.candidate.open_cfw_queue_next_host_reset(0, 2, 2, 128)
        self.candidate.open_cfw_queue_next_host_configure_queue(4, 0, 0, 0, 127)
        self.assertEqual(
            self.candidate.open_cfw_queue_next_host_execute(1, 19), ASSERTED
        )
        self.assertEqual(self.candidate.open_cfw_queue_next_host_get_messages(), 1)
        self.assertEqual(self.candidate.open_cfw_queue_next_host_get_assert_calls(), 1)
        self.assertEqual(self.candidate.open_cfw_queue_next_host_get_set_mask_calls(), 2)
        self.assertEqual(self.candidate.open_cfw_queue_next_host_get_clear_mask_calls(), 0)

        self.candidate.open_cfw_queue_next_host_reset(0, 2, 2, 4)
        self.assertEqual(
            self.candidate.open_cfw_queue_next_host_execute_ownerless_remove(),
            ASSERTED,
        )
        self.assertEqual(self.candidate.open_cfw_queue_next_host_get_assert_calls(), 1)

    def test_source_upstream_and_production_overlay_are_pinned(self) -> None:
        for path, size, digest in (
            (SOURCE, SOURCE_SIZE, SOURCE_SHA256),
            (HEADER, HEADER_SIZE, HEADER_SHA256),
            (CANDIDATE_FIXTURE, CANDIDATE_FIXTURE_SIZE, CANDIDATE_FIXTURE_SHA256),
            (ORACLE_FIXTURE, ORACLE_FIXTURE_SIZE, ORACLE_FIXTURE_SHA256),
        ):
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        self.assertEqual(sha256(UPSTREAM_QUEUE), UPSTREAM_QUEUE_SHA256)
        self.assertEqual(sha256(UPSTREAM_TASKS), UPSTREAM_TASKS_SHA256)
        subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

        upstream_queue = UPSTREAM_QUEUE.read_text()
        upstream_tasks = UPSTREAM_TASKS.read_text()
        for token in (
            "BaseType_t xQueueGiveFromISR( QueueHandle_t xQueue,",
            "prvIncrementQueueTxLock( pxQueue, cTxLock );",
            "*pxHigherPriorityTaskWoken = pdTRUE;",
        ):
            self.assertIn(token, upstream_queue)
        for token in (
            "BaseType_t xTaskRemoveFromEventList( const List_t * const pxEventList )",
            "prvResetNextTaskUnblockTime();",
            "xYieldPending = pdTRUE;",
        ):
            self.assertIn(token, upstream_tasks)
        config = json.loads(OVERLAY_CONFIG.read_text())
        self.assertEqual(
            [
                function
                for function in config["functions"]
                if function in PRODUCTION_ORDER
            ],
            PRODUCTION_ORDER,
        )
        self.assertEqual(
            config["expected"],
            PRODUCTION_AGGREGATES["apple-clang"],
        )
        self.assertEqual(
            config["toolchain_profiles"]["linux-clang"]["expected"],
            PRODUCTION_AGGREGATES["linux-clang"],
        )
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
        }
        for function in PRODUCTION_ORDER[:2]:
            leaf = leaves[function]
            self.assertEqual(
                leaf["source"]["path"],
                SOURCE.relative_to(ROOT).as_posix(),
            )
            self.assertEqual(leaf["source"]["size"], SOURCE_SIZE)
            self.assertEqual(leaf["source"]["sha256"], SOURCE_SHA256)
            self.assertEqual(
                leaf["expected"],
                PRODUCTION_PINS["apple-clang"][function],
            )
            linux = leaf["toolchain_profiles"]["linux-clang"]
            self.assertEqual(
                linux["reviewed_version_prefix"],
                "Homebrew clang version 22.1.8",
            )
            self.assertEqual(
                linux["expected"],
                PRODUCTION_PINS["linux-clang"][function],
            )
        remove_leaf = leaves[
            "open_cfw_freertos_task_remove_from_event_list"
        ]
        give_leaf = leaves["open_cfw_freertos_queue_give_from_isr"]
        self.assertEqual(remove_leaf["relocations"], [])
        self.assertEqual(
            remove_leaf["toolchain_profiles"]["linux-clang"][
                "relocations"
            ],
            [],
        )
        self.assertEqual(give_leaf["relocations"], [PRODUCTION_RELOCATION])
        self.assertEqual(
            give_leaf["toolchain_profiles"]["linux-clang"][
                "relocations"
            ],
            [PRODUCTION_RELOCATION],
        )

        patches = {
            item["name"]: item
            for item in config["patch_sites"]
        }
        for stock_name, function, patch_name in (
            (
                "give",
                "open_cfw_freertos_queue_give_from_isr",
                "replace_freertos_queue_give_from_isr",
            ),
            (
                "remove",
                "open_cfw_freertos_task_remove_from_event_list",
                "replace_freertos_task_remove_from_event_list",
            ),
        ):
            start, end, _digest = STOCK[stock_name]
            patch = patches[patch_name]
            self.assertEqual(patch["runtime_address"], start)
            self.assertEqual(
                patch["expected_hex"],
                self.application[start - BASE:end - BASE].hex(),
            )
            self.assertEqual(patch["branch"], "b_w")
            self.assertEqual(patch["target_function"], function)

        overlay_runtime = BASE + len(self.application)
        for profile in ("apple-clang", "linux-clang"):
            for stock_name, function in (
                ("give", "open_cfw_freertos_queue_give_from_isr"),
                (
                    "remove",
                    "open_cfw_freertos_task_remove_from_event_list",
                ),
            ):
                entry = STOCK[stock_name][0]
                target = (
                    overlay_runtime
                    + PRODUCTION_PINS[profile][function]["offset"]
                )
                branch = self.apollo_overlay.encode_thumb_b_w(entry, target)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        entry,
                        branch,
                        link=False,
                    ),
                    target,
                )

        manifest = CORE_SOURCE_MANIFEST.read_text()
        for token in PRODUCTION_ORDER[:2]:
            self.assertNotIn(token, manifest)
        header = HEADER.read_text()
        for name, address in HEADER_FIXED_ADDRESSES.items():
            self.assertIn(f"{name} = 0x{address:08X}U", header)

    def test_official_spans_calls_callers_and_reference_topology_are_exact(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(hashlib.sha256(self.package).hexdigest(), PACKAGE_SHA256)
        bodies = []
        for name, (start, end, digest) in STOCK.items():
            body = self.application[start - BASE:end - BASE]
            bodies.append(body)
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

            observed_callers = []
            observed_outgoing = []
            jumps = []
            interior = []
            for offset in range(0, len(self.application) - 3, 2):
                address = BASE + offset
                encoded = self.application[offset:offset + 4]
                for link in (True, False):
                    try:
                        target = self.apollo_overlay.decode_thumb_branch(
                            address, encoded, link=link
                        )
                    except self.apollo_overlay.BuildError:
                        continue
                    if target == start:
                        (observed_callers if link else jumps).append(
                            (address, encoded.hex())
                        )
                    if start <= address < end and link:
                        observed_outgoing.append((address, target))
                    if start < target < end and not start <= address < end:
                        interior.append((address, target, link))
            self.assertEqual(observed_callers, CALLERS[name])
            self.assertEqual(observed_outgoing, OUTGOING[name])
            self.assertEqual(jumps, [])
            self.assertEqual(interior, [])
            self.assertEqual(
                hashlib.sha256(b"".join(
                    struct.pack("<I", address)
                    for address, _ in observed_callers
                )).hexdigest(),
                CALLER_ADDRESS_SHA256[name],
            )
            self.assertEqual(
                hashlib.sha256(b"".join(
                    struct.pack("<I", address) + bytes.fromhex(encoded)
                    for address, encoded in observed_callers
                )).hexdigest(),
                CALLER_RECORD_SHA256[name],
            )

            raw_hits = []
            for offset in range(0, len(self.application) - 3):
                value = struct.unpack_from("<I", self.application, offset)[0]
                if start <= (value & ~1) < end:
                    raw_hits.append((BASE + offset, value))
            self.assertNotIn(start, {value & ~1 for _, value in raw_hits})
            self.assertEqual(
                hashlib.sha256(b"".join(
                    struct.pack("<II", *record) for record in raw_hits
                )).hexdigest(),
                RAW_POINTER_HIT_SHA256[name],
            )
        self.assertEqual(hashlib.sha256(b"".join(bodies)).hexdigest(), CLOSURE_SHA256)
        for literal_address, expected_value in STOCK_RAM_LITERALS.items():
            self.assertEqual(
                struct.unpack_from(
                    "<I", self.application, literal_address - BASE
                )[0],
                expected_value,
            )

    def test_apple_target_is_deterministic_with_one_text_relocation(self) -> None:
        self.assertEqual(
            self.target_objects[0].read_bytes(), self.target_objects[1].read_bytes()
        )
        for target in self.target_objects:
            data, sections = self.apollo_overlay.parse_elf32(target)
            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            for name, (expected_size, expected_digest) in self.target_functions.items():
                symbol = next(item for item in symbols if item["name"] == name)
                section = sections[int(symbol["section_index"])]
                body = data[
                    int(section["offset"]):
                    int(section["offset"]) + int(section["size"])
                ]
                self.assertEqual(int(section["alignment"]), 4)
                self.assertEqual((int(symbol["value"]), int(symbol["size"])),
                                 (1, expected_size))
                self.assertEqual(len(body), expected_size)
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected_digest)

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
                parsed_symbols.append(
                    (self.apollo_overlay.elf_string(strings, fields[0], "symbol"), fields)
                )
            self.assertEqual(
                [name for name, fields in parsed_symbols if name and fields[5] == 0],
                [],
            )
            text_relocations = []
            exidx_relocations = []
            for section in sections:
                if int(section["type"]) != 9:
                    continue
                relocated = sections[int(section["info"])]
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II", data, int(section["offset"]) + index * 8
                    )
                    record = (
                        relocated["name"], offset, information & 0xFF,
                        parsed_symbols[information >> 8][0],
                    )
                    if str(relocated["name"]).startswith(".text"):
                        text_relocations.append(record)
                    elif str(relocated["name"]).startswith(".ARM.exidx"):
                        exidx_relocations.append(record)
                    else:
                        self.fail(f"unexpected relocated section: {record!r}")
            self.assertEqual(text_relocations, TARGET_TEXT_RELOCATIONS)
            self.assertEqual(
                [(name, kind) for name, _offset, kind, _symbol in exidx_relocations],
                [
                    (".ARM.exidx.text.open_cfw_freertos_task_remove_from_event_list", 42),
                    (".ARM.exidx.text.open_cfw_freertos_queue_give_from_isr", 42),
                ],
            )
            for section in sections:
                if section["name"] in (".data", ".bss", ".rodata"):
                    self.assertEqual(int(section["size"]), 0)


if __name__ == "__main__":
    unittest.main()
