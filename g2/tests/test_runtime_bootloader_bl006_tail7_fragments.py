#!/usr/bin/env python3
"""BL-006: seven dead-tail leaves plus four fragment/data slots as source.

Admits 84 bytes across seven official_blob regions as reviewed MIT
C through the bootloader component's in-place mechanisms:

leaves (74 B, single-entry; out-of-span branches use reviewed
explicit-width encodings because the relocatable object cannot
resolve far-absolute mnemonic operands):
- 0x00426C22..0x00426C24 (2 B): memset-wrapper terminal return
  (`pop {r4, pc}`).
- 0x00426C70..0x00426C72 (2 B): CLKGEN HFADJ-enable terminal
  return (bare `bx lr`, r0 pass-through).
- 0x00427ABE..0x00427AD6 (24 B): command-queue status remainder
  (clear pending flag, booleanize mask hit, publish, return 0).
- 0x00427D84..0x00427D98 (20 B): binary32 remainder-code
  remainder (conditional complement, restore r4, branch to
  0x004275C4 on carry-clear else return).
- 0x004275C4..0x004275D2 (14 B): System-PLL alternate setter
  entry (load cell pointer, select 0x21, join the shared body at
  0x004275DE inside the routed range-error span).
- 0x00425162..0x00425166 (4 B): MSPI disable mini-tail
  (zero return, restore head-owned block, return).
- 0x004264B2..0x004264BA (8 B): MSPI interrupt-disable publish
  tail (store word at base + 0x200, return 0);

data (10 B, no loader in any routed span; layout preservation):
- 0x00425160 (2 B): orphaned second halfword of the replaced
  disable head's `bl` (authentic stream decoded anchored at
  0x00425140 shows the branch spanning 0x0042515E..0x00425162).
- 0x00425166 (2 B): alignment NOP before the lifecycle word.
- 0x00425168 (4 B): lifecycle literal word 0x0007FFFF.
- 0x004264B0 (2 B): orphaned second halfword of the replaced
  interrupt-disable head's `adds.w` at 0x004264AE.

Deadness: the 0x00425160, 0x004264B0, 0x00427ABE and 0x00427588
regions grade corroborated_unreachable_control_flow; the
0x00426C22, 0x00426C70 and 0x00427D84 regions grade
no_control_flow_reference_found (zero inbound references; the
weaker verdict is asserted explicitly, not upgraded). A
whole-image `bl` sweep finds no caller of any new entry. No live
traffic is claimed.

Evidence:
`g2/docs/research/g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md`.
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

LEAF_FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror", "-fno-ident",
]

DATA_FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]

# (source file, function, address, size, stock sha256, survey verdict)
LEAVES: tuple[dict, ...] = (
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_terminal_returns_426c22.c",
        "function": "open_cfw_bootloader_memset_term_tail_426c22",
        "address": 0x00426C22, "size": 2,
        "sha256": "d61f3ece088ca2fb6ebd3f47479ea5514bdbc39d0decd1f678f629b107878331",
        "verdict": "no_control_flow_reference_found",
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_terminal_returns_426c22.c",
        "function": "open_cfw_bootloader_clkgen_hfadj_term_426c70",
        "address": 0x00426C70, "size": 2,
        "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
        "verdict": "no_control_flow_reference_found",
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_cmdq_status_binary32_tails_427abe.c",
        "function": "open_cfw_bootloader_cmdq_status_rem_tail_427abe",
        "address": 0x00427ABE, "size": 24,
        "sha256": "ba93a98be719d439c0f4e3d362c1df2174a73fcc44ae3f82a1a413d3ed051785",
        "verdict": "corroborated_unreachable_control_flow",
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_cmdq_status_binary32_tails_427abe.c",
        "function": "open_cfw_bootloader_binary32_rem_tail_427d84",
        "address": 0x00427D84, "size": 20,
        "sha256": "f35a5cb7dfcde48c147a027e717db6113d416a95014c14703077f500022a44eb",
        "verdict": "no_control_flow_reference_found",
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_syspll_alt_entry_4275c4.c",
        "function": "open_cfw_bootloader_syspll_alt_entry_4275c4",
        "address": 0x004275C4, "size": 14,
        "sha256": "a19e550e2348b6ab72f1f7ef0d2d2afa12d5b6e0944b3df1251c96119706d103",
        "verdict": "corroborated_unreachable_control_flow",
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_disable_tail_425162.c",
        "function": "open_cfw_bootloader_mspi_disable_tail_425162",
        "address": 0x00425162, "size": 4,
        "sha256": "39db35cdc8a3648d1290136b2bda70dee2ed777bd3ff3c5d3705f7830f99887b",
        "verdict": "corroborated_unreachable_control_flow",
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_irq_disable_tail_4264b2.c",
        "function": "open_cfw_bootloader_mspi_irq_disable_tail_4264b2",
        "address": 0x004264B2, "size": 8,
        "sha256": "95f1b19d4d488b37fd91939552d88e79d1361f2f99f005c937e1d178aadd4256",
        "verdict": "corroborated_unreachable_control_flow",
    },
)

FRAG_PATH = "components/bootloader/core_overlay/runtime_bl006_tail_fragments_425160.c"

# (symbol, section, address, size, stock sha256); every slot must
# keep zero loaders in routed spans.
GROUPS: tuple[dict, ...] = (
    {
        "symbol": "open_cfw_bootloader_bl006_frag_425160",
        "section": ".rodata.bl006_frag_425160",
        "address": 0x00425160, "size": 2, "alignment": 2,
        "sha256": "7e514f4d67033d5a47c08c087464bfdd9c8870fcd3d107afcb6d0d147e3d604b",
    },
    {
        "symbol": "open_cfw_bootloader_bl006_pad_425166",
        "section": ".rodata.bl006_pad_425166",
        "address": 0x00425166, "size": 2, "alignment": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
    },
    {
        "symbol": "open_cfw_bootloader_bl006_word_425168",
        "section": ".rodata.bl006_word_425168",
        "address": 0x00425168, "size": 4, "alignment": 4,
        "sha256": "5341298afd21f5e76cac512809a468048bf5475e24b7e0105dd97be2c99d8b7f",
    },
    {
        "symbol": "open_cfw_bootloader_bl006_frag_4264b0",
        "section": ".rodata.bl006_frag_4264b0",
        "address": 0x004264B0, "size": 2, "alignment": 2,
        "sha256": "fa61e3dec3439589f4784c893bf321d0084f04c572c7af2b68e3f3360a35b486",
    },
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "apollo_overlay_bl006_tail7", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u32(buf: bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


class Bl006TailLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-bl006-tail7-")
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        cls.libs = {}
        for path in {l["path"] for l in LEAVES}:
            library = Path(cls.temporary.name) / (Path(path).stem + ".so")
            subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
                 "-fPIC", str(ROOT / path), "-o", str(library)],
                cwd=ROOT, check=True,
            )
            cls.libs[path] = ctypes.CDLL(str(library))
        lib = cls.libs[
            "components/bootloader/core_overlay/runtime_bl006_terminal_returns_426c22.c"]
        cls.term_pop = lib.open_cfw_bootloader_memset_term_tail_426c22
        cls.term_pop.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                 ctypes.c_void_p]
        cls.term_pop.restype = None
        cls.term_bx = lib.open_cfw_bootloader_clkgen_hfadj_term_426c70
        cls.term_bx.argtypes = [ctypes.c_uint32]
        cls.term_bx.restype = ctypes.c_uint32
        lib = cls.libs[
            "components/bootloader/core_overlay/runtime_bl006_cmdq_status_binary32_tails_427abe.c"]
        cls.status = lib.open_cfw_bootloader_cmdq_status_rem_tail_427abe
        cls.status.argtypes = [ctypes.c_uint32, ctypes.c_void_p,
                               ctypes.c_void_p]
        cls.status.restype = ctypes.c_uint32
        cls.rem = lib.open_cfw_bootloader_binary32_rem_tail_427d84
        cls.rem.argtypes = [ctypes.c_uint32] * 5 + [ctypes.c_void_p] * 2
        cls.rem.restype = None
        lib = cls.libs[
            "components/bootloader/core_overlay/runtime_bl006_syspll_alt_entry_4275c4.c"]
        cls.alt = lib.open_cfw_bootloader_syspll_alt_entry_4275c4
        cls.alt.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.alt.restype = ctypes.c_uint32
        lib = cls.libs[
            "components/bootloader/core_overlay/runtime_bl006_disable_tail_425162.c"]
        cls.disable = lib.open_cfw_bootloader_mspi_disable_tail_425162
        cls.disable.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.disable.restype = None
        lib = cls.libs[
            "components/bootloader/core_overlay/runtime_bl006_irq_disable_tail_4264b2.c"]
        cls.irq = lib.open_cfw_bootloader_mspi_irq_disable_tail_4264b2
        cls.irq.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.irq.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def stock(self, address: int, size: int) -> bytes:
        return self.image[address - RUN_BASE:address - RUN_BASE + size]

    def compile_leaf(self, leaf: dict) -> tuple[bytes, dict]:
        source_bytes = (ROOT / leaf["path"]).read_bytes()
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
                        "path": leaf["path"],
                        "size": len(source_bytes),
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                    },
                    "toolchain": {"target": "arm-none-eabi",
                                  "flags": LEAF_FLAGS},
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

    def compile_group(self, group: dict) -> tuple[bytes, dict]:
        source_bytes = (ROOT / FRAG_PATH).read_bytes()
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as directory:
            payload, report = self.module.compile_in_place_data_group(
                root=ROOT,
                clang=CLANG,
                group_config={
                    "symbol": group["symbol"],
                    "section": group["section"],
                    "source": {
                        "path": FRAG_PATH,
                        "size": len(source_bytes),
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                    },
                    "toolchain": {"target": "arm-none-eabi",
                                  "flags": DATA_FLAGS},
                    "expected": {"size": group["size"],
                                 "sha256": group["sha256"],
                                 "alignment": group.get("alignment", 1)},
                    "placements": [
                        {
                            "name": group["symbol"].split("bl006_", 1)[1],
                            "runtime_address": group["address"],
                            "source_offset": 0,
                            "size": group["size"],
                            "stock_sha256": group["sha256"],
                        }
                    ],
                },
                object_path=Path(directory) / "data.o",
            )
        return payload, report

    def test_stock_spans_unchanged(self) -> None:
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                observed = hashlib.sha256(
                    self.stock(leaf["address"], leaf["size"])).hexdigest()
                self.assertEqual(observed, leaf["sha256"])
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                observed = hashlib.sha256(
                    self.stock(group["address"], group["size"])).hexdigest()
                self.assertEqual(observed, group["sha256"])

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

    def test_compiled_groups_match_stock(self) -> None:
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                payload, report = self.compile_group(group)
                self.assertEqual(
                    payload, self.stock(group["address"], group["size"]))
                extraction = report["extraction"]
                self.assertEqual(extraction["relocation_count"], 0)
                self.assertEqual(extraction["symbol"], group["symbol"])

    def test_overlay_registers_entries(self) -> None:
        leaves = {item["function"]: item
                  for item in self.overlay.get("in_place_leaves", [])}
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                self.assertIn(leaf["function"], leaves)
                entry = leaves[leaf["function"]]
                self.assertEqual(entry["runtime_address"], leaf["address"])
                self.assertEqual(entry["expected"]["size"], leaf["size"])
                self.assertEqual(entry["expected"]["sha256"], leaf["sha256"])
                self.assertEqual(entry["stock"]["sha256"], leaf["sha256"])
                self.assertEqual(entry["relocations"], [])
                self.assertTrue(entry["strict_relocation_contract"])
                self.assertEqual(entry["source"]["license"], "MIT")
                self.assertEqual(entry["source"]["path"], leaf["path"])
        groups = {item["symbol"]: item
                  for item in self.overlay.get("in_place_data", [])}
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                self.assertIn(group["symbol"], groups)
                entry = groups[group["symbol"]]
                self.assertEqual(entry["section"], group["section"])
                self.assertEqual(entry["expected"]["size"], group["size"])
                self.assertEqual(entry["expected"]["sha256"], group["sha256"])
                placements = entry["placements"]
                self.assertEqual(len(placements), 1)
                self.assertEqual(
                    placements[0]["runtime_address"], group["address"])
                self.assertEqual(placements[0]["source_offset"], 0)
                self.assertEqual(placements[0]["size"], group["size"])
                self.assertEqual(
                    placements[0]["stock_sha256"], group["sha256"])
                self.assertEqual(entry["source"]["path"], FRAG_PATH)
                self.assertEqual(entry["source"]["license"], "MIT")

    def test_survey_grades_spans(self) -> None:
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
        # Leaves pin their region's exact survey verdict; the three
        # no-control-flow spans keep the weaker verdict explicitly.
        region_of = {
            0x00426C22: 0x00426C22, 0x00426C70: 0x00426C70,
            0x00427ABE: 0x00427ABE, 0x00427D84: 0x00427D84,
            0x004275C4: 0x00427588, 0x00425162: 0x00425160,
            0x004264B2: 0x004264B0,
        }
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                region = by_start.get(region_of[leaf["address"]])
                self.assertIsNotNone(
                    region, f"no survey region for {leaf['address']:#x}")
                assert region is not None
                self.assertEqual(region["verdict"], leaf["verdict"])
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                start = 0x00425160 if group["address"] < 0x00426000 else 0x004264B0
                region = by_start.get(start)
                self.assertIsNotNone(region)
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
        # corroborates the survey verdicts above rather than
        # standing alone.
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

    def test_fragment_slots_keep_no_loader(self) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        # Dead documentation leaves (in-place leaves inside
        # survey-graded corroborated_unreachable spans) reproduce
        # stock pool loads without executing; only a LIVE loader
        # would change a slot's standing. The BL-006 region-1
        # leaf references 0x00425168 from two dead F3 arms.
        path = ROOT / "tools/analyze_g2_bootloader_bl006_retained_survey.py"
        spec = importlib.util.spec_from_file_location(
            "analyze_g2_bootloader_bl006_retained_survey_loader", path)
        assert spec is not None and spec.loader is not None
        survey_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = survey_module
        spec.loader.exec_module(survey_module)
        dead: list[tuple[int, int]] = []
        for region in survey_module.survey()["regions"]:
            if region.get("verdict") != "corroborated_unreachable_control_flow":
                continue
            try:
                dead.append((int(str(region["start"]), 16),
                             int(str(region["end"]), 16)))
            except (KeyError, ValueError):
                continue

        def is_dead_span(start: int, end: int) -> bool:
            return any(dstart <= start and end <= dend
                       for dstart, dend in dead)

        wanted = {g["address"] for g in GROUPS}
        spans: list[tuple[int, int, str, str]] = []
        for entry in self.overlay.get("in_place_leaves", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["expected"]["size"])
            if is_dead_span(start, end):
                continue
            spans.append((start, end, entry["function"], "in_place"))
        for entry in self.overlay.get("patch_sites", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["expected_size"])
            spans.append((start, end, entry["name"], "patch_stock"))
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        live: dict[int, list[str]] = {}
        for start, end, name, kind in sorted(spans):
            if kind != "in_place":
                continue
            code = self.image[start - RUN_BASE:end - RUN_BASE]
            for insn in decoder.disasm(code, start):
                for op in insn.operands:
                    target = None
                    if op.type == ARM_OP_MEM and insn.reg_name(
                            op.mem.base) == "pc":
                        target = ((insn.address + 4) & ~3) + op.mem.disp
                    elif op.type == ARM_OP_IMM and insn.mnemonic.startswith(
                            "adr"):
                        target = ((insn.address + 4) & ~3) + op.imm
                    if target in wanted:
                        live.setdefault(target, []).append(name)
        for slot in sorted(wanted):
            self.assertEqual(
                live.get(slot, []), [],
                f"fragment slot {slot:#x} gained a routed loader")

    def test_term_pop_restores_slots(self) -> None:
        for r4, ret in ((0x00000000, 0x004201BA),
                        (0xDEADBEEF, 0xFFFFFFFF),
                        (0x12345678, 0x00000001)):
            with self.subTest(r4=hex(r4)):
                sp = (ctypes.c_uint32 * 2)(r4, ret)
                r4_out = (ctypes.c_uint32 * 1)(0)
                ret_out = (ctypes.c_uint32 * 1)(0)
                self.term_pop(sp, r4_out, ret_out)
                self.assertEqual(r4_out[0], r4 & 0xFFFFFFFF)
                self.assertEqual(ret_out[0], ret & 0xFFFFFFFF)

    def test_term_bx_passthrough(self) -> None:
        for value in (0x00000000, 0x00000001, 0xDEADBEEF, 0xFFFFFFFF):
            with self.subTest(value=hex(value)):
                self.assertEqual(
                    self.term_bx(value), value & 0xFFFFFFFF)

    def test_status_publish_and_zero_return(self) -> None:
        for status, mask in ((0x00000000, 0x00000000),
                             (0xFFFFFFFF, 0x00000001),
                             (0x004201BA, 0x000000FF),
                             (0xDEADBEEF, 0xF0000000)):
            with self.subTest(status=hex(status), mask=hex(mask)):
                ctx4 = bytearray(b"\xa5" * 0x10)
                link = bytearray(b"\xa5" * 0x30)
                struct.pack_into("<I", link, 0x20, mask)
                ctx5 = bytearray(b"\xa5" * 0x30)
                struct.pack_into("@P", ctx5, 0x24,
                                 ctypes.addressof(
                                     ctypes.c_char.from_buffer(link)))
                ret = self.status(
                    status,
                    ctypes.addressof(ctypes.c_char.from_buffer(ctx4)),
                    ctypes.addressof(ctypes.c_char.from_buffer(ctx5)))
                self.assertEqual(ret, 0)
                self.assertEqual(ctx4[0x0D], 0)
                self.assertEqual(ctx4[0x0E], 1 if (status & mask) else 0)
                for i, byte in enumerate(ctx4):
                    if i in (0x0D, 0x0E):
                        continue
                    self.assertEqual(byte, 0xA5, f"stray write at +{i:#x}")

    def test_remainder_complement_and_branch(self) -> None:
        # (r1, r2, r3, C_in, Z_in, expected_complement, expected_branch)
        # expected values follow the stock IT structure: HS takes
        # ~r3 with head flags; LO re-derives flags from r1 + r2.
        cases = (
            (0x11111111, 0x22222222, 0x12345678, 1, 0, True, False),
            (0x11111111, 0x22222222, 0x12345678, 1, 1, True, False),
            (0x00000000, 0x00000000, 0xAAAAAAAA, 0, 0, False, True),
            (0x00000001, 0x00000002, 0xAAAAAAAA, 0, 0, True, True),
            (0xFFFFFFFF, 0x00000001, 0xAAAAAAAA, 0, 0, False, False),
        )
        for r1, r2, r3, cin, zin, comp, branch in cases:
            with self.subTest(r1=hex(r1), r2=hex(r2), cin=cin):
                apsr = ((cin & 1) << 29) | ((zin & 1) << 30)
                r0 = (ctypes.c_uint32 * 1)(0)
                br = (ctypes.c_uint32 * 1)(0)
                self.rem(0x55555555, r1, r2, r3, apsr, r0, br)
                want = (~r3 & 0xFFFFFFFF) if comp else 0x55555555
                self.assertEqual(r0[0], want)
                self.assertEqual(br[0], 1 if branch else 0)

    def test_alt_entry_selects_0x21(self) -> None:
        for cell in (0x20027194, 0x00000000, 0xFFFFFFFF):
            with self.subTest(cell=hex(cell)):
                sel = (ctypes.c_uint32 * 1)(0)
                ret = self.alt(cell, sel)
                self.assertEqual(ret, cell & 0xFFFFFFFF)
                self.assertEqual(sel[0], 0x21)

    def test_disable_tail_zeroes_and_restores(self) -> None:
        for slots in ((0x11111111, 0x22222222, 0x33333333, 0x004201BA),
                      (0x00000000, 0x00000000, 0x00000000, 0x00000000),
                      (0xDEADBEEF, 0xCAFEBABE, 0xA5A5A5A5, 0xFFFFFFFF)):
            with self.subTest(slots=[hex(s) for s in slots]):
                sp = (ctypes.c_uint32 * 4)(*slots)
                out = (ctypes.c_uint32 * 5)(0, 0, 0, 0, 0)
                self.disable(sp, out)
                self.assertEqual(out[0], 0)
                self.assertEqual(tuple(out[1:]), tuple(s & 0xFFFFFFFF
                                                       for s in slots))

    def test_irq_disable_publish(self) -> None:
        for value in (0x00000000, 0x12345678, 0xFFFFFFFF):
            with self.subTest(value=hex(value)):
                mem = bytearray(b"\xa5" * (0x300 + 4))
                base = ctypes.addressof(ctypes.c_char.from_buffer(mem))
                ret = self.irq(value, base)
                self.assertEqual(ret, 0)
                self.assertEqual(u32(mem, 0x200), value & 0xFFFFFFFF)
                self.assertEqual(mem[0x200 + 3], (value >> 24) & 0xFF)
                self.assertEqual(mem[0x1FF], 0xA5)
                self.assertEqual(mem[0x204], 0xA5)


if __name__ == "__main__":
    unittest.main()
