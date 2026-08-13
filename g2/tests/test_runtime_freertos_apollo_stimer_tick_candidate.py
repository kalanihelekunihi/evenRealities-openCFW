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
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_apollo_stimer_tick_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_apollo_stimer_tick_candidate_host.c"
AUDIT = ROOT / "docs/research/freertos-apollo-stimer-tick-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000
FUNCTIONS = (
    "open_cfw_freertos_apollo_stimer_elapsed_ticks_dispatch",
    "open_cfw_freertos_apollo_stimer_compare_a_interrupt",
)

STOCK = {
    FUNCTIONS[0]: (
        0x0045_63B4,
        0x0045_6426,
        "43a3151849cd96e46d45ad12bb338ea09f586e9fe734b01d485fb9b21c6775fa",
        (0x0045_6438,),
        ((0x005A_BCDB, 0x0045_63C0),),
        ((0x4563BA, 0x48D654), (0x4563F4, 0x48D670), (0x4563F8, 0x5FA0A4), (0x456408, 0x45504C), (0x456420, 0x5FA0BA)),
    ),
    FUNCTIONS[1]: (
        0x0045_6426,
        0x0045_643E,
        "518fea2d6b0fab0ff4dce31adcaa55015c872000ee314e97987aed9459040f4a",
        (),
        ((0x0043_80C0, 0x0045_6427),),
        ((0x45642A, 0x48D6F0), (0x456434, 0x48D6E6), (0x456438, 0x4563B4)),
    ),
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

FUNCTION_PINS = {
    FUNCTIONS[0]: (130, 4, "3f5ddb117c218c09bd4c50164ac95157710a1df30c57f87d63daddac06934396"),
    FUNCTIONS[1]: (28, 4, "4d9ec6702f3d225e32c4f60c5e3b3c544475b453dbf60d0be99ffb4b32a80cf2"),
}

RELOCATIONS = {
    FUNCTIONS[0]: [
        (2, 10, "open_cfw_retained_freertos_stimer_counter_get"),
        (6, 47, "open_cfw_retained_freertos_stimer_last_compare"),
        (10, 48, "open_cfw_retained_freertos_stimer_last_compare"),
        (24, 47, "open_cfw_retained_freertos_stimer_counts_per_tick"),
        (32, 48, "open_cfw_retained_freertos_stimer_counts_per_tick"),
        (68, 10, "open_cfw_retained_freertos_stimer_compare_delta_set"),
        (72, 10, "open_cfw_retained_freertos_interrupt_mask_set"),
        (90, 10, "open_cfw_freertos_task_increment_tick"),
        (106, 47, "open_cfw_retained_freertos_interrupt_control_state"),
        (110, 48, "open_cfw_retained_freertos_interrupt_control_state"),
        (126, 30, "open_cfw_retained_freertos_interrupt_mask_clear"),
    ],
    FUNCTIONS[1]: [
        (4, 10, "open_cfw_retained_freertos_stimer_interrupt_status_get"),
        (16, 10, "open_cfw_retained_freertos_stimer_interrupt_clear"),
        (24, 30, FUNCTIONS[0]),
    ],
}

UNDEFINED = [
    "open_cfw_freertos_task_increment_tick",
    "open_cfw_retained_freertos_interrupt_control_state",
    "open_cfw_retained_freertos_interrupt_mask_clear",
    "open_cfw_retained_freertos_interrupt_mask_set",
    "open_cfw_retained_freertos_stimer_compare_delta_set",
    "open_cfw_retained_freertos_stimer_counter_get",
    "open_cfw_retained_freertos_stimer_counts_per_tick",
    "open_cfw_retained_freertos_stimer_interrupt_clear",
    "open_cfw_retained_freertos_stimer_interrupt_status_get",
    "open_cfw_retained_freertos_stimer_last_compare",
]

TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (2300, "a57be26f3424d7ddef546c8510191b5ee168860474c8d465c6c14920474b5141"),
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (2280, "dab49d2e696ca0f8a45b20dab73fa2d3c10e66ad50c2f06f9edd7881ff2a6f8e"),
    },
}

LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (3421, "466da3c036a6cfccbabb659d32f7b728f056d8114fbe87a43428d77224a12ce8"),
    HEADER: (875, "ee26b49523a53bf8ba61727361566a3ed8c284dad364cd8a626af9d822cba58d"),
    FIXTURE: (4033, "ef6c31c2c5d19510aad647ed29ff4a8460d1981f7670ede5ecc0ba0b5bacb389"),
    AUDIT: (2873, "514f79e63f1909e880630cbf2e64748920b3708a0997b7d8fba1337715d4562e"),
}


class FreeRTOSApolloSTimerTickCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("stimer_tick.dylib" if sys.platform == "darwin" else "stimer_tick.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_freertos_stimer_tick_reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_test_freertos_stimer_tick_set_result.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.target_object = temp / "stimer_tick.o"
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
        count = cls.u32("open_cfw_test_freertos_stimer_tick_event_count")
        events = list((ctypes.c_uint32 * count).in_dll(cls.loaded, "open_cfw_test_freertos_stimer_tick_events"))
        arguments = list((ctypes.c_uint32 * count).in_dll(cls.loaded, "open_cfw_test_freertos_stimer_tick_arguments"))
        return events, arguments

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
        functions, relocations = {}, {}
        for function in FUNCTIONS:
            section = apollo_overlay.section_named(sections, ".text." + function)
            body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            functions[function] = (len(body), int(section["alignment"]), hashlib.sha256(body).hexdigest())
            values = []
            for relsec in sections:
                if int(relsec["type"]) == 9 and int(relsec["info"]) == int(section["index"]):
                    for index in range(int(relsec["size"]) // 8):
                        offset, info = struct.unpack_from("<II", data, int(relsec["offset"]) + index * 8)
                        values.append((offset, info & 0xFF, symbols[info >> 8][0]))
            relocations[function] = values
        return {
            "object": (len(data), hashlib.sha256(data).hexdigest()),
            "functions": functions,
            "relocations": relocations,
            "undefined": sorted(name for name, fields in symbols if name and fields[5] == 0),
        }

    def test_elapsed_ticks_rearm_and_aggregate_pendsv(self) -> None:
        self.loaded.open_cfw_test_freertos_stimer_tick_reset(0, 32, 100, 0)
        for index, result in enumerate((0, 1, 0)):
            self.loaded.open_cfw_test_freertos_stimer_tick_set_result(index, result)
        self.loaded.open_cfw_freertos_apollo_stimer_elapsed_ticks_dispatch()
        self.assertEqual(self.trace(), ([1, 2, 3, 4, 5, 5, 5, 6], [0, 0, 28, 0, 0, 1, 0, 0]))
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_last_compare"), 96)
        self.assertEqual(self.u32("open_cfw_retained_freertos_interrupt_control_state"), 0x1000_0000)

    def test_wrap_preserves_stock_missing_plus_one(self) -> None:
        self.loaded.open_cfw_test_freertos_stimer_tick_reset(0xFFFF_FFF0, 32, 0x20, 0)
        self.loaded.open_cfw_freertos_apollo_stimer_elapsed_ticks_dispatch()
        self.assertEqual(self.trace(), ([1, 2, 3, 4, 5, 6], [0, 0, 17, 0, 0, 0]))
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_last_compare"), 0x11)

    def test_partial_tick_rearms_without_kernel_tick_or_pendsv(self) -> None:
        self.loaded.open_cfw_test_freertos_stimer_tick_reset(0, 32, 31, 0)
        self.loaded.open_cfw_freertos_apollo_stimer_elapsed_ticks_dispatch()
        self.assertEqual(self.trace(), ([1, 2, 3, 4, 6], [0, 0, 1, 0, 0]))
        self.assertEqual(self.u32("open_cfw_retained_freertos_stimer_last_compare"), 0)
        self.assertEqual(self.u32("open_cfw_retained_freertos_interrupt_control_state"), 0)

    def test_irq_gates_clear_and_dispatch_on_compare_a_only(self) -> None:
        self.loaded.open_cfw_test_freertos_stimer_tick_reset(0, 32, 0, 0x8000_0000)
        self.loaded.open_cfw_freertos_apollo_stimer_compare_a_interrupt()
        self.assertEqual(self.trace(), ([7], [0]))
        self.loaded.open_cfw_test_freertos_stimer_tick_reset(0, 32, 0, 0x8000_0001)
        self.loaded.open_cfw_freertos_apollo_stimer_compare_a_interrupt()
        self.assertEqual(self.trace(), ([7, 8, 1, 2, 3, 4, 6], [0, 1, 0, 0, 32, 0, 0]))

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

    def test_stock_spans_call_graph_and_vector_are_exact(self) -> None:
        for function, (start, end, digest, expected_callers, expected_raw, expected_outgoing) in STOCK.items():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (end - start, digest))
            callers = tuple(BASE + offset for offset in range(0, len(self.application) - 3, 2) if self.decode_bl(self.application, BASE + offset) == start)
            self.assertEqual(callers, expected_callers, function)
            outgoing = tuple((address, target) for address in range(start, end, 2) if (target := self.decode_bl(self.application, address)) is not None)
            self.assertEqual(outgoing, expected_outgoing, function)
            raw = []
            for offset in range(len(self.application) - 3):
                value = struct.unpack_from("<I", self.application, offset)[0]
                if start <= (value & ~1) < end:
                    raw.append((BASE + offset, value))
            self.assertEqual(tuple(raw), expected_raw, function)
        self.assertEqual(struct.unpack_from("<I", self.application, 0x456574 - BASE)[0], 0xE000_ED04)

    def test_target_object_is_dual_profile_pinned(self) -> None:
        profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        pin = TARGET_PINS[profile]
        self.assertEqual(self.version, pin["version"])
        self.assertEqual(self.target["object"], pin["object"])
        self.assertEqual(self.target["functions"], FUNCTION_PINS)
        self.assertEqual(self.target["relocations"], RELOCATIONS)
        self.assertEqual(self.target["undefined"], UNDEFINED)

    def test_artifacts_are_pinned_and_production_excluded(self) -> None:
        for path, (size, digest) in LOCAL_PINS.items():
            body = path.read_bytes()
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (size, digest))
        forbidden = (SOURCE.name, HEADER.name, *FUNCTIONS)
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text()
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
