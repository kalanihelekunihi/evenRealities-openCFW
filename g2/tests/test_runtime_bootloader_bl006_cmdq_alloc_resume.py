#!/usr/bin/env python3
"""BL-006: allocator / error-resume dead interiors as reviewed source.

Admits 58 bytes across two official_blob regions as reviewed MIT C
through the bootloader component's in-place-leaf mechanism:

- 0x0042799E..0x004279BE (32 B): command-queue allocator remainder
  (wrap publish, failure return, slow-path bounds check; three
  entries fed only from the replaced allocator head, exits rejoin
  the head success path at 0x00427970 or the head epilogue at
  0x00427984).
- 0x00427B90..0x00427BAA (26 B): command-queue error-resume
  remainder (scan loop-back plus match epilogue: register publish,
  entry-pointer publish, prefix bit-25 clear, return 0).

The five narrow unconditional exits into the replaced heads cannot
name far-absolute mnemonic operands in the relocatable object, so
each is spelled with its reviewed 16-bit encoding (`.inst.n`);
six in-source assembler probes prove the reference assembler emits
the identical bytes for an identical branch at the identical
offset (same precedent as the binary32 remainder tail).

Deadness (both spans): the whole-image retained survey grades each
span corroborated_unreachable_control_flow, and a whole-image `bl`
sweep finds no caller of either entry. The live allocator and
error-resume behavior is already source-owned by the
AmbiqSuite-adapted runtime_cmdq_services_427794.c; these leaves
document the dead bytes and pin the behavior the live heads cover.
No live traffic is claimed.

Evidence:
`g2/docs/research/g2-bootloader-bl006-tail-leaves-42799e-427b90-source-closure.md`.
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
    "runtime_bl006_cmdq_alloc_resume_tails_42799e.c"
)

LEAVES: tuple[dict, ...] = (
    {
        "function": "open_cfw_bootloader_cmdq_alloc_rem_tail_42799e",
        "address": 0x0042799E,
        "size": 32,
        "sha256": "dcf9d1eae1901c914dcc21e28cc1f8de507044dc67797f930c622068fd307b97",
        "relocations": [
            {"offset": 4, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_cmdq_alloc_success_427970",
             "symbol_type": "STT_NOTYPE", "target_address": 0x427970},
            {"offset": 8, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_cmdq_alloc_epilogue_427984",
             "symbol_type": "STT_NOTYPE", "target_address": 0x427984},
            {"offset": 26, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_cmdq_alloc_success_427970",
             "symbol_type": "STT_NOTYPE", "target_address": 0x427970},
            {"offset": 30, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_cmdq_alloc_epilogue_427984",
             "symbol_type": "STT_NOTYPE", "target_address": 0x427984},
        ],
    },
    {
        "function": "open_cfw_bootloader_cmdq_errresume_rem_tail_427b90",
        "address": 0x00427B90,
        "size": 26,
        "sha256": "083d6df438d62d8c22618063fe1a0756dd25ad4f4dda8eb7bb71f0ecc0c4a27f",
        "relocations": [
            {"offset": 0, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_cmdq_error_resume_scan_427b76",
             "symbol_type": "STT_NOTYPE", "target_address": 0x427B76},
        ],
    },
)

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror", "-fno-ident",
]

# Assembler probes: (function, pad bytes before/after the branch,
# branch position, branch bytes). Backward probes are pad +
# branch; the forward bhs probe is branch + two NOPs.
PROBES: tuple[dict, ...] = (
    {"function": "open_cfw_bl006_ax_probe_b_54_back",
     "pad": 50, "side": "back", "encoding": bytes.fromhex("e5e7")},
    {"function": "open_cfw_bl006_ax_probe_b_38_back",
     "pad": 34, "side": "back", "encoding": bytes.fromhex("ede7")},
    {"function": "open_cfw_bl006_ax_probe_bhs_2_fwd",
     "pad": 4, "side": "front", "encoding": bytes.fromhex("01d2")},
    {"function": "open_cfw_bl006_ax_probe_b_76_back",
     "pad": 72, "side": "back", "encoding": bytes.fromhex("dae7")},
    {"function": "open_cfw_bl006_ax_probe_b_60_back",
     "pad": 56, "side": "back", "encoding": bytes.fromhex("e2e7")},
    {"function": "open_cfw_bl006_ax_probe_b_30_back",
     "pad": 26, "side": "back", "encoding": bytes.fromhex("f1e7")},
)

NOP = bytes.fromhex("00bf")  # `nop` = 0xBF00 stored little-endian


def load_module():
    spec = importlib.util.spec_from_file_location(
        "apollo_overlay_bl006_ax_tails", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u32(buf: bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def probe_section_bytes(probe: dict) -> bytes:
    if probe["side"] == "back":
        return b"\x00" * probe["pad"] + probe["encoding"]
    return probe["encoding"] + NOP * (probe["pad"] // 2)


class Bl006AllocResumeTailLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-bl006-ax-tails-")
        library = Path(cls.temporary.name) / "bl006-ax-tails.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(ROOT / SOURCE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.alloc = cls.lib.open_cfw_bootloader_cmdq_alloc_rem_tail_42799e
        cls.alloc.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.c_void_p, ctypes.c_uint,
                              ctypes.c_void_p]
        cls.alloc.restype = ctypes.c_uint32
        cls.resume = cls.lib.open_cfw_bootloader_cmdq_errresume_rem_tail_427b90
        cls.resume.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                               ctypes.c_void_p, ctypes.c_void_p]
        cls.resume.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def stock(self, address: int, size: int) -> bytes:
        return self.image[address - RUN_BASE:address - RUN_BASE + size]

    def compile_function(
        self,
        function: str,
        size: int,
        sha256: str,
        *,
        address: int = 0x00420000,
        relocations: list[dict] | None = None,
        strict_relocation_contract: bool = False,
    ) -> tuple[bytes, dict]:
        source_bytes = (ROOT / SOURCE).read_bytes()
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as directory:
            payload, report = self.module.compile_in_place_leaf(
                root=ROOT,
                clang=CLANG,
                leaf_config={
                    "function": function,
                    "runtime_address": address,
                    "source": {
                        "path": SOURCE,
                        "size": len(source_bytes),
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                    },
                    "toolchain": {"target": "arm-none-eabi",
                                  "flags": FLAGS},
                    "strict_relocation_contract": strict_relocation_contract,
                    "expected": {"size": size, "sha256": sha256},
                    "stock": {"size": size, "sha256": sha256},
                    "relocations": [dict(row) for row in (relocations or [])],
                    "allow_discarded_alloc_sections": True,
                },
                object_path=Path(directory) / "leaf.o",
            )
        return payload, report

    def compile_leaf(self, leaf: dict) -> tuple[bytes, dict]:
        return self.compile_function(
            leaf["function"], leaf["size"], leaf["sha256"],
            address=leaf["address"],
            relocations=leaf["relocations"],
            strict_relocation_contract=True,
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
                self.assertEqual(
                    [
                        {
                            key: row[key]
                            for key in (
                                "offset", "type", "symbol",
                                "target_address", "symbol_type",
                            )
                        }
                        for row in extraction["relocations"]
                    ],
                    leaf["relocations"],
                )
                self.assertEqual(extraction["function"], leaf["function"])
                self.assertEqual(extraction["size"], leaf["size"])
                self.assertEqual(extraction["sha256"], leaf["sha256"])

    def test_probes_emit_stock_encodings(self) -> None:
        for probe in PROBES:
            with self.subTest(function=probe["function"]):
                want = probe_section_bytes(probe)
                payload, report = self.compile_function(
                    probe["function"], len(want),
                    hashlib.sha256(want).hexdigest())
                self.assertEqual(payload, want)
                if probe["side"] == "back":
                    self.assertEqual(payload[-2:], probe["encoding"])
                else:
                    self.assertEqual(payload[:2], probe["encoding"])
                extraction = report["extraction"]
                self.assertEqual(extraction["relocation_count"], 0)

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
                self.assertEqual(entry["relocations"], leaf["relocations"])
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

    def test_alloc_wrap_publish(self) -> None:
        for f1 in (0x00000000, 0x00000001, 0x12345678, 0xFFFFFFFF):
            with self.subTest(f1=hex(f1)):
                slot = (ctypes.c_uint32 * 2)(0xA5A5A5A5, 0xA5A5A5A5)
                exit_kind = (ctypes.c_uint32 * 1)(0xFFFFFFFF)
                ret = self.alloc(f1, 0, 0, 0, slot, 0, exit_kind)
                self.assertEqual(ret, f1 & 0xFFFFFFFF)
                self.assertEqual(slot[0], 0xA5A5A5A5)
                self.assertEqual(slot[1], f1 & 0xFFFFFFFF)
                self.assertEqual(exit_kind[0], 0)

    def test_alloc_fail_returns_five(self) -> None:
        exit_kind = (ctypes.c_uint32 * 1)(0xFFFFFFFF)
        slot = (ctypes.c_uint32 * 2)(0, 0)
        ret = self.alloc(0, 0, 0, 0, slot, 1, exit_kind)
        self.assertEqual(ret, 5)
        self.assertEqual(exit_kind[0], 1)
        self.assertEqual(slot[0], 0)
        self.assertEqual(slot[1], 0)

    def test_alloc_bounds_check(self) -> None:
        mask = 0xFFFFFFFF
        vectors = [
            # (base, limit, index)
            (0x20000000, 0x20000100, 0),
            (0x20000000, 0x20000100, 15),
            (0x20000000, 0x20000100, 16),
            (0x20000000, 0x20000008, 0),
            (0x20000000, 0x20000009, 0),
            (0x00000000, 0x00000001, 0),
            (0xFFFFFFFF, 0xFFFFFFFF, 0),
            (0xFFFFFFFF, 0x00000000, 0),
            (0xFFFFFFF8, 0x00000008, 0),
            (0x20000000, 0x20000000, 0xFFFFFFFF),
            (0x00000000, 0x00000000, 0xFFFFFFFF),
            (0x12345678, 0x9ABCDEF0, 0x004201BA),
            (0x00000000, 0xFFFFFFFF, 0x1FFFFFFE),
            (0x00000000, 0xFFFFFFFF, 0x1FFFFFFF),
        ]
        for base, limit, index in vectors:
            with self.subTest(base=hex(base), limit=hex(limit),
                               index=hex(index)):
                slot = (ctypes.c_uint32 * 2)(0xA5A5A5A5, 0xA5A5A5A5)
                exit_kind = (ctypes.c_uint32 * 1)(0xFFFFFFFF)
                ret = self.alloc(0, base, limit, index, slot, 2, exit_kind)
                end = (base + ((((index + 1) & mask) << 3) & mask)) & mask
                if end >= limit:
                    self.assertEqual(ret, 5)
                    self.assertEqual(exit_kind[0], 1)
                else:
                    self.assertEqual(ret, base & mask)
                    self.assertEqual(exit_kind[0], 0)
                self.assertEqual(slot[0], 0xA5A5A5A5)
                self.assertEqual(slot[1], 0xA5A5A5A5)

    def test_errresume_match_epilogue(self) -> None:
        for prefix, qval in ((0x00000000, 0x00000000),
                             (0xFFFFFFFF, 0x12345678),
                             (0x02000000, 0xFFFFFFFF),
                             (0x004201BA, 0x004201BA),
                             (0xFDFFFFFF, 0xDEADBEEF)):
            with self.subTest(prefix=hex(prefix), qval=hex(qval)):
                entry = (ctypes.c_uint32 * 1)(0xA5A5A5A5)
                slot = (ctypes.c_void_p * 1)(None)
                prefix_box = (ctypes.c_uint32 * 1)(prefix)
                ret = self.resume(entry, qval, slot, prefix_box)
                self.assertEqual(ret, 0)
                self.assertEqual(entry[0], qval & 0xFFFFFFFF)
                self.assertEqual(slot[0], ctypes.addressof(entry))
                self.assertEqual(prefix_box[0],
                                 (prefix & ~0x2000000) & 0xFFFFFFFF)


if __name__ == "__main__":
    unittest.main()
