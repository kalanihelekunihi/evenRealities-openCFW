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
SOURCE = ROOT / "components/shared/freertos/runtime_freertos_task_switch_context.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_freertos_task_switch_context_host.c"
AUDIT = ROOT / "docs/research/freertos-task-switch-context-source-candidate-audit.md"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
UPSTREAM = ROOT / "third_party/freertos-kernel/tasks.c"
PROVENANCE = ROOT / "third_party/freertos-kernel/PROVENANCE.json"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"
BASE = 0x0043_8000
FUNCTION = "open_cfw_freertos_task_switch_context"

STOCK_START = 0x0045_51B4
STOCK_END = 0x0045_5282
STOCK_SHA256 = "fe979ce2eed1eeac9ca5c54192d428ef98825775f1665113ccbe0caf302c7343"
STOCK_CALLERS = (0x0044_2204, 0x005F_A0F6)
STOCK_OUTGOING_CALLS = (
    (0x0045_51FC, 0x0046_D86C),
    (0x0045_5230, 0x005F_A0A4),
)
RAW_INTERIOR_WORD_CANDIDATES = (
    (0x0057_7BD7, 0x0045_5200),
    (0x006E_B0D2, 0x0045_5255),
    (0x006F_F9B4, 0x0045_5255),
    (0x0073_639F, 0x0045_5241),
    (0x0074_AF87, 0x0045_524F),
    (0x0075_0897, 0x0045_524F),
    (0x0075_746A, 0x0045_5241),
    (0x0077_FDD1, 0x0045_5255),
    (0x0078_3945, 0x0045_5255),
    (0x0078_66EC, 0x0045_5255),
    (0x0078_671B, 0x0045_5255),
    (0x0078_AB40, 0x0045_5255),
    (0x0078_E216, 0x0045_524F),
)
STOCK_LITERALS = {
    0x0045_5468: 0x2007_4A58,
    0x0045_5A14: 0x2007_4A44,
    0x0045_5C34: 0x2007_4A20,
    0x0045_5C38: 0x2007_4A5C,
    0x0045_5C3C: 0x2006_F348,
    0x0045_5C40: 0x2007_4A38,
    0x0045_5DBC: 0x2006_A49C,
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]
TARGET_UNDEFINED = [
    "open_cfw_retained_freertos_stack_overflow_hook",
    "ulSetInterruptMask",
]
TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.33.1)",
        "object": (1364, "d57f7dc725ac289dd2ca8016a2face85a1646e4cf4a725cb9367e752ffbb3db8"),
        "function": (266, 4, "37bfb94e9294e10861e68f6e191e12db2be17cef97a412e15a2857fa32874c0b"),
        "relocations": [
            (66, 10, "open_cfw_retained_freertos_stack_overflow_hook"),
            (224, 10, "ulSetInterruptMask"),
        ],
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (1344, "abcef8aada535b4c8aba7367039b79bedd9b4d581ad353567901996021545eb4"),
        "function": (266, 4, "d5d43e9359c06270e28900321583ac9663caf9191becd82de54985e085c2b5f8"),
        "relocations": [
            (66, 10, "open_cfw_retained_freertos_stack_overflow_hook"),
            (226, 10, "ulSetInterruptMask"),
        ],
    },
}
LOCAL_PINS: dict[Path, tuple[int, str]] = {
    SOURCE: (3197, "4ba2014b9dfada5eeeeae7d5d2ddea5a80efaa86c9aec6cabf7b47fb7ce6c2ea"),
    HEADER: (8571, "79135fc816cf1a08e1c1e67fd6a418b38cf0072fd2a39c04d6bf85ee38151c6b"),
    FIXTURE: (8905, "4fc3f2c775378bb82e085a7790f8b69ef5653c1294a023e2914118ce0e5a9e4a"),
    AUDIT: (4598, "349ccc3e68450d3fe01887109ae867dcc0097e3f99484136e7480393d7700a67"),
}


class FreeRTOSTaskSwitchContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temp = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temp / ("switch.dylib" if sys.platform == "darwin" else "switch.so")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        for name in (
            "open_cfw_test_switch_set_suspended", "open_cfw_test_switch_set_current",
            "open_cfw_test_switch_set_top_priority", "open_cfw_test_switch_set_trace_index",
        ):
            getattr(cls.loaded, name).argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_test_switch_set_stack_word.argtypes = [ctypes.c_uint32] * 3
        cls.loaded.open_cfw_test_switch_add_ready.argtypes = [ctypes.c_uint32] * 2
        cls.loaded.open_cfw_test_switch_set_ready_index.argtypes = [ctypes.c_uint32] * 2
        for name in (
            "open_cfw_test_switch_get_current", "open_cfw_test_switch_get_top_priority",
            "open_cfw_test_switch_get_yield_pending", "open_cfw_test_switch_get_trace_index",
            "open_cfw_test_switch_get_assertions", "open_cfw_test_switch_get_overflows",
            "open_cfw_test_switch_get_overflow_task",
        ):
            getattr(cls.loaded, name).restype = ctypes.c_uint32
        for name in ("open_cfw_test_switch_get_trace_out", "open_cfw_test_switch_get_trace_in", "open_cfw_test_switch_get_ready_index"):
            getattr(cls.loaded, name).argtypes = [ctypes.c_uint32]
            getattr(cls.loaded, name).restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_switch_get_overflow_name.restype = ctypes.c_char_p

        cls.target_object = temp / "switch.o"
        subprocess.run([clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target_object)], check=True, capture_output=True, text=True)
        cls.version = subprocess.run([clang, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
        cls.target = cls.parse_target(cls.target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

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

    def reset(self) -> None:
        self.loaded.open_cfw_test_switch_reset()

    def test_suspended_path_only_pends_yield(self) -> None:
        self.reset()
        self.loaded.open_cfw_test_switch_set_current(3)
        self.loaded.open_cfw_test_switch_set_suspended(2)
        self.loaded.open_cfw_test_switch_set_trace_index(9)
        self.loaded.open_cfw_freertos_task_switch_context()
        self.assertEqual(self.loaded.open_cfw_test_switch_get_yield_pending(), 1)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_current(), 3)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_index(), 9)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_out(9), 0xCCCCCCCC)

    def test_priority_descent_round_robin_and_sentinel_skip(self) -> None:
        self.reset()
        self.loaded.open_cfw_test_switch_add_ready(4, 1)
        self.loaded.open_cfw_test_switch_add_ready(4, 2)
        self.loaded.open_cfw_test_switch_set_top_priority(10)
        expected = [(1, 100, 101), (2, 101, 102), (1, 102, 101)]
        for trace_index, (task, switched_out, switched_in) in enumerate(expected):
            self.loaded.open_cfw_freertos_task_switch_context()
            self.assertEqual(self.loaded.open_cfw_test_switch_get_current(), task)
            self.assertEqual(self.loaded.open_cfw_test_switch_get_top_priority(), 4)
            self.assertEqual(self.loaded.open_cfw_test_switch_get_ready_index(4), task)
            self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_out(trace_index), switched_out)
            self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_in(trace_index), switched_in)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_index(), 3)

    def test_each_stack_guard_word_takes_hook_before_selection(self) -> None:
        for word in range(4):
            with self.subTest(word=word):
                self.reset()
                self.loaded.open_cfw_test_switch_add_ready(2, 1)
                self.loaded.open_cfw_test_switch_set_top_priority(2)
                self.loaded.open_cfw_test_switch_set_stack_word(0, word, 0xA5A5A5A4)
                self.loaded.open_cfw_freertos_task_switch_context()
                self.assertEqual(self.loaded.open_cfw_test_switch_get_overflows(), 1)
                self.assertEqual(self.loaded.open_cfw_test_switch_get_overflow_task(), 0)
                self.assertEqual(self.loaded.open_cfw_test_switch_get_overflow_name(), b"T0")
                self.assertEqual(self.loaded.open_cfw_test_switch_get_current(), 1)

    def test_trace_slot_63_wraps_to_zero(self) -> None:
        self.reset()
        self.loaded.open_cfw_test_switch_set_current(7)
        self.loaded.open_cfw_test_switch_add_ready(55, 2)
        self.loaded.open_cfw_test_switch_set_top_priority(55)
        self.loaded.open_cfw_test_switch_set_trace_index(63)
        self.loaded.open_cfw_freertos_task_switch_context()
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_out(63), 107)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_in(63), 102)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_index(), 0)

    def test_empty_priority_zero_takes_assert_seam_after_trace_out(self) -> None:
        self.reset()
        self.loaded.open_cfw_freertos_task_switch_context()
        self.assertEqual(self.loaded.open_cfw_test_switch_get_yield_pending(), 0)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_assertions(), 1)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_out(0), 100)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_in(0), 0xCCCCCCCC)
        self.assertEqual(self.loaded.open_cfw_test_switch_get_trace_index(), 0)

    def test_stock_span_topology_literals_and_tcb_offsets_are_exact(self) -> None:
        body = self.application[STOCK_START - BASE:STOCK_END - BASE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (206, STOCK_SHA256))
        callers = tuple(BASE + offset for offset in range(0, len(self.application) - 3, 2) if self.decode_bl(self.application, BASE + offset) == STOCK_START)
        self.assertEqual(callers, STOCK_CALLERS)
        outgoing = tuple((address, target) for address in range(STOCK_START, STOCK_END, 2) if (target := self.decode_bl(self.application, address)) is not None)
        self.assertEqual(outgoing, STOCK_OUTGOING_CALLS)
        raw_candidates = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if STOCK_START <= (value & ~1) < STOCK_END:
                raw_candidates.append((BASE + offset, value))
        self.assertEqual(tuple(raw_candidates), RAW_INTERIOR_WORD_CANDIDATES)
        self.assertEqual({address: struct.unpack_from("<I", self.application, address - BASE)[0] for address in STOCK_LITERALS}, STOCK_LITERALS)
        text = HEADER.read_text()
        for token in ("0x30U", "0x34U", "0x58U", "0x70U", "0xA5A5A5A5U", "64U", "56U"):
            self.assertIn(token, text)

    def test_authenticated_upstream_and_exact_commit_are_present(self) -> None:
        provenance = json.loads(PROVENANCE.read_text())
        self.assertEqual(provenance["upstream"]["selected_tag"], "V10.5.1")
        self.assertEqual(provenance["upstream"]["selected_commit"], "def7d2df2b0506d3d249334974f51e427c17a41c")
        self.assertEqual(provenance["upstream"]["selected_tree"], "7496dfa815c3cea2f45a090c6e92d113f494b930")
        upstream = UPSTREAM.read_bytes()
        self.assertEqual((len(upstream), hashlib.sha256(upstream).hexdigest()), (223695, "14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463"))
        source = UPSTREAM.read_text()
        self.assertIn("void vTaskSwitchContext( void )", source)
        self.assertIn("taskSELECT_HIGHEST_PRIORITY_TASK()", source)
        self.assertIn("traceTASK_SWITCHED_IN()", source)

    def test_target_object_is_dual_profile_pinned(self) -> None:
        profile = os.environ.get(
            "OPENCFW_EXPECT_PROFILE",
            os.environ.get(
                "OPENCFW_TOOLCHAIN_PROFILE",
                "apple-clang" if sys.platform == "darwin" else "linux-clang",
            ),
        )
        expected = TARGET_PINS[profile]
        self.assertEqual(self.version, expected["version"])
        self.assertEqual(self.target["object"], expected["object"])
        self.assertEqual(self.target["function"], expected["function"])
        self.assertEqual(self.target["relocations"], expected["relocations"])
        self.assertEqual(self.target["undefined"], TARGET_UNDEFINED)

    def test_artifacts_are_pinned_and_production_routed(self) -> None:
        for path, expected in LOCAL_PINS.items():
            data = path.read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), expected)
        source_path = str(SOURCE.relative_to(ROOT))
        self.assertIn(source_path, OVERLAY.read_text())
        self.assertIn(FUNCTION, OVERLAY.read_text())
        self.assertIn("freertos-scheduler-start-core-closure", MAKEFILE.read_text())
        self.assertIn("freertos_task_switch_context_source_text", MANIFEST.read_text())


if __name__ == "__main__":
    unittest.main()
