#!/usr/bin/env python3
"""BL-006: six dead-tail leaves as reviewed in-place source.

Admits 70 bytes across six single-exit, call-free, branch-free,
literal-free stock tails that survive as unreachable bytes after
replaced heads:

- 0x004278BC..0x004278C8 (12 B): command-queue enable remainder
  (bit-25 merge into the enable word; returns 0).
- 0x004278FC..0x0042790A (14 B): command-queue disable remainder
  (status publish, then bit-25 clear; returns 0).
- 0x00427A4C..0x00427A56 (10 B): command-queue block-post
  remainder (register-table publish; returns 0).
- 0x00427B2E..0x00427B38 (10 B): command-queue termination
  remainder (state-table publish through the head-owned slot;
  returns 0 via pop {r1, r4, r5, pc}).
- 0x00427C02..0x00427C12 (16 B): command-queue reset remainder
  (queue publish, then bit-25 clear; returns 0).
- 0x0042647C..0x00426484 (8 B): MSPI interrupt-enable remainder
  (register publish at base + 0x200; returns 0).

Deadness (all six): the whole-image retained survey grades each
span corroborated_unreachable_control_flow, and a whole-image `bl`
sweep finds no caller of any entry. The reconstructions document
the bytes from reviewed source and pin the behavior the replaced
heads must cover; no live traffic is claimed.

Evidence:
`g2/docs/research/g2-bootloader-bl006-tail-leaves-42647c-427c02-source-closure.md`.
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
    "runtime_bl006_cmdq_irq_tails_4278bc.c"
)

LEAVES: tuple[dict, ...] = (
    {
        "function": "open_cfw_bootloader_cmdq_enable_tail_4278bc",
        "address": 0x004278BC,
        "size": 12,
        "sha256": "7e1a874b7a215628e732acc984029a1a50a095918168bf2ba22cdd7d8d266b48",
    },
    {
        "function": "open_cfw_bootloader_cmdq_disable_tail_4278fc",
        "address": 0x004278FC,
        "size": 14,
        "sha256": "9b37f68b03d4c5eb24064b1fb71666ba59d61118d182378739420160b6e2a0d8",
    },
    {
        "function": "open_cfw_bootloader_cmdq_post_tail_427a4c",
        "address": 0x00427A4C,
        "size": 10,
        "sha256": "b9327206787bf96e58b025028eebf974d282b0032718c442f2aedbb009b6a397",
    },
    {
        "function": "open_cfw_bootloader_cmdq_term_tail_427b2e",
        "address": 0x00427B2E,
        "size": 10,
        "sha256": "433eb6ef5ddfdd266cf77c2c82da47fb640852dc55956f4a77a6bf5350bd3acf",
    },
    {
        "function": "open_cfw_bootloader_cmdq_reset_rem_tail_427c02",
        "address": 0x00427C02,
        "size": 16,
        "sha256": "ba0d5f35c22a12d89ad358608d72c30eb7e64acc726eccacbb991bfc80aab1f9",
    },
    {
        "function": "open_cfw_bootloader_mspi_irq_enable_tail_42647c",
        "address": 0x0042647C,
        "size": 8,
        "sha256": "95f1b19d4d488b37fd91939552d88e79d1361f2f99f005c937e1d178aadd4256",
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
        "apollo_overlay_bl006_cq_tails", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u32(buf: bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


class Bl006CmdqIrqTailLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-bl006-cq-tails-")
        library = Path(cls.temporary.name) / "bl006-cq-tails.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(ROOT / SOURCE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.tail_e = cls.lib.open_cfw_bootloader_cmdq_enable_tail_4278bc
        cls.tail_e.argtypes = [ctypes.c_void_p]
        cls.tail_e.restype = ctypes.c_uint32
        cls.tail_f = cls.lib.open_cfw_bootloader_cmdq_disable_tail_4278fc
        cls.tail_f.argtypes = [ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.c_void_p]
        cls.tail_f.restype = ctypes.c_uint32
        cls.tail_g = cls.lib.open_cfw_bootloader_cmdq_post_tail_427a4c
        cls.tail_g.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.tail_g.restype = ctypes.c_uint32
        cls.tail_h = cls.lib.open_cfw_bootloader_cmdq_term_tail_427b2e
        cls.tail_h.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.tail_h.restype = ctypes.c_uint32
        cls.tail_i = cls.lib.open_cfw_bootloader_cmdq_reset_rem_tail_427c02
        cls.tail_i.argtypes = [ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.c_void_p]
        cls.tail_i.restype = ctypes.c_uint32
        cls.tail_j = cls.lib.open_cfw_bootloader_mspi_irq_enable_tail_42647c
        cls.tail_j.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.tail_j.restype = ctypes.c_uint32

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

    def test_tail_e_enable_merge(self) -> None:
        for initial in (0x00000000, 0x00000001, 0x02000000,
                        0xFFFFFFFF, 0x004201BA):
            with self.subTest(initial=hex(initial)):
                reg = (ctypes.c_uint32 * 1)(initial)
                ret = self.tail_e(reg)
                self.assertEqual(ret, 0)
                self.assertEqual(reg[0], (initial | 0x2000000) & 0xFFFFFFFF)

    def test_tail_f_disable_publish_and_clear(self) -> None:
        for initial, value in ((0xFFFFFFFF, 0x12345678),
                               (0x00000000, 0x00000000),
                               (0x02000000, 0xFFFFFFFF),
                               (0x004201BA, 0xA5A5A5A5)):
            with self.subTest(initial=hex(initial), value=hex(value)):
                reg = (ctypes.c_uint32 * 1)(initial)
                dst = (ctypes.c_uint32 * 1)(0xA5A5A5A5)
                ret = self.tail_f(value, reg, dst)
                self.assertEqual(ret, 0)
                self.assertEqual(dst[0], value & 0xFFFFFFFF)
                self.assertEqual(reg[0], (initial & ~0x2000000) & 0xFFFFFFFF)

    def test_tail_g_post_publish(self) -> None:
        for value in (0x00000000, 0x000000AB, 0x12345678, 0xFFFFFFFF):
            with self.subTest(value=hex(value)):
                ctx = bytearray(0x40)
                t1 = bytearray(0x20)
                t2 = bytearray(0x10)
                for buf in (ctx, t1, t2):
                    for i in range(len(buf)):
                        buf[i] = 0xA5
                t1_p = ctypes.addressof(ctypes.c_char.from_buffer(t1))
                t2_p = ctypes.addressof(ctypes.c_char.from_buffer(t2))
                # Host twin uses native (8-byte) pointer slots; the
                # target twin uses 4-byte slots. Same shape.
                struct.pack_into("@P", ctx, 0x24, t1_p)
                struct.pack_into("@P", t1, 0x0C, t2_p)
                ctx_p = ctypes.addressof(ctypes.c_char.from_buffer(ctx))
                ret = self.tail_g(value, ctx_p)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(t2, 0), value & 0xFFFFFFFF)

    def test_tail_h_term_publish(self) -> None:
        for value in (0x00000000, 0x00000001, 0xDEADBEEF, 0xFFFFFFFF):
            with self.subTest(value=hex(value)):
                slot = bytearray(0x40)
                t1 = bytearray(0x20)
                t2 = bytearray(0x10)
                for buf in (slot, t1, t2):
                    for i in range(len(buf)):
                        buf[i] = 0xA5
                t1_p = ctypes.addressof(ctypes.c_char.from_buffer(t1))
                t2_p = ctypes.addressof(ctypes.c_char.from_buffer(t2))
                struct.pack_into("@P", slot, 0x24, t1_p)
                struct.pack_into("@P", t1, 0x10, t2_p)
                slot_p = ctypes.addressof(ctypes.c_char.from_buffer(slot))
                ret = self.tail_h(value, slot_p)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(t2, 0), value & 0xFFFFFFFF)

    def test_tail_i_reset_publish_and_clear(self) -> None:
        for initial, value in ((0xFFFFFFFF, 0x000000AB),
                               (0x00000000, 0x12345678),
                               (0x02000000, 0xFFFFFFFF)):
            with self.subTest(initial=hex(initial), value=hex(value)):
                reg = (ctypes.c_uint32 * 1)(initial)
                ctx = bytearray(0x20)
                word = bytearray(0x10)
                for i in range(len(ctx)):
                    ctx[i] = 0xA5
                for i in range(len(word)):
                    word[i] = 0xA5
                word_p = ctypes.addressof(ctypes.c_char.from_buffer(word))
                struct.pack_into("@P", ctx, 4, word_p)
                ctx_p = ctypes.addressof(ctypes.c_char.from_buffer(ctx))
                ret = self.tail_i(value, reg, ctx_p)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(word, 0), value & 0xFFFFFFFF)
                self.assertEqual(reg[0], (initial & ~0x2000000) & 0xFFFFFFFF)

    def test_tail_j_irq_enable_publish(self) -> None:
        for value in (0x00000000, 0x00000001, 0xFFFFFFFF, 0x004201BA):
            with self.subTest(value=hex(value)):
                mem = bytearray(0x400)
                for i in range(len(mem)):
                    mem[i] = 0xA5
                base = ctypes.addressof(ctypes.c_char.from_buffer(mem))
                ret = self.tail_j(value, base)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(mem, 0x200), value & 0xFFFFFFFF)
                for i, byte in enumerate(mem):
                    if 0x200 <= i < 0x204:
                        continue
                    self.assertEqual(byte, 0xA5, f"stray write at +{i:#x}")


if __name__ == "__main__":
    unittest.main()
