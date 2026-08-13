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
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_port_start_scheduler.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_port_start_scheduler_host.c"
AUDIT = ROOT / "docs/research/freertos-port-start-scheduler-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
UPSTREAM = ROOT / "third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure/port.c"
PROVENANCE = ROOT / "third_party/freertos-kernel/PROVENANCE.json"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000
FUNCTION = "open_cfw_freertos_port_start_scheduler"

STOCK_START = 0x0044_21E2
STOCK_END = 0x0044_2210
STOCK_SHA256 = "66bacaafa2fa8e76a548eb9da62c2d3e1f058a471efe0bdfa072f59bf38ae1c0"
STOCK_CALLERS = (0x0045_4D5A,)
STOCK_OUTGOING_CALLS = (
    (0x0044_21F6, 0x0045_643E),
    (0x0044_2200, 0x005F_A08C),
    (0x0044_2204, 0x0045_51B4),
    (0x0044_2208, 0x0044_207C),
)

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

RELOCATIONS = [
    (2, 47, "open_cfw_retained_freertos_system_handler_priority"),
    (6, 48, "open_cfw_retained_freertos_system_handler_priority"),
    (26, 10, "open_cfw_retained_freertos_timer_interrupt_setup"),
    (30, 47, "open_cfw_retained_freertos_critical_nesting"),
    (34, 48, "open_cfw_retained_freertos_critical_nesting"),
    (42, 10, "open_cfw_retained_freertos_start_first_task"),
    (46, 10, "open_cfw_retained_freertos_task_switch_context"),
    (50, 10, "open_cfw_retained_freertos_task_exit_error"),
]

UNDEFINED = [
    "open_cfw_retained_freertos_critical_nesting",
    "open_cfw_retained_freertos_start_first_task",
    "open_cfw_retained_freertos_system_handler_priority",
    "open_cfw_retained_freertos_task_exit_error",
    "open_cfw_retained_freertos_task_switch_context",
    "open_cfw_retained_freertos_timer_interrupt_setup",
]

TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (1484, "a7accfc2d0e6f3b92c7705cd61e7a233f45a5e35c091f9764841ddd03c64e790"),
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (1464, "2fb45e4c57f9fedbdbfb15813a891c2ecca7c256b0f387c39988785ad6304cf7"),
    },
}

FUNCTION_PIN = (58, 4, "c02d239a4f345d45184ae3f9720abd43d28fff09c6b8ae5e51db75940cf51a88")
LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (1409, "9eb813ef59b4cedb5f7626b61f5d82f027e215ccf39b0b7d10677728e4c853ca"),
    HEADER: (719, "9716209bc68631c39e726d58bb20e9be122c63112fb399b270d2699bef6b8c33"),
    FIXTURE: (2300, "5db8911757423bd30371c179db31d36664cb77ba3aa5fc5c0d353c369caec68b"),
    AUDIT: (2675, "25a8ae992cb386370f20b3a4be7a86053e4b0061e63741ed2e4ddfc243af6ef3"),
}


class FreeRTOSPortStartSchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("port_start.dylib" if sys.platform == "darwin" else "port_start.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_freertos_port_start_reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_freertos_port_start_scheduler.restype = ctypes.c_int32
        cls.target_object = temp / "port_start.o"
        subprocess.run([clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target_object)], check=True, capture_output=True, text=True)
        cls.version = subprocess.run([clang, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
        cls.target = cls.parse_target(cls.target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def u32(cls, name: str) -> int:
        return ctypes.c_uint32.in_dll(cls.loaded, name).value

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
        return {
            "object": (len(data), hashlib.sha256(data).hexdigest()),
            "function": (len(body), int(section["alignment"]), hashlib.sha256(body).hexdigest()),
            "relocations": relocations,
            "undefined": sorted(name for name, fields in symbols if name and fields[5] == 0),
        }

    def test_priority_setup_timer_and_first_task_order(self) -> None:
        self.loaded.open_cfw_test_freertos_port_start_reset(0x1234_5678, 7)
        self.assertEqual(self.loaded.open_cfw_freertos_port_start_scheduler(), 0)
        count = self.u32("open_cfw_test_freertos_port_start_event_count")
        events = (ctypes.c_uint32 * count).in_dll(self.loaded, "open_cfw_test_freertos_port_start_events")
        self.assertEqual(list(events), [1, 2, 3, 4])
        self.assertEqual(self.u32("open_cfw_retained_freertos_system_handler_priority"), 0xFFFF_5678)
        self.assertEqual(self.u32("open_cfw_test_freertos_port_start_timer_priority"), 0xFFFF_5678)
        self.assertEqual(self.u32("open_cfw_test_freertos_port_start_first_task_priority"), 0xFFFF_5678)
        self.assertEqual(self.u32("open_cfw_test_freertos_port_start_first_task_nesting"), 0)
        self.assertEqual(self.u32("open_cfw_retained_freertos_critical_nesting"), 0)

    def test_priority_or_operations_preserve_unrelated_bits(self) -> None:
        for initial, expected in ((0, 0xFFFF_0000), (0x0000_FFFF, 0xFFFF_FFFF), (0xA500_005A, 0xFFFF_005A)):
            with self.subTest(initial=initial):
                self.loaded.open_cfw_test_freertos_port_start_reset(initial, 0xFFFF_FFFF)
                self.loaded.open_cfw_freertos_port_start_scheduler()
                self.assertEqual(self.u32("open_cfw_retained_freertos_system_handler_priority"), expected)

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

    def test_stock_span_call_graph_and_fixed_globals_are_exact(self) -> None:
        body = self.application[STOCK_START - BASE:STOCK_END - BASE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (46, STOCK_SHA256))
        callers = tuple(BASE + offset for offset in range(0, len(self.application) - 3, 2) if self.decode_bl(self.application, BASE + offset) == STOCK_START)
        self.assertEqual(callers, STOCK_CALLERS)
        outgoing = tuple((address, target) for address in range(STOCK_START, STOCK_END, 2) if (target := self.decode_bl(self.application, address)) is not None)
        self.assertEqual(outgoing, STOCK_OUTGOING_CALLS)
        raw = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if STOCK_START <= (value & ~1) < STOCK_END:
                raw.append((BASE + offset, value))
        self.assertEqual(raw, [])
        self.assertEqual(struct.unpack_from("<I", self.application, 0x0044_2224 - BASE)[0], 0xE000_ED20)
        self.assertEqual(struct.unpack_from("<I", self.application, 0x0044_2210 - BASE)[0], 0x2000_309C)

    def test_authenticated_upstream_port_source_and_commit_are_present(self) -> None:
        source = UPSTREAM.read_text()
        start = source.index("BaseType_t xPortStartScheduler( void )")
        end = source.index("void vPortEndScheduler( void )", start)
        body = source[start:end]
        for token in (
            "portNVIC_SHPR3_REG |= portNVIC_PENDSV_PRI",
            "portNVIC_SHPR3_REG |= portNVIC_SYSTICK_PRI",
            "vPortSetupTimerInterrupt",
            "ulCriticalNesting = 0",
            "vStartFirstTask",
            "vTaskSwitchContext",
            "prvTaskExitError",
            "return 0",
        ):
            self.assertIn(token, body)
        self.assertIn("def7d2df2b0506d3d249334974f51e427c17a41c", PROVENANCE.read_text())

    def test_target_object_is_dual_profile_pinned(self) -> None:
        profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        pin = TARGET_PINS[profile]
        self.assertEqual(self.version, pin["version"])
        self.assertEqual(self.target["object"], pin["object"])
        self.assertEqual(self.target["function"], FUNCTION_PIN)
        self.assertEqual(self.target["relocations"], RELOCATIONS)
        self.assertEqual(self.target["undefined"], UNDEFINED)

    def test_artifacts_are_pinned_and_production_excluded(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            body = path.read_bytes()
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (size, digest))
        forbidden = (SOURCE.name, HEADER.name, FUNCTION)
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text()
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
