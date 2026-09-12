#!/usr/bin/env python3
"""BL-006 cluster: source-owned literal seams/pools around 0x0042220E.

Pins nine reviewed in-place data closures (192 bytes) against the
authenticated stock image and checks every literal word still has a live
PC-relative consumer in a production-routed span.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-4220b2-422ad4-source-closure.md`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import struct
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
#  required live-consumer function substrings per word slot; empty means
#  the slot must have NO routed consumer, i.e. documented fill)
GROUPS: tuple[dict, ...] = (
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mode_seams_42220e.c",
        "symbol": "open_cfw_bootloader_bl006_seam_42220e",
        "section": ".rodata.bl006_seam_42220e",
        "address": 0x0042220E,
        "size": 18,
        "sha256": "34fb2e40d40a342dcdc1d23c99581a89280341ef5be58a15a5765d4328a99a9e",
        "words": {
            0x00422210: ("bitmap",),
            0x00422214: ("mode_service",),
            0x00422218: ("mode_service",),
            0x0042221C: ("mode_service", "dual", "bitmap_client", "mode1_enable", "mode0_enable"),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mode_seams_42220e.c",
        "symbol": "open_cfw_bootloader_bl006_seam_42228e",
        "section": ".rodata.bl006_seam_42228e",
        "address": 0x0042228E,
        "size": 18,
        "sha256": "08388290f49d6fd437c9ccef1aaab3fe54465ec3d251b281f154e02e341a151a",
        "words": {
            0x00422290: ("mode_service", "row4_enable"),
            0x00422294: ("mode_service", "row4_enable"),
            0x00422298: ("mode_service", "mode0_poll", "row4_enable"),
            0x0042229C: ("mode_service", "mode0_poll", "row4_enable"),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mode_seams_42220e.c",
        "symbol": "open_cfw_bootloader_bl006_seam_4222d2",
        "section": ".rodata.bl006_seam_4222d2",
        "address": 0x004222D2,
        "size": 30,
        "sha256": "1f137d5f192d742c2f2d77edfb99116475879ab56011173bd5531e68929285f5",
        "words": {
            0x004222D4: ("mode_service", "row4_enable"),
            0x004222D8: ("dual_mode_service",),
            0x004222DC: ("dual_mode_service", "row5"),
            0x004222E0: ("dual_mode_service",),
            0x004222E4: ("dual_mode_service",),
            0x004222E8: ("dual_mode_service", "row5"),
            0x004222EC: ("dual_mode_service", "row5_enable"),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_debug_pool_422430.c",
        "symbol": "open_cfw_bootloader_bl006_pool_422430",
        "section": ".rodata.bl006_pool_422430",
        "address": 0x00422430,
        "size": 56,
        "sha256": "178bf3040304055de474d0ffb04a4f33e265679c33253ff3a6c13427947c261d",
        "words": {
            0x00422430: ("bitmap_client", "row6"),
            0x00422434: ("bitmap_client",),
            0x00422438: ("bitmap_client", "row6_enable"),
            0x0042243C: ("mode1_enable",),
            0x00422440: ("mode1_disable",),
            0x00422444: ("mode1_poll_cleanup", "mode0_enable", "mode0_disable"),
            0x00422448: ("mode1_poll_cleanup", "mode0_enable", "mode0_disable"),
            0x0042244C: ("mode0_poll_cleanup", "row4_enable"),
            0x00422450: ("row4_poll_cleanup", "row5"),
            0x00422454: ("row4_poll_cleanup", "row5"),
            0x00422458: ("row5_enable", "row5_disable"),
            0x0042245C: ("row6_enable", "row6_disable"),
            0x00422460: ("row6_enable", "row6_disable"),
            0x00422464: ("mode_configuration_copy",),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_debug_pool_422430.c",
        "symbol": "open_cfw_bootloader_bl006_pool_422574",
        "section": ".rodata.bl006_pool_422574",
        "address": 0x00422574,
        "size": 28,
        "sha256": "82d8e4094be3bec9b384ed5df514b62e04f9af0b28bc15b7c1e00ef79613d62e",
        "words": {
            0x00422574: (),
            0x00422578: ("debug_disable",),
            0x0042257C: ("debug_disable",),
            0x00422580: ("debug_power",),
            0x00422584: ("debug_power",),
            0x00422588: ("debug_trace_disable",),
            0x0042258C: ("debug_trace_disable",),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_debug_pool_422430.c",
        "symbol": "open_cfw_bootloader_bl006_island_4225ac",
        "section": ".rodata.bl006_island_4225ac",
        "address": 0x004225AC,
        "size": 36,
        "sha256": "6a1c3b3c218a63a0485994c42f851a99bff4fedd5443396ba4a7bbe7a1ba5b25",
        "words": {
            0x004225AC: ("constraint_dispatch",),
            0x004225B0: ("constraint_dispatch",),
        },
        "string_at": (0x004225B0, b"constraint handler: bad message\x00"),
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_align_fill_422712.c",
        "symbol": "open_cfw_bootloader_bl006_align_422712",
        "section": ".rodata.bl006_align_422712",
        "alignment": 2,
        "address": 0x00422712,
        "size": 2,
        "sha256": "b35429818002e6e8ced180b98b8273bd2fc11f8ed0b0ff54eade7a5920a15ed4",
        "words": {0x00422712: ()},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_align_fill_422712.c",
        "symbol": "open_cfw_bootloader_bl006_align_422872",
        "section": ".rodata.bl006_align_422872",
        "alignment": 2,
        "address": 0x00422872,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "words": {0x00422872: ()},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_align_fill_422712.c",
        "symbol": "open_cfw_bootloader_bl006_align_422ad2",
        "section": ".rodata.bl006_align_422ad2",
        "alignment": 2,
        "address": 0x00422AD2,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "words": {0x00422AD2: ()},
    },
)

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006ClusterTests(unittest.TestCase):
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
                            "name": group["symbol"],
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
                if "string_at" in group:
                    address, text = group["string_at"]
                    self.assertEqual(
                        payload[address - group["address"]:address - group["address"] + len(text)],
                        text)

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
        for entry in self.overlay.get("patch_sites", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["expected_size"])
            if start < window[1] and end > window[0]:
                spans.append((start, end, entry["name"], "patch_stock"))
        self.assertGreater(len(spans), 50)

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        wanted: set[int] = set()
        for group in GROUPS:
            wanted.update(group["words"].keys())
        hits: dict[int, list[tuple[str, str]]] = {}
        for start, end, name, kind in sorted(spans):
            code = self.image[start - RUN_BASE:end - RUN_BASE]
            for insn in decoder.disasm(code, start):
                targets: list[int] = []
                for op in insn.operands:
                    if op.type == ARM_OP_MEM and insn.reg_name(op.mem.base) == "pc":
                        targets.append(((insn.address + 4) & ~3) + op.mem.disp)
                    elif op.type == ARM_OP_IMM and insn.mnemonic.startswith("adr"):
                        targets.append(((insn.address + 4) & ~3) + op.imm)
                        targets.append((insn.address + 4) + op.imm)
                for target in targets:
                    if target in wanted:
                        hits.setdefault(target, []).append((name, kind))
        dead_kinds = {kind for consumers in hits.values() for _, kind in consumers}
        self.assertNotIn("patch_stock", dead_kinds)
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                for slot, required in group["words"].items():
                    consumers = [name for name, kind in hits.get(slot, [])]
                    if not required:
                        self.assertEqual(consumers, [], f"fill at {slot:#x} gained a consumer")
                    else:
                        for want in required:
                            self.assertTrue(
                                any(want in name for name in consumers),
                                f"{slot:#x} lost consumer {want}; have {consumers}")


if __name__ == "__main__":
    unittest.main()
