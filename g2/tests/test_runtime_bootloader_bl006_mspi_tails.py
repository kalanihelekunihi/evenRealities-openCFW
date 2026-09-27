#!/usr/bin/env python3
"""BL-006: MSPI dead interiors as reviewed source.

Admits 2792 bytes across five official_blob regions as reviewed
MIT C through the bootloader component's in-place-leaf
mechanism. All five spans are dead interiors after
entry-redirect-replaced heads; the whole-image retained survey
grades each corroborated_unreachable_control_flow and a
whole-image `bl` sweep finds no caller of any entry, so no leaf
executes in the shipped image.

Leaves (M/N/O/P/Q in span order):

- 0x004248E2..0x00424976 (148 B, M): PIO-mixed nibble arms (7
  entries, shared return-0 epilogue). No calls, no out-of-span
  branches, no relocations.
- 0x004263E0..0x0042644C (108 B, N): blocking-transfer end
  (mode dispatch to the in-place FIFO read/write services,
  error restore, retained delay call, single pop return). Two
  reviewed R_ARM_THM_CALL relocations plus one reviewed
  `.inst.w` for the retained-target call (with probe).
- 0x0042612C..0x004262E0 (436 B, O): control-dispatcher arms
  (8 entries, exits rejoin the head joins, never returns). One
  reviewed call relocation plus thirteen reviewed branch
  spellings: 2 narrow with assembler probes, 11 wide pinned by
  decoder verification (the reference assembler emits a variant
  `b.w` encoding for these offsets).
- 0x00424E84..0x00425066 (482 B, P): public device-configuration
  body (13 entries: main build, 9 divider arms, fail stub, head
  jump, conditional bit-0 path; returns 0/5 through the shared
  pop). Two reviewed call relocations plus ten reviewed narrow
  `.inst` spellings with nine probes (the two -114 exits share
  one encoding).
- 0x0042423C..0x0042488E (1618 B, Q): device-configuration arms
  (30 entries, 24 arms in 4 sub-patterns, shared return-0
  epilogue). No calls, no out-of-span branches, no
  relocations.

Out-of-span branches cannot name far-absolute mnemonic operands
in the relocatable object, so each is spelled with its reviewed
encoding (`.inst` / `.inst.w`); in-source probes prove the
reference assembler emits the identical bytes at the identical
offsets (binary32-tail precedent). Internal flow uses unique
Q-labels (numeric locals miscompile alongside relocations in
the ten-target P block). Pool loads reuse retained pool words
through stock PC-relative offsets (bitmap-client precedent).

Live MSPI behavior stays covered by the already-routed
AmbiqSuite-adapted services; these leaves document dead bytes
and pin the behavior the replaced heads must cover.

Evidence:
`g2/docs/research/g2-bootloader-bl006-tail-leaves-4248e2-4263e0-source-closure.md`.
"""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/apollo_overlay.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY_CONFIG = ROOT / "components/bootloader/core_overlay/overlay.json"
RUN_BASE = 0x00410000
CLANG = "/usr/bin/clang"

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
    "-Wall", "-Wextra", "-Werror", "-fno-ident",
]

