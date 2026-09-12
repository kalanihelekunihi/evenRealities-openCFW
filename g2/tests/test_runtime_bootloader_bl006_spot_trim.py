#!/usr/bin/env python3
"""BL-006: SPOT trim-search span as reviewed source.

Admits the last 1316 retained bytes (the single official_blob
region 0x00427E54..0x00428378) as reviewed MIT C through the
bootloader component's in-place-leaf mechanism. Four dead
interiors after entry-redirect-replaced heads: the float
classifier suffix tail T0 plus three trim-search variants
F1/F2/F3. The whole-image retained survey grades the span
corroborated_unreachable_control_flow and a whole-image `bl`
sweep finds no caller of any entry, so no leaf executes in the
shipped image.

Leaves (all in one MIT source):

- 0x00427E54..0x00427E84 (48 B, T0): classifier tail (s0 vs
  50.0f/1000.0f pools, returns 2/3/4, `bx lr`). No calls, no
  relocations. VFP mnemonics assemble natively under the
  reviewed leaf flags (reference-assembler probe).
- 0x00427E84..0x00428068 (484 B, F1): variant A (trim-match
  path or measure path). Nine reviewed R_ARM_THM_CALL
  relocations. The 14-byte alignment/float-pool tail after the
  return is reproduced exactly.
- 0x00428068..0x00428240 (472 B, F2): variant B (two clamps).
  Eight reviewed call relocations.
- 0x00428240..0x00428378 (312 B, F3): variant C
  (transition_start(50)). Four reviewed call relocations.

No `.inst` spellings are needed: pool loads reuse the retained
SPOT-table slots through stock PC-relative immediates, which
encode identically in the relocatable object, and every call
targets a source-named symbol. There are no probes; the
byte-exact rebuild plus the relocation-set check pins every
immediate.

Host twins in the same file model the 15 absolute-word cells
and count callee invocations. They were developed against a
unicorn execution differential of the stock Thumb bodies (180
randomized trials across F1/F2/F3: full memory-image plus
call-trace agreement), which caught two real twin bugs (the
signed `blt` clamp gate and F2's pulse-register merge target).
Unicorn cannot execute T0's VFP instructions, so T0's twin is
qualified by anchored decode plus the host truth table here
(including the NaN unordered derivation).

Live SPOT behavior stays covered by the already-routed
SPOT-manager sources; these leaves document dead bytes and pin
the behavior the replaced heads must cover.

Evidence:
`g2/docs/research/g2-bootloader-bl006-span-427e54-spot-trim-source-closure.md`.
"""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/apollo_overlay.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
RUN_BASE = 0x00410000
CLANG = "/usr/bin/clang"

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror", "-fno-ident",
]

SOURCE = ("components/bootloader/core_overlay/"
          "runtime_bl006_spot_trim_span_427e54.c")

