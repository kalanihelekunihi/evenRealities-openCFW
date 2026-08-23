from __future__ import annotations

import ctypes
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_task_start_scheduler.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_task_start_scheduler_host.c"
AUDIT = ROOT / "docs/research/freertos-task-start-scheduler-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
UPSTREAM = ROOT / "third_party/freertos-kernel/tasks.c"
PROVENANCE = ROOT / "third_party/freertos-kernel/PROVENANCE.json"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000
FUNCTION = "open_cfw_freertos_task_start_scheduler"

STOCK_START = 0x0045_4CEC
STOCK_END = 0x0045_4D7C
STOCK_SHA256 = "2fabf4882dc6db88c73cd573ba3f454e7f6f0cafb1329670ad52e39ef1cbe01d"
STOCK_CALLERS = (0x0044_90BE,)
STOCK_OUTGOING_CALLS = (
    (0x0045_4CFE, 0x0048_D558),
    (0x0045_4D1E, 0x0045_4820),
    (0x0045_4D34, 0x0047_E674),
    (0x0045_4D3C, 0x005F_A0A4),
    (0x0045_4D5A, 0x0044_21E2),
    (0x0045_4D6E, 0x005F_A0A4),
)
RAW_INTERIOR_WORD_CANDIDATES = (
    (0x004A_498B, 0x0045_4D20),
    (0x0074_889D, 0x0045_4D49),
    (0x0074_F1C8, 0x0045_4D49),
    (0x0075_ED8A, 0x0045_4D41),
    (0x0076_168A, 0x0045_4D41),
    (0x0077_2AAC, 0x0045_4D55),
    (0x0077_2E47, 0x0045_4D55),
    (0x0077_3C62, 0x0045_4D55),
    (0x0077_5D30, 0x0045_4D55),
    (0x0077_CFD7, 0x0045_4D55),
    (0x0078_D1E8, 0x0045_4D41),
)

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

TARGET_UNDEFINED = [
    "open_cfw_freertos_port_start_scheduler",
    "open_cfw_freertos_start_assert_failure",
    "open_cfw_retained_freertos_idle_task_entry",
    "open_cfw_retained_freertos_idle_task_handle",
    "open_cfw_retained_freertos_idle_task_memory_get",
    "open_cfw_retained_freertos_idle_task_name",
    "open_cfw_retained_freertos_interrupt_mask_set",
    "open_cfw_retained_freertos_next_task_unblock_time",
    "open_cfw_retained_freertos_scheduler_running",
    "open_cfw_retained_freertos_task_create_static",
    "open_cfw_retained_freertos_tick_count",
    "open_cfw_retained_freertos_timer_task_create",
    "open_cfw_retained_freertos_top_used_priority",
]

TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (2084, "5bf5adfe142611efd28f4fb77d645f62011ee54330934ce52a6547ddd030f020"),
        "function": (156, 4, "64d46ee081e3b16e4542d19d8236139ebe014cb3d9419d21e009ecd617c3ab9b"),
        "relocations": [
            (18, 10, "open_cfw_retained_freertos_idle_task_memory_get"),
            (34, 49, "open_cfw_retained_freertos_idle_task_entry"),
            (38, 50, "open_cfw_retained_freertos_idle_task_entry"),
            (42, 49, "open_cfw_retained_freertos_idle_task_name"),
            (46, 50, "open_cfw_retained_freertos_idle_task_name"),
            (56, 10, "open_cfw_retained_freertos_task_create_static"),
            (60, 47, "open_cfw_retained_freertos_idle_task_handle"),
            (64, 48, "open_cfw_retained_freertos_idle_task_handle"),
            (74, 10, "open_cfw_retained_freertos_timer_task_create"),
            (86, 10, "open_cfw_retained_freertos_interrupt_mask_set"),
            (90, 47, "open_cfw_retained_freertos_next_task_unblock_time"),
            (94, 48, "open_cfw_retained_freertos_next_task_unblock_time"),
            (104, 47, "open_cfw_retained_freertos_scheduler_running"),
            (108, 48, "open_cfw_retained_freertos_scheduler_running"),
            (116, 47, "open_cfw_retained_freertos_tick_count"),
            (120, 48, "open_cfw_retained_freertos_tick_count"),
            (128, 10, "open_cfw_freertos_port_start_scheduler"),
            (134, 10, "open_cfw_freertos_start_assert_failure"),
            (140, 49, "open_cfw_retained_freertos_top_used_priority"),
            (144, 50, "open_cfw_retained_freertos_top_used_priority"),
        ],
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (2068, "2589c03f5abe1208bfa198d1a5cd36c85760e027100ef2d56f56452fe9f6b19e"),
        "function": (160, 4, "d6f533bac74d68ad545b70f022de3c922e2f678ed2a6557b9f8a57341a52cf02"),
        "relocations": [
            (18, 10, "open_cfw_retained_freertos_idle_task_memory_get"),
            (34, 49, "open_cfw_retained_freertos_idle_task_entry"),
            (38, 50, "open_cfw_retained_freertos_idle_task_entry"),
            (42, 49, "open_cfw_retained_freertos_idle_task_name"),
            (46, 50, "open_cfw_retained_freertos_idle_task_name"),
            (60, 10, "open_cfw_retained_freertos_task_create_static"),
            (64, 47, "open_cfw_retained_freertos_idle_task_handle"),
            (68, 48, "open_cfw_retained_freertos_idle_task_handle"),
            (78, 10, "open_cfw_retained_freertos_timer_task_create"),
            (90, 10, "open_cfw_retained_freertos_interrupt_mask_set"),
            (94, 47, "open_cfw_retained_freertos_next_task_unblock_time"),
            (98, 48, "open_cfw_retained_freertos_next_task_unblock_time"),
            (108, 47, "open_cfw_retained_freertos_scheduler_running"),
            (112, 48, "open_cfw_retained_freertos_scheduler_running"),
            (120, 47, "open_cfw_retained_freertos_tick_count"),
            (124, 48, "open_cfw_retained_freertos_tick_count"),
            (132, 10, "open_cfw_freertos_port_start_scheduler"),
            (138, 10, "open_cfw_freertos_start_assert_failure"),
            (144, 49, "open_cfw_retained_freertos_top_used_priority"),
            (148, 50, "open_cfw_retained_freertos_top_used_priority"),
        ],
    },
}

LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (3427, "aa0d3c9e1c2168cdd2dab95014363f6f3b69d9e77b0def2b47cf42932c1055b5"),
    HEADER: (1124, "7805df41dc3eea1cbbb9821b3c598c3e9615480bebe8857d10ab923d610d257c"),
    FIXTURE: (5635, "ca6678e80b3aee90b8a685a7bca9a479f71c0d141553714693b362a12a03d0f2"),
    AUDIT: (4422, "8ffa42334f71102dcd03441cd4a0efd1bcf955b6daeb22ce1377a4d82724ed34"),
}


class FreeRTOSTaskStartSchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("scheduler.dylib" if sys.platform == "darwin" else "scheduler.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_freertos_start_reset.argtypes = [ctypes.c_uint32, ctypes.c_int32]
        cls.target_object = temp / "scheduler.o"
        subprocess.run([clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target_object)], check=True, capture_output=True, text=True)
        cls.version = subprocess.run([clang, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
        cls.target = cls.parse_target(cls.target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def u32(cls, name: str) -> int:
        return ctypes.c_uint32.in_dll(cls.loaded, name).value

    @classmethod
    def i32(cls, name: str) -> int:
        return ctypes.c_int32.in_dll(cls.loaded, name).value

    @classmethod
    def events(cls) -> list[int]:
        count = cls.u32("open_cfw_test_freertos_start_event_count")
        values = (ctypes.c_uint32 * count).in_dll(cls.loaded, "open_cfw_test_freertos_start_events")
        return list(values)

    @staticmethod
    def parse_target(path: Path) -> dict[str, object]:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        data, sections = apollo_overlay.parse_elf32(path)
        symtab = apollo_overlay.section_named(sections, ".symtab")
        strtab = sections[int(symtab["link"])]
        strings = data[int(strtab["offset"]):int(strtab["offset"]) + int(strtab["size"])]
        symbols = []
        for index in range(int(symtab["size"]) // 16):
            fields = struct.unpack_from("<IIIBBH", data, int(symtab["offset"]) + index * 16)
            symbols.append((apollo_overlay.elf_string(strings, fields[0], "symbol"), fields))
        section = apollo_overlay.section_named(sections, ".text." + FUNCTION)
        body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
        relocations = []
        for relsec in sections:
            if int(relsec["type"]) == 9 and int(relsec["info"]) == int(section["index"]):
                for index in range(int(relsec["size"]) // 8):
                    offset, info = struct.unpack_from("<II", data, int(relsec["offset"]) + index * 8)
                    relocations.append((offset, info & 0xFF, symbols[info >> 8][0]))
        undefined = sorted(name for name, fields in symbols if name and fields[5] == 0)
        return {
            "object": (len(data), hashlib.sha256(data).hexdigest()),
            "function": (len(body), int(section["alignment"]), hashlib.sha256(body).hexdigest()),
            "relocations": relocations,
            "undefined": undefined,
        }

    def test_success_creates_both_tasks_then_publishes_scheduler_state(self) -> None:
        self.loaded.open_cfw_test_freertos_start_reset(1, 1)
        self.loaded.open_cfw_freertos_task_start_scheduler()
        self.assertEqual(self.events(), [1, 2, 3, 4, 5])
        self.assertEqual(ctypes.c_void_p.in_dll(self.loaded, "open_cfw_retained_freertos_idle_task_handle").value, 0x3333_3333)
        self.assertTrue(self.u32("open_cfw_test_freertos_start_created_entry"))
        self.assertEqual(ctypes.c_char_p.in_dll(self.loaded, "open_cfw_test_freertos_start_created_name").value, b"IDLE")
        self.assertEqual(self.u32("open_cfw_test_freertos_start_created_depth"), 0x2468)
        self.assertEqual(self.u32("open_cfw_test_freertos_start_created_argument"), 0)
        self.assertEqual(self.u32("open_cfw_test_freertos_start_created_priority"), 0)
        self.assertEqual(self.u32("open_cfw_test_freertos_start_created_stack"), 0x1111_1110)
        self.assertEqual(self.u32("open_cfw_test_freertos_start_created_tcb"), 0x2222_2220)
        self.assertEqual(self.u32("open_cfw_test_freertos_start_port_next_unblock"), 0xFFFF_FFFF)
        self.assertEqual(self.i32("open_cfw_test_freertos_start_port_running"), 1)
        self.assertEqual(self.u32("open_cfw_test_freertos_start_port_tick"), 0)

    def test_idle_creation_failure_skips_timer_and_port(self) -> None:
        self.loaded.open_cfw_test_freertos_start_reset(0, 1)
        self.loaded.open_cfw_freertos_task_start_scheduler()
        self.assertEqual(self.events(), [1, 2])
        self.assertEqual(self.u32("open_cfw_retained_freertos_next_task_unblock_time"), 0x1234_5678)
        self.assertEqual(self.u32("open_cfw_retained_freertos_tick_count"), 0x8765_4321)

    def test_timer_zero_failure_returns_without_assert_or_state_writes(self) -> None:
        self.loaded.open_cfw_test_freertos_start_reset(1, 0)
        self.loaded.open_cfw_freertos_task_start_scheduler()
        self.assertEqual(self.events(), [1, 2, 3])
        self.assertEqual(self.i32("open_cfw_retained_freertos_scheduler_running"), 0)

    def test_timer_allocation_failure_takes_assert_seam(self) -> None:
        self.loaded.open_cfw_test_freertos_start_reset(1, -1)
        self.loaded.open_cfw_freertos_task_start_scheduler()
        self.assertEqual(self.events(), [1, 2, 3, 6])
        self.assertEqual(self.i32("open_cfw_retained_freertos_scheduler_running"), 0)

    @staticmethod
    def decode_bl(application: bytes, address: int) -> int | None:
        first, second = struct.unpack_from("<HH", application, address - BASE)
        if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
            return None
        sign = first >> 10 & 1; i10 = first & 0x3FF; j1 = second >> 13 & 1; j2 = second >> 11 & 1; i11 = second & 0x7FF
        i1 = (~(j1 ^ sign)) & 1; i2 = (~(j2 ^ sign)) & 1
        immediate = sign << 24 | i1 << 23 | i2 << 22 | i10 << 12 | i11 << 1
        if sign: immediate -= 1 << 25
        return address + 4 + immediate

    def test_stock_span_call_graph_globals_and_idle_memory_are_exact(self) -> None:
        body = self.application[STOCK_START - BASE:STOCK_END - BASE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (144, STOCK_SHA256))
        callers = tuple(
            BASE + offset
            for offset in range(0, len(self.application) - 3, 2)
            if self.decode_bl(self.application, BASE + offset) == STOCK_START
        )
        self.assertEqual(callers, STOCK_CALLERS)
        outgoing = tuple(
            (address, target)
            for address in range(STOCK_START, STOCK_END, 2)
            if (target := self.decode_bl(self.application, address)) is not None
        )
        self.assertEqual(outgoing, STOCK_OUTGOING_CALLS)
        raw_candidates = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if STOCK_START <= (value & ~1) < STOCK_END:
                raw_candidates.append((BASE + offset, value))
        self.assertEqual(tuple(raw_candidates), RAW_INTERIOR_WORD_CANDIDATES)
        self.assertEqual(
            tuple(struct.unpack_from("<I", self.application, address - BASE)[0] for address in (0x45571C, 0x455720, 0x455724, 0x455314, 0x45546C, 0x4558C8)),
            (0x20074A54, 0x0078EAA4, 0x20074A50, 0x20074A3C, 0x20074A34, 0x20003DA0),
        )
        self.assertEqual(self.application[0x0078_EAA4 - BASE:0x0078_EAA9 - BASE], b"IDLE\0")
        self.assertEqual(self.application[0x0048_D558 - BASE:0x0048_D568 - BASE].hex(), "034b0360034808604ff4806010607047")
        self.assertEqual(tuple(struct.unpack_from("<II", self.application, 0x0048_D568 - BASE)), (0x20071E30, 0x2005F154))

    def test_authenticated_upstream_scheduler_source_and_commit_are_present(self) -> None:
        source = UPSTREAM.read_text()
        start = source.index("void vTaskStartScheduler( void )")
        end = source.index("void vTaskEndScheduler( void )", start)
        body = source[start:end]
        for token in (
            "vApplicationGetIdleTaskMemory",
            "xTaskCreateStatic",
            "xTimerCreateTimerTask",
            "xNextTaskUnblockTime = portMAX_DELAY",
            "xSchedulerRunning = pdTRUE",
            "xTickCount = ( TickType_t ) configINITIAL_TICK_COUNT",
            "xPortStartScheduler",
            "xReturn != errCOULD_NOT_ALLOCATE_REQUIRED_MEMORY",
            "uxTopUsedPriority",
        ):
            self.assertIn(token, body)
        self.assertIn("def7d2df2b0506d3d249334974f51e427c17a41c", PROVENANCE.read_text())

    def test_target_object_is_dual_profile_pinned(self) -> None:
        profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        pin = TARGET_PINS[profile]
        self.assertEqual(self.version, pin["version"])
        self.assertEqual(self.target["object"], pin["object"])
        self.assertEqual(self.target["function"], pin["function"])
        self.assertEqual(self.target["relocations"], pin["relocations"])
        self.assertEqual(self.target["undefined"], TARGET_UNDEFINED)

    def test_artifacts_are_pinned_and_production_routed(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            body = path.read_bytes()
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (size, digest))
        self.assertIn(str(SOURCE.relative_to(ROOT)), OVERLAY.read_text())
        self.assertIn(FUNCTION, OVERLAY.read_text())
        self.assertIn("freertos-scheduler-start-core-closure", MAKEFILE.read_text())
        self.assertIn("freertos_task_start_scheduler_source_text", MANIFEST.read_text())


if __name__ == "__main__":
    unittest.main()
