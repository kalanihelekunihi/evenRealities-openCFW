#!/usr/bin/env python3
"""BL-006: four dead-tail leaves as reviewed in-place source.

Admits 70 bytes across four single-exit, call-free, branch-free,
literal-free stock tails that survive as unreachable bytes after
replaced heads:

- 0x004264F6..0x00426506 (16 B): MSPI interrupt-status remainder
  (scaled status-word publish; returns 0).
- 0x00426CC4..0x00426CCC (8 B): CLKGEN dual-clock-switch terminal
  tail (slot-derived publish; returns 0 via pop {r1, pc}).
- 0x0042784C..0x00427878 (44 B): command-queue initializer
  remainder (accumulate/publish/configure/state-out; returns 0).
- 0x004279EE..0x004279F0 (2 B): command-queue block-release
  terminal return (bare `bx lr`, r0 pass-through).

Deadness (all four): the whole-image retained survey grades each
span corroborated_unreachable_control_flow, and a whole-image `bl`
sweep finds no caller of any entry. The stock-internal branches
that target into these tails originate in the replaced head spans
(the source-owned heads return/jump away in the built image), so
no tail executes in the shipped image. The reconstructions
document the bytes from reviewed source and pin the behavior the
replaced heads must cover; no live traffic is claimed.

The retained 10-byte slice at 0x004264B0..0x004264BA is
deliberately NOT a leaf here: the authentic stock stream holds a
32-bit ADD.W at 0x004264AE spanning 0x004264AE..0x004264B2, so
the slice starts mid-instruction and cannot be framed as a
behavior-leaf entry; it needs the data/fill route.

Evidence:
`g2/docs/research/g2-bootloader-bl006-tail-leaves-4264f6-4279ee-source-closure.md`.
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

SOURCE = (
    "components/bootloader/core_overlay/"
    "runtime_bl006_mspi_clkgen_cmdq_tails_4264f6.c"
)

LEAVES: tuple[dict, ...] = (
    {
        "function": "open_cfw_bootloader_mspi_irq_status_tail_4264f6",
        "address": 0x004264F6,
        "size": 16,
        "sha256": "d23bae4506efde890d16f3ac9dbf8753b6970db0c5854c39280dbbb30c8a0eab",
    },
    {
        "function": "open_cfw_bootloader_clkgen_dualclock_term_tail_426cc4",
        "address": 0x00426CC4,
        "size": 8,
        "sha256": "d7d2a4025d26ea346c59aacce99c433ac393769f80658c1d6586235cda9af704",
    },
    {
        "function": "open_cfw_bootloader_cmdq_init_rem_tail_42784c",
        "address": 0x0042784C,
        "size": 44,
        "sha256": "d6d5c013eeebd40c063fc7586b9b5c531c55498b1e006a3c6305b47045b6de9b",
    },
    {
        "function": "open_cfw_bootloader_cmdq_blockrel_term_4279ee",
        "address": 0x004279EE,
        "size": 2,
        "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
    },
)

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror", "-fno-ident",
]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "apollo_overlay_bl006_mc_tails", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u32(buf: bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


class Bl006MspiClkgenCmdqTailLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-bl006-mc-tails-")
        library = Path(cls.temporary.name) / "bl006-mc-tails.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(ROOT / SOURCE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.tail_l = cls.lib.open_cfw_bootloader_mspi_irq_status_tail_4264f6
        cls.tail_l.argtypes = [ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.c_void_p]
        cls.tail_l.restype = ctypes.c_uint32
        cls.tail_m = cls.lib.open_cfw_bootloader_clkgen_dualclock_term_tail_426cc4
        cls.tail_m.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_void_p]
        cls.tail_m.restype = ctypes.c_uint32
        cls.tail_n = cls.lib.open_cfw_bootloader_cmdq_init_rem_tail_42784c
        cls.tail_n.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                               ctypes.c_void_p, ctypes.c_void_p]
        cls.tail_n.restype = ctypes.c_uint32
        cls.tail_o = cls.lib.open_cfw_bootloader_cmdq_blockrel_term_4279ee
        cls.tail_o.argtypes = [ctypes.c_uint32]
        cls.tail_o.restype = ctypes.c_uint32

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
            payload, report = self.module.compile_in_place_leaf(
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
                    "relocations": [],
                    "allow_discarded_alloc_sections": True,
                },
                object_path=Path(directory) / "leaf.o",
            )
        return payload, report

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
                self.assertEqual(extraction["relocation_count"], 0)
                self.assertEqual(extraction["relocations"], [])
                self.assertEqual(extraction["function"], leaf["function"])
                self.assertEqual(extraction["runtime_address"], leaf["address"])
                self.assertEqual(extraction["size"], leaf["size"])
                self.assertEqual(extraction["sha256"], leaf["sha256"])

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
                self.assertEqual(entry["relocations"], [])
                self.assertTrue(entry["strict_relocation_contract"])
                self.assertEqual(entry["source"]["license"], "MIT")
                self.assertEqual(entry["source"]["path"], SOURCE)

    def test_survey_grades_spans_unreachable(self) -> None:
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
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                region = by_start.get(leaf["address"])
                self.assertIsNotNone(
                    region, f"no survey region at {leaf['address']:#x}")
                assert region is not None
                self.assertEqual(
                    region["verdict"], "corroborated_unreachable_control_flow")

    def test_no_bl_caller_of_any_entry(self) -> None:
        from capstone import CS_ARCH_ARM, CS_MODE_THUMB, CS_OP_IMM, Cs

        entries = {leaf["address"] for leaf in LEAVES}
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        decoder.detail = True
        hits: dict[int, list[int]] = {entry: [] for entry in entries}
        # Linear sweep can desynchronize inside data; this check
        # corroborates the survey verdict above rather than standing
        # alone.
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

    def test_tail_l_irq_status_publish(self) -> None:
        for index, base_val in ((0, 0x11111111), (1, 0x22222222),
                               (3, 0xDEADBEEF), (0xFF, 0xA5A5A5A5)):
            with self.subTest(index=index):
                mem = bytearray(b"\xa5" * (0x100000 + 0x300))
                base = ctypes.addressof(ctypes.c_char.from_buffer(mem))
                out = (ctypes.c_uint32 * 1)(0xA5A5A5A5)
                ret = self.tail_l(index, out, base)
                self.assertEqual(ret, 0)
                want = u32(mem, (index << 12) + 0x204)
                self.assertEqual(out[0], want)
                # The slot read must observe the pre-seeded pattern:
                # high byte of each untouched word stays 0xA5.
                self.assertEqual(mem[(index << 12) + 0x204 + 3], 0xA5)

    def test_tail_m_dualclock_slot_publish(self) -> None:
        for slot, value in ((0, 0x12345678), (1, 0xFFFFFFFF),
                            (2, 0x00000000), (5, 0x004201BA)):
            with self.subTest(slot=slot):
                region = bytearray(0x100)
                for i in range(len(region)):
                    region[i] = 0xA5
                region_p = ctypes.addressof(
                    ctypes.c_char.from_buffer(region))
                ret = self.tail_m(value, slot, region_p)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(region, slot * 16), value & 0xFFFFFFFF)
                for i, byte in enumerate(region):
                    if slot * 16 <= i < slot * 16 + 4:
                        continue
                    self.assertEqual(byte, 0xA5, f"stray write at +{i:#x}")

    def test_tail_n_init_accumulate_and_publish(self) -> None:
        class HostLink(ctypes.Structure):
            # Host model of the target link word: the target's
            # 4-byte slots at +0x00/+0x04 would overlap as 8-byte
            # host pointers, so the word is named native fields.
            # The state -> link thread is preserved.
            _fields_ = [("v14", ctypes.c_uint32),
                        ("p10", ctypes.c_void_p),
                        ("p04", ctypes.c_void_p),
                        ("p00", ctypes.c_void_p)]

        for inw, cfgw1, cfgb8 in ((0x00000000, 0x11111111, 0x00),
                                  (0xFFFFFFFF, 0x22222222, 0x01),
                                  (0x004201BA, 0xDEADBEEF, 0xAB)):
            with self.subTest(inw=hex(inw)):
                state = bytearray(b"\xa5" * 0x40)
                w10 = bytearray(b"\xa5" * 0x20)
                w04 = bytearray(b"\xa5" * 0x20)
                w00 = bytearray(b"\xa5" * 0x20)
                cfg = bytearray(b"\xa5" * 0x10)
                link = HostLink()
                link.v14 = 0x0F0F0F0F
                link.p10 = ctypes.addressof(
                    ctypes.c_char.from_buffer(w10))
                link.p04 = ctypes.addressof(
                    ctypes.c_char.from_buffer(w04))
                link.p00 = ctypes.addressof(
                    ctypes.c_char.from_buffer(w00))
                struct.pack_into("@P", state, 0x24,
                                 ctypes.addressof(link))
                struct.pack_into("<I", cfg, 4, cfgw1)
                cfg[8] = cfgb8
                in_w = (ctypes.c_uint32 * 1)(inw)
                out = (ctypes.c_void_p * 1)(None)
                state_p = ctypes.addressof(
                    ctypes.c_char.from_buffer(state))
                cfg_p = ctypes.addressof(ctypes.c_char.from_buffer(cfg))
                ret = self.tail_n(in_w, cfg_p, out, state_p)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(w10, 0),
                                 (inw | 0x0F0F0F0F) & 0xFFFFFFFF)
                self.assertEqual(u32(w04, 0), cfgw1 & 0xFFFFFFFF)
                self.assertEqual(u32(w00, 0), ((cfgb8 << 1) & 2) & 0xFFFFFFFF)
                self.assertEqual(out[0], state_p)

    def test_tail_o_blockrel_passthrough(self) -> None:
        for value in (0x00000000, 0x00000001, 0xDEADBEEF, 0xFFFFFFFF):
            with self.subTest(value=hex(value)):
                self.assertEqual(self.tail_o(value), value & 0xFFFFFFFF)


if __name__ == "__main__":
    unittest.main()