LEAVES: tuple[dict, ...] = (
    {
        "function": "open_cfw_bootloader_spot_trim_classify_tail_427e54",
        "address": 0x00427E54,
        "size": 48,
        "sha256": "609d289f0975ea5c58c0666883dd8c46b023df79951bad5c75b7cf5de791ab2c",
        "relocations": [],
    },
    {
        "function": "open_cfw_bootloader_spot_trim_search_a_427e84",
        "address": 0x00427E84,
        "size": 484,
        "sha256": "b5072ed73bf47a2e3d0de0f25752fd2de966c0f8f0c8f6278a5e6fb63cd021fa",
        "relocations": [
            {"offset": 148, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc",
             "symbol_type": "STT_NOTYPE", "target_address": 0x42A1BC},
            {"offset": 170, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_trim_finalize_41ccd6",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41CCD6},
            {"offset": 198, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 222, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a",
             "symbol_type": "STT_NOTYPE", "target_address": 0x42A04A},
            {"offset": 282, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc",
             "symbol_type": "STT_NOTYPE", "target_address": 0x42A1BC},
            {"offset": 340, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 372, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_irq_pause_41e22e",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41E22E},
            {"offset": 400, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 410, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_irq_resume_41e1e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41E1E8},
        ],
    },
    {
        "function": "open_cfw_bootloader_spot_trim_search_b_428068",
        "address": 0x00428068,
        "size": 472,
        "sha256": "7828372b3a4b3704f7d9202a325edc738dcf1af81ad60af87d11495e284388ad",
        "relocations": [
            {"offset": 134, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 158, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a",
             "symbol_type": "STT_NOTYPE", "target_address": 0x42A04A},
            {"offset": 222, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc",
             "symbol_type": "STT_NOTYPE", "target_address": 0x42A1BC},
            {"offset": 324, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 386, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 418, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_irq_pause_41e22e",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41E22E},
            {"offset": 454, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 464, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_irq_resume_41e1e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41E1E8},
        ],
    },
    {
        "function": "open_cfw_bootloader_spot_trim_search_c_428240",
        "address": 0x00428240,
        "size": 312,
        "sha256": "aed159d19382e0b72478d67e5204326070f9f6f27e1f426a3716cd97cbf41289",
        "relocations": [
            {"offset": 128, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_retained_delay_41d1c0",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D1C0},
            {"offset": 152, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a",
             "symbol_type": "STT_NOTYPE", "target_address": 0x42A04A},
            {"offset": 212, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc",
             "symbol_type": "STT_NOTYPE", "target_address": 0x42A1BC},
            {"offset": 296, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_spotmgr_transition_start_41cc48",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41CC48},
        ],
    },
)

# Host memory-image slot order (mirrors the source header):
# 0 gate 0x400083E0, 1 trim id 0x20000154, 2 poll 0x40008064,
# 3 ctrl 0x40020044, 4 pulse 0x4002004C, 5 systick 0xE000ED14,
# 6 pwr 0x4002037C, 7 field 0x40020080, 8..13 SRAM words,
# 14 status byte cell (bits 16..23).


def load_module():
    spec = importlib.util.spec_from_file_location(
        "apollo_overlay_bl006_spot_trim", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u32_at(buf: bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def view(buf: bytearray):
    return (ctypes.c_uint8 * len(buf)).from_buffer(buf)


class Bl006SpotTrimLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-bl006-spot-trim-")
        library = Path(cls.temporary.name) / "spot_trim.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
             "-shared", "-fPIC", str(ROOT / SOURCE),
             "-o", str(library)],
            cwd=ROOT, check=True,
        )
        lib = ctypes.CDLL(str(library))
        cls.t0 = lib.open_cfw_bootloader_spot_trim_classify_tail_427e54
        cls.t0.argtypes = [ctypes.c_uint32, ctypes.c_float, ctypes.c_uint32]
        cls.t0.restype = ctypes.c_uint32
        cls.fa = lib.open_cfw_bootloader_spot_trim_search_a_427e84
        cls.fb = lib.open_cfw_bootloader_spot_trim_search_b_428068
        cls.fc = lib.open_cfw_bootloader_spot_trim_search_c_428240
        for fn in (cls.fa, cls.fb, cls.fc):
            fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.c_void_p,
                                                   ctypes.c_void_p,
                                                   ctypes.c_void_p]
            fn.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def stock(self, address: int, size: int) -> bytes:
        return self.image[address - RUN_BASE:address - RUN_BASE + size]

    def compile_leaf(self, leaf: dict) -> tuple[bytes, dict]:
        source_bytes = (ROOT / SOURCE).read_bytes()
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as directory:
            return self.module.compile_in_place_leaf(
                root=ROOT,
                clang=CLANG,
                leaf_config={
                    "function": leaf["function"],
                    "runtime_address": leaf["address"],
                    "source": {
                        "path": SOURCE,
                        "size": len(source_bytes),
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                    },
                    "toolchain": {"target": "arm-none-eabi",
                                  "flags": FLAGS},
                    "strict_relocation_contract": True,
                    "expected": {"size": leaf["size"],
                                 "sha256": leaf["sha256"]},
                    "stock": {"size": leaf["size"],
                              "sha256": leaf["sha256"]},
                    "relocations": leaf["relocations"],
                    "allow_discarded_alloc_sections": True,
                },
                object_path=Path(directory) / "leaf.o",
            )

    def test_stock_spans_unchanged(self) -> None:
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                observed = hashlib.sha256(
                    self.stock(leaf["address"], leaf["size"])).hexdigest()
                self.assertEqual(observed, leaf["sha256"])

    def test_compiled_leaves_match_stock(self) -> None:
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                payload, report = self.compile_leaf(leaf)
                self.assertEqual(
                    payload, self.stock(leaf["address"], leaf["size"]))
                extraction = report["extraction"]
                self.assertEqual(
                    extraction["relocation_count"], len(leaf["relocations"]))
                self.assertEqual(extraction["function"], leaf["function"])
                self.assertEqual(extraction["size"], leaf["size"])
                self.assertEqual(extraction["sha256"], leaf["sha256"])
                if leaf["relocations"]:
                    seen = {(r["offset"], r["type"], r["symbol"])
                            for r in extraction["relocations"]}
                    want = {(r["offset"], r["type"], r["symbol"])
                            for r in leaf["relocations"]}
                    self.assertEqual(seen, want)

    def test_overlay_registers_leaves(self) -> None:
        registered = {item["function"]: item
                      for item in self.overlay.get("in_place_leaves", [])}
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                self.assertIn(leaf["function"], registered)
                entry = registered[leaf["function"]]
                self.assertEqual(entry["runtime_address"], leaf["address"])
                self.assertEqual(entry["expected"]["size"], leaf["size"])
                self.assertEqual(entry["expected"]["sha256"], leaf["sha256"])
                self.assertEqual(entry["stock"]["sha256"], leaf["sha256"])
                self.assertTrue(entry["strict_relocation_contract"])
                self.assertEqual(entry["source"]["license"], "MIT")
                self.assertEqual(entry["source"]["path"], SOURCE)
                seen = {(r["offset"], r["type"], r.get("symbol"),
                         r.get("target_address"))
                        for r in entry.get("relocations", [])}
                want = {(r["offset"], r["type"], r.get("symbol"),
                         r.get("target_address"))
                        for r in leaf["relocations"]}
                self.assertEqual(seen, want)

    def test_survey_grades_span_unreachable(self) -> None:
        path = ROOT / "tools/analyze_g2_bootloader_bl006_retained_survey.py"
        spec = importlib.util.spec_from_file_location(
            "analyze_g2_bootloader_bl006_retained_survey", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        by_start = {}
        for region in module.survey()["regions"]:
            try:
                by_start[int(str(region["start"]), 16)] = region
            except (KeyError, ValueError):
                continue
        region = by_start.get(0x00427E54)
        self.assertIsNotNone(region, "no survey region at 0x00427E54")
        assert region is not None
        self.assertEqual(
            region["verdict"], "corroborated_unreachable_control_flow")
        # All four leaves sit inside this one surveyed span.
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                self.assertLessEqual(0x00427E54, leaf["address"])
                self.assertLessEqual(
                    leaf["address"] + leaf["size"], 0x00428378)

    def test_no_bl_caller_of_any_entry(self) -> None:
        from capstone import CS_ARCH_ARM, CS_MODE_THUMB, CS_OP_IMM, Cs

        entries = {leaf["address"] for leaf in LEAVES}
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        decoder.detail = True
        hits: dict[int, list[int]] = {entry: [] for entry in entries}
        for insn in decoder.disasm(bytes(self.image), RUN_BASE):
            if insn.mnemonic != "bl":
                continue
            for op in insn.operands:
                if op.type == CS_OP_IMM and op.value.imm in hits:
                    hits[op.value.imm].append(insn.address)
        for entry, callers in hits.items():
            self.assertEqual(
                callers, [],
                f"entry {entry:#x} gains a caller at "
                f"{[hex(c) for c in callers]}; deadness changed")

    def fresh(self, words: int = 24):
        tab = bytearray(4 * words)
        mem = bytearray(4 * 15)
        calls = bytearray(4 * 11)
        return tab, mem, calls

    def run3(self, fn, r0: int, r1: int, r2: int, tab, mem, calls) -> int:
        return fn(r0, r1, r2, view(tab), view(mem), view(calls))

    def test_t0_truth_table(self) -> None:
        for n_in, value, want in (
                (1, 0.0, 2), (1, 500.0, 2), (1, float("nan"), 2),
                (0, -1.0, 4), (0, 0.0, 4), (0, 49.9, 4),
                (0, 50.0, 3), (0, 50.1, 3), (0, 500.0, 3),
                (0, 999.9, 3), (0, 1000.0, 4), (0, 1000.1, 4),
                (0, 1e30, 4), (0, float("inf"), 4),
                (0, float("-inf"), 4),
                # Unordered (NaN): VCMP raises N=Z=C=V=1, so
                # neither blt nor bpl is taken and the tail
                # falls through to 3.
                (0, float("nan"), 3)):
            with self.subTest(n_in=n_in, value=value):
                self.assertEqual(self.t0(0xDEAD, value, n_in), want)

    def test_f1_trim_match_path(self) -> None:
        tab, mem, calls = self.fresh()
        struct.pack_into("<I", tab, 4 * 4, 0x12345678)
        struct.pack_into("<I", mem, 0 * 4, 1)
        struct.pack_into("<I", mem, 1 * 4, 3)
        ret = self.run3(self.fa, 3, 0, 0xAA, tab, mem, calls)
        self.assertEqual(ret, 0)
        sb = (0x12345678 >> 21) & 0x7F
        self.assertEqual(sb, 17)
        self.assertEqual(u32_at(calls, 8 * 4), 1)  # ton_calls
        self.assertEqual(u32_at(calls, 9 * 4), 0xAA)  # ton_a0
        self.assertEqual(u32_at(calls, 10 * 4), 3)  # ton_a1
        self.assertEqual(u32_at(mem, 3 * 4), 17)  # CTRL44 merge
        self.assertEqual(u32_at(calls, 5 * 4), 1)  # finalize
        self.assertEqual(u32_at(mem, 14 * 4), 0x1A0000)  # status byte
        for i in (0, 1, 2, 3, 4, 6, 7):
            self.assertEqual(u32_at(calls, i * 4), 0)

    def test_f1_measure_path_quiet(self) -> None:
        tab, mem, calls = self.fresh()
        ret = self.run3(self.fa, 2, 1, 0x55, tab, mem, calls)
        self.assertEqual(ret, 0)
        self.assertEqual(u32_at(mem, 8 * 4), 0x55)
        self.assertEqual(u32_at(mem, 9 * 4), 2)
        for slot in (10, 11, 12, 13):
            self.assertEqual(u32_at(mem, slot * 4), 0)
        self.assertEqual(u32_at(mem, 4 * 4), 0)  # clamp bfi path
        self.assertEqual(u32_at(mem, 6 * 4), 0x2010000)
        self.assertEqual(u32_at(mem, 3 * 4), 0)
        self.assertEqual(u32_at(mem, 7 * 4), 0)
        self.assertEqual(u32_at(calls, 8 * 4), 1)  # ton
        self.assertEqual(u32_at(calls, 9 * 4), 0x55)
        self.assertEqual(u32_at(calls, 10 * 4), 2)
        self.assertEqual(u32_at(calls, 0 * 4), 2)  # delay 50, 20
        self.assertEqual(u32_at(calls, 1 * 4), 20)
        for i in (2, 3, 4, 5, 6, 7):
            self.assertEqual(u32_at(calls, i * 4), 0)

    def test_f1_full_loop_and_pause(self) -> None:
        tab, mem, calls = self.fresh()
        struct.pack_into("<I", mem, 0 * 4, 1)
        struct.pack_into("<I", mem, 1 * 4, 0xDEAD)
        struct.pack_into("<I", mem, 2 * 4, 0)  # bit30 clear: 60 polls
        struct.pack_into("<I", mem, 5 * 4, 0x20000)  # bit17: pause
        ret = self.run3(self.fa, 1, 0, 7, tab, mem, calls)
        self.assertEqual(ret, 0)
        self.assertEqual(u32_at(calls, 0 * 4), 62)  # 60 + 50 + 20
        self.assertEqual(u32_at(calls, 1 * 4), 20)
        self.assertEqual(u32_at(calls, 2 * 4), 1)  # pause
        self.assertEqual(u32_at(calls, 3 * 4), 1)  # resume
        self.assertEqual(u32_at(calls, 4 * 4), 1)  # timer
        self.assertEqual(u32_at(mem, 8 * 4), 7)
        self.assertEqual(u32_at(mem, 9 * 4), 1)

    def test_f1_clamp_saturates(self) -> None:
        tab, mem, calls = self.fresh()
        struct.pack_into("<I", tab, 1 * 4, 0x7F)  # sl/sb source
        struct.pack_into("<I", tab, 2 * 4, 0x10)  # r8 source byte
        ret = self.run3(self.fa, 0, 1, 0, tab, mem, calls)
        self.assertEqual(ret, 0)
        # d = 0x7F - 0x10 = 0x6F; q = 0xDE; s = 0xEE: saturate.
        # The post-delay merge then republishes sl (also 0x7F).
        self.assertEqual(u32_at(mem, 4 * 4), 0x7F)
        self.assertEqual(u32_at(mem, 13 * 4), 0x7F)
        self.assertEqual(u32_at(mem, 12 * 4), 0)
        self.assertEqual(u32_at(mem, 3 * 4), 0)

    def test_f2_quiet_path(self) -> None:
        tab, mem, calls = self.fresh()
        ret = self.run3(self.fb, 2, 5, 0x80E3B32A, tab, mem, calls)
        self.assertEqual(ret, 0)
        self.assertEqual(u32_at(mem, 8 * 4), 0x80E3B32A)
        self.assertEqual(u32_at(mem, 9 * 4), 2)
        self.assertEqual(u32_at(calls, 8 * 4), 1)
        self.assertEqual(u32_at(calls, 9 * 4), 0x80E3B32A)
        self.assertEqual(u32_at(calls, 10 * 4), 2)
        self.assertEqual(u32_at(calls, 0 * 4), 3)  # delays 50, 5, 20
        self.assertEqual(u32_at(calls, 1 * 4), 20)
        self.assertEqual(u32_at(mem, 6 * 4), 0x10000 | 8 | 0x40)
        for i in (2, 3, 4, 5, 6, 7):
            self.assertEqual(u32_at(calls, i * 4), 0)

    def test_f2_saturate_pause_resume(self) -> None:
        tab, mem, calls = self.fresh()
        struct.pack_into("<I", tab, 3 * 4, 0x80B3D863)  # sav: sb 0x63 r8 0x05
        struct.pack_into("<I", tab, 6 * 4, 0x67DC560E)  # w1: r6 0x0E r7 0x3E
        struct.pack_into("<I", mem, 0 * 4, 1)
        struct.pack_into("<I", mem, 1 * 4, 9)
        struct.pack_into("<I", mem, 2 * 4, 0x40000000)  # bit30: no loop wait
        struct.pack_into("<I", mem, 5 * 4, 0x20000)  # pause
        struct.pack_into("<I", mem, 3 * 4, 0x5A6CDA30)
        struct.pack_into("<I", mem, 4 * 4, 0x1548B593)
        ret = self.run3(self.fb, 2, 5, 0x11, tab, mem, calls)
        self.assertEqual(ret, 0)
        self.assertEqual(u32_at(calls, 4 * 4), 1)  # timer, no delay(1)
        self.assertEqual(u32_at(calls, 0 * 4), 3)
        # Clamp#1 saturates (0x1548B5FF), then the sb merge
        # republishes sb: 0x63 | (0x1548B5FF & ~0x7F).
        self.assertEqual(u32_at(mem, 4 * 4), 0x1548B5E3)
        # Clamp#2 takes the bfi path (negative d), then r8 merge.
        self.assertEqual(u32_at(mem, 3 * 4),
                         0x05 | (0x5A6CDA30 & ~0x7F))
        self.assertEqual(u32_at(calls, 2 * 4), 1)  # pause
        self.assertEqual(u32_at(calls, 3 * 4), 1)  # resume
        self.assertEqual(u32_at(calls, 9 * 4), 0x11)  # ton_a0 = sl
        self.assertEqual(u32_at(mem, 8 * 4), 0x11)
        self.assertEqual(u32_at(mem, 9 * 4), 2)
        self.assertEqual(u32_at(mem, 6 * 4) & (0x10000 | 8 | 0x40),
                         0x10000 | 8 | 0x40)

    def test_f3_quiet_path(self) -> None:
        tab, mem, calls = self.fresh(words=24)
        ret = self.run3(self.fc, 4, 0, 0x22, tab, mem, calls)
        self.assertEqual(ret, 0)
        self.assertEqual(u32_at(mem, 8 * 4), 0x22)
        self.assertEqual(u32_at(mem, 9 * 4), 4)
        self.assertEqual(u32_at(mem, 1 * 4), 4)  # trim id stored
        self.assertEqual(u32_at(calls, 6 * 4), 1)  # transition_start
        self.assertEqual(u32_at(calls, 7 * 4), 50)  # ... with r0 = 50
        self.assertEqual(u32_at(mem, 14 * 4), 0x020000)
        self.assertEqual(u32_at(calls, 8 * 4), 1)  # ton
        self.assertEqual(u32_at(calls, 9 * 4), 0x22)
        for i in (0, 2, 3, 4, 5):
            self.assertEqual(u32_at(calls, i * 4), 0)

    def test_f3_loop_and_table_merge(self) -> None:
        tab, mem, calls = self.fresh(words=24)
        struct.pack_into("<I", tab, 20 * 4, 0xAB)  # table+0x50 low 7 = 0x2B
        struct.pack_into("<I", mem, 0 * 4, 1)
        struct.pack_into("<I", mem, 1 * 4, 7)
        struct.pack_into("<I", mem, 2 * 4, 0)  # 60 polls
        ret = self.run3(self.fc, 1, 2, 0x33, tab, mem, calls)
        self.assertEqual(ret, 0)
        self.assertEqual(u32_at(calls, 0 * 4), 60)
        self.assertEqual(u32_at(calls, 1 * 4), 1)
        self.assertEqual(u32_at(calls, 4 * 4), 1)  # timer
        self.assertEqual(u32_at(mem, 4 * 4), 0x2B)  # pulse merge
        self.assertEqual(u32_at(mem, 1 * 4), 1)
        self.assertEqual(u32_at(calls, 6 * 4), 1)
        self.assertEqual(u32_at(calls, 7 * 4), 50)


if __name__ == "__main__":
    unittest.main()
