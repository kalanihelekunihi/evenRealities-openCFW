#!/usr/bin/env python3
"""BL-006 cluster: source-owned MX25 shared literal pools.

Pins nine reviewed in-place data closures (208 bytes) against the
authenticated stock image and checks every literal slot against its
stock loader PCs plus the reviewed consumer source that names its
meaning.

The consumers live in entry-redirect stock spans, so the relocated
leaves carry their own copies and these pools are NOT address-live
in the final image; they are admitted as authenticated layout
reproductions with reviewed meanings, not as live traffic. Every
loader PC below was verified by Capstone decode from its consuming
function's exact stock entry.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-42086c-420f70-source-closure.md`.
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

SOURCE = "components/bootloader/core_overlay/runtime_bl006_mx25_pools_42086c.c"
IRQ = "components/bootloader/core_overlay/runtime_irq_services_41fdc0.c"
CONTROL = "components/bootloader/core_overlay/runtime_mspi_control_41fe28.c"
EVENT = "components/bootloader/core_overlay/runtime_event_flags_service_41fe62.c"
FOURBYTE = "components/bootloader/core_overlay/runtime_mspi_4byte_mode_420800.c"
GUARD = "components/bootloader/core_overlay/runtime_mspi_guard_41ff08.c"
SCAN = "components/bootloader/core_overlay/runtime_mspi_timing_scan_420002.c"
AUTO = "components/bootloader/core_overlay/runtime_mspi_timing_auto_4201ba.c"
LOWINIT = "components/bootloader/core_overlay/runtime_mspi_low_level_init_420254.c"
SERIAL = "components/bootloader/core_overlay/runtime_mspi_set_serial_mode_420f10.c"
DRIVER = "components/bootloader/core_overlay/runtime_mspi_driver_init_420476.c"
SOFTRESET = "components/bootloader/core_overlay/runtime_mspi_soft_reset_42052a.c"
READID = "components/bootloader/core_overlay/runtime_mspi_read_id_42059e.c"
LATCH = "components/bootloader/core_overlay/runtime_mspi_write_latch_420984.c"
READXFER = "components/bootloader/core_overlay/runtime_mspi_read_transfer_4205f4.c"
QUAD = "components/bootloader/core_overlay/runtime_mspi_quad_enable_420c5c.c"

# (slot address, stock loader PCs that must read it via a PC-relative
# literal load, required hex constant text in the reviewed consumer
# source that names its meaning; a fourth element overrides the text
# that must appear, e.g. for decimal-written constants)
GROUPS: tuple[dict, ...] = (
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_42086c",
        "section": ".rodata.bl006_pool_42086c",
        "address": 0x0042086C,
        "size": 36,
        "sha256": "bd568192057107608070c8993444e0e2bdc34243a5ddf9972040371697be4eca",
        "slots": {
            0x00420870: ((0x0041FDE8,), "0xE000E400", IRQ),
            0x00420874: ((0x0041FE38, 0x0041FE4E, 0x0041FF54, 0x00420030,
                           0x00420292, 0x0042060A, 0x004206AA),
                          "0x200270DC", CONTROL),
            0x00420878: ((0x0041FE2A, 0x0041FE5A), "0x200271C6", CONTROL),
            0x0042087C: ((0x0041FE64, 0x0041FE9E, 0x0041FED6),
                          "0x200270E0", EVENT),
            0x00420880: ((0x0041FE6E,), "0x00433CF8", EVENT),
            0x00420884: ((0x0041FE7E,), "0x004329FC", EVENT),
            0x00420888: ((0x0041FE88,), "0x0043376C", EVENT),
            0x0042088C: ((0x0041FEB6,), "0x00432CA0", EVENT),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_420978",
        "section": ".rodata.bl006_pool_420978",
        "address": 0x00420978,
        "size": 12,
        "sha256": "6b00f23868a0bcfbca264efd5b172d74ab278103dc8869e0bc94eb9f08358b59",
        "slots": {
            0x00420978: ((0x0041FE8C, 0x0041FEC4, 0x0041FEF8, 0x004200D6,
                           0x00420206, 0x00420242, 0x004202C4, 0x0042030A,
                           0x0042035A, 0x00420394, 0x004203F8, 0x00420460,
                           0x0042049C, 0x004204E0, 0x00420504, 0x00420550,
                           0x00420588, 0x004205C8, 0x00420780, 0x00420832,
                           0x0042085C, 0x004208B8, 0x004208E0, 0x00420914,
                           0x0042093E, 0x00420966),
                          "0x00431540", FOURBYTE),
            0x0042097C: ((0x0041FEC0,), "0x00433784", EVENT),
            0x00420980: ((0x0041FEEA,), "0x00432A24", EVENT),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_island_4209be",
        "section": ".rodata.bl006_island_4209be",
        "address": 0x004209BE,
        "size": 6,
        "sha256": "da7c6b1527680ce2ccd4b90a5cbf4b5e3f55ca2148ae0bdf0403905053bc245a",
        "slots": {
            0x004209C0: ((0x0041FEF4,), "0x0043379C", EVENT),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_4209fc",
        "section": ".rodata.bl006_pool_4209fc",
        "address": 0x004209FC,
        "size": 12,
        "sha256": "24e3dd42d22fb00fcda8010047ae549a2110c8e5c77f230fb43a071466a26aa4",
        "slots": {
            0x004209FC: ((0x0041FDD0,), "0xE000E100", IRQ),
            0x00420A00: ((0x0041FDF4,), "0xE000ED18", IRQ),
            0x00420A04: ((0x0041FF3E, 0x0041FF48, 0x0041FF4E, 0x004201D2,
                           0x00420216),
                          "0x2000023C", AUTO),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_420ada",
        "section": ".rodata.bl006_pool_420ada",
        "address": 0x00420ADA,
        "size": 50,
        "sha256": "619fd98be5ccc3286a0a39c06f1c556503edee5868456a01e8e15c67b2fb5ed2",
        "slots": {
            0x00420ADC: ((0x0041FE90, 0x0041FEC8, 0x0041FEFC, 0x004200D2,
                           0x0042020A, 0x00420246, 0x004202C8, 0x0042030E,
                           0x0042035E, 0x00420398, 0x004203FC, 0x00420464,
                           0x004204A0, 0x004204E4, 0x00420508, 0x00420554,
                           0x0042058C, 0x004205CC, 0x00420782, 0x00420834,
                           0x0042085E, 0x004208BA, 0x004208E2, 0x00420916,
                           0x00420940, 0x00420968, 0x004209F0, 0x00420A32),
                          "0x00433CD8", LATCH),
            0x00420AE0: ((0x0041FF0E, 0x0041FF20), "0x200271C5", GUARD),
            0x00420AE4: ((0x00420046,), "0x002539C2", SCAN),
            0x00420AE8: ((0x00420070, 0x004200FC), "0x20000244", SCAN),
            0x00420AEC: ((0x004200DA,), "0x00433AB0", SCAN),
            0x00420AF0: ((0x004200E2,), "0x0043160C", SCAN),
            0x00420AF4: ((0x0042013A,), "0x004313D8", SCAN),
            0x00420AF8: ((0x004201F6,), "0x00430BD0", AUTO),
            0x00420AFC: ((0x00420202, 0x0042023E), "0x004337B4", AUTO),
            0x00420B00: ((0x00420232,), "0x00430C4C", AUTO),
            0x00420B04: ((0x00420278, 0x0042041C), "0x20026FD0", LOWINIT),
            0x00420B08: ((0x004202B4,), "0x00432CC4", LOWINIT),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_420c18",
        "section": ".rodata.bl006_pool_420c18",
        "address": 0x00420C18,
        "size": 68,
        "sha256": "eef5f99dd587a5904e1e43c6571a3e380ff8e11ef7b9ca80f1182a7027b907af",
        "slots": {
            0x00420C18: ((0x00420162,), "0x004334B4", SCAN),
            0x00420C1C: ((0x004202C0, 0x00420306, 0x00420356, 0x00420390,
                           0x004203F4, 0x0042045C),
                          "0x00433180", LOWINIT),
            0x00420C20: ((0x004202DC,), "0x200F4C00", LOWINIT),
            0x00420C24: ((0x004202FA,), "0x00432CE8", LOWINIT),
            0x00420C28: ((0x00420336,), "0x20000224", LOWINIT),
            0x00420C2C: ((0x0042034A,), "0x00432624", LOWINIT),
            0x00420C30: ((0x00420384,), "0x004331A0", LOWINIT),
            0x00420C34: ((0x004203E8,), "0x00432A4C", LOWINIT),
            0x00420C38: ((0x0042042C,), "0x2000020C", SERIAL),
            0x00420C3C: ((0x00420450,), "0x00432A74", LOWINIT),
            0x00420C40: ((0x00420478,), "0x200270D8", DRIVER),
            0x00420C44: ((0x0042048C,), "0x004337E4", DRIVER),
            0x00420C48: ((0x00420498, 0x004204DC, 0x00420500),
                          "0x004337CC", DRIVER),
            0x00420C4C: ((0x004204D0,), "0x00433AC4", DRIVER),
            0x00420C50: ((0x004204F4,), "0x00433AD8", DRIVER),
            0x00420C54: ((0x00420540,), "0x004334EC", SOFTRESET),
            0x00420C58: ((0x0042054C, 0x00420584), "0x004334D0", SOFTRESET),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_420dfa",
        "section": ".rodata.bl006_pool_420dfa",
        "address": 0x00420DFA,
        "size": 14,
        "sha256": "8b41f058c64229c00d3a505f11715874ac3dcada1086d696f408e9365a2b3b6f",
        "slots": {
            0x00420DFC: ((0x0042099C, 0x004209DC, 0x00420578),
                          "0x00432650", LATCH),
            0x00420E00: ((0x004205B8,), "0x00433AEC", READID),
            0x00420E04: ((0x004205C4,), "0x004337FC", READID),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_word_420f0c",
        "section": ".rodata.bl006_word_420f0c",
        "address": 0x00420F0C,
        "alignment": 4,
        "size": 4,
        "sha256": "cee19cda5a705d63da91e2090a5ebb792a8ea1040f92b95717823e8aa9299830",
        "slots": {
            0x00420F0C: ((0x00420672, 0x00420720), "0xF4240",
                          READXFER, "1000000"),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_text_420f6a",
        "section": ".rodata.bl006_text_420f6a",
        "address": 0x00420F6A,
        "size": 6,
        "sha256": "86d14b79fc1438915684e8f5b80873e3458147a166ffdaa3a0d42aa9588c690f",
        "slots": {},
    },
)

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]

# Exact stock code spans decoded for loader checks: one span per
# consuming function, each decoded from its exact stock entry so
# Thumb decode stays in sync across the interleaved literal pools.
SPANS = (
    (0x0041FDC0, 0x0041FDDE),
    (0x0041FDDE, 0x0041FE06),
    (0x0041FE06, 0x0041FE28),
    (0x0041FE28, 0x0041FE48),
    (0x0041FE48, 0x0041FE62),
    (0x0041FE62, 0x0041FE9C),
    (0x0041FE9C, 0x0041FED4),
    (0x0041FED4, 0x0041FF08),
    (0x0041FF08, 0x0041FF1E),
    (0x0041FF1E, 0x0041FF34),
    (0x0041FF34, 0x0041FF60),
    (0x0041FF60, 0x0041FF74),
    (0x0041FF74, 0x00420002),
    (0x00420002, 0x004201BA),
    (0x004201BA, 0x00420254),
    (0x00420254, 0x00420476),
    (0x00420476, 0x0042052A),
    (0x0042052A, 0x0042059E),
    (0x0042059E, 0x004205F4),
    (0x004205F4, 0x0042069E),
    (0x0042069E, 0x0042074E),
    (0x0042074E, 0x004207A2),
    (0x004207A2, 0x004207F4),
    (0x004207F4, 0x00420800),
    (0x00420800, 0x0042086C),
    (0x00420890, 0x00420978),
    (0x00420984, 0x004209BE),
    (0x004209C4, 0x004209FC),
    (0x00420A08, 0x00420ADA),
    (0x00420B0C, 0x00420C14),
    (0x00420C5C, 0x00420DFA),
    (0x00420E08, 0x00420E8C),
    (0x00420E8C, 0x00420F0C),
    (0x00420F10, 0x00420F6A),
    (0x00420F70, 0x00420FF2),
)


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_mx25", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006Mx25PoolTests(unittest.TestCase):
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
        observed: dict[int, int] = {}
        for start, end in SPANS:
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

    def test_set_text_selected_by_adr(self) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        code = self.image[0x00420C5C - RUN_BASE:0x00420DFA - RUN_BASE]
        found = False
        for insn in decoder.disasm(code, 0x00420C5C):
            if insn.mnemonic == "adr":
                for op in insn.operands:
                    if op.type == ARM_OP_IMM:
                        target = ((insn.address + 4) & ~3) + op.imm
                        if insn.address == 0x00420DD2 and target == 0x00420F6C:
                            found = True
        self.assertTrue(found, "adr at 0x420dd2 no longer selects 0x420f6c")
        self.assertEqual(self.stock(0x00420F6A, 6), b"\x00\x00set\x00")
        self.assertIn("0x00420F6C", (ROOT / QUAD).read_text())


if __name__ == "__main__":
    unittest.main()
