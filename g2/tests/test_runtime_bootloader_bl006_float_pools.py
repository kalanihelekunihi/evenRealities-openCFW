#!/usr/bin/env python3
"""BL-006 cluster: reserved words plus float/System-PLL literal pools.

Pins two reviewed reserved words (0x00420C14, 0x00422D7A) and three
reviewed literal pools (0x00427032, 0x0042714C, 0x00427308) against
the authenticated stock image.

Liveness grades (see the audits for why):
- "reserved" slots have no loader in any routed span and no reviewed
  meaning; they preserve layout only, not claimed data.
- "pad" slots are zero fills with no loader in any routed span.
- "dead" slots carry a float spelling named by a reviewed consumer
  source; every routed loader must live in an entry-redirect stock
  (patch) span, which is dead by construction. Any loader from a
  byte-exact shipped body fails the test and forces re-derivation.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-426d2c-427754-source-closure.md`,
`g2/docs/research/g2-bootloader-bl006-cluster-42086c-420f70-source-closure.md`,
`g2/docs/research/g2-bootloader-bl006-cluster-4220b2-422ad4-source-closure.md`.
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

FLOAT_DIR = "components/bootloader/core_overlay"

# (source file, symbol, section, runtime address, size, stock sha256,
#  per-slot consumer contract.)
GROUPS: tuple[dict, ...] = (
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_reserved_words_420c14.c",
        "symbol": "open_cfw_bootloader_bl006_word_420c14",
        "section": ".rodata.bl006_word_420c14",
        "address": 0x00420C14,
        "size": 4,
        "sha256": "e20412b1425a4800384330a810a654f2a1f2b7b338a33f03e991eb27ca9e07a1",
        "alignment": 4,
        "words": {0x00420C14: {"reserved": "0x000081F6"}},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_reserved_words_420c14.c",
        "symbol": "open_cfw_bootloader_bl006_word_422d7a",
        "section": ".rodata.bl006_word_422d7a",
        "address": 0x00422D7A,
        "size": 4,
        "sha256": "31f3a0337ae2102f7205453fb1b5cf94d31d04e8951016c229aafacd29b75048",
        "alignment": 4,
        "words": {0x00422D7A: {"reserved": "0x20000002"}},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_float_syspll_pools_427032.c",
        "symbol": "open_cfw_bootloader_bl006_pool_427032",
        "section": ".rodata.bl006_pool_427032",
        "address": 0x00427032,
        "size": 14,
        "sha256": "94542922bcc73242bc10178a2790c3d10c998df2f5b6a9c93d840957f402f3f4",
        "words": {
            0x00427032: {"pad": True},
            0x00427034: {"dead": ("0x1p-23f", (
                "runtime_float_gcd_426d48.c",
                "runtime_float_ratio_426db4.c",
                "runtime_float_multiplier_426eac.c",
            ))},
            0x00427038: {"dead": ("0x1.000002p-23f", (
                "runtime_float_ratio_426db4.c",
            ))},
            0x0042703C: {"dead": ("0x1.e00002p+9f", (
                "runtime_float_ratio_426db4.c",
                "runtime_float_encoding_select_426f6c.c",
            ))},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_float_syspll_pools_427032.c",
        "symbol": "open_cfw_bootloader_bl006_pool_42714c",
        "section": ".rodata.bl006_pool_42714c",
        "address": 0x0042714C,
        "size": 20,
        "sha256": "d2fd6d50093232dbbe37ee054454fd606fb53fda088a33e29d23ee6528d1cc9f",
        "words": {
            0x0042714C: {"dead": ("0x1.f80002p+5f", (
                "runtime_float_ratio_426db4.c",
                "runtime_float_multiplier_426eac.c",
            ))},
            0x00427150: {"reserved": "0x00000000"},
            0x00427154: {"dead": ("0x1p+24f", (
                "runtime_float_multiplier_426eac.c",
            ))},
            0x00427158: {"dead": ("0x1.800002p+6f", (
                "runtime_float_multiplier_426eac.c",
            ))},
            0x0042715C: {"dead": ("60.0f", (
                "runtime_float_encoding_select_426f6c.c",
            ))},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_float_syspll_pools_427032.c",
        "symbol": "open_cfw_bootloader_bl006_pool_427308",
        "section": ".rodata.bl006_pool_427308",
        "address": 0x00427308,
        "size": 8,
        "sha256": "90c7a6a98a6f94c175f4def78616baab7e97e70b48835904297f87726111cd4a",
        "words": {
            0x00427308: {"dead": ("240.0f", (
                "runtime_float_encoding_select_426f6c.c",
            ))},
            0x0042730C: {"dead": ("1000000.0f", (
                "runtime_syspll_min_fvco_427040.c",
            ))},
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
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_float", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def spelling_bits(spelling: str) -> int:
    text = spelling[:-1] if spelling.endswith("f") else spelling
    value = float.fromhex(text) if text.startswith("0x") else float(text)
    return struct.unpack("<I", struct.pack("<f", value))[0]


class Bl006FloatPoolTests(unittest.TestCase):
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
                self.assertEqual(entry["expected"]["alignment"],
                                 group.get("alignment", 1))
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

    def test_dead_spellings_match_stock_and_sources(self) -> None:
        for group in GROUPS:
            for slot, contract in group["words"].items():
                if "dead" not in contract:
                    continue
                spelling, sources = contract["dead"]
                with self.subTest(slot=hex(slot)):
                    self.assertEqual(
                        spelling_bits(spelling).to_bytes(4, "little"),
                        self.stock(slot, 4),
                        f"stock word at {slot:#x} is not {spelling}",
                    )
                    for source in sources:
                        text = (ROOT / FLOAT_DIR / source).read_text()
                        self.assertIn(
                            spelling, text,
                            f"{spelling} not named by reviewed consumer {source}")

    def test_reserved_words_spelled_in_source(self) -> None:
        for group in GROUPS:
            for slot, contract in group["words"].items():
                if "reserved" not in contract:
                    continue
                with self.subTest(slot=hex(slot)):
                    self.assertEqual(
                        int(contract["reserved"], 16).to_bytes(4, "little"),
                        self.stock(slot, 4),
                        f"stock word at {slot:#x} changed",
                    )
                    text = (ROOT / group["path"]).read_text()
                    self.assertIn(contract["reserved"] + "u", text)

    def test_literal_consumers_only_in_replaced_spans(self) -> None:
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        exact = {
            entry["function"]
            for entry in self.overlay.get("in_place_leaves", [])
            if hashlib.sha256(
                self.stock(int(entry["runtime_address"]),
                           int(entry["expected"]["size"]))).hexdigest()
            == entry["expected"]["sha256"]
        }
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        patch_spans = [
            (int(e["runtime_address"]),
             int(e["runtime_address"]) + int(e["expected_size"]), e["name"])
            for e in self.overlay.get("patch_sites", [])
        ]
        for group in GROUPS:
            window = (group["address"] - 0x1000,
                      group["address"] + group["size"] + 0x1000)
            spans: list[tuple[int, int, str, str]] = []
            for entry in self.overlay.get("in_place_leaves", []):
                start = int(entry["runtime_address"])
                end = start + int(entry["expected"]["size"])
                if start < window[1] and end > window[0]:
                    spans.append((start, end, entry["function"], "leaf"))
            for start, end, name in patch_spans:
                if start < window[1] and end > window[0]:
                    spans.append((start, end, name, "patch_stock"))
            self.assertGreater(len(spans), 3)
            wanted = set(group["words"].keys())
            for slot in wanted:
                live: list[str] = []
                foreign: list[str] = []
                for start, end, name, kind in sorted(spans):
                    code = self.image[start - RUN_BASE:end - RUN_BASE]
                    for insn in decoder.disasm(code, start):
                        targets: list[int] = []
                        for op in insn.operands:
                            if op.type == ARM_OP_MEM and insn.reg_name(op.mem.base) == "pc":
                                targets.append(((insn.address + 4) & ~3) + op.mem.disp)
                            elif op.type == ARM_OP_IMM and insn.mnemonic.startswith("adr"):
                                targets.append(((insn.address + 4) & ~3) + op.imm)
                        if slot not in targets:
                            continue
                        if kind == "patch_stock":
                            if not any(s <= insn.address < e
                                       for s, e, _ in patch_spans):
                                foreign.append(f"{name}@{insn.address:#x}")
                        elif name in exact:
                            live.append(name)
                        else:
                            foreign.append(f"{name}@{insn.address:#x}")
                with self.subTest(symbol=group["symbol"], slot=hex(slot)):
                    self.assertEqual(live, [],
                                     f"{slot:#x} gained a byte-exact loader; re-derive")
                    self.assertEqual(foreign, [],
                                     f"{slot:#x} has a loader outside replaced spans")


if __name__ == "__main__":
    unittest.main()
