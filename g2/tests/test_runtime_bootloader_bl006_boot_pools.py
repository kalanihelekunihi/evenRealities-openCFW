#!/usr/bin/env python3
"""BL-006 cluster: source-owned boot-initialization literal pools.

Pins six reviewed in-place data closures (198 bytes) against the
authenticated stock image and checks every literal slot against its
stock loader PCs plus the reviewed consumer host model that names
its meaning.

The loaders live in entry-redirect stock spans, so the relocated
leaves carry their own copies and these pools are NOT address-live
in the final image; they are admitted as authenticated layout
reproductions with reviewed meanings, not as live traffic.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-41f9b6-41fdc0-source-closure.md`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/apollo_overlay.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
RUN_BASE = 0x00410000
CLANG = "/usr/bin/clang"

SOURCE = "components/bootloader/core_overlay/runtime_bl006_boot_init_pools_41f9b6.c"

# (slot address, stock loader PCs that must read it via a PC-relative
# literal load, required hex constant text in the reviewed consumer
# source that names its meaning; empty loader tuple means the slot is
# an orphaned literal or fill with architectural/reviewed value only)
GROUPS: tuple[dict, ...] = (
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_41f9b6",
        "section": ".rodata.bl006_pool_41f9b6",
        "address": 0x0041F9B6,
        "size": 22,
        "sha256": "fa5a136eee884d5e2228cb5af37c4f4e481317dcc129efcd59df1e92d36c2b87",
        "slots": {
            # 0x0041F9B6 fill has no slot entry (2-byte pad, not a word).
            0x0041F9B8: ((), "0xE000E100",
                         "components/bootloader/core_overlay/runtime_irq_services_41fdc0.c"),
            0x0041F9BC: ((), "0xE000E280",
                         "third_party/cmsis-core/CMSIS/Core/Include/core_cm55.h",
                         "Offset: 0x180 (R/W)  Interrupt Clear Pending Register"),
            0x0041F9C0: ((), "0xE000E400",
                         "components/bootloader/core_overlay/runtime_irq_services_41fdc0.c"),
            0x0041F9C4: ((), "0xE000ED18",
                         "components/bootloader/core_overlay/runtime_irq_services_41fdc0.c"),
            0x0041F9C8: ((0x0041F93A,), "0x20000454",
                         "components/bootloader/core_overlay/runtime_easylogger_transport_41b854.c"),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_align_41f9ee",
        "section": ".rodata.bl006_align_41f9ee",
        "address": 0x0041F9EE,
        "alignment": 2,
        "size": 2,
        "sha256": "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7",
        "slots": {},
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_41fa40",
        "section": ".rodata.bl006_pool_41fa40",
        "address": 0x0041FA40,
        "size": 16,
        "sha256": "39565a709f9618f4a352619d052d4cd6340f9bb446178f346a30ec557bdb362f",
        "slots": {
            0x0041FA40: ((0x0041F9FA,), "0x00433440",
                         "components/bootloader/core_overlay/runtime_boot_services_41f9d8.c"),
            0x0041FA44: ((0x0041F9FC,), "0x00433460",
                         "components/bootloader/core_overlay/runtime_boot_services_41f9d8.c"),
            0x0041FA48: ((0x0041FA10,), "0x20022E00",
                         "components/bootloader/core_overlay/runtime_boot_services_41f9d8.c"),
            0x0041FA4C: ((0x0041FA1A,), "0x0041F9F1",
                         "components/bootloader/core_overlay/runtime_boot_services_41f9d8.c"),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_41fad0",
        "section": ".rodata.bl006_pool_41fad0",
        "address": 0x0041FAD0,
        "size": 12,
        "sha256": "4c991d43a1173b4c27ada6be4c12a50eee2bfc0d8df510dd6e7369d268b37b64",
        "slots": {
            0x0041FAD0: ((0x0041FA9A,), "0x20027198",
                         "components/bootloader/core_overlay/runtime_guarded_teardown_41fa98.c"),
            0x0041FAD4: ((0x0041FA70,), "0x00433A9C",
                         "components/bootloader/core_overlay/runtime_platform_setup_41fa50.c"),
            0x0041FAD8: ((0x0041FABE,), "0x00434154",
                         "components/bootloader/core_overlay/runtime_guarded_teardown_41fa98.c"),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_41fcf6",
        "section": ".rodata.bl006_pool_41fcf6",
        "address": 0x0041FCF6,
        "size": 122,
        "sha256": "a336f9a95b7426fb8c078b298098471dcf02e7e7fd66730d0dcdc2d3427db2ec",
        "slots": {
            # slot: ((loader,), value-hex, reviewer). All reviewers are
            # the pin-group dispatcher; the value is 0x20000000+offset.
            0x0041FCF8: ((0x0041FBE0,), "0x20000010",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FCFC: ((0x0041FBD4,), "0x2000000C",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD00: ((0x0041FC04,), "0x20000008",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD04: ((0x0041FBF8,), "0x20000004",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD08: ((0x0041FBEC,), "0x20000000",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD0C: ((0x0041FCA2,), "0x2000005C",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD10: ((0x0041FC96,), "0x20000058",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD14: ((0x0041FCC6,), "0x20000054",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD18: ((0x0041FCBA,), "0x20000050",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD1C: ((0x0041FCAE,), "0x2000004C",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD20: ((0x0041FB38,), "0x20000028",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD24: ((0x0041FB44,), "0x2000002C",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD28: ((0x0041FB50,), "0x20000030",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD2C: ((0x0041FB5C,), "0x20000034",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD30: ((0x0041FB68,), "0x20000038",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD34: ((0x0041FB74,), "0x2000003C",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD38: ((0x0041FB80,), "0x20000040",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD3C: ((0x0041FB8C,), "0x20000044",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD40: ((0x0041FB98,), "0x20000048",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD44: ((0x0041FBA4,), "0x20000014",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD48: ((0x0041FBB0,), "0x20000018",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD4C: ((0x0041FBBC,), "0x2000001C",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD50: ((0x0041FBC8,), "0x20000020",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD54: ((0x0041FC10,), "0x20000024",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD58: ((0x0041FC66,), "0x20000060",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD5C: ((0x0041FC72,), "0x20000064",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD60: ((0x0041FC7E,), "0x20000068",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD64: ((0x0041FC8A,), "0x2000006C",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD68: ((0x0041FCD2,), "0x20000070",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
            0x0041FD6C: ((0x0041FCDE,), "0x20000074",
                         "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c",
                         "OPEN_CFW_PIN_CONFIG_BASE"),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_41fda8",
        "section": ".rodata.bl006_pool_41fda8",
        "address": 0x0041FDA8,
        "size": 24,
        "sha256": "37ce43e7948cf49f74162a9509e41cc23f206b64a12b7e4f038f578d57b6d17b",
        "slots": {
            0x0041FDA8: ((0x0041FD78,), "0x20081000",
                         "components/bootloader/core_overlay/runtime_allocator_init_41fd70.c"),
            0x0041FDAC: ((0x0041FD8C,), "0x2002718C",
                         "components/bootloader/core_overlay/runtime_allocator_init_41fd70.c"),
            0x0041FDB0: ((0x0041FD90,), "0x00434010",
                         "components/bootloader/core_overlay/runtime_allocator_init_41fd70.c"),
            0x0041FDB4: ((0x0041FD98,), "0x00433CA4",
                         "components/bootloader/core_overlay/runtime_allocator_init_41fd70.c"),
            0x0041FDB8: ((0x0041FD9A,), "0x004315C8",
                         "components/bootloader/core_overlay/runtime_allocator_init_41fd70.c"),
            0x0041FDBC: ((0x0041FD9C,), "0x00434144",
                         "components/bootloader/core_overlay/runtime_allocator_init_41fd70.c"),
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
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_boot", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006BootPoolTests(unittest.TestCase):
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

    def test_stock_loaders_target_slots(self) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_MEM

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        wanted: dict[int, list[int]] = {}
        for group in GROUPS:
            for slot, entry in group["slots"].items():
                wanted[slot] = list(entry[0])
        loader_to_slot = {pc: slot for slot, pcs in wanted.items() for pc in pcs}
        # Decode each loader's stock function span from its exact entry
        # so Thumb decode stays in sync (a single window decode drifts
        # on the interleaved literal pools).
        spans = (
            (0x0041F918, 0x0041F9B6),
            (0x0041F9D8, 0x0041FA40),
            (0x0041FA50, 0x0041FAD0),
            (0x0041FADC, 0x0041FCF6),
            (0x0041FD70, 0x0041FDC0),
        )
        observed: dict[int, int] = {}
        for start, end in spans:
            code = self.image[start - RUN_BASE:end - RUN_BASE]
            for insn in decoder.disasm(code, start):
                for op in insn.operands:
                    if op.type == ARM_OP_MEM and insn.reg_name(op.mem.base) == "pc":
                        target = ((insn.address + 4) & ~3) + op.mem.disp
                        if target in wanted and insn.address in loader_to_slot:
                            if loader_to_slot[insn.address] == target:
                                observed[insn.address] = target
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                for slot, entry in group["slots"].items():
                    for pc in entry[0]:
                        self.assertEqual(
                            observed.get(pc), slot,
                            f"loader {pc:#x} no longer reads slot {slot:#x}")

    def test_slot_values_named_in_reviewed_sources(self) -> None:
        for group in GROUPS:
            with self.subTest(symbol=group["symbol"]):
                for slot, entry in group["slots"].items():
                    _, value_hex, reviewer = entry[0], entry[1], entry[2]
                    required = entry[3] if len(entry) > 3 else value_hex
                    text = (ROOT / reviewer).read_text()
                    self.assertIn(
                        required.lower(), text.lower(),
                        f"slot {slot:#x} value {value_hex} not named in {reviewer}")
                    offset = slot - group["address"]
                    actual = self.stock(group["address"], group["size"])[offset:offset + 4]
                    self.assertEqual(struct.unpack("<I", actual)[0], int(value_hex, 16),
                                     f"slot {slot:#x} stock word != {value_hex}")


if __name__ == "__main__":
    unittest.main()
