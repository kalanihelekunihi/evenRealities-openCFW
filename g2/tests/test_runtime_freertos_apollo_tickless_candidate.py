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
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_apollo_tickless_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_apollo_tickless_candidate_host.c"
AUDIT = ROOT / "docs/research/freertos-apollo-tickless-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000
FUNCTION = "open_cfw_freertos_apollo_suppress_ticks_and_sleep"

STOCK_START = 0x0045_6498
STOCK_END = 0x0045_655C
STOCK_SHA256 = "d6716a7a132b61665a401d513ce75119e5210640f69f5d16424067cb4216e8da"
STOCK_CALLERS = (0x0045_55FC,)
STOCK_OUTGOING_CALLS = (
    (0x4564B2, 0x455648),
    (0x4564BE, 0x48D654),
    (0x4564E4, 0x48D670),
    (0x4564EA, 0x46D836),
    (0x4564FE, 0x46D856),
    (0x456502, 0x48D654),
    (0x456534, 0x48D6E6),
    (0x45653A, 0x456374),
    (0x456546, 0x48D670),
    (0x456552, 0x454FD8),
)

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

RELOCATIONS = [
    (4, 47, "open_cfw_retained_freertos_stimer_max_suppressed_ticks"),
    (8, 48, "open_cfw_retained_freertos_stimer_max_suppressed_ticks"),
    (22, 10, "open_cfw_retained_freertos_global_interrupt_disable"),
    (26, 10, "open_cfw_retained_freertos_confirm_sleep_mode_status"),
    (34, 10, "open_cfw_retained_freertos_stimer_counter_get"),
    (38, 47, "open_cfw_retained_freertos_stimer_last_compare"),
    (42, 48, "open_cfw_retained_freertos_stimer_last_compare"),
    (48, 47, "open_cfw_retained_freertos_stimer_counts_per_tick"),
    (54, 48, "open_cfw_retained_freertos_stimer_counts_per_tick"),
    (76, 10, "open_cfw_retained_freertos_stimer_compare_delta_set"),
    (82, 10, "open_cfw_retained_freertos_pre_sleep_processing"),
    (90, 10, "open_cfw_retained_freertos_wait_for_interrupt"),
    (96, 10, "open_cfw_retained_freertos_post_sleep_processing"),
    (100, 10, "open_cfw_retained_freertos_stimer_counter_get"),
    (150, 10, "open_cfw_retained_freertos_stimer_interrupt_clear"),
    (156, 10, "open_cfw_retained_freertos_nvic_pending_clear"),
    (168, 10, "open_cfw_retained_freertos_stimer_compare_delta_set"),
    (180, 10, "open_cfw_freertos_task_step_tick"),
    (188, 30, "open_cfw_retained_freertos_global_interrupt_enable"),
]

UNDEFINED = [
    "open_cfw_freertos_task_step_tick",
    "open_cfw_retained_freertos_confirm_sleep_mode_status",
    "open_cfw_retained_freertos_global_interrupt_disable",
    "open_cfw_retained_freertos_global_interrupt_enable",
    "open_cfw_retained_freertos_nvic_pending_clear",
    "open_cfw_retained_freertos_post_sleep_processing",
    "open_cfw_retained_freertos_pre_sleep_processing",
    "open_cfw_retained_freertos_stimer_compare_delta_set",
    "open_cfw_retained_freertos_stimer_counter_get",
    "open_cfw_retained_freertos_stimer_counts_per_tick",
    "open_cfw_retained_freertos_stimer_interrupt_clear",
    "open_cfw_retained_freertos_stimer_last_compare",
    "open_cfw_retained_freertos_stimer_max_suppressed_ticks",
    "open_cfw_retained_freertos_wait_for_interrupt",
]

TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (2260, "d48efce527610f422d19a33e43f89e37b0f26811d18002e7025a18b8e3ed00c4"),
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (2240, "75211fd04388f5987a0eec5d148d2fbf2f17d96bbd0909cd2bd30d688b256bbd"),
    },
}

