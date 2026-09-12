#!/usr/bin/env python3
"""BL-006 cluster: source-owned hardware-service and MSPI pools.

Pins eight reviewed in-place data closures (154 bytes) against the
authenticated stock image and checks every literal word still has a live
PC-relative consumer in a production-routed span.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-4233e0-4251c0-source-closure.md`.
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
        "path": "components/bootloader/core_overlay/runtime_bl006_hw_service_pools_4233e0.c",
        "symbol": "open_cfw_bootloader_bl006_pool_4233e0",
        "section": ".rodata.bl006_pool_4233e0",
        "address": 0x004233E0,
        "size": 8,
        "sha256": "dc6d6e468128844ba51e86cea994b84359c5e7b1bc741b6212e39b7a06161f72",
        "words": {
            0x004233E0: ("hw_initializer", "hw_instance_init", "hw_instance_service"),
            0x004233E4: ("hw_instance_init",),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_hw_service_pools_4233e0.c",
        "symbol": "open_cfw_bootloader_bl006_pool_423430",
        "section": ".rodata.bl006_pool_423430",
        "address": 0x00423430,
        "size": 20,
        "sha256": "84930f336c385f7f711daa4578dfe4b8e07a7cd18b80a375ace9a96a8b84e002",
        "words": {
            0x00423430: ("hw_instance_init",),
            0x00423434: ("hw_initializer", "hw_instance_service"),
            0x00423438: ("hw_initializer", "hw_instance_service"),
            0x0042343C: ("hw_initializer", "hw_instance_service"),
            0x00423440: ("hw_clock_divider", "hw_initializer", "hw_instance_service",
                          "hw_register_clear", "hw_status_map"),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_hw_register_pools_4236fa.c",
        "symbol": "open_cfw_bootloader_bl006_pool_4236fa",
        "section": ".rodata.bl006_pool_4236fa",
        "address": 0x004236FA,
        "size": 6,
        "sha256": "5f37ee3be00f7af81377ea45215056b9da7925ead403c1ff84274f0c17846ab7",
        "words": {
            0x004236FC: ("hw_clock_divider",),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_hw_register_pools_4236fa.c",
        "symbol": "open_cfw_bootloader_bl006_pool_423764",
        "section": ".rodata.bl006_pool_423764",
        "address": 0x00423764,
        "size": 24,
        "sha256": "2a5b0ce73bc2295f563559c798d0262265fa3010bee7c38c18a29ef3d75786ee",
        "words": {
            0x00423764: ("hw_fifo_pump", "hw_fifo_read", "hw_fifo_write",
                          "hw_register_clear", "hw_register_or", "hw_register_query",
                          "hw_register_write", "hw_shutdown"),
            0x00423768: ("hw_status_map",),
            0x0042376C: ("hw_status_map",),
            0x00423770: ("hw_status_map",),
            0x00423774: ("hw_status_map",),
            0x00423778: ("hw_status_map",),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_hw_register_pools_4236fa.c",
        "symbol": "open_cfw_bootloader_bl006_pool_42382c",
        "section": ".rodata.bl006_pool_42382c",
        "address": 0x0042382C,
        "size": 56,
        "sha256": "1c53b412e3fbb0cb88a21c22d1e2338353506516a1f4f531c09b24b49463db29",
        "words": {
            0x0042382C: ("hw_status_map",),
            0x00423830: ("hw_descriptor_init", "hw_mode_dispatch", "hw_register_or",
                          "hw_register_query", "hw_register_write", "hw_service_dispatch"),
            0x00423834: ("hw_clock_divider",),
            0x00423838: ("hw_clock_divider",),
            0x0042383C: ("hw_clock_divider",),
            0x00423840: ("hw_clock_divider",),
            0x00423844: ("hw_clock_divider",),
            0x00423848: ("hw_clock_divider",),
            0x0042384C: ("hw_clock_divider",),
            0x00423850: ("hw_config_latch",),
            0x00423854: ("hw_config_latch_secondary",),
            0x00423858: ("hw_shutdown",),
            0x0042385C: ("hw_fifo_snapshot",),
            0x00423860: ("hw_service_dispatch",),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_pools_423e0c.c",
        "symbol": "open_cfw_bootloader_bl006_pool_423e0c",
        "section": ".rodata.bl006_pool_423e0c",
        "address": 0x00423E0C,
        "size": 8,
        "sha256": "eb9eccfa0c7b87835a778c7ab67a2f4201b14d38a0d6b02bbb85a110f172d963",
        "words": {
            0x00423E0C: ("hw_control_critical",),
            0x00423E10: ("hw_control_critical",),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_pools_423e0c.c",
        "symbol": "open_cfw_bootloader_bl006_word_42499c",
        "section": ".rodata.bl006_word_42499c",
        "alignment": 4,
        "address": 0x0042499C,
        "size": 4,
        "sha256": "512cda42a9c3b00954f5ebd4cc8487efe02285b6c25f63e91df882b8846d7ded",
        "words": {
            0x0042499C: ("mspi_device_configure", "mspi_fifo_read", "mspi_fifo_write"),
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_pools_423e0c.c",
        "symbol": "open_cfw_bootloader_bl006_pool_4251a4",
        "section": ".rodata.bl006_pool_4251a4",
        "address": 0x004251A4,
        "size": 28,
        "sha256": "46dcf5abe08d382febe2de91c04fb274c4178e6cba750838ea210aafae585a7b",
        "words": {
            0x004251A4: ("mspi_device_configure_public", "mspi_disable", "mspi_enable",
                          "mspi_piomixed_configure", "mspi_seq_loopback"),
            0x004251A8: ("mspi_clkgen_ctrl",),
            0x004251AC: ("mspi_configure", "mspi_initialize"),
            0x004251B0: ("mspi_configure", "mspi_deinitialize",
                          "mspi_device_configure_public", "mspi_disable", "mspi_enable"),
            0x004251B4: ("mspi_configure",),
            0x004251B8: (),
            0x004251BC: ("mspi_enable",),
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
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_hw", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006HwPoolTests(unittest.TestCase):
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
