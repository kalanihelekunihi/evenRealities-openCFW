#!/usr/bin/env python3
"""BL-006: four dead-tail leaves as reviewed in-place source.

Admits 156 bytes across four single-exit, call-free, literal-free
stock tails that survive as unreachable bytes after replaced heads:

- 0x00424AB2..0x00424AEA (56 B): per-instance MSPI state-initializer
  tail (publishes u8[0x0C]=0, u32[0x18]=0, u8[0x8C9]=7, u32[0x8CC]=8
  and the instance address through the out slot; returns 0).
- 0x00424B88..0x00424BD4 (76 B): public MSPI device-configuration
  pre-step tail (0x858-field publish, 0x101-clamp to 0x100, config
  byte copy to offsets 9/8, 0x1A to offset 0xA; returns 0).
- 0x004250E6..0x004250F0 (10 B): MSPI enable epilogue (bit-25 merge
  and publish; returns 0).
- 0x00427C72..0x00427C80 (14 B): command-queue reset epilogue
  (narrow-and-publish through the register table; returns 0).

Deadness (all four): the whole-image retained survey grades each
span corroborated_unreachable_control_flow, and a whole-image `bl`
sweep finds no caller of any entry. The reconstructions document
the bytes from reviewed source and pin the behavior the replaced
heads must cover; no live traffic is claimed.

Evidence:
`g2/docs/research/g2-bootloader-bl006-tail-leaves-424ab2-4250e6-427c72-source-closure.md`.
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

SOURCES = (
    "components/bootloader/core_overlay/runtime_bl006_mspi_state_tails_424ab2.c",
    "components/bootloader/core_overlay/runtime_bl006_epilogue_tails_4250e6.c",
)

LEAVES: tuple[dict, ...] = (
    {
        "function": "open_cfw_bootloader_mspi_state_init_tail_424ab2",
        "address": 0x00424AB2,
        "size": 56,
        "sha256": "213f290182ee49afc1b6b8daee27519211c99dca941611c247a2ac87437bc231",
    },
    {
        "function": "open_cfw_bootloader_mspi_config_pre_tail_424b88",
        "address": 0x00424B88,
        "size": 76,
        "sha256": "3e4088f04c633d066dccba4423ca3d63b1328ae7798809af3b156241f4203edb",
    },
    {
        "function": "open_cfw_bootloader_mspi_enable_tail_4250e6",
        "address": 0x004250E6,
        "size": 10,
        "sha256": "1bb97734fb42a005414ee4a5ea9783acf43addb631e489d8ea445d39ba5d5492",
    },
    {
        "function": "open_cfw_bootloader_cmdq_reset_tail_427c72",
        "address": 0x00427C72,
        "size": 14,
        "sha256": "77c01bfefef2ae36baff14339b0f796d2a9d1686bd9f4352a194fbb5e5590389",
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
        "apollo_overlay_bl006_tails", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u32(buf: bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def set_u32(buf: bytearray, off: int, value: int) -> None:
    struct.pack_into("<I", buf, off, value & 0xFFFFFFFF)


class Bl006TailLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-bl006-tails-")
        library = Path(cls.temporary.name) / "bl006-tails.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", *[str(ROOT / s) for s in SOURCES], "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.tail_a = cls.lib.open_cfw_bootloader_mspi_state_init_tail_424ab2
        cls.tail_a.argtypes = [ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_void_p]
        cls.tail_a.restype = ctypes.c_uint32
        cls.tail_b = cls.lib.open_cfw_bootloader_mspi_config_pre_tail_424b88
        cls.tail_b.argtypes = [ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.c_void_p, ctypes.c_uint32,
                               ctypes.c_void_p]
        cls.tail_b.restype = ctypes.c_uint32
        cls.tail_c = cls.lib.open_cfw_bootloader_mspi_enable_tail_4250e6
        cls.tail_c.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.tail_c.restype = ctypes.c_uint32
        cls.tail_d = cls.lib.open_cfw_bootloader_cmdq_reset_tail_427c72
        cls.tail_d.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.tail_d.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def stock(self, address: int, size: int) -> bytes:
        return self.image[address - RUN_BASE:address - RUN_BASE + size]

    def source_of(self, function: str) -> str:
        for entry in self.overlay.get("in_place_leaves", []):
            if entry["function"] == function:
                return entry["source"]["path"]
        if function.endswith("424ab2") or function.endswith("424b88"):
            return SOURCES[0]
        return SOURCES[1]

    def compile_leaf(self, leaf: dict, path: str) -> tuple[bytes, dict]:
        source_bytes = (ROOT / path).read_bytes()
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
                        "path": path,
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
                payload, report = self.compile_leaf(
                    leaf, self.source_of(leaf["function"]))
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
                self.assertEqual(entry["source"]["path"],
                                 self.source_of(leaf["function"]))

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

    def test_tail_a_init_window(self) -> None:
        for stride, index in ((0x900, 0), (0x900, 1), (0x940, 2), (0x8D4, 3)):
            with self.subTest(stride=hex(stride), index=index):
                mem = bytearray(0x4000)
                for i in range(len(mem)):
                    mem[i] = 0xA5
                out = (ctypes.c_uint32 * 1)()
                base = ctypes.addressof(ctypes.c_char.from_buffer(mem))
                ret = self.tail_a(stride, out, 0, index, base)
                self.assertEqual(ret, 0)
                poff = index * stride
                self.assertEqual(mem[poff + 0x0C], 0)
                self.assertEqual(u32(mem, poff + 0x18), 0)
                self.assertEqual(mem[poff + 0x8C9], 7)
                self.assertEqual(u32(mem, poff + 0x8CC), 8)
                self.assertEqual(out[0], (base + poff) & 0xFFFFFFFF)
                touched = {poff + 0x0C, poff + 0x8C9}
                touched.update(range(poff + 0x18, poff + 0x1C))
                touched.update(range(poff + 0x8CC, poff + 0x8D0))
                for i, byte in enumerate(mem):
                    if i not in touched:
                        self.assertEqual(byte, 0xA5, f"stray write at +{i:#x}")

    def test_tail_b_config_pre_step(self) -> None:
        for key, field, cfg8 in ((2, 0x00000000, 0x5A),
                                 (2, 0x00000100, 0x00),
                                 (3, 0x00000101, 0xFF),
                                 (1, 0xDEADBEEF, 0x33)):
            with self.subTest(key=key, field=hex(field)):
                mem = bytearray(0x4000)
                for i in range(len(mem)):
                    mem[i] = 0xA5
                cfg = bytearray(16)
                cfg[8] = cfg8
                k = key + 0x42A
                qoff = k * key
                set_u32(mem, qoff + 0x858, field)
                base = ctypes.addressof(ctypes.c_char.from_buffer(mem))
                cfg_p = ctypes.addressof(ctypes.c_char.from_buffer(cfg))
                dst = base  # destination word lives at dst + 0x858
                value = 0x12345678
                ret = self.tail_b(value, cfg_p, dst, key, base)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(mem, 0x858), value)
                self.assertEqual(
                    u32(mem, qoff + 0x858),
                    0x100 if field >= 0x101 else field)
                self.assertEqual(mem[qoff + 9], cfg8)
                self.assertEqual(mem[qoff + 8], 1)
                self.assertEqual(mem[qoff + 0xA], 0x1A)

    def test_tail_c_enable_merge(self) -> None:
        for value in (0x00000000, 0x00000001, 0x02000000, 0xFFFFFFFF,
                      0x004201BA):
            with self.subTest(value=hex(value)):
                reg = (ctypes.c_uint32 * 1)(0xA5A5A5A5)
                ret = self.tail_c(value, reg)
                self.assertEqual(ret, 0)
                self.assertEqual(reg[0], (value | 0x2000000) & 0xFFFFFFFF)

    def test_tail_d_reset_publish(self) -> None:
        for value in (0x00000000, 0x000000AB, 0x000001AB, 0xFFFFFFFF):
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
                ret = self.tail_d(value, ctx_p)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(t2, 0), value & 0xFF)


if __name__ == "__main__":
    unittest.main()
