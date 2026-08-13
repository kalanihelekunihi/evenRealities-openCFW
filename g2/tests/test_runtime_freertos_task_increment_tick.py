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
    / "runtime_freertos_task_increment_tick.c"
)
HEADER = SOURCE.with_suffix(".h")
CANDIDATE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_task_increment_tick_host.c"
)
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_task_increment_tick_upstream_oracle_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_VERIFIER = ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
FREERTOS_INCLUDE = ROOT / "third_party" / "freertos-kernel" / "include"
FREERTOS_PORT = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
)
FREERTOS_CONFIG = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "candidates"
    / "cmsis_freertos_constructors"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
CORE_SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

SOURCE_SIZE = 6_927
SOURCE_SHA256 = "0fb59aba7fb8b8ab1f7fc2b2cc5095f9bb05334770d44790a42b33ad80369cb2"
HEADER_SIZE = 11_502
HEADER_SHA256 = "0e7990ad52bc620fd9529b350baab42c22b06cb6ad916e6bcf535f12f560d906"
CANDIDATE_FIXTURE_SIZE = 26_629
CANDIDATE_FIXTURE_SHA256 = "5ada37e8754a711ab14d456d74be14fe352f4bb6a9e5e8b791037b8ef12003df"
ORACLE_FIXTURE_SIZE = 16_051
ORACLE_FIXTURE_SHA256 = "432ad24d7bb999cdd4f785ad0ac90b2720717171475a6cd4f86fe6e4b0b30cdf"

BASE = 0x00438000
START = 0x0045504C
END = 0x0045519E
STOCK_BYTES = (
    "f8b50025dff814040068002840f09a80dff80c040468641c0460002c19d1dff8"
    "041408680068002806d0a5f115f800205ff0ff310860fee70868dff8ec231368"
    "0b601060dff8640a0168491c016000f0ecfbdff884160868844262d357e01068"
    "c068c268506884425ad35069d3689668b3609368d66873604368161db34201d1"
    "d36843600023536103685b1e0360906a002812d0906a136ad669b360d369166a"
    "7360436812f11806b34201d1136a43600023936203685b1e036029480368d66a"
    "b34201d2d36a036026481423d66a5e43064476689660b768d760171dd6f808c0"
    "ccf80470171db760d66a5e4306445661d66a5e43d76a03fb07f3c3585b1c835"
    "115480068c06ad26a904200d20125c54a106800680028a2d15ff0ff30086000e0"
    "08600d4800680f49c26a142042438858022800d30125dff890080068002806d0"
    "012504e0dff884080168491c01602800f2bd"
)
STOCK_SHA256 = "438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050"
CALLERS = [
    (0x0044211C, "12f096ff"),
    (0x00454ECC, "00f0bef8"),
    (0x00456408, "fef720fe"),
]
CALLER_ADDRESS_SHA256 = "1a3ea5d9db1d906a1f91d344c8e6228b55ed15522fc8ca7186f50e5846f25d7d"
CALLER_RECORD_SHA256 = "2102130f9d20f69f316b7e41d3d36c9e142ab1c323c19647b815347364fa9cfb"
POINTER_CANDIDATES = [
    (0x0049A747, 0x004550FF, 0x004550FE),
    (0x00571373, 0x00455100, 0x00455100),
    (0x0058F87B, 0x00455100, 0x00455100),
    (0x006840FF, 0x004550FF, 0x004550FE),
    (0x0077FCE3, 0x00455059, 0x00455058),
    (0x0078B9A3, 0x00455059, 0x00455058),
]
POINTER_RECORD_SHA256 = "a62e912b15215e33f75cb097bcf6575df948fb0ee4d5ca7a1a2192f4e75d7c6c"
LITERALS = {
    0x004551A4: 0x20074A20,
    0x004551AC: 0x20074A38,
    0x004551B0: 0x2006A49C,
    0x00455468: 0x20074A58,
    0x0045546C: 0x20074A34,
    0x00455470: 0x20074A24,
    0x00455474: 0x20074A28,
    0x00455724: 0x20074A50,
    0x00455A14: 0x20074A44,
    0x00455A18: 0x20074A40,
    0x00455AF8: 0x20074A48,
}

