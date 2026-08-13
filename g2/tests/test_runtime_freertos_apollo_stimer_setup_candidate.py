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
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_apollo_stimer_setup_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_apollo_stimer_setup_candidate_host.c"
AUDIT = ROOT / "docs/research/freertos-apollo-stimer-setup-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
AMBIQ_HEADER = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/am_hal_stimer.h"
AMBIQ_PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000
FUNCTION = "open_cfw_freertos_apollo_stimer_setup"

STOCK_START = 0x0045_643E
STOCK_END = 0x0045_6496
STOCK_SHA256 = "5a54cfc80b658ae5b645ac53b60f0e3098f0fd24fd4b5bedcfb0f822007b30ae"
STOCK_CALLERS = (0x0044_21F6,)
STOCK_OUTGOING_CALLS = (
    (0x0045_6458, 0x0048_D6DC),
    (0x0045_6460, 0x0045_6390),
    (0x0045_6466, 0x0045_6358),
    (0x0045_646E, 0x0048_D588),
    (0x0045_6474, 0x0048_D654),
    (0x0045_6480, 0x0048_D670),
    (0x0045_6490, 0x0048_D588),
)

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

RELOCATIONS = [
    (2, 47, "open_cfw_retained_freertos_stimer_counts_per_tick"),
    (6, 48, "open_cfw_retained_freertos_stimer_counts_per_tick"),
    (24, 47, "open_cfw_retained_freertos_stimer_max_suppressed_ticks"),
    (30, 48, "open_cfw_retained_freertos_stimer_max_suppressed_ticks"),
    (38, 10, "open_cfw_retained_freertos_stimer_interrupt_enable"),
    (46, 10, "open_cfw_retained_freertos_nvic_priority_set"),
    (52, 10, "open_cfw_retained_freertos_nvic_enable"),
    (60, 10, "open_cfw_retained_freertos_stimer_config"),
    (66, 10, "open_cfw_retained_freertos_stimer_counter_get"),
    (70, 47, "open_cfw_retained_freertos_stimer_last_compare"),
    (74, 48, "open_cfw_retained_freertos_stimer_last_compare"),
    (84, 10, "open_cfw_retained_freertos_stimer_compare_delta_set"),
    (106, 30, "open_cfw_retained_freertos_stimer_config"),
]

UNDEFINED = [
    "open_cfw_retained_freertos_nvic_enable",
    "open_cfw_retained_freertos_nvic_priority_set",
    "open_cfw_retained_freertos_stimer_compare_delta_set",
    "open_cfw_retained_freertos_stimer_config",
    "open_cfw_retained_freertos_stimer_counter_get",
    "open_cfw_retained_freertos_stimer_counts_per_tick",
    "open_cfw_retained_freertos_stimer_interrupt_enable",
    "open_cfw_retained_freertos_stimer_last_compare",
    "open_cfw_retained_freertos_stimer_max_suppressed_ticks",
]

TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (1780, "ff492566a9d8c4ad3fc5c37db5f767c9fd1642c339834803221cac0155d25050"),
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (1760, "e72114eadafc5f007650123154fd3d5e72590a375d0a5a129cecd82e91d7c545"),
    },
}

FUNCTION_PIN = (110, 4, "3465bd44998d9919dc56a679d1f0985bf15cfb9f5c4b8fd61d7505b57d1b055e")
LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (2809, "eb02a736ba417aad921367ed25ae9038050387b46cab68a9f89ed99fb581b222"),
    HEADER: (730, "5a461abd1840778bbd9420ce6fa1740949a16e15af1e06b4dd3060866e90e6e0"),
    FIXTURE: (2847, "cf047a6ec48f801b88c8dcc04b87abfd75cd4d707508a6d5fbc35ed8e5ed8e95"),
    AUDIT: (2682, "17fb93a0c4ded4de9fb9f917e064ac887663122e199a6ad093646c009fc50730"),
}


class FreeRTOSApolloSTimerSetupCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("stimer.dylib" if sys.platform == "darwin" else "stimer.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_freertos_stimer_reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.target_object = temp / "stimer.o"
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
    def array(cls, name: str, count: int) -> list[int]:
        return list((ctypes.c_uint32 * count).in_dll(cls.loaded, name))

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

    def test_setup_preserves_exact_call_and_argument_order(self) -> None:
        self.loaded.open_cfw_test_freertos_stimer_reset(0xA5A5_5A5A, 0x1234_5678)
        self.loaded.open_cfw_freertos_apollo_stimer_setup()
        count = self.u32("open_cfw_test_freertos_stimer_event_count")
        self.assertEqual(self.array("open_cfw_test_freertos_stimer_events", count), [1, 2, 3, 4, 5, 6, 7, 8, 5])
        self.assertEqual(
            self.array("open_cfw_test_freertos_stimer_arguments", count),
            [1, 32, 255, 32, 0x8000_0000, 0, 0, 32, 0x25A5_5B53],
        )
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_counts_per_tick"), 32)
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_max_suppressed_ticks"), 0x07FF_FFFB)
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_last_compare"), 0x1234_5678)

    def test_configuration_mask_and_enable_bits(self) -> None:
        for saved, expected in ((0, 0x103), (0xFFFF_FFFF, 0x7FFF_FFF3), (0x8000_000F, 0x103), (0x1234_5678, 0x1234_5773)):
            with self.subTest(saved=saved):
                self.loaded.open_cfw_test_freertos_stimer_reset(saved, 7)
                self.loaded.open_cfw_freertos_apollo_stimer_setup()
                count = self.u32("open_cfw_test_freertos_stimer_event_count")
                self.assertEqual(self.array("open_cfw_test_freertos_stimer_arguments", count)[-1], expected)

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
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (88, STOCK_SHA256))
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
            tuple(struct.unpack_from("<I", self.application, address - BASE)[0] for address in (0x45656C, 0x456570, 0x456578, 0x45657C)),
            (0x20074884, 0x20074888, 0x2007488C, 0x7FFFFFF0),
        )

    def test_ambiqsuite_constants_and_selected_commit_are_authenticated(self) -> None:
        header = AMBIQ_HEADER.read_text()
        for token in (
            "AM_HAL_STIMER_CFG_CLEAR",
            "AM_HAL_STIMER_CFG_COMPARE_A_ENABLE",
            "AM_HAL_STIMER_XTAL_32KHZ",
        ):
            self.assertIn(token, header)
        provenance = json.loads(AMBIQ_PROVENANCE.read_text())
        self.assertEqual(provenance["upstream"]["selected_commit"], "5efc0228528a8adce5eae0d226fac85d2551eb3b")

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
