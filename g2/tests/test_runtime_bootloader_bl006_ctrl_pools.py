#!/usr/bin/env python3
"""BL-006 cluster: source-owned hardware-control and MSPI ISR pools.

Pins four reviewed in-place data closures (36 bytes) against the
authenticated stock image and checks every literal word still has a
live PC-relative consumer in a production-routed span.

Two liveness grades are distinguished (see the audit for why):
- "exact" slots must keep at least one loader in a byte-exact
  shipped body (whose stock PC-relative addressing is preserved);
- "valuelive" slots (the two command-queue callback pointers) carry
  values the shipped functional control body stores, but no
  byte-exact shipped body loads the slot itself, so the test pins
  the complete in-place consumer set instead of an open-ended
  substring match: any new loader forces re-derivation.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-423d9a-426c10-source-closure.md`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
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
#  per-slot consumer contract: {"exact": (...)} requires those
#  substrings among byte-exact-or-live routed loaders;
#  {"valuelive": (...)} requires the in-place loader set to equal
#  exactly those function names (no byte-exact loader exists today);
#  {"pad": True} requires zero routed loaders.)
GROUPS: tuple[dict, ...] = (
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_hw_control_pool_423d9a.c",
        "symbol": "open_cfw_bootloader_bl006_pool_423d9a",
        "section": ".rodata.bl006_pool_423d9a",
        "address": 0x00423D9A,
        "size": 6,
        "sha256": "7cf4979cad48b6ce2b499300c3c3b8ed96387be1abbadcd932aba625b082f975",
        "words": {
            0x00423D9A: {"pad": True},
            0x00423D9C: {"exact": ("hw_global_service", "hw_control_query")},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_hw_control_pool_423d9a.c",
        "symbol": "open_cfw_bootloader_bl006_align_423dce",
        "section": ".rodata.bl006_align_423dce",
        "alignment": 2,
        "address": 0x00423DCE,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "words": {
            0x00423DCE: {"pad": True},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_isr_pools_4267fe.c",
        "symbol": "open_cfw_bootloader_bl006_pool_4267fe",
        "section": ".rodata.bl006_pool_4267fe",
        "address": 0x004267FE,
        "size": 10,
        "sha256": "f0ef1fedd08c40bdcdbac2afa7a8df77f7a1b6cebf3ccbe24145340afa295b16",
        "words": {
            0x004267FE: {"pad": True},
            0x00426800: {"valuelive": ("open_cfw_bootloader_mspi_control_upstream_4251c0",)},
            0x00426804: {"exact": ("mspi_interrupt_service",)},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_isr_pools_4267fe.c",
        "symbol": "open_cfw_bootloader_bl006_pool_426bfe",
        "section": ".rodata.bl006_pool_426bfe",
        "address": 0x00426BFE,
        "size": 18,
        "sha256": "6d01aee7b0ea94693ad3e39e729d72dbdcf694fa0bb121442d026ca719b3d5c4",
        "words": {
            0x00426BFE: {"pad": True},
            0x00426C00: {"valuelive": ("open_cfw_bootloader_mspi_control_upstream_4251c0",)},
            0x00426C04: {"exact": ("mspi_interrupt_service", "mspi_power_control")},
            0x00426C08: {"exact": ("mspi_interrupt_service",)},
            0x00426C0C: {"exact": ("mspi_power_control",)},
        },
    },
)

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_ctrl", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006CtrlPoolTests(unittest.TestCase):
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

    def test_literal_consumers_alive(self) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        addresses = [g["address"] for g in GROUPS]
        window = (min(addresses) - 0x1000, max(a + g["size"] for a, g in zip(addresses, GROUPS)) + 0x1000)
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
        self.assertGreater(len(spans), 50)

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        wanted: set[int] = set()
        for group in GROUPS:
            wanted.update(group["words"].keys())
        live: dict[int, list[str]] = {}
        dead: dict[int, list[tuple[str, int]]] = {}
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
                    if target in wanted:
                        if kind == "in_place":
                            live.setdefault(target, []).append(name)
                        else:
                            dead.setdefault(target, []).append((name, insn.address))
        # Every reference from an entry-redirect stock span must sit
        # inside a span the shipped image overwrites (redirect + NOP
        # fill), i.e. it is dead by construction, never a live
        # consumer.
        for slot, hits in dead.items():
            for name, pc in hits:
                self.assertTrue(
                    any(start <= pc < end for start, end, _ in patch_spans),
                    f"{slot:#x} stock-span loader {name}@{pc:#x} outside any overwritten span")
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                for slot, contract in group["words"].items():
                    consumers = live.get(slot, [])
                    if contract.get("pad"):
                        self.assertEqual(consumers, [], f"fill at {slot:#x} gained a consumer")
                    elif "exact" in contract:
                        for want in contract["exact"]:
                            self.assertTrue(
                                any(want in name for name in consumers),
                                f"{slot:#x} lost exact consumer {want}; have {consumers}")
                    else:
                        self.assertEqual(
                            sorted(set(consumers)), sorted(contract["valuelive"]),
                            f"{slot:#x} loader set changed; re-derive the slot")


if __name__ == "__main__":
    unittest.main()