FUNCTION = "open_cfw_freertos_task_increment_tick"
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
TARGET_PROFILES = {
    "apple-clang": {
        "version_prefix": "Apple clang version 21.0.0",
        "size": 344,
        "sha256": "453dd5addafa0fade84729e0f215668b067055eea7daf43cc089b9ee98e02888",
        "bytes": (
            "2de9f04381b044f62429c2f20709d9f8340040b1d9f81c000130c9f81c000020"
            "01b0bde8f083d9f8100010f10108c9f8108019d3d9f80000006830b1fff7feff"
            "4ff0ff3000210160fee7d9f80000d9f80410c9f80010c9f80400d9f824000130"
            "c9f82400fff7feffd9f82c004af29c4e8045c2f2060e01d200205be0d9f80000"
            "4ff0000c006800284cd0002022e000bfd96ad9f81440a14284bfc9f81410d96a"
            "01eb81040eeb84056e685d61b7689e60df607a60b2605ef8242001324ef82420"
            "59f8042cd26ad9f80030914288bf0120196859b3d9f80010c968cb681a4652f8"
            "041f884524d359699f68de684d68be609542776008bf4e600d68013d0d60996a"
            "0029c5d0df691e6a4c6803f11805be60ac42776008bf4e60c3f828c00c68013c"
            "0c60b5e74ff0ff31002001e04ff0ff31c9f82c1059f8041cc96a01eb81015ef8"
            "2110012988bf0120d9f82010002918bf012001b0bde8f083"
        ),
        "relocations": [
            (0x3C, 10, "ulSetInterruptMask"),
            (0x64, 10, "open_cfw_freertos_task_reset_next_task_unblock_time"),
        ],
    },
    "linux-clang": {
        "version_prefix": "Homebrew clang version 22.1.8",
        "size": 338,
        "sha256": "889ae62e4116bbd1bd8c8db65612b779372dfe8a4f26e5c78e3a0828e1671c5a",
        "bytes": (
            "2de9f04744f6242ac2f2070adaf8340038b1daf81c000130caf81c000020bde8"
            "f087daf8100010f10108caf8108019d3daf80000006830b1fff7feff4ff0ff30"
            "00210160fee7daf80000daf80410caf80010caf80400daf824000130caf82400ff"
            "f7feffdaf82c004af29c4e8045c2f2060e01d200205be0daf800004ff0000c00"
            "6800284cd0002022e000bfd96adaf81450a94284bfcaf81410d96a01eb81050e"
            "eb850677685e61bc68c3e902746260ba605ef8252001324ef825205af8042cd26a"
            "daf80030914288bf0120196859b3daf80010c968cb681a4652f8041f884524d359"
            "69d3e902764d68be609542776008bf4e600d68013d0d60996a0029c5d0d3e907"
            "764d6803f11809be604d45776008bf4e60c3f828c00d68013d0d60b5e74ff0ff"
            "31002001e04ff0ff31caf82c105af8041cc96a01eb81015ef82110012988bf0120"
            "daf82010002918bf0120bde8f087"
        ),
        "relocations": [
            (0x38, 10, "ulSetInterruptMask"),
            (0x60, 10, "open_cfw_freertos_task_reset_next_task_unblock_time"),
        ],
    },
}

NULL = 0xFFFFFFFF
SENTINEL = 0xFFFFFFFE
READY = 0x100
EVENT = 0x200

EV_SUSPENDED_LOAD = 1
EV_TICK_LOAD = 2
EV_TICK_STORE = 3
EV_DELAYED_LOAD = 4
EV_DELAYED_STORE = 5
EV_OVERFLOW_LOAD = 6
EV_OVERFLOW_STORE = 7
EV_OVERFLOW_COUNT_LOAD = 8
EV_OVERFLOW_COUNT_STORE = 9
EV_NEXT_LOAD = 10
EV_NEXT_STORE = 11
EV_TOP_LOAD = 12
EV_TOP_STORE = 13
EV_CURRENT_LOAD = 14
EV_READY_SELECT = 15
EV_YIELD_LOAD = 16
EV_PENDED_LOAD = 17
EV_PENDED_STORE = 18
EV_RESET_HELPER = 19
EV_ASSERT = 20


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


