#!/usr/bin/env python3
"""BL-006 cluster: command-queue suffix pool plus MSPI aperture mask.

Pins the reviewed 16-byte pool at 0x00427C80 (queue state-table
base, register-table base, initialized-prefix magic, shared-RAM
base) and the reviewed mask word at 0x0042644C (XIP aperture-base
mask 0x1FFF0000) against the authenticated stock image.

Liveness grades (see the audit for why): every slot is "stale" --
its reviewed spelling is named by a reviewed consumer source, every
routed loader lives in a named functionally-replaced span whose
shipped replacement carries zero data relocations (stale by
construction), and no loader sits in any byte-exact shipped body,
any retained dead span, any relocated source, or any pointer table.

Loader discovery uses a sync-independent whole-window encoding
sweep for every literal-load form (`ldr [pc]`, `ldr.w/`ldrb.w`/`
ldrh.w`/`ldrsb.w [pc]`, `adr`/`adr.w` over [slot-0x1000,
slot+0x1000)); anchored Capstone span decode desynchronizes inside
the error-resume and post-loop spans and misses two magic loaders,
so Capstone is only a per-loader confirmation here, not the
search. Each pinned loader is confirmed by decoding anchored at
the loader address itself.

Evidence:
`g2/docs/research/g2-bootloader-bl006-cluster-427c80-42644c-source-closure.md`.
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

STATE_DIR = "components/bootloader/core_overlay"

GROUPS: tuple[dict, ...] = (
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_cmdq_suffix_pool_427c80.c",
        "symbol": "open_cfw_bootloader_bl006_pool_427c80",
        "section": ".rodata.bl006_pool_427c80",
        "address": 0x00427C80,
        "size": 16,
        "sha256": "06400bbf256919b539528f0eb9b5f247f49adee63166abc1b575be7f22cb91fa",
        "alignment": 1,
        "words": {
            0x00427C80: {"stale": (
                "0x200262F0U",
                ("runtime_cmdq_services_427794.c",),
                (0x004277BE,),
            )},
            0x00427C84: {"stale": (
                "0x00430880U",
                ("runtime_cmdq_services_427794.c",),
                (0x00427820,),
            )},
            0x00427C88: {"stale": (
                "OPEN_CFW_CMDQ_INITIALIZED | OPEN_CFW_CMDQ_MAGIC",
                ("runtime_cmdq_services_427794.c",),
                (0x00427884, 0x004278D4, 0x0042791E, 0x004279CA,
                 0x004279FC, 0x00427A66, 0x00427AE6, 0x00427B44,
                 0x00427BB6, 0x00427C1E),
            )},
            0x00427C8C: {"stale": (
                "0x20080000U",
                ("runtime_cmdq_services_427794.c",),
                (0x004278A0, 0x00427A38, 0x00427C64),
            )},
        },
    },
    {
        "path": "components/bootloader/core_overlay/runtime_bl006_mspi_aperture_mask_42644c.c",
        "symbol": "open_cfw_bootloader_bl006_word_42644c",
        "section": ".rodata.bl006_word_42644c",
        "address": 0x0042644C,
        "size": 4,
        "sha256": "ef687e2efa23e1e75be3a54e35142aa695c2c26028fdc627285ed6535eada977",
        "alignment": 1,
        "words": {
            0x0042644C: {"stale": (
                "0x1FFF0000",
                ("runtime_mspi_control_4251c0.c",),
                (0x004257BC,),
            )},
        },
    },
)

# Every pinned loader PC mapped to the replaced span that owns it.
# Each owning span's shipped replacement must carry zero data
# relocations (checked below), making these loaders stale by
# construction.
STALE_SPANS = {
    0x004277BE: "open_cfw_bootloader_cmdq_init_427794",
    0x00427820: "open_cfw_bootloader_cmdq_init_427794",
    0x00427884: "open_cfw_bootloader_cmdq_enable_427878",
    0x004278A0: "open_cfw_bootloader_cmdq_enable_427878",
    0x004278D4: "open_cfw_bootloader_cmdq_disable_4278c8",
    0x0042791E: "open_cfw_bootloader_cmdq_alloc_block_42790a",
    0x004279CA: "open_cfw_bootloader_cmdq_release_block_4279be",
    0x004279FC: "open_cfw_bootloader_cmdq_post_block_4279f0",
    0x00427A38: "open_cfw_bootloader_cmdq_post_block_4279f0",
    0x00427A66: "open_cfw_bootloader_cmdq_get_status_427a56",
    0x00427AE6: "open_cfw_bootloader_cmdq_term_427ad6",
    0x00427B44: "open_cfw_bootloader_cmdq_error_resume_427b38",
    0x00427BB6: "open_cfw_bootloader_cmdq_error_resume_427b38",
    0x00427C1E: "open_cfw_bootloader_cmdq_post_loop_block_427c12",
    0x00427C64: "open_cfw_bootloader_cmdq_post_loop_block_427c12",
    0x004257BC: "open_cfw_bootloader_mspi_control_upstream_4251c0",
}

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "apollo_overlay_bl006_cmdq", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def halfword(image: bytes, address: int) -> int:
    off = address - RUN_BASE
    return image[off] | (image[off + 1] << 8)


def encoding_sweep_loaders(image: bytes, slot: int) -> list[int]:
    """Every literal-load site targeting slot, found by encoding.

    Sync-independent: matches `ldr Rt,[pc,#imm]` (0x4800..0x4FFF),
    `ldr.w`/`ldrb.w`/`ldrh.w`/`ldrsb.w [pc]` (0xF8DF/0xF89F/0xF8BF/
    0xF99F + imm12, forward-only but scanned wider for coherence),
    and `adr`/`adr.w` over [slot-0x1000, slot+0x1000). Data bytes
    shaped like loads can over-approximate; every pinned hit below
    is additionally confirmed as a genuine instruction.
    """
    found: list[int] = []
    for pc in range(slot - 0x1000, slot + 0x1000, 2):
        first = halfword(image, pc)
        target = None
        if 0x4800 <= first <= 0x4FFF:
            target = ((pc + 4) & ~3) + (first & 0xFF) * 4
        elif first in (0xF8DF, 0xF89F, 0xF8BF, 0xF99F):
            target = ((pc + 4) & ~3) + (halfword(image, pc + 2) & 0xFFF)
        elif first == 0xF2AF:
            second = halfword(image, pc + 2)
            imm = ((second & 0xFF) | ((second >> 4) & 0x700)
                   | ((first & 0xF) << 12))
            if imm & 0x8000:
                imm -= 0x10000
            target = ((pc + 4) & ~3) + imm
        elif 0xA000 <= first <= 0xA7FF:
            target = ((pc + 4) & ~3) + (first & 0xFF) * 4
        if target == slot:
            found.append(pc)
    return found


class Bl006CmdqSuffixPoolTests(unittest.TestCase):
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

    def exact_functions(self) -> set[str]:
        return {
            entry["function"]
            for entry in self.overlay.get("in_place_leaves", [])
            if hashlib.sha256(
                self.stock(int(entry["runtime_address"]),
                           int(entry["expected"]["size"]))).hexdigest()
            == entry["expected"]["sha256"]
        }

    def confirm_loader(self, pc: int, slot: int) -> None:
        """The pinned PC really decodes as a PC-relative load of slot."""
        from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
        from capstone.arm import ARM_OP_IMM, ARM_OP_MEM

        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        decoder.detail = True
        code = self.image[pc - RUN_BASE:pc - RUN_BASE + 6]
        targets: list[int] = []
        for insn in decoder.disasm(code, pc):
            if insn.address != pc:
                continue
            for op in insn.operands:
                if (op.type == ARM_OP_MEM
                        and insn.reg_name(op.mem.base) == "pc"):
                    targets.append(((insn.address + 4) & ~3) + op.mem.disp)
                elif (op.type == ARM_OP_IMM
                      and insn.mnemonic.startswith("adr")):
                    targets.append(((insn.address + 4) & ~3) + op.imm)
        self.assertIn(
            slot, targets,
            f"{pc:#x} does not decode as a PC-relative load of {slot:#x}")

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

    def test_encoding_sweep_pins_exact_loader_sets(self) -> None:
        for group in GROUPS:
            for slot, contract in group["words"].items():
                spelling, sources, want = contract["stale"]
                with self.subTest(slot=hex(slot)):
                    self.assertEqual(sorted(encoding_sweep_loaders(self.image, slot)),
                                     sorted(want),
                                     f"{slot:#x} loader set changed; re-derive")
                    for pc in want:
                        self.confirm_loader(pc, slot)

    def test_no_loader_in_byte_exact_body(self) -> None:
        exact = self.exact_functions()
        leaves = {entry["function"]: entry
                  for entry in self.overlay.get("in_place_leaves", [])}
        for pc, function in STALE_SPANS.items():
            with self.subTest(pc=hex(pc)):
                self.assertIn(function, leaves)
                self.assertNotIn(
                    function, exact,
                    f"{function} became byte-exact; {pc:#x} grade is void")

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

    def test_stale_spellings_named_by_sources(self) -> None:
        for group in GROUPS:
            for slot, contract in group["words"].items():
                spelling, sources, want = contract["stale"]
                with self.subTest(slot=hex(slot)):
                    for source in sources:
                        text = (ROOT / STATE_DIR / source).read_text()
                        self.assertIn(spelling, text,
                                      f"{spelling} not named by {source}")

    def test_slot_addresses_unreferenced_as_words(self) -> None:
        slots = [slot for group in GROUPS for slot in group["words"]]
        words = {
            struct.unpack("<I", self.image[i:i + 4])[0]
            for i in range(0, len(self.image) // 4 * 4, 4)
        }
        for slot in slots:
            with self.subTest(slot=hex(slot)):
                self.assertNotIn(slot, words)
                self.assertNotIn(slot | 1, words)


if __name__ == "__main__":
    unittest.main()