LEAVES: tuple[dict, ...] = (
    {
        "function": "open_cfw_bootloader_mspi_piomix_rem_tail_4248e2",
        "source": ("components/bootloader/core_overlay/"
                   "runtime_bl006_mspi_piomix_tail_4248e2.c"),
        "address": 0x004248E2,
        "size": 148,
        "sha256": "4185510b7bd0813409986cbfbbaee0c75192ff4bf21bdd0dcc92e9898254c1d9",
        "relocations": [],
    },
    {
        "function": "open_cfw_bootloader_mspi_blocking_rem_tail_4263e0",
        "source": ("components/bootloader/core_overlay/"
                   "runtime_bl006_mspi_blocking_tail_4263e0.c"),
        "address": 0x004263E0,
        "size": 108,
        "sha256": "87f7deeb376def9dc9183a17a119e755a49be7263b7a9a721406862e72c19dfc",
        "relocations": [
            {"offset": 22, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_mspi_fifo_read_423e8a",
             "symbol_type": "STT_NOTYPE", "target_address": 0x423E8A},
            {"offset": 44, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_mspi_fifo_write_423e40",
             "symbol_type": "STT_NOTYPE", "target_address": 0x423E40},
            {"offset": 84, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_delay_service_41d246",
             "symbol_type": "STT_NOTYPE", "target_address": 0x41D246},
        ],
    },
    {
        "function": "open_cfw_bootloader_mspi_control_rem_tail_42612c",
        "source": ("components/bootloader/core_overlay/"
                   "runtime_bl006_mspi_control_tail_42612c.c"),
        "address": 0x0042612C,
        "size": 436,
        "sha256": "c83b4119f0991198d619c51dd5bcd92807c4aafa4d181444e7d9cb484f453bfe",
        "relocations": [
            {"offset": 0x12, "type": "R_ARM_THM_JUMP8",
             "symbol": "open_cfw_bootloader_mspi_control_head_4260f4",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4260F4},
            {"offset": 22, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_mspi_cq_enable_423f8e",
             "symbol_type": "STT_NOTYPE", "target_address": 0x423F8E},
            {"offset": 0x1E, "type": "R_ARM_THM_JUMP8",
             "symbol": "open_cfw_bootloader_mspi_control_head_4260f4",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4260F4},
            {"offset": 0x22, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e8_4252e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E8},
            {"offset": 0x2E, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e8_4252e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E8},
            {"offset": 0x40, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e8_4252e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E8},
            {"offset": 0x72, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e6_4252e6",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E6},
            {"offset": 0x7C, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e8_4252e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E8},
            {"offset": 0xBA, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e6_4252e6",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E6},
            {"offset": 0xD0, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e6_4252e6",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E6},
            {"offset": 0xE6, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e6_4252e6",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E6},
            {"offset": 0xF0, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e8_4252e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E8},
            {"offset": 0x1AA, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e6_4252e6",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E6},
            {"offset": 0x1B0, "type": "R_ARM_THM_JUMP24",
             "symbol": "open_cfw_bootloader_mspi_control_exit_e8_4252e8",
             "symbol_type": "STT_NOTYPE", "target_address": 0x4252E8},
        ],
    },
    {
        "function": "open_cfw_bootloader_mspi_devconfig_rem_tail_424e84",
        "source": ("components/bootloader/core_overlay/"
                   "runtime_bl006_mspi_devconfig_tail_424e84.c"),
        "address": 0x00424E84,
        "size": 482,
        "sha256": "96be3ed2b6277d645863984409f19be4ca6321dd94c6579eb5659de53d06b41a",
        "relocations": [
            {"offset": 0x22, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x28, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x2E, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x34, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x3A, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x40, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x46, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x4C, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x52, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_divider_424e5c",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E5C},
            {"offset": 0x58, "type": "R_ARM_THM_JUMP11",
             "symbol": "open_cfw_bootloader_mspi_devconfig_head_jump_424e6e",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424E6E},
            {"offset": 398, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_mspi_device_configure_424120",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424120},
            {"offset": 418, "type": "R_ARM_THM_CALL",
             "symbol": "open_cfw_bootloader_mspi_xip_off_delay_424a18",
             "symbol_type": "STT_NOTYPE", "target_address": 0x424A18},
        ],
    },
    {
        "function": "open_cfw_bootloader_mspi_devconfig2_rem_tail_42423c",
        "source": ("components/bootloader/core_overlay/"
                   "runtime_bl006_mspi_devconfig2_tail_42423c.c"),
        "address": 0x0042423C,
        "size": 1618,
        "sha256": "b8c84b34f444b4959fb39b8ae8fbb0b5f40a0a19a413d552a39892986985e44e",
        "relocations": [],
    },
)

NOP = bytes.fromhex("00bf")  # `nop` = 0xBF00 stored little-endian

# Assembler probes: (source file, function, pad bytes, side,
# expected branch bytes). Backward probes are zero pad + branch;
# the forward bhs probe is branch + two NOPs.
PROBES: tuple[dict, ...] = (
    {"source": LEAVES[1]["source"],
     "function": "open_cfw_bl006_bt_probe_bl_37362_back",
     "pad": 37358, "side": "back",
     "encoding": bytes.fromhex("f6f707ff")},
    {"source": LEAVES[2]["source"],
     "function": "open_cfw_bl006_cd_probe_bne_78_back",
     "pad": 74, "side": "back", "encoding": bytes.fromhex("d9d1")},
    {"source": LEAVES[2]["source"],
     "function": "open_cfw_bl006_cd_probe_beq_90_back",
     "pad": 86, "side": "back", "encoding": bytes.fromhex("d3d0")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_78_back",
     "pad": 74, "side": "back", "encoding": bytes.fromhex("d9e7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_84_back",
     "pad": 80, "side": "back", "encoding": bytes.fromhex("d6e7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_90_back",
     "pad": 86, "side": "back", "encoding": bytes.fromhex("d3e7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_96_back",
     "pad": 92, "side": "back", "encoding": bytes.fromhex("d0e7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_102_back",
     "pad": 98, "side": "back", "encoding": bytes.fromhex("cde7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_108_back",
     "pad": 104, "side": "back", "encoding": bytes.fromhex("cae7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_114_back",
     "pad": 110, "side": "back", "encoding": bytes.fromhex("c7e7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_120_back",
     "pad": 116, "side": "back", "encoding": bytes.fromhex("c4e7")},
    {"source": LEAVES[3]["source"],
     "function": "open_cfw_bl006_dc2_probe_b_126_back",
     "pad": 122, "side": "back", "encoding": bytes.fromhex("c1e7")},
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "apollo_overlay_bl006_mspi_tails", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def u32_at(buf: bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def view(buf: bytearray):
    return (ctypes.c_uint8 * len(buf)).from_buffer(buf)


def probe_section_bytes(probe: dict) -> bytes:
    if probe["side"] == "back":
        return b"\x00" * probe["pad"] + probe["encoding"]
    return probe["encoding"] + NOP * (probe["pad"] // 2)


class Bl006MspiTailLeavesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.image = OFFICIAL.read_bytes()
        import json

        cls.overlay = json.loads(OVERLAY_CONFIG.read_text())
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-bl006-mspi-tails-")
        libs = {}
        for leaf in LEAVES:
            stem = Path(leaf["source"]).stem
            library = Path(cls.temporary.name) / (stem + ".so")
            subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-shared", "-fPIC", str(ROOT / leaf["source"]),
                 "-o", str(library)],
                cwd=ROOT, check=True,
            )
            libs[leaf["function"]] = ctypes.CDLL(str(library))
        cls.libs = libs
        piomix = libs[LEAVES[0]["function"]]
        cls.piomix = piomix.open_cfw_bootloader_mspi_piomix_rem_tail_4248e2
        cls.piomix.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                               ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_uint]
        cls.piomix.restype = ctypes.c_uint32
        blocking = libs[LEAVES[1]["function"]]
        cls.blocking = blocking.open_cfw_bootloader_mspi_blocking_rem_tail_4263e0
        # (window, base_off, index, mode, r0_in, fifo, delay, r6, r7)
        cls.blocking.argtypes = [ctypes.c_void_p] + [ctypes.c_uint32] * 8
        cls.blocking.restype = ctypes.c_uint32
        control = libs[LEAVES[2]["function"]]
        cls.control = control.open_cfw_bootloader_mspi_control_rem_tail_42612c
        cls.control.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_void_p, ctypes.c_void_p,
                                ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_uint32, ctypes.c_uint,
                                ctypes.c_void_p, ctypes.c_void_p]
        cls.control.restype = ctypes.c_uint32
        devconfig = libs[LEAVES[3]["function"]]
        cls.devconfig = devconfig.open_cfw_bootloader_mspi_devconfig_rem_tail_424e84
        cls.devconfig.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                  ctypes.c_uint32, ctypes.c_void_p,
                                  ctypes.c_void_p, ctypes.c_uint32,
                                  ctypes.c_uint32, ctypes.c_uint,
                                  ctypes.c_void_p, ctypes.c_void_p]
        cls.devconfig.restype = ctypes.c_uint32
        devconfig2 = libs[LEAVES[4]["function"]]
        cls.devconfig2 = devconfig2.open_cfw_bootloader_mspi_devconfig2_rem_tail_42423c
        cls.devconfig2.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                   ctypes.c_uint32, ctypes.c_uint32,
                                   ctypes.c_uint32, ctypes.c_uint]
        cls.devconfig2.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def stock(self, address: int, size: int) -> bytes:
        return self.image[address - RUN_BASE:address - RUN_BASE + size]

    def compile_function(self, source: str, function: str, address: int,
                         size: int, sha256: str,
                         relocations: list) -> tuple[bytes, dict]:
        source_bytes = (ROOT / source).read_bytes()
        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_root) as directory:
            payload, report = self.module.compile_in_place_leaf(
                root=ROOT,
                clang=CLANG,
                leaf_config={
                    "function": function,
                    "runtime_address": address,
                    "source": {
                        "path": source,
                        "size": len(source_bytes),
                        "sha256": hashlib.sha256(source_bytes).hexdigest(),
                    },
                    "toolchain": {"target": "arm-none-eabi",
                                  "flags": FLAGS},
                    "strict_relocation_contract": True,
                    "expected": {"size": size, "sha256": sha256},
                    "stock": {"size": size, "sha256": sha256},
                    "relocations": relocations,
                    "allow_discarded_alloc_sections": True,
                },
                object_path=Path(directory) / "leaf.o",
            )
        return payload, report

    def compile_leaf(self, leaf: dict) -> tuple[bytes, dict]:
        return self.compile_function(
            leaf["source"], leaf["function"], leaf["address"],
            leaf["size"], leaf["sha256"], leaf["relocations"])

    def test_stock_spans_unchanged(self) -> None:
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                observed = hashlib.sha256(
                    self.stock(leaf["address"], leaf["size"])).hexdigest()
                self.assertEqual(observed, leaf["sha256"])

    def test_compiled_leaves_match_stock(self) -> None:
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                payload, report = self.compile_leaf(leaf)
                self.assertEqual(
                    payload, self.stock(leaf["address"], leaf["size"]))
                extraction = report["extraction"]
                self.assertEqual(
                    extraction["relocation_count"], len(leaf["relocations"]))
                self.assertEqual(extraction["function"], leaf["function"])
                self.assertEqual(extraction["size"], leaf["size"])
                self.assertEqual(extraction["sha256"], leaf["sha256"])
                if leaf["relocations"]:
                    seen = {(r["offset"], r["type"], r["symbol"])
                            for r in extraction["relocations"]}
                    want = {(r["offset"], r["type"], r["symbol"])
                            for r in leaf["relocations"]}
                    self.assertEqual(seen, want)

    def test_probes_emit_stock_encodings(self) -> None:
        for probe in PROBES:
            with self.subTest(function=probe["function"]):
                want = probe_section_bytes(probe)
                payload, report = self.compile_function(
                    probe["source"], probe["function"], 0x00420000,
                    len(want), hashlib.sha256(want).hexdigest(), [])
                self.assertEqual(payload, want)
                if probe["side"] == "back":
                    self.assertEqual(payload[-len(probe["encoding"]):],
                                     probe["encoding"])
                else:
                    self.assertEqual(payload[:len(probe["encoding"]):],
                                     probe["encoding"])
                self.assertEqual(
                    report["extraction"]["relocation_count"], 0)

    def test_wide_branch_spellings_decode(self) -> None:
        # The eleven wide out-of-span exits of leaf O cannot
        # carry assembler probes: the reference assembler emits
        # a one-variant-bit different (yet equally correct)
        # `b.w` encoding than the stock toolchain for these
        # offsets. Instead the verifier decodes each spelled
        # site with an independent decoder and checks the branch
        # reaches the documented head join.
        from capstone import CS_ARCH_ARM, CS_MODE_THUMB, CS_OP_IMM, Cs

        sites = {
            0x0042614E: 0x004252E8, 0x0042615A: 0x004252E8,
            0x0042616C: 0x004252E8, 0x004261A8: 0x004252E8,
            0x0042621C: 0x004252E8, 0x004262DC: 0x004252E8,
            0x0042619E: 0x004252E6, 0x004261E6: 0x004252E6,
            0x004261FC: 0x004252E6, 0x00426212: 0x004252E6,
            0x004262D6: 0x004252E6,
        }
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        decoder.detail = True
        for site, target in sites.items():
            with self.subTest(site=hex(site)):
                code = self.stock(site, 4)
                insns = list(decoder.disasm(code, site))
                self.assertEqual(len(insns), 1)
                self.assertEqual(insns[0].mnemonic, "b.w")
                self.assertEqual(insns[0].operands[0].type, CS_OP_IMM)
                self.assertEqual(insns[0].operands[0].value.imm, target)

    def test_overlay_registers_leaves(self) -> None:
        registered = {item["function"]: item
                      for item in self.overlay.get("in_place_leaves", [])}
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                self.assertIn(leaf["function"], registered)
                entry = registered[leaf["function"]]
                self.assertEqual(entry["runtime_address"], leaf["address"])
                self.assertEqual(entry["expected"]["size"], leaf["size"])
                self.assertEqual(entry["expected"]["sha256"], leaf["sha256"])
                self.assertEqual(entry["stock"]["sha256"], leaf["sha256"])
                self.assertTrue(entry["strict_relocation_contract"])
                self.assertEqual(entry["source"]["license"], "MIT")
                self.assertEqual(entry["source"]["path"], leaf["source"])
                seen = {(r["offset"], r["type"], r.get("symbol"),
                         r.get("target_address"))
                        for r in entry.get("relocations", [])}
                want = {(r["offset"], r["type"], r.get("symbol"),
                         r.get("target_address"))
                        for r in leaf["relocations"]}
                self.assertEqual(seen, want)

    def test_survey_grades_spans_unreachable(self) -> None:
        path = ROOT / "tools/analyze_g2_bootloader_bl006_retained_survey.py"
        spec = importlib.util.spec_from_file_location(
            "analyze_g2_bootloader_bl006_retained_survey", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        by_start = {}
        for region in module.survey()["regions"]:
            try:
                by_start[int(str(region["start"]), 16)] = region
            except (KeyError, ValueError):
                continue
        for leaf in LEAVES:
            with self.subTest(function=leaf["function"]):
                region = by_start.get(leaf["address"])
                self.assertIsNotNone(
                    region, f"no survey region at {leaf['address']:#x}")
                assert region is not None
                self.assertEqual(
                    region["verdict"], "corroborated_unreachable_control_flow")

    def test_no_bl_caller_of_any_entry(self) -> None:
        from capstone import CS_ARCH_ARM, CS_MODE_THUMB, CS_OP_IMM, Cs

        entries = {leaf["address"] for leaf in LEAVES}
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        decoder.detail = True
        hits: dict[int, list[int]] = {entry: [] for entry in entries}
        # Linear sweep can desynchronize inside data; this check
        # corroborates the survey verdict above rather than standing
        # alone.
        for insn in decoder.disasm(bytes(self.image), RUN_BASE):
            if insn.mnemonic != "bl":
                continue
            for op in insn.operands:
                if op.type == CS_OP_IMM and op.value.imm in hits:
                    hits[op.value.imm].append(insn.address)
        for entry, callers in hits.items():
            self.assertEqual(
                callers, [],
                f"entry {entry:#x} gains a caller at "
                f"{[hex(c) for c in callers]}; deadness changed")

    def test_piomix_nibble_arms(self) -> None:
        nibbles = (1, 3, 5, 7, None, 9, 11)
        for arm, nib in enumerate(nibbles):
            for initial in (0x00000000, 0xFFFFFFFF, 0x12345678):
                with self.subTest(arm=arm, initial=hex(initial)):
                    window = bytearray(0x8000)
                    struct.pack_into("<I", window, 0x100,
                                     0x40060000 + 0x100)
                    base_off = 0x1000 if arm else 0x200
                    slot_off = (base_off + 4) if arm == 0 else \
                        (base_off + (3 << 12) + 4)
                    struct.pack_into("<I", window, slot_off, initial)
                    ret = self.piomix(view(window), base_off, base_off, 3, arm)
                    self.assertEqual(ret, 0)
                    if nib is None:
                        self.assertEqual(u32_at(window, slot_off),
                                         initial & ~0xF)
                    else:
                        self.assertEqual(u32_at(window, slot_off),
                                         (initial & ~0xF) | nib)
                    # No stray writes outside the slot.
                    for off in range(0, len(window), 4):
                        if off == slot_off or off == 0x100:
                            continue
                        self.assertEqual(u32_at(window, off), 0)

    def test_blocking_dispatch(self) -> None:
        for mode, fifo, delay, r0_in in (
                (0, 0, 0x77, 0), (0, 5, 0x77, 0),
                (1, 0, 0x88, 0), (1, 9, 0x88, 0),
                (2, 0, 0x99, 0), (2, 7, 0x99, 0),
                (7, 0, 0, 0x1234), (255, 0xABC, 0, 0)):
            with self.subTest(mode=mode, fifo=fifo):
                window = bytearray(0x4000)
                base_off, index = 0x1000, 2
                ret = self.blocking(view(window), base_off, index, mode,
                                    r0_in, fifo, delay, 0x61E551, 0x71E551)
                want = fifo if mode in (0, 1) else r0_in
                if want == 0:
                    want = delay
                self.assertEqual(ret, want & 0xFFFFFFFF)
                base = base_off + (index << 12)
                self.assertEqual(u32_at(window, base + 0x208), 0x71E551)
                self.assertEqual(u32_at(window, base + 0x200), 0x61E551)

    def test_control_arms(self) -> None:
        desc = bytearray([0x02, 0x01] + [0] * 14)
        desc2 = bytearray([0x03, 0x01, 0x01, 0x01, 0x01, 0, 0, 0, 0,
                           0x15, 0, 0, 0x01, 0, 0, 0])
        # Entry 0: counter + enable gate.
        window = bytearray(0x10000)
        struct.pack_into("<I", window, 0x85C, 41)
        r0_out = (ctypes.c_uint32 * 1)(0)
        exit_out = (ctypes.c_uint32 * 1)(9)
        self.control(view(window), 0, 0x2000, 1, view(desc), view(desc2), 0, 0, 0, 0,
                     7, 0, r0_out, exit_out)
        self.assertEqual(u32_at(window, 0x85C), 42)
        self.assertEqual(exit_out[0], 1)
        self.assertEqual(r0_out[0], 7)
        # Entry 0 with r6 set exits to the head.
        self.control(view(window), 0, 0x2000, 1, view(desc), view(desc2), 0, 1, 0, 0,
                     7, 0, r0_out, exit_out)
        self.assertEqual(exit_out[0], 2)
        # Entry 7 is the constant failure stub.
        self.control(view(window), 0, 0x2000, 1, view(desc), view(desc2), 0, 0, 0, 0,
                     0, 7, r0_out, exit_out)
        self.assertEqual((exit_out[0], r0_out[0]), (1, 6))
        # Entry 1 validates and programs the 0x84 fields.
        window = bytearray(0x10000)
        struct.pack_into("<I", window, 0x2000 + (1 << 12) + 0x84,
                         0xFFFFFFFF)
        self.control(view(window), 0, 0x2000, 1, view(desc), view(desc2), 0, 0, 0, 0,
                     0, 1, r0_out, exit_out)
        want = (0xFFFFFFFF & ~0x80 & ~0x60) | (1 << 7) | (2 << 5)
        self.assertEqual(
            u32_at(window, 0x2000 + (1 << 12) + 0x84), want & 0xFFFFFFFF)
        self.assertEqual((exit_out[0], r0_out[0]), (0, 2))
        # Entry 1 rejects out-of-range descriptors.
        bad = bytearray([0x04, 0x01] + [0] * 14)
        self.control(view(window), 0, 0x2000, 1, view(bad), view(desc2), 0, 0, 0, 0,
                     0, 1, r0_out, exit_out)
        self.assertEqual((exit_out[0], r0_out[0]), (1, 6))
        # Entry 4 clears bit 6; entry 5 sets it.
        for arm, bit in ((4, 0), (5, 0x40)):
            window = bytearray(0x10000)
            struct.pack_into("<I", window, 0x2000 + (1 << 12) + 0x90,
                             0xFFFFFFFF)
            self.control(view(window), 0, 0x2000, 1, view(desc), view(desc2), 0, 0, 0,
                         0, 0, arm, r0_out, exit_out)
            self.assertEqual(
                u32_at(window, 0x2000 + (1 << 12) + 0x90),
                (0xFFFFFFFF & ~0x40) | bit)
            self.assertEqual(exit_out[0], 0)

    def test_devconfig_main_and_dividers(self) -> None:
        cfg = bytearray(24)
        cfg[0], cfg[4], cfg[5] = 0x12, 0x34, 0x56
        cfg[6], cfg[7] = 0x78, 0x9A
        cfg[8], cfg[9] = 0xBC, 0xDE
        cfg[0xB], cfg[0xC] = 0x07, 0x03
        cfg[0xD], cfg[0xE], cfg[0xF] = 0x01, 0x01, 0x01
        cfg[0x10], cfg[0x12] = 0x01, 0x02
        cfg[0x14], cfg[0x15], cfg[0x16] = 0x11, 0x22, 0x03
        state = bytearray(32)
        state[0x18] = 1
        window = bytearray(0x20000)
        struct.pack_into("<I", window, 0x1000 + 0x88, 0xFFFFFFFF)
        struct.pack_into("<I", window, 0x1000 + 0x8C, 0xFFFFFFFF)
        r0_out = (ctypes.c_uint32 * 1)(0)
        exit_out = (ctypes.c_uint32 * 1)(9)
        ret = self.devconfig(view(window), 0x1000, 0, view(cfg), view(state),
                             0xFFFFFFFF, 0, 0, r0_out, exit_out)
        self.assertEqual(ret, 0)
        self.assertEqual((exit_out[0], r0_out[0]), (0, 0))
        self.assertEqual(u32_at(window, 0x1000 + 0x88) & 1, 1)
        self.assertEqual(u32_at(window, 0x1000 + 0x8C) >> 31, 1)
        self.assertEqual((u32_at(window, 0x1000 + 0x8C) >> 17) & 3, 2)
        self.assertEqual(u32_at(window, 0x1000 + 0x30) & 1, 0)
        self.assertEqual((u32_at(window, 0x1000 + 0x30) >> 4) & 0xF, 7)
        r2 = (u32_at(window, 0x1000 + 0x90))
        self.assertEqual(r2 & 0xC, 0xC)
        self.assertEqual(r2 & 0x20, 0x20)
        self.assertEqual(r2 & 0x40, 0x40)
        self.assertEqual(r2 & 0x80, 0x80)
        self.assertEqual(state[0xA], 0xBC)
        self.assertEqual(state[0xC], 0x07)
        self.assertEqual(u32_at(state, 0x10), 0x2710)
        # cfg[0xB] = 7 selects the alternate divider path.
        self.assertEqual(u32_at(window, 0x1000 + 0x114), 0x20)
        self.assertEqual(u32_at(window, 0x1000 + 0x118) & 0x1F, 8)
        self.assertEqual((u32_at(window, 0x1000 + 0x20) >> 8) & 0x3F, 0x1E)
        self.assertEqual((u32_at(window, 0x1000 + 0x118) >> 8) & 0x1F, 8)
        # Main divider path (cfg[0xB] = 0x13) and reject path (0x18).
        for cfg_b, want_exit, want_r0, want_low5 in (
                (0x13, 0, 0, 0xC), (0x18, 1, 5, None)):
            window2 = bytearray(0x20000)
            state2 = bytearray(state)
            cfg2 = bytearray(cfg)
            cfg2[0xB] = cfg_b
            self.devconfig(view(window2), 0x1000, 0, view(cfg2), view(state2),
                           0xFFFFFFFF, 0, 0, r0_out, exit_out)
            self.assertEqual((exit_out[0], r0_out[0]),
                             (want_exit, want_r0))
            if want_low5 is not None:
                self.assertEqual(
                    u32_at(window2, 0x1000 + 0x118) & 0x1F, want_low5)
        # Divider arms OR their constant and exit to the head.
        for arm, const in enumerate(
                (0x20000, 0x30000, 0x40000, 0x60000, 0x80000,
                 0xC0000, 0x100000, 0x180000, 0x200000), start=1):
            with self.subTest(arm=arm):
                self.devconfig(view(window), 0x1000, 0, view(cfg), view(state),
                               0xFFFFFFFF, 0x12345, arm, r0_out,
                               exit_out)
                self.assertEqual(exit_out[0], 2)
                self.assertEqual(r0_out[0], 0x12345 | const)
        # Fail stub returns 5; jump exits to the head.
        self.devconfig(view(window), 0x1000, 0, view(cfg), view(state), 0xFFFFFFFF,
                       0, 10, r0_out, exit_out)
        self.assertEqual((exit_out[0], r0_out[0]), (1, 5))
        self.devconfig(view(window), 0x1000, 0, view(cfg), view(state), 0xFFFFFFFF,
                       0, 11, r0_out, exit_out)
        self.assertEqual(exit_out[0], 2)

    def test_devconfig2_arms(self) -> None:
        nibbles = (5, 6, 9, 0xA, 0xD, 0xE, 1, 2, 1, 2, 1, 2,
                   0xD, 0xE, 0x11, 0x12, 1, 2, 1, 2, 1, 2, 1, 2)
        nibble_b = (0, 0, 0, 0, 0, 0, 9, 9, 0xB, 0xB, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        r0consts = (0x103, 0x103, 0x10F, 0x10F, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0x103, 0x103, 0x103, 0x103,
                    0x10F, 0x10F, 0x10F, 0x10F, 0x103, 0x103)
        for arm in range(24):
            for b9 in (0, 1):
                with self.subTest(arm=arm, b9=b9):
                    window = bytearray(0x20000)
                    base, idx = 0x5000, 3
                    for off in (0x84, 0x90, 0x44):
                        struct.pack_into("<I", window, base + (idx << 12) + off,
                                         0xFFFFFFFF)
                    ret = self.devconfig2(view(window), idx, b9, base,
                                          0x80000013, arm)
                    self.assertEqual(ret, 0)
                    b = base + (idx << 12)
                    self.assertEqual(
                        u32_at(window, b + 0x84),
                        (0xFFFFFFFF & ~0x1F & ~0x2000000) | nibbles[arm])
                    if 6 <= arm <= 9:
                        self.assertEqual(
                            u32_at(window, b + 0x90),
                            (0xFFFFFFFF & ~0xF00) | (nibble_b[arm] << 8))
                        self.assertEqual(u32_at(window, b + 0x44), 0x3FF)
                    elif arm in (12, 13):
                        self.assertEqual(u32_at(window, b + 0x90),
                                         0xFFFFFFFF & ~0xF00)
                        self.assertEqual(u32_at(window, b + 0x44), 0x80000013)
                    elif arm in (4, 5, 10, 11):
                        self.assertEqual(u32_at(window, b + 0x90),
                                         0xFFFFFFFF & ~0xF00)
                        self.assertEqual(u32_at(window, b + 0x44), 0x3FF)
                    else:
                        self.assertEqual(u32_at(window, b + 0x90),
                                         0xFFFFFFFF & ~0xF00)
                        want = 0x80000013 if b9 else r0consts[arm]
                        self.assertEqual(u32_at(window, b + 0x44), want)


if __name__ == "__main__":
    unittest.main()
