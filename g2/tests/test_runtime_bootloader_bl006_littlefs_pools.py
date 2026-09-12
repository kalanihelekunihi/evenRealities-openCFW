#!/usr/bin/env python3
"""BL-006 cluster: source-owned LittleFS-adjacent literal pools.

Pins three reviewed in-place data closures (334 bytes) against the
authenticated stock image and checks every literal slot against its
stock loader PCs plus the reviewed consumer source that names its
meaning.

The MX25 consumers live in entry-redirect stock spans, so the
relocated leaves carry their own copies; the mapped-memory selector
consumers at 0x004213EC..0x00421548 are compiled in place and read
the 0x0042156E pool live. Every loader PC below was verified by
Capstone decode from its consuming function's exact stock entry.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-420ff2-421584-source-closure.md`.
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

SOURCE = "components/bootloader/core_overlay/runtime_bl006_littlefs_pools_420ff2.c"
READXFER = "components/bootloader/core_overlay/runtime_mspi_read_transfer_4205f4.c"
WRITEXFER = "components/bootloader/core_overlay/runtime_mspi_write_transfer_42069e.c"
BUSY = "components/bootloader/core_overlay/runtime_mspi_busy_status_42074e.c"
FOURBYTE = "components/bootloader/core_overlay/runtime_mspi_4byte_mode_420800.c"
ENTER4 = "components/bootloader/core_overlay/runtime_mspi_enter_4byte_mode_420890.c"
LATCH = "components/bootloader/core_overlay/runtime_mspi_write_latch_420984.c"
ERASE = "components/bootloader/core_overlay/runtime_mspi_sector_erase_420a08.c"
PROG = "components/bootloader/core_overlay/runtime_mspi_program_420b0c.c"
QUAD = "components/bootloader/core_overlay/runtime_mspi_quad_enable_420c5c.c"
DEVREC = "components/bootloader/core_overlay/runtime_mspi_device_reconfigure_420e08.c"
QUADMODE = "components/bootloader/core_overlay/runtime_mspi_set_quad_mode_420e8c.c"
SERIAL = "components/bootloader/core_overlay/runtime_mspi_set_serial_mode_420f10.c"
READ = "components/bootloader/core_overlay/runtime_mspi_read_420f70.c"
FSDIR = "components/bootloader/core_overlay/runtime_fs_directories_4210c8.c"
FORMAT = "components/bootloader/core_overlay/runtime_littlefs_format_4211b0.c"
INIT = "components/bootloader/core_overlay/runtime_littlefs_init_421210.c"
READCB = "components/bootloader/core_overlay/runtime_littlefs_read_4212d8.c"
PROGCB = "components/bootloader/core_overlay/runtime_littlefs_program_421310.c"
ERASECB = "components/bootloader/core_overlay/runtime_littlefs_erase_421348.c"
MEMSEL = "components/bootloader/core_overlay/runtime_memory_select_copy_4213e6.c"

# (slot address, stock loader PCs that must read it via a PC-relative
# literal load, required hex constant text in the reviewed consumer
# source that names its meaning; a fourth element overrides the text
# that must appear, e.g. for decimal-written constants)
GROUPS: tuple[dict, ...] = (
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_420ff2",
        "section": ".rodata.bl006_pool_420ff2",
        "address": 0x00420FF2,
        "size": 214,
        "sha256": "21ac43cfda25ec0bc55b6df8e70c3341923392c939cf989b96f0945e7b151ba3",
        "slots": {
            0x00420FF4: ((0x0042068E,), "0x00431420", READXFER),
            0x00420FF8: ((0x0042073E,), "0x00431468", WRITEXFER),
            0x00420FFC: ((0x00420770,), "0x00433508", BUSY),
            0x00421000: ((0x0042077C,), "0x00433B00", BUSY),
            0x00421004: ((0x00420822,), "0x00433814", FOURBYTE),
            0x00421008: ((0x0042082E, 0x00420858), "0x00433524", FOURBYTE),
            0x0042100C: ((0x0042084C,), "0x00432D0C", FOURBYTE),
            0x00421010: ((0x00420892, 0x00420A0C, 0x00420B18, 0x00420C62, 0x00420E0C, 0x00420EE4, 0x00420F44, 0x00420F7A), "0x200270DC", ENTER4),
            0x00421014: ((0x004208A8,), "0x00433CE8", ENTER4),
            0x00421018: ((0x004208B4, 0x004208DC, 0x00420910, 0x0042093A, 0x00420962), "0x004331C0", ENTER4),
            0x0042101C: ((0x004208D0,), "0x00431ED8", ENTER4),
            0x00421020: ((0x00420904,), "0x004331E0", ENTER4),
            0x00421024: ((0x0042092E,), "0x00433200", ENTER4),
            0x00421028: ((0x00420956,), "0x0043382C", ENTER4),
            0x0042102C: ((0x004209A8,), "0x00433220", LATCH),
            0x00421030: ((0x004209AC, 0x004209EC, 0x00420A2E, 0x00420C9A, 0x00420CE8, 0x00420D14, 0x00420D74, 0x00420DA8, 0x00420DE6, 0x00420E24, 0x00420E4A, 0x00420E6E, 0x00420EC8, 0x00420EFC, 0x00420F28, 0x00420F5C), "0x00431540", QUAD),
            0x00421034: ((0x004209B0, 0x00420C9E, 0x00420CEC, 0x00420D16, 0x00420D76, 0x00420DAA, 0x00420DE8, 0x00420E26, 0x00420E4C, 0x00420E70, 0x00420ECA, 0x00420EFE, 0x00420F2A, 0x00420F5E), "0x00433CD8", QUAD),
            0x00421038: ((0x004209E8,), "0x00432D30", LATCH),
            0x0042103C: ((0x00420A1E,), "0x00432D54", ERASE),
            0x00421040: ((0x00420A2A,), "0x00433540", ERASE),
            0x00421044: ((0x00420A5A,), "0x00432148", ERASE),
            0x00421048: ((0x00420A74,), "0x0043267C", ERASE),
            0x0042104C: ((0x00420A98,), "0x00432178", ERASE),
            0x00421050: ((0x00420AAC,), "0x004321A8", ERASE),
            0x00421054: ((0x00420AC6,), "0x004321D8", ERASE),
            0x00421058: ((0x00420B30,), "0x004326A8", PROG),
            0x0042105C: ((0x00420B48,), "0x004326D4", PROG),
            0x00421060: ((0x00420BBE,), "0x00431AF0", PROG),
            0x00421064: ((0x00420BD0,), "0x00431F0C", PROG),
            0x00421068: ((0x00420BE0,), "0x00432208", PROG),
            0x0042106C: ((0x00420BEE,), "0x00431B28", PROG),
            0x00421070: ((0x00420C00,), "0x00431B60", PROG),
            0x00421074: ((0x00420C8A,), "0x00432D78", QUAD),
            0x00421078: ((0x00420C96, 0x00420CE4, 0x00420D10, 0x00420D72, 0x00420DA6, 0x00420DE4), "0x00433844", QUAD),
            0x0042107C: ((0x00420CD8,), "0x00432D9C", QUAD),
            0x00421080: ((0x00420D04,), "0x00432A9C", QUAD),
            0x00421084: ((0x00420D66,), "0x00432DC0", QUAD),
            0x00421088: ((0x00420D9C,), "0x0043355C", QUAD),
            0x0042108C: ((0x00420DD6,), "0x00434034", QUAD),
            0x00421090: ((0x00420DDA,), "0x0043385C", QUAD),
            0x00421094: ((0x00420E18,), "0x00432E08", DEVREC),
            0x00421098: ((0x00420E22, 0x00420E48, 0x00420E6C), "0x00432DE4", DEVREC),
            0x0042109C: ((0x00420E3E, 0x00420E62), "0x00432E2C", DEVREC),
            0x004210A0: ((0x00420E7E,), "0x200270D8", DEVREC),
            0x004210A4: ((0x00420E92,), "0x20000224", QUADMODE),
            0x004210A8: ((0x00420EBC,), "0x00432E50", QUADMODE),
            0x004210AC: ((0x00420EC6, 0x00420EFA), "0x00433578", QUADMODE),
            0x004210B0: ((0x00420EF0,), "0x00433240", QUADMODE),
            0x004210B4: ((0x00420F12,), "0x2000020C", SERIAL),
            0x004210B8: ((0x00420F1C,), "0x00432E74", SERIAL),
            0x004210BC: ((0x00420F26, 0x00420F5A), "0x00433594", SERIAL),
            0x004210C0: ((0x00420F50,), "0x00433260", SERIAL),
            0x004210C4: ((0x00420FDC,), "0xF4240", READ, "1000000"),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_421372",
        "section": ".rodata.bl006_pool_421372",
        "address": 0x00421372,
        "size": 98,
        "sha256": "69c23d9c23df577cb63407fd0899c61afc102f15fc1a38f710fde8d829b71d2b",
        "slots": {
            0x00421374: ((0x004210CE,), "0x00433E58", FSDIR),
            0x00421378: ((0x004210E2,), "0x00433934", FSDIR),
            0x0042137C: ((0x004210EA, 0x0042110E, 0x00421158, 0x00421176, 0x00421198), "0x00433300", FSDIR),
            0x00421380: ((0x004210EC, 0x00421110, 0x0042115A, 0x00421178, 0x0042119A, 0x004211DE, 0x004211FE, 0x00421244, 0x00421264, 0x004212C8), "0x00430E60", FSDIR),
            0x00421384: ((0x004210EE, 0x00421112, 0x0042115C, 0x0042117A, 0x0042119C, 0x004211E0, 0x00421200, 0x00421246, 0x00421266, 0x004212CA), "0x00433FBC", FSDIR),
            0x00421388: ((0x00421106,), "0x0043394C", FSDIR),
            0x0042138C: ((0x00421120, 0x004211B4, 0x00421214), "0x20026878", FSDIR),
            0x00421390: ((0x00421150,), "0x00433320", FSDIR),
            0x00421394: ((0x0042116E,), "0x00432FDC", FSDIR),
            0x00421398: ((0x00421190,), "0x00433340", FSDIR),
            0x0042139C: ((0x004211BC, 0x00421216), "0x00431070", FORMAT),
            0x004213A0: ((0x004211D4,), "0x00433964", FORMAT),
            0x004213A4: ((0x004211DC, 0x004211FC), "0x00433E28", FORMAT),
            0x004213A8: ((0x004211F4,), "0x00433000", FORMAT),
            0x004213AC: ((0x0042123A,), "0x0043397C", INIT),
            0x004213B0: ((0x00421242, 0x00421262, 0x004212C6), "0x00433E38", INIT),
            0x004213B4: ((0x0042125A,), "0x0043178C", INIT),
            0x004213B8: ((0x00421274,), "0x2002711C", INIT),
            0x004213BC: ((0x0042127C,), "0x20026C0C", INIT),
            0x004213C0: ((0x00421282,), "0x00433FC8", INIT),
            0x004213C4: ((0x004212BE,), "0x00433E48", INIT),
            0x004213C8: ((0x00421300,), "0x004317CC", READCB),
            0x004213CC: ((0x00421338,), "0x0043180C", PROGCB),
            0x004213D0: ((0x00421362,), "0x00432568", ERASECB),
        },
    },
    {
        "path": SOURCE,
        "symbol": "open_cfw_bootloader_bl006_pool_42156e",
        "section": ".rodata.bl006_pool_42156e",
        "address": 0x0042156E,
        "size": 22,
        "sha256": "0ba5bda2afbb0b139d9a8ffdd65e988e3a169baae65dcbf62df014d0a76aa18b",
        "slots": {
            0x00421570: ((0x004213F2,), "0x400201BC", MEMSEL),
            0x00421574: ((0x00421408,), "0x40021008", MEMSEL),
            0x00421578: ((0x004214B6, 0x00421502), "0x42004000", MEMSEL),
            0x0042157C: ((0x004214E0, 0x00421518), "0x42006000", MEMSEL),
            0x00421580: ((0x004214EC, 0x0042152A), "0x42002000", MEMSEL),
        },
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
    (0x004210C8, 0x004211B0),
    (0x004211B0, 0x00421210),
    (0x00421210, 0x004212D8),
    (0x004212D8, 0x00421310),
    (0x00421310, 0x00421348),
    (0x00421348, 0x00421372),
    (0x004213D4, 0x004213D8),
    (0x004213EC, 0x004214C8),
    (0x004214C8, 0x004214E6),
    (0x004214E6, 0x00421548),
    (0x00421548, 0x0042156E),
)


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_lfs", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006LittlefsPoolTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