class RuntimeFreeRTOSTaskIncrementTickTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.profile_name = os.environ.get(
            "OPENCFW_TOOLCHAIN_PROFILE",
            "apple-clang" if sys.platform == "darwin" else "linux-clang",
        )
        if cls.profile_name not in TARGET_PROFILES:
            raise AssertionError(f"unreviewed toolchain profile {cls.profile_name!r}")
        cls.profile = TARGET_PROFILES[cls.profile_name]
        version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout
        if not version.startswith(str(cls.profile["version_prefix"])):
            raise AssertionError(
                f"compiler does not match {cls.profile_name}: {version!r}"
            )

        cls.candidate = cls.compile_host(
            temporary / library_name("runtime_tick_candidate"),
            CANDIDATE_FIXTURE,
            [],
        )
        cls.oracle = cls.compile_host(
            temporary / library_name("runtime_tick_oracle"),
            ORACLE_FIXTURE,
            [
                "-ffreestanding",
                "-fno-builtin",
                "-I",
                str(FREERTOS_CONFIG),
                "-I",
                str(FREERTOS_INCLUDE),
                "-I",
                str(FREERTOS_PORT),
            ],
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate, "open_cfw_candidate_freertos_task_increment_tick_"
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle, "open_cfw_oracle_freertos_task_increment_tick_"
        )

        cls.target_objects = [
            temporary / "runtime_tick_1.o",
            temporary / "runtime_tick_2.o",
        ]
        for target_object in cls.target_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(target_object)],
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
    def compile_host(cls, output: Path, source: Path, extra: list[str]):
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            *extra,
            str(source),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(output)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(output))

    @staticmethod
    def bind_api(library, prefix: str) -> dict[str, object]:
        api: dict[str, object] = {}
        signatures = {
            "reset": ([ctypes.c_uint32] * 3 + [ctypes.c_int32] * 2 +
                      [ctypes.c_uint32] * 4, None),
            "set_task": ([ctypes.c_uint32] * 3, None),
            "insert_delayed": ([ctypes.c_uint32] * 2, None),
            "insert_event": ([ctypes.c_uint32] * 2, None),
            "insert_ready": ([ctypes.c_uint32] * 2, None),
            "set_index": ([ctypes.c_uint32] * 2, None),
            "execute": ([], ctypes.c_int32),
            "get_tick": ([], ctypes.c_uint32),
            "get_suspended": ([], ctypes.c_uint32),
            "get_pended": ([], ctypes.c_uint32),
            "get_yield": ([], ctypes.c_int32),
            "get_overflow": ([], ctypes.c_int32),
            "get_next": ([], ctypes.c_uint32),
            "get_top": ([], ctypes.c_uint32),
            "get_delayed_selector": ([], ctypes.c_uint32),
            "get_assert_failures": ([], ctypes.c_uint32),
            "get_list_count": ([ctypes.c_uint32], ctypes.c_uint32),
            "get_list_index": ([ctypes.c_uint32], ctypes.c_uint32),
            "get_list_owner": ([ctypes.c_uint32] * 2, ctypes.c_uint32),
            "get_task_priority": ([ctypes.c_uint32], ctypes.c_uint32),
            "get_task_wake": ([ctypes.c_uint32], ctypes.c_uint32),
            "get_task_container": ([ctypes.c_uint32], ctypes.c_uint32),
            "get_event_container": ([ctypes.c_uint32], ctypes.c_uint32),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(library, prefix + name)
            function.argtypes = arguments
            function.restype = result
            api[name] = function
        return api

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    @staticmethod
    def apply(api: dict[str, object], operation: tuple) -> None:
        getattr(api[operation[0]], "__call__")(*operation[1:])

    @staticmethod
    def snapshot(api: dict[str, object]) -> dict:
        scalar_names = (
            "tick", "suspended", "pended", "yield", "overflow", "next",
            "top", "delayed_selector", "assert_failures",
        )
        kinds = [0, 1] + [READY + priority for priority in range(56)] + [
            EVENT + event for event in range(4)
        ]
        lists = {}
        for kind in kinds:
            count = api["get_list_count"](kind)
            lists[kind] = {
                "count": count,
                "index": api["get_list_index"](kind),
                "owners": [
                    api["get_list_owner"](kind, position)
                    for position in range(count)
                ],
            }
        return {
            "globals": {name: api["get_" + name]() for name in scalar_names},
            "lists": lists,
            "tasks": [
                (
                    api["get_task_priority"](identifier),
                    api["get_task_wake"](identifier),
                    api["get_task_container"](identifier),
                    api["get_event_container"](identifier),
                )
                for identifier in range(16)
            ],
        }

    def run_differential(
        self,
        reset: tuple[int, ...],
        operations: list[tuple],
        expected_result: int | None = None,
    ) -> dict:
        for api in (self.candidate_api, self.oracle_api):
            api["reset"](*reset)
            for operation in operations:
                self.apply(api, operation)
        candidate_result = self.candidate_api["execute"]()
        oracle_result = self.oracle_api["execute"]()
        self.assertEqual(candidate_result, oracle_result)
        if expected_result is not None:
            self.assertEqual(candidate_result, expected_result)
        candidate = self.snapshot(self.candidate_api)
        oracle = self.snapshot(self.oracle_api)
        self.assertEqual(candidate, oracle)
        return candidate

    def candidate_events(self) -> list[tuple[int, int, int]]:
        prefix = "open_cfw_candidate_freertos_task_increment_tick_get_event_"
        count = getattr(self.candidate, prefix + "count")
        count.argtypes = []
        count.restype = ctypes.c_uint32
        getters = []
        for suffix in ("kind", "subject", "value"):
            function = getattr(self.candidate, prefix + suffix)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32
            getters.append(function)
        return [tuple(function(index) for function in getters) for index in range(count())]

    def test_authenticated_sources_abi_and_pristine_oracle_are_pinned(self) -> None:
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE)), (SOURCE_SIZE, SOURCE_SHA256))
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER)), (HEADER_SIZE, HEADER_SHA256))
        self.assertEqual(
            (CANDIDATE_FIXTURE.stat().st_size, sha256(CANDIDATE_FIXTURE)),
            (CANDIDATE_FIXTURE_SIZE, CANDIDATE_FIXTURE_SHA256),
        )
        self.assertEqual(
            (ORACLE_FIXTURE.stat().st_size, sha256(ORACLE_FIXTURE)),
            (ORACLE_FIXTURE_SIZE, ORACLE_FIXTURE_SHA256),
        )
        self.assertEqual((UPSTREAM_TASKS.stat().st_size, sha256(UPSTREAM_TASKS)), (
            223_695,
            "14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463",
        ))
        verified = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verified.stdout)

        oracle = ORACLE_FIXTURE.read_text(encoding="utf-8")
        self.assertIn('../../third_party/freertos-kernel/tasks.c', oracle)
        self.assertIn("xTaskIncrementTick()", oracle)
        self.assertNotIn("constant_tick_count", oracle)
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("FreeRTOS Kernel V10.5.1", source)
        self.assertIn("def7d2df2b0506d3d249334974f51e427c17a41c", source)
        self.assertIn("[0x0045504C, 0x0045519E)", source)
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "OPEN_CFW_FREERTOS_TICK_CURRENT_TCB_ADDRESS = 0x20074A20U",
            "OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_POINTER_ADDRESS = 0x20074A24U",
            "OPEN_CFW_FREERTOS_TICK_OVERFLOW_LIST_POINTER_ADDRESS = 0x20074A28U",
            "OPEN_CFW_FREERTOS_TICK_COUNT_ADDRESS = 0x20074A34U",
            "OPEN_CFW_FREERTOS_TICK_TOP_READY_PRIORITY_ADDRESS = 0x20074A38U",
            "OPEN_CFW_FREERTOS_TICK_READY_LISTS_ADDRESS = 0x2006A49CU",
            "OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_1_ADDRESS = 0x20073CFCU",
            "OPEN_CFW_FREERTOS_TICK_DELAYED_LIST_2_ADDRESS = 0x20073D10U",
            "OPEN_CFW_FREERTOS_TICK_LIST_ITEM_SIZE = 0x14U",
            "OPEN_CFW_FREERTOS_TICK_TCB_PRIORITY_OFFSET = 0x2CU",
        ):
            self.assertIn(token, header)

    def test_official_body_globals_calls_and_topology_are_exact(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(
            hashlib.sha256(self.application).hexdigest(),
            "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701",
        )
        body = self.span(START, END)
        self.assertEqual((len(body), body.hex()), (338, STOCK_BYTES))
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        for address, value in LITERALS.items():
            self.assertEqual(struct.unpack("<I", self.span(address, address + 4))[0], value)

        outgoing = []
        for offset in range(0, len(body) - 3, 2):
            address = START + offset
            try:
                target = self.apollo_overlay.decode_thumb_branch(
                    address, body[offset:offset + 4], link=True
                )
            except self.apollo_overlay.BuildError:
                continue
            outgoing.append((address, target, body[offset:offset + 4].hex()))
        self.assertEqual(outgoing, [
            (0x00455076, 0x005FA0A4, "a5f115f8"),
            (0x0045509A, 0x00455876, "00f0ecfb"),
        ])

        callers = []
        jumps = []
        exterior_interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address, encoded, link=link
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target == START:
                    observed.append((address, encoded.hex()))
                if START < target < END and not START <= address < END:
                    exterior_interior.append((address, target, link, encoded.hex()))
        self.assertEqual(callers, CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(exterior_interior, [])
        self.assertEqual(
            hashlib.sha256(b"".join(struct.pack("<I", address) for address, _ in callers)).hexdigest(),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(b"".join(
                struct.pack("<I", address) + bytes.fromhex(encoded)
                for address, encoded in callers
            )).hexdigest(),
            CALLER_RECORD_SHA256,
        )

    def test_byte_granular_pointer_closure_is_only_six_unaligned_false_positives(self) -> None:
        candidates = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            normalized = value & ~1 if value & 1 else value
            if START <= normalized < END:
                candidates.append((BASE + offset, value, normalized))
        self.assertEqual(candidates, POINTER_CANDIDATES)
        self.assertTrue(all(location & 1 for location, _, _ in candidates))
        record = b"".join(struct.pack("<III", *candidate) for candidate in candidates)
        self.assertEqual(hashlib.sha256(record).hexdigest(), POINTER_RECORD_SHA256)

    def test_suspended_and_no_expiry_paths_match_and_preserve_access_order(self) -> None:
        state = self.run_differential(
            (0xFFFFFFFF, 1, 0xFFFFFFFF, 1, -7, 9, 3, 0, 0),
            [],
            0,
        )
        self.assertEqual(state["globals"]["pended"], 0)
        self.assertEqual(
            self.candidate_events(),
            [
                (EV_SUSPENDED_LOAD, 0, 1),
                (EV_PENDED_LOAD, 0, 0xFFFFFFFF),
                (EV_PENDED_STORE, 0, 0),
            ],
        )

        state = self.run_differential(
            (10, 0, 7, 0, 2, 100, 3, 0, 0),
            [("set_task", 0, 3, 0), ("insert_ready", 3, 0)],
            0,
        )
        self.assertEqual(state["globals"]["tick"], 11)
        self.assertEqual(
            self.candidate_events(),
            [
                (EV_SUSPENDED_LOAD, 0, 0),
                (EV_TICK_LOAD, 0, 10),
                (EV_TICK_STORE, 0, 11),
                (EV_NEXT_LOAD, 0, 100),
                (EV_CURRENT_LOAD, 0, 0),
                (EV_READY_SELECT, 3, 1),
                (EV_YIELD_LOAD, 0, 0),
            ],
        )

    def test_wrap_swaps_lists_resets_deadline_and_asserts_before_mutation(self) -> None:
        empty = self.run_differential(
            (0xFFFFFFFF, 0, 0, 0, 7, 123, 3, 0, 0),
            [("set_task", 0, 3, 0), ("insert_ready", 3, 0)],
            0,
        )
        self.assertEqual(empty["globals"]["delayed_selector"], 1)
        self.assertEqual(empty["globals"]["overflow"], 8)
        self.assertEqual(empty["globals"]["next"], 0xFFFFFFFF)
        kinds = [event[0] for event in self.candidate_events()]
        self.assertEqual(kinds[:13], [
            EV_SUSPENDED_LOAD, EV_TICK_LOAD, EV_TICK_STORE,
            EV_DELAYED_LOAD, EV_DELAYED_LOAD, EV_OVERFLOW_LOAD,
            EV_DELAYED_STORE, EV_OVERFLOW_STORE,
            EV_OVERFLOW_COUNT_LOAD, EV_OVERFLOW_COUNT_STORE,
            EV_RESET_HELPER, EV_NEXT_LOAD, EV_CURRENT_LOAD,
        ])

        nonempty = self.run_differential(
            (0xFFFFFFFF, 0, 0, 0, 0, 77, 3, 0, 0),
            [
                ("set_task", 0, 3, 0),
                ("insert_ready", 3, 0),
                ("set_task", 1, 4, 5),
                ("insert_delayed", 1, 1),
            ],
            0,
        )
        self.assertEqual(nonempty["globals"]["delayed_selector"], 1)
        self.assertEqual(nonempty["globals"]["next"], 5)

        api = self.candidate_api
        api["reset"](0xFFFFFFFF, 0, 0, 0, 0, 9, 3, 0, 0)
        for operation in (
            ("set_task", 0, 3, 0),
            ("insert_ready", 3, 0),
            ("set_task", 1, 2, 0xFFFFFFFF),
            ("insert_delayed", 0, 1),
        ):
            self.apply(api, operation)
        self.assertEqual(api["execute"](), -0x80000000)
        self.assertEqual(api["get_assert_failures"](), 1)
        self.assertEqual(api["get_delayed_selector"](), 0)
        self.assertEqual(api["get_overflow"](), 0)
        self.assertEqual([event[0] for event in self.candidate_events()][-1], EV_ASSERT)

    def test_delayed_expiry_event_removal_priorities_and_future_head_match(self) -> None:
        # Equal priority does not set the immediate preemption flag, but the
        # newly readied peer makes the time-slice check request a switch.
        for priority, expected in ((4, 1), (3, 1), (2, 0)):
            with self.subTest(priority=priority):
                state = self.run_differential(
                    (9, 0, 0, 0, 0, 10, 3, 0, 0),
                    [
                        ("set_task", 0, 3, 0),
                        ("insert_ready", 3, 0),
                        ("set_task", 1, priority, 10),
                        ("insert_delayed", 0, 1),
                        ("insert_event", 0, 1),
                    ],
                    expected,
                )
                self.assertEqual(state["tasks"][1][2], READY + priority)
                self.assertEqual(state["tasks"][1][3], NULL)
                self.assertEqual(state["globals"]["next"], 0xFFFFFFFF)
                self.assertEqual(state["globals"]["top"], max(3, priority))

        future = self.run_differential(
            (9, 0, 0, 0, 0, 1, 3, 0, 0),
            [
                ("set_task", 0, 3, 0),
                ("insert_ready", 3, 0),
                ("set_task", 1, 2, 20),
                ("insert_delayed", 0, 1),
            ],
            0,
        )
        self.assertEqual(future["globals"]["next"], 20)
        self.assertEqual(future["tasks"][1][2], 0)

    def test_multiple_due_tasks_index_repair_and_non_sentinel_ready_index_match(self) -> None:
        state = self.run_differential(
            (9, 0, 0, 0, 0, 8, 3, 0, 0),
            [
                ("set_task", 0, 3, 0),
                ("insert_ready", 3, 0),
                ("set_task", 1, 4, 8),
                ("insert_delayed", 0, 1),
                ("insert_event", 0, 1),
                ("set_task", 2, 4, 10),
                ("insert_delayed", 0, 2),
                ("insert_event", 0, 2),
                ("set_task", 3, 2, 20),
                ("insert_delayed", 0, 3),
                ("set_task", 4, 4, 0),
                ("insert_ready", 4, 4),
                ("set_index", 0, 2),
                ("set_index", EVENT, 2),
                ("set_index", READY + 4, 4),
            ],
            1,
        )
        self.assertEqual(state["lists"][0]["owners"], [3])
        self.assertEqual(state["lists"][0]["index"], SENTINEL)
        self.assertEqual(state["lists"][EVENT]["count"], 0)
        self.assertEqual(state["lists"][EVENT]["index"], SENTINEL)
        self.assertEqual(state["lists"][READY + 4]["owners"], [1, 2, 4])
        self.assertEqual(state["lists"][READY + 4]["index"], 4)
        self.assertEqual(state["globals"]["next"], 20)

    def test_time_slicing_and_yield_pending_force_switch(self) -> None:
        common = [("set_task", 0, 3, 0), ("insert_ready", 3, 0)]
        self.run_differential((1, 0, 0, 0, 0, 100, 3, 0, 0), common, 0)
        self.run_differential(
            (1, 0, 0, 0, 0, 100, 3, 0, 0),
            common + [("set_task", 1, 3, 0), ("insert_ready", 3, 1)],
            1,
        )
        self.run_differential((1, 0, 0, 1, 0, 100, 3, 0, 0), common, 1)

    def test_target_profiles_are_exact_deterministic_and_relocation_bounded(self) -> None:
        parsed = []
        for object_path in self.target_objects:
            data, sections = self.apollo_overlay.parse_elf32(object_path)
            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            section = self.apollo_overlay.section_named(
                sections, f".text.{FUNCTION}"
            )
            leaf = data[
                int(section["offset"]):int(section["offset"]) + int(section["size"])
            ]
            self.assertEqual(int(section["alignment"]), 4)
            self.assertEqual((len(leaf), leaf.hex()), (
                int(self.profile["size"]), str(self.profile["bytes"])
            ))
            self.assertEqual(hashlib.sha256(leaf).hexdigest(), self.profile["sha256"])
            function_symbols = [
                symbol for symbol in symbols
                if symbol["name"] == FUNCTION and int(symbol["type"]) == 2
            ]
            self.assertEqual(len(function_symbols), 1)
            self.assertEqual(int(function_symbols[0]["value"]), 1)
            self.assertEqual(int(function_symbols[0]["size"]), len(leaf))

            relocations = []
            all_relocations = []
            for relocation_section in sections:
                if int(relocation_section["type"]) != 9:
                    continue
                for index in range(
                    int(relocation_section["size"]) // int(relocation_section["entry_size"])
                ):
                    offset, info = struct.unpack_from(
                        "<II",
                        data,
                        int(relocation_section["offset"]) + index * 8,
                    )
                    record = (
                        str(relocation_section["name"]),
                        offset,
                        info & 0xFF,
                        str(symbols[info >> 8]["name"]),
                    )
                    all_relocations.append(record)
                    if int(relocation_section["info"]) == int(section["index"]):
                        relocations.append(record[1:])
            self.assertEqual(relocations, self.profile["relocations"])
            self.assertEqual(
                [record for record in all_relocations if record not in [
                    (f".rel.text.{FUNCTION}", *relocation)
                    for relocation in self.profile["relocations"]
                ]],
                [(f".rel.ARM.exidx.text.{FUNCTION}", 0, 42, "")],
            )
            self.assertEqual(
                {
                    symbol["name"] for symbol in symbols
                    if symbol["name"] and int(symbol["section_index"]) == 0
                },
                {
                    "ulSetInterruptMask",
                    "open_cfw_freertos_task_reset_next_task_unblock_time",
                },
            )
            self.assertEqual(
                [
                    section["name"] for section in sections
                    if int(section["flags"]) & 0x3 == 0x3 and int(section["size"])
                ],
                [],
            )
            parsed.append((leaf, all_relocations))
        self.assertEqual(parsed[0], parsed[1])
        self.assertEqual(self.target_objects[0].read_bytes(), self.target_objects[1].read_bytes())

    def test_source_is_registered_in_production_inputs(self) -> None:
        overlay = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        manifest = json.loads(CORE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
        serialized = json.dumps([overlay, manifest], sort_keys=True)
        self.assertIn(SOURCE.name, serialized)
        self.assertIn(FUNCTION, serialized)
        self.assertIn(
            "freertos_task_increment_tick_source_replacement",
            serialized,
        )
        self.assertIn(
            "apollo_freertos_task_increment_tick_source_leaf",
            serialized,
        )


if __name__ == "__main__":
    unittest.main()