FUNCTION_PIN = (192, 4, "253c0ab060d9ed9eee8c73e89e028b17c5eb61b810410fe00a106b0d51ab265b")
LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (4463, "324c6e43793113bef6b562f43bfed6e47bbd2a837bff1e6acce1aa038152cf46"),
    HEADER: (808, "1683cb8288c9e489337c615421399a9b532cad44eb698adc7d595b542ad60d3c"),
    FIXTURE: (3939, "4aa097e5f1f91242efe40300e6586aab2d2405c641b4e4e456857713e3ca6499"),
    AUDIT: (2598, "c9d298b62c7f6ea7dab46b98849e7878b9660ff08b88bd8a8bd7cc14835c060c"),
}


class FreeRTOSApolloTicklessCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("tickless.dylib" if sys.platform == "darwin" else "tickless.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_freertos_tickless_reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_freertos_apollo_suppress_ticks_and_sleep.argtypes = [ctypes.c_uint32]
        cls.target_object = temp / "tickless.o"
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
    def trace(cls) -> tuple[list[int], list[int]]:
        count = cls.u32("open_cfw_test_freertos_tickless_event_count")
        events = list((ctypes.c_uint32 * count).in_dll(cls.loaded, "open_cfw_test_freertos_tickless_events"))
        arguments = list((ctypes.c_uint32 * count).in_dll(cls.loaded, "open_cfw_test_freertos_tickless_arguments"))
        return events, arguments

    @staticmethod
    def parse_target(path: Path) -> dict[str, object]:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
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

    def test_sleep_path_rearms_steps_and_orders_power_hooks(self) -> None:
        self.loaded.open_cfw_test_freertos_tickless_reset(0, 32, 100, 1, 1, 4, 100)
        self.loaded.open_cfw_freertos_apollo_suppress_ticks_and_sleep(5)
        self.assertEqual(
            self.trace(),
            ([1, 2, 3, 4, 5, 6, 7, 8, 3, 9, 10, 4, 5, 12, 11],
             [0, 0, 4, 0, 156, 5, 0, 5, 100, 1, 32, 0, 28, 3, 0]),
        )
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_last_compare"), 96)

    def test_abort_reenables_interrupts_without_touching_timer(self) -> None:
        self.loaded.open_cfw_test_freertos_tickless_reset(7, 32, 100, 0, 1, 4, 100)
        self.loaded.open_cfw_freertos_apollo_suppress_ticks_and_sleep(5)
        self.assertEqual(self.trace(), ([1, 2, 11], [0, 0, 0]))
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_last_compare"), 7)

    def test_clamp_caps_hook_and_step_tick_and_pre_hook_can_skip_wfi(self) -> None:
        self.loaded.open_cfw_test_freertos_tickless_reset(0, 32, 3, 1, 0, 0, 200)
        self.loaded.open_cfw_freertos_apollo_suppress_ticks_and_sleep(5)
        events, arguments = self.trace()
        self.assertNotIn(7, events)
        self.assertEqual(arguments[events.index(6)], 3)
        self.assertEqual(arguments[events.index(8)], 3)
        self.assertEqual(arguments[events.index(12)], 3)
        compare_arguments = [arguments[index + 1] for index, event in enumerate(events[:-1]) if event == 4]
        self.assertEqual(compare_arguments, [96, 24])

    def test_wrap_uses_same_stock_missing_plus_one_before_and_after_sleep(self) -> None:
        self.loaded.open_cfw_test_freertos_tickless_reset(0xFFFF_FFF0, 32, 10, 1, 1, 0x10, 0x50)
        self.loaded.open_cfw_freertos_apollo_suppress_ticks_and_sleep(2)
        events, arguments = self.trace()
        compare_arguments = [arguments[index + 1] for index, event in enumerate(events[:-1]) if event == 4]
        self.assertEqual(compare_arguments, [33, 1])
        self.assertEqual(arguments[events.index(12)], 2)
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_last_compare"), 0x31)

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

    def test_stock_span_topology_and_globals_are_exact(self) -> None:
        body = self.application[STOCK_START - BASE:STOCK_END - BASE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (196, STOCK_SHA256))
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
        self.assertEqual(
            tuple(struct.unpack_from("<I", self.application, address - BASE)[0] for address in (0x45656C, 0x456570, 0x456578)),
            (0x20074884, 0x20074888, 0x2007488C),
        )

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
