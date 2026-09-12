#!/usr/bin/env python3
"""BL-006 cluster: source-owned CLKGEN pool and zero-alignment pads.

Pins one reviewed in-place data pool (28 bytes at 0x00426D2C) and four
reviewed zero-alignment halfwords (0x00426DB2, 0x00426F6A, 0x004276BA,
0x00427752) against the authenticated stock image.

Liveness grades (see the audit for why):
- "pad" slots must keep zero loaders in any routed span;
- "dead" slots (the six CLKGEN register words) must keep zero loaders
  in any byte-exact shipped body. Their values are named by reviewed
  consumer sources, and the only in-place hits are stock decodes of
  functionally replaced bodies that embed their own copies; the test
  recompiles those bodies and proves their PC-relative targets avoid
  every dead slot. Entry-redirect-span references are dead by
  construction (span containment, as in the ctrl-pools test).

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-426d2c-427754-source-closure.md`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/apollo_overlay.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
RUN_BASE = 0x00410000
CLANG = "/usr/bin/clang"

# (source file, symbol, section, runtime address, size, stock sha256,
#  per-slot consumer contract: {"pad": True} requires zero routed
#  loaders; {"dead": (hex value, (consumer source paths, ...))}
#  requires the value to appear in each named reviewed consumer and
#  no loader in any byte-exact shipped body.)
GROUPS: tuple[dict, ...] = (
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_clkgen_pool_426d2c.c",
        "symbol": "open_cfw_bootloader_bl006_pool_426d2c",
        "section": ".rodata.bl006_pool_426d2c",
        "address": 0x00426D2C,
        "size": 28,
        "sha256": "30f0e66dd252b9acdfb5b00d677bb6ea54ea2252753fa16db8f7e5b5d6de2624",
        "words": {
            0x00426D2C: {"pad": True},
            0x00426D30: {"dead": ("0x40004044", (
                "components/bootloader/core_overlay/runtime_clkgen_hfadj_enable_426c58.c",
                "components/bootloader/core_overlay/runtime_dual_switch_426c8c.c",
            ))},
            0x00426D34: {"dead": ("0x40004020", (
                "components/bootloader/core_overlay/runtime_clkgen_config_426ccc.c",
                "components/bootloader/core_overlay/runtime_clkgen_hfadj_config_426c72.c",
                "components/bootloader/core_overlay/runtime_clkgen_hfadj_disable_426c7e.c",
            ))},
            0x00426D38: {"dead": ("0x40004030", (
                "components/bootloader/core_overlay/runtime_dual_switch_426c8c.c",
            ))},
            0x00426D3C: {"dead": ("0x4000404C", (
                "components/bootloader/core_overlay/runtime_clkgen_config_426ccc.c",
            ))},
            0x00426D40: {"dead": ("0x40004048", (
                "components/bootloader/core_overlay/runtime_clkgen_config_426ccc.c",
            ))},
            0x00426D44: {"dead": ("0x40004050", (
                "components/bootloader/core_overlay/runtime_clkgen_disable_426d1e.c",
            ))},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_zero_pads_426db2.c",
        "symbol": "open_cfw_bootloader_bl006_pad_426db2",
        "section": ".rodata.bl006_pad_426db2",
        "alignment": 2,
        "address": 0x00426DB2,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "words": {0x00426DB2: {"pad": True}},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_zero_pads_426db2.c",
        "symbol": "open_cfw_bootloader_bl006_pad_426f6a",
        "section": ".rodata.bl006_pad_426f6a",
        "alignment": 2,
        "address": 0x00426F6A,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "words": {0x00426F6A: {"pad": True}},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_zero_pads_426db2.c",
        "symbol": "open_cfw_bootloader_bl006_pad_4276ba",
        "section": ".rodata.bl006_pad_4276ba",
        "alignment": 2,
        "address": 0x004276BA,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "words": {0x004276BA: {"pad": True}},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_zero_pads_426db2.c",
        "symbol": "open_cfw_bootloader_bl006_pad_427752",
        "section": ".rodata.bl006_pad_427752",
        "alignment": 2,
        "address": 0x00427752,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "words": {0x00427752: {"pad": True}},
    },
)

# In-place bodies whose stock decode references a dead slot but whose
# shipped (compiled) bodies are functionally replaced. The staleness
# proof recompiles each one and checks its PC-relative targets.
STALE_FUNCTIONS = (
    "open_cfw_bootloader_clkgen_hfadj_enable_426c58",
    "open_cfw_bootloader_dual_switch_426c8c",
)

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_clkgen", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006ClkgenPoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())

    def stock(self, address: int, size: int) -> bytes:
        return self.image[address - RUN_BASE:address - RUN_BASE + size]

    def compile_section(self, group: dict) -> tuple[bytes, dict]:
        path = group["path"]
        source_bytes = (ROOT / path).read_bytes()
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
                        "path": path,
                        "size": len(source_bytes),
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                    },
                    "toolchain": {"target": "arm-none-eabi", "flags": FLAGS},
                    "expected": {
                        "size": group["size"],
                        "sha256": group["sha256"],
                        "alignment": group.get("alignment", 1),
                    },
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

    def test_stock_regions_unchanged(self) -> None:
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                observed = hashlib.sha256(
                    self.stock(group["address"], group["size"])).hexdigest()
                self.assertEqual(observed, group["sha256"])

    def test_compiled_payload_matches_stock(self) -> None:
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                payload, report = self.compile_section(group)
                self.assertEqual(payload, self.stock(group["address"], group["size"]))
                extraction = report["extraction"]
                self.assertEqual(extraction["relocation_count"], 0)
                self.assertEqual(extraction["symbol"], group["symbol"])

    def test_overlay_registers_groups(self) -> None:
        registered = {item["symbol"]: item
                      for item in self.overlay.get("in_place_data", [])}
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                self.assertIn(group["symbol"], registered)
                entry = registered[group["symbol"]]
                self.assertEqual(entry["section"], group["section"])
                self.assertEqual(entry["expected"]["size"], group["size"])
                self.assertEqual(entry["expected"]["sha256"], group["sha256"])
                placements = entry["placements"]
                self.assertEqual(len(placements), 1)
                self.assertEqual(placements[0]["runtime_address"], group["address"])
                self.assertEqual(placements[0]["source_offset"], 0)
                self.assertEqual(placements[0]["size"], group["size"])
                self.assertEqual(placements[0]["stock_sha256"], group["sha256"])
                self.assertEqual(entry["source"]["path"], group["path"])
                self.assertEqual(entry["source"]["license"], "MIT")

    def test_dead_values_named_by_reviewed_sources(self) -> None:
        for group in GROUPS:
            for slot, contract in group["words"].items():
                if "dead" not in contract:
                    continue
                value, sources = contract["dead"]
                with self.subTest(slot=hex(slot)):
                    self.assertEqual(
                        int(value, 16).to_bytes(4, "little"),
                        self.stock(slot, 4),
                        f"stock word at {slot:#x} is not {value}",
                    )
                    for source in sources:
                        text = (ROOT / source).read_text()
                        self.assertIn(
                            value, text,
                            f"{value} not named by reviewed consumer {source}")

    def routed_spans_near(self, address: int, size: int):
        window = (address - 0x1000, address + size + 0x1000)
        spans: list[tuple[int, int, str, str]] = []
        for entry in self.overlay.get("in_place_leaves", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["expected"]["size"])
            if start < window[1] and end > window[0]:
                spans.append((start, end, entry["function"], "in_place"))
        patch_spans: list[tuple[int, int, str]] = []
        for entry in self.overlay.get("patch_sites", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["expected_size"])
            patch_spans.append((start, end, entry["name"]))
            if start < window[1] and end > window[0]:
                spans.append((start, end, entry["name"], "patch_stock"))
        return spans, patch_spans

    def byte_exact_bodies(self) -> set[str]:
        exact: set[str] = set()
        for entry in self.overlay.get("in_place_leaves", []):
            start = int(entry["runtime_address"])
            size = int(entry["expected"]["size"])
            observed = hashlib.sha256(self.stock(start, size)).hexdigest()
            if observed == entry["expected"]["sha256"]:
                exact.add(entry["function"])
        return exact

    def test_literal_consumers_dead_or_absent(self) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        exact = self.byte_exact_bodies()
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        for group in GROUPS:
            spans, patch_spans = self.routed_spans_near(group["address"], group["size"])
            self.assertGreater(len(spans), 5)
            wanted = set(group["words"].keys())
            live_exact: dict[int, list[str]] = {}
            stale: dict[int, list[str]] = {}
            for start, end, name, kind in sorted(spans):
                code = self.image[start - RUN_BASE:end - RUN_BASE]
                for insn in decoder.disasm(code, start):
                    targets: list[int] = []
                    for op in insn.operands:
                        if op.type == ARM_OP_MEM and insn.reg_name(op.mem.base) == "pc":
                            targets.append(((insn.address + 4) & ~3) + op.mem.disp)
                        elif op.type == ARM_OP_IMM and insn.mnemonic.startswith("adr"):
                            targets.append(((insn.address + 4) & ~3) + op.imm)
                    for target in targets:
                        if target not in wanted:
                            continue
                        if kind == "patch_stock":
                            self.assertTrue(
                                any(start <= insn.address < end
                                    for start, end, _ in patch_spans),
                                f"{target:#x} stock-span loader {name}@{insn.address:#x} "
                                "outside any overwritten span")
                        elif name in exact:
                            live_exact.setdefault(target, []).append(name)
                        else:
                            stale.setdefault(target, []).append(name)
            for slot, contract in group["words"].items():
                with self.subTest(symbol=group["symbol"], slot=hex(slot)):
                    self.assertEqual(
                        live_exact.get(slot, []), [],
                        f"{slot:#x} gained a byte-exact loader; re-derive the slot")
                    if contract.get("pad"):
                        self.assertEqual(
                            stale.get(slot, []), [],
                            f"fill at {slot:#x} gained a consumer")
                    else:
                        for name in stale.get(slot, []):
                            self.assertIn(
                                name, STALE_FUNCTIONS,
                                f"{slot:#x} loader {name} is not a proven-stale body")

    def test_stale_loader_bodies_avoid_pool(self) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        dead_slots: set[int] = set()
        for group in GROUPS:
            for slot, contract in group["words"].items():
                if "dead" in contract:
                    dead_slots.add(slot)
        self.assertTrue(dead_slots)
        leaves = {entry["function"]: entry
                  for entry in self.overlay.get("in_place_leaves", [])}
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        for function in STALE_FUNCTIONS:
            with self.subTest(function=function):
                entry = leaves[function]
                runtime = int(entry["runtime_address"])
                with tempfile.TemporaryDirectory(dir=build_root) as directory:
                    payload, _ = self.module.compile_in_place_leaf(
                        root=ROOT,
                        clang=CLANG,
                        leaf_config=entry,
                        object_path=Path(directory) / "leaf.o",
                    )
                for insn in decoder.disasm(payload, runtime):
                    for op in insn.operands:
                        target = None
                        if op.type == ARM_OP_MEM and insn.reg_name(op.mem.base) == "pc":
                            target = ((insn.address + 4) & ~3) + op.mem.disp
                        elif op.type == ARM_OP_IMM and insn.mnemonic.startswith("adr"):
                            target = ((insn.address + 4) & ~3) + op.imm
                        if target is not None:
                            self.assertNotIn(
                                target, dead_slots,
                                f"shipped {function}@{insn.address:#x} loads dead slot "
                                f"{target:#x}; the slot is live")


if __name__ == "__main__":
    unittest.main()
