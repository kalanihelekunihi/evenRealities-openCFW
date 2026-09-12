#!/usr/bin/env python3
"""BL-006 cluster: MSPI state-literal island/pool plus boot-island tail.

Pins the reviewed island at 0x00424AEA (alignment pad plus the
0x2001CAA0 MSPI state-table base), the reviewed pool at 0x00424BD4
(pause timeout, MSPI0 base, two pad-configuration words), and three
reserved boot-island words (0x0041F9CC/0x0041F9D0/0x0041F9D4)
against the authenticated stock image.

Liveness grades (see the audits for why):
- "live" slots are loaded by at least one byte-exact shipped body;
  every other loader must sit in a named functionally-replaced span
  whose shipped replacement carries zero data relocations (stale by
  construction). Any loader anywhere else fails the test.
- "stale" slots carry a spelling named by a reviewed consumer source
  but every routed loader lives in a named replaced span with zero
  data relocations; they preserve layout, not claimed live data.
- "unloaded" slots carry a reviewed spelling but have no loader in
  any routed span; layout preservation only.
- "reserved" slots have no loader and no reviewed meaning; layout
  preservation only.
- "pad" slots are zero fills with no loader.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-424aea-424be4-source-closure.md`,
`g2/docs/research/g2-bootloader-bl006-cluster-41f9b6-41fdc0-source-closure.md`.
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

STATE_DIR = "components/bootloader/core_overlay"

GROUPS: tuple[dict, ...] = (
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_state_pools_424aea.c",
        "symbol": "open_cfw_bootloader_bl006_island_424aea",
        "section": ".rodata.bl006_island_424aea",
        "address": 0x00424AEA,
        "size": 6,
        "sha256": "05f70b6d4faf34b32669a915ea9752d71c18d1820455e135c96884678d1a580a",
        "alignment": 1,
        "words": {
            0x00424AEA: {"pad": True},
            0x00424AEC: {"live": (
                "0x2001caa0U",
                ("runtime_mspi_cq_init_423f28.c",),
                (0x00423F36, 0x00423F5C),
                (),
            )},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_state_pools_424aea.c",
        "symbol": "open_cfw_bootloader_bl006_pool_424bd4",
        "section": ".rodata.bl006_pool_424bd4",
        "address": 0x00424BD4,
        "size": 16,
        "sha256": "94e6a862be3bc0ed1203d19a3a0273a063cd153d5048ee5914400fbe0dcd45e4",
        "alignment": 1,
        "words": {
            0x00424BD4: {"live": (
                "100000U",
                ("runtime_mspi_cq_pause_423fb8.c",),
                (0x00423FBE,),
                (),
            )},
            0x00424BD8: {"live": (
                "0x40060000U",
                ("runtime_mspi_cq_pause_423fb8.c",),
                (0x00423FC4, 0x00424070, 0x004240DE),
                (0x00424B1A,),
            )},
            0x00424BDC: {"stale": (
                "0x80000013U",
                ("runtime_mspi_device_configure_424120.c",),
                (0x004241E0, 0x00424228),
            )},
            0x00424BE0: {"unloaded": "0x8000001F"},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_reserved_words_420c14.c",
        "symbol": "open_cfw_bootloader_bl006_word_41f9cc",
        "section": ".rodata.bl006_word_41f9cc",
        "address": 0x0041F9CC,
        "size": 4,
        "sha256": "cb1bd9155a64554d51a19743656817ea04cb2a46e92f73f7544604eac0076640",
        "alignment": 4,
        "words": {0x0041F9CC: {"reserved": "0x0043419C"}},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_reserved_words_420c14.c",
        "symbol": "open_cfw_bootloader_bl006_word_41f9d0",
        "section": ".rodata.bl006_word_41f9d0",
        "address": 0x0041F9D0,
        "size": 4,
        "sha256": "e019fba5a03a649d9ae3abd5397d4ea92c558cd01b88708dc8395a9339e83886",
        "alignment": 4,
        "words": {0x0041F9D0: {"reserved": "0x00434158"}},
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_reserved_words_420c14.c",
        "symbol": "open_cfw_bootloader_bl006_word_41f9d4",
        "section": ".rodata.bl006_word_41f9d4",
        "address": 0x0041F9D4,
        "size": 4,
        "sha256": "2e08677789c0cc974075cc4a3624a63e90d51e9b992fb40b9895f6cc13b45e4b",
        "alignment": 4,
        "words": {0x0041F9D4: {"reserved": "0x0043415C"}},
    },
)

# Spans whose shipped bytes are functionally replaced (not byte-exact)
# and whose overlay relocation contracts carry zero data relocations,
# so stock-decode literal hits inside them are stale by construction.
STALE_SPANS = {
    0x00424B1A: "open_cfw_bootloader_mspi_configure_424af0",
    0x004241E0: "open_cfw_bootloader_mspi_device_configure_424120",
    0x00424228: "open_cfw_bootloader_mspi_device_configure_424120",
}

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]


def load_module():
    spec = importlib.util.spec_from_file_location("apollo_overlay_bl006_mspi", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Bl006MspiStatePoolTests(unittest.TestCase):
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

    def routed_spans(self, address: int, size: int):
        window = (address - 0x1000, address + size + 0x1000)
        spans: list[tuple[int, int, str, str]] = []
        for entry in self.overlay.get("in_place_leaves", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["expected"]["size"])
            if start < window[1] and end > window[0]:
                spans.append((start, end, entry["function"], "leaf"))
        for entry in self.overlay.get("patch_sites", []):
            start = int(entry["runtime_address"])
            end = start + int(entry["expected_size"])
            if start < window[1] and end > window[0]:
                spans.append((start, end, entry["name"], "patch_stock"))
        return spans

    def exact_functions(self) -> set[str]:
        return {
            entry["function"]
            for entry in self.overlay.get("in_place_leaves", [])
            if hashlib.sha256(
                self.stock(int(entry["runtime_address"]),
                           int(entry["expected"]["size"]))).hexdigest()
            == entry["expected"]["sha256"]
        }

    def loaders_of(self, slot: int, spans, exact: set[str]):
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        patch_spans = [
            (int(e["runtime_address"]),
             int(e["runtime_address"]) + int(e["expected_size"]))
            for e in self.overlay.get("patch_sites", [])
        ]
        live: list[int] = []
        stale: list[int] = []
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
                    if not any(s <= insn.address < e for s, e in patch_spans):
                        foreign.append(f"{name}@{insn.address:#x}")
                    else:
                        foreign.append(f"patch@{insn.address:#x}")
                elif name in exact:
                    live.append(insn.address)
                elif insn.address in STALE_SPANS and STALE_SPANS[insn.address] == name:
                    stale.append(insn.address)
                else:
                    foreign.append(f"{name}@{insn.address:#x}")
        return live, stale, foreign

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

    def test_live_slots_have_pinned_loaders_and_spellings(self) -> None:
        exact = self.exact_functions()
        for group in GROUPS:
            spans = self.routed_spans(group["address"], group["size"])
            self.assertGreater(len(spans), 3)
            for slot, contract in group["words"].items():
                if "live" not in contract:
                    continue
                spelling, sources, want_live, want_stale = contract["live"]
                with self.subTest(slot=hex(slot)):
                    live, stale, foreign = self.loaders_of(slot, spans, exact)
                    self.assertEqual(foreign, [],
                                     f"{slot:#x} has a loader outside pinned spans")
                    self.assertEqual(sorted(live), sorted(want_live),
                                     f"{slot:#x} live-loader set changed; re-derive")
                    self.assertEqual(sorted(stale), sorted(want_stale),
                                     f"{slot:#x} stale-loader set changed; re-derive")
                    self.assertGreater(len(live), 0,
                                       f"{slot:#x} lost all exact loaders")
                    for source in sources:
                        text = (ROOT / STATE_DIR / source).read_text()
                        self.assertIn(spelling, text,
                                      f"{spelling} not named by {source}")

    def test_stale_spans_carry_no_data_relocations(self) -> None:
        leaves = {entry["function"]: entry
                  for entry in self.overlay.get("in_place_leaves", [])}
        for pc, function in STALE_SPANS.items():
            with self.subTest(function=function):
                self.assertIn(function, leaves)
                for reloc in leaves[function].get("relocations", []):
                    self.assertEqual(reloc["type"], "R_ARM_THM_CALL",
                                     f"{function} has a data relocation; "
                                     f"stale-loader claim at {pc:#x} is void")

    def test_stale_and_unloaded_spellings(self) -> None:
        exact = self.exact_functions()
        for group in GROUPS:
            spans = self.routed_spans(group["address"], group["size"])
            for slot, contract in group["words"].items():
                if "stale" in contract:
                    spelling, sources, want_stale = contract["stale"]
                    with self.subTest(slot=hex(slot)):
                        live, stale, foreign = self.loaders_of(slot, spans, exact)
                        self.assertEqual(live, [],
                                         f"{slot:#x} gained a byte-exact loader")
                        self.assertEqual(foreign, [],
                                         f"{slot:#x} has a loader outside pinned spans")
                        self.assertEqual(sorted(stale), sorted(want_stale),
                                         f"{slot:#x} stale-loader set changed")
                        for source in sources:
                            text = (ROOT / STATE_DIR / source).read_text()
                            self.assertIn(spelling, text)
                elif "unloaded" in contract:
                    with self.subTest(slot=hex(slot)):
                        live, stale, foreign = self.loaders_of(slot, spans, exact)
                        self.assertEqual(live, [], f"{slot:#x} gained a loader")
                        self.assertEqual(stale, [], f"{slot:#x} gained a loader")
                        self.assertEqual(foreign, [], f"{slot:#x} gained a loader")
                        text = (ROOT / group["path"]).read_text()
                        self.assertIn(contract["unloaded"] + "u", text)

    def test_reserved_words_unloaded_and_spelled(self) -> None:
        exact = self.exact_functions()
        for group in GROUPS:
            spans = self.routed_spans(group["address"], group["size"])
            for slot, contract in group["words"].items():
                if "reserved" not in contract:
                    continue
                with self.subTest(slot=hex(slot)):
                    live, stale, foreign = self.loaders_of(slot, spans, exact)
                    self.assertEqual(live, [], f"{slot:#x} gained a loader")
                    self.assertEqual(stale, [], f"{slot:#x} gained a loader")
                    self.assertEqual(foreign, [], f"{slot:#x} gained a loader")
                    self.assertEqual(
                        int(contract["reserved"], 16).to_bytes(4, "little"),
                        self.stock(slot, 4),
                        f"stock word at {slot:#x} changed",
                    )
                    text = (ROOT / group["path"]).read_text()
                    self.assertIn(contract["reserved"] + "u", text)

    def test_pad_slot_zero_and_unloaded(self) -> None:
        exact = self.exact_functions()
        for group in GROUPS:
            spans = self.routed_spans(group["address"], group["size"])
            for slot, contract in group["words"].items():
                if "pad" not in contract:
                    continue
                with self.subTest(slot=hex(slot)):
                    self.assertEqual(self.stock(slot, 2), b"\x00\x00")
                    live, stale, foreign = self.loaders_of(slot, spans, exact)
                    self.assertEqual(live + stale, [])
                    self.assertEqual(foreign, [])


if __name__ == "__main__":
    unittest.main()
