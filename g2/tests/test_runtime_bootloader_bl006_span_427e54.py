#!/usr/bin/env python3
"""BL-006: structural survey of the 1,316-byte span at 0x00427E54.

The last unexamined BL-006 region (`0x00427E54..0x00428378`, between the
source-owned binary32 runtime and the source-owned SPOT-manager
transition) is code-shaped, not a literal pool, so the named-field
`in_place_data` route used for the other BL-006 pools cannot admit it,
and no reviewed clean-room C reproduces it. This test pins what the
span *is* -- four single-exit subspans with exact byte hashes,
prologue/epilogue encodings, out-of-span callee sets, and data-pool
targets -- plus the two properties a future fill or reconstruction
pass will need: no word anywhere in the image equals any subspan
entry (not even with the Thumb bit set), and the whole-image survey
still finds no surviving external branch into the region.

Subspan structure (all verified by anchored Capstone decode; a
whole-span linear sweep desynchronizes through the embedded `50.0f` /
`1000.0f` pool words at `0x00428060`/`0x00428064`, so every span here
is decoded anchored at its own prologue):

- T0 `0x00427E54..0x00427E84` (48 B): suffix tail of the stock
  `float_range_classify_427e0c` body. The reviewed replacement covers
  only the first 72 of the 120 stock bytes
  (see `g2-bootloader-float-math-427c90-427e84-source-closure.md`);
  this tail compares `s0` against `50.0f`/`1000.0f` (`vcmp.f32`,
  `vldr` from the embedded pool) and returns 2/3/4 via the single
  `bx lr` at `0x00427E82`. No calls.
- F1 `0x00427E84..0x00428068` (484 B): `push.w {r3-r11,lr}` frame,
  single `pop.w {r0,r4-r11,pc}` exit at `0x00428056`. Calls the
  SPOT trim/delay/IRQ helpers; no local stack carve-out.
- F2 `0x00428068..0x00428240` (472 B): `push.w {r1-r11,lr}` frame,
  single `pop.w {r0-r2,r4-r11,pc}` exit at `0x0042823C`.
- F3 `0x00428240..0x00428378` (312 B): `push.w {r3-r11,lr}` frame,
  single `pop.w {r0,r4-r11,pc}` exit at `0x00428374`; the following
  `push {r7,lr}` at `0x00428378` belongs to the source-owned
  SPOT-manager transition sequence.

Callee key (all out-of-span, all named by reviewed consumer
sources): `0x0041CC48` spotmgr transition start, `0x0041CCD6`
spotmgr trim finalize, `0x0041D1C0` delay cycles, `0x0041E1E8`
spotmgr IRQ resume, `0x0041E22E` spotmgr IRQ pause, `0x0042A04A`
SPOT timer service, `0x0042A1BC` VDDC/VDDF Ton-trim selector.

Every PC-relative data target sits in retained SPOT-table regions
owned by other items (`0x004283E2..` gaps): SRAM state words and
power registers, including one `0.9f` (`0x3F666666`) word. The
whole-image literal-word scan and the survey verdict below are the
deadness evidence; hardware behavior is not qualified.

Evidence:
`g2/docs/research/g2-bootloader-bl006-span-427e54-spot-trim-survey.md`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
RUN_BASE = 0x00410000
BLOB_SHA256 = (
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
)

SPAN_START = 0x00427E54
SPAN_END = 0x00428378
SPAN_SHA256 = (
    "0ce1f6634fd2f9b54629e04ef7606fc28e0830c02f4262a7bae95abb38658821"
)

# (name, start, end, sha256, prologue bytes or None, epilogue addr/bytes)
SUBSPANS = (
    (
        "T0-classifier-tail",
        0x00427E54,
        0x00427E84,
        "609d289f0975ea5c58c0666883dd8c46b023df79951bad5c75b7cf5de791ab2c",
        None,
        (0x00427E82, bytes.fromhex("7047")),
    ),
    (
        "F1",
        0x00427E84,
        0x00428068,
        "b5072ed73bf47a2e3d0de0f25752fd2de966c0f8f0c8f6278a5e6fb63cd021fa",
        bytes.fromhex("2de9f84f"),
        (0x00428056, bytes.fromhex("bde8f18f")),
    ),
    (
        "F2",
        0x00428068,
        0x00428240,
        "7828372b3a4b3704f7d9202a325edc738dcf1af81ad60af87d11495e284388ad",
        bytes.fromhex("2de9fe4f"),
        (0x0042823C, bytes.fromhex("bde8f78f")),
    ),
    (
        "F3",
        0x00428240,
        0x00428378,
        "aed159d19382e0b72478d67e5204326070f9f6f27e1f426a3716cd97cbf41289",
        bytes.fromhex("2de9f84f"),
        (0x00428374, bytes.fromhex("bde8f18f")),
    ),
)

CALLEES = {
    "T0-classifier-tail": set(),
    "F1": {
        0x0041CCD6,
        0x0041D1C0,
        0x0041E1E8,
        0x0041E22E,
        0x0042A04A,
        0x0042A1BC,
    },
    "F2": {
        0x0041D1C0,
        0x0041E1E8,
        0x0041E22E,
        0x0042A04A,
        0x0042A1BC,
    },
    "F3": {
        0x0041CC48,
        0x0041D1C0,
        0x0042A04A,
        0x0042A1BC,
    },
}

LITERALS = {
    "T0-classifier-tail": {0x00428060, 0x00428064},
    "F1": {
        0x00428A78,
        0x00428A7C,
        0x00428A80,
        0x00428A84,
        0x00428A88,
        0x00428A8C,
        0x00428A90,
        0x00428BA8,
        0x00428BAC,
        0x00428C84,
        0x00428C88,
        0x00428C90,
        0x00428C94,
        0x00428C98,
        0x00428C9C,
        0x00428CA0,
    },
    "F2": {
        0x00428A78,
        0x00428A7C,
        0x00428A84,
        0x00428A88,
        0x00428A8C,
        0x00428A90,
        0x00428BA8,
        0x00428BAC,
        0x00428C84,
        0x00428C90,
        0x00428C94,
        0x00428C98,
        0x00428C9C,
        0x00428CA0,
    },
    "F3": {
        0x00428A78,
        0x00428A7C,
        0x00428A80,
        0x00428A84,
        0x00428A88,
        0x00428A8C,
        0x00428A90,
        0x00428BA8,
        0x00428C84,
        0x00428C88,
        0x00428C90,
        0x00428C94,
        0x00428C98,
    },
}

try:
    from capstone import (
        CS_ARCH_ARM,
        CS_GRP_CALL,
        CS_MODE_THUMB,
        CS_OP_IMM,
        CS_OP_MEM,
        Cs,
    )

    HAVE_CAPSTONE = True
except ImportError:  # pragma: no cover
    HAVE_CAPSTONE = False


def _load_image() -> bytes:
    image = OFFICIAL.read_bytes()
    if hashlib.sha256(image).hexdigest() != BLOB_SHA256:
        raise unittest.SkipTest("stock bootloader image hash mismatch")
    return image


def _decode(span: bytes, base: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    return list(md.disasm(span, base))


class Bl006Span427E54Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not HAVE_CAPSTONE:
            raise unittest.SkipTest("capstone is unavailable")
        cls.image = _load_image()

    def _span_bytes(self, start: int, end: int) -> bytes:
        return self.image[start - RUN_BASE : end - RUN_BASE]

    def test_span_hash_matches_survey_pin(self) -> None:
        self.assertEqual(
            hashlib.sha256(self._span_bytes(SPAN_START, SPAN_END)).hexdigest(),
            SPAN_SHA256,
        )

    def test_subspan_layout_and_hashes(self) -> None:
        total = 0
        for name, start, end, sha, prologue, (epi_addr, epi_bytes) in SUBSPANS:
            with self.subTest(subspan=name):
                body = self._span_bytes(start, end)
                self.assertEqual(hashlib.sha256(body).hexdigest(), sha)
                total += end - start
                if prologue is not None:
                    self.assertEqual(
                        body[: len(prologue)],
                        prologue,
                        f"{name} prologue encoding changed",
                    )
                epi_off = epi_addr - start
                self.assertEqual(
                    body[epi_off : epi_off + len(epi_bytes)],
                    epi_bytes,
                    f"{name} epilogue encoding changed",
                )
        self.assertEqual(total, SPAN_END - SPAN_START)

    def test_single_bx_lr_in_span(self) -> None:
        # Exactly one 16-bit `bx lr` exists in the whole span (T0's
        # return); F1/F2/F3 exit only through their 32-bit `pop.w pc`
        # epilogues pinned above. Any new return means the structure
        # changed and the audit must be re-derived.
        body = self._span_bytes(SPAN_START, SPAN_END)
        hits = [
            SPAN_START + i
            for i in range(0, len(body) - 1, 2)
            if body[i] == 0x70 and body[i + 1] == 0x47
        ]
        self.assertEqual(hits, [0x00427E82])

    def test_callee_sets(self) -> None:
        for name, start, end, _sha, _pro, _epi in SUBSPANS:
            with self.subTest(subspan=name):
                insns = _decode(self._span_bytes(start, end), start)
                calls = set()
                for insn in insns:
                    if insn.group(CS_GRP_CALL):
                        for op in insn.operands:
                            if op.type == CS_OP_IMM:
                                calls.add(op.value.imm)
                self.assertEqual(calls, CALLEES[name])
                for target in calls:
                    self.assertTrue(
                        target < SPAN_START or target >= SPAN_END,
                        f"{name} calls inside the span at {target:#x}; "
                        "internal structure changed",
                    )

    def test_literal_targets(self) -> None:
        for name, start, end, _sha, _pro, _epi in SUBSPANS:
            with self.subTest(subspan=name):
                insns = _decode(self._span_bytes(start, end), start)
                targets = set()
                for insn in insns:
                    for op in insn.operands:
                        if op.type == CS_OP_MEM and op.value.mem.base in (
                            11,
                            15,
                        ):
                            # Thumb PC-relative literal rule used by the
                            # prior BL-006 loader scans: Align(PC,4)+imm.
                            # Validated here by the 50.0f/1000.0f pool
                            # words the T0 vldr pair resolves to.
                            targets.add(
                                ((insn.address + 4) & ~3)
                                + op.value.mem.disp
                            )
                self.assertEqual(targets, LITERALS[name])

    def test_float_pool_words(self) -> None:
        pool = self._span_bytes(0x00428060, 0x00428068)
        self.assertEqual(
            struct.unpack("<ff", pool), (50.0, 1000.0)
        )

    def test_no_pointer_word_targets_any_entry(self) -> None:
        entries = {s for _n, s, _e, _h, _p, _epi in SUBSPANS}
        hits: dict[int, list[int]] = {entry: [] for entry in entries}
        for off in range(0, len(self.image) - 3, 4):
            word = struct.unpack_from("<I", self.image, off)[0] & ~1
            if word in hits:
                addr = RUN_BASE + off
                if not SPAN_START <= addr < SPAN_END:
                    hits[word].append(addr)
        for entry, addrs in hits.items():
            self.assertEqual(
                addrs,
                [],
                f"entry {entry:#x} appears as a pointer word at "
                f"{[hex(a) for a in addrs]}; reachability changed",
            )

    def test_survey_still_flags_nothing_for_this_region(self) -> None:
        path = ROOT / "tools/analyze_g2_bootloader_bl006_retained_survey.py"
        spec = importlib.util.spec_from_file_location(
            "analyze_g2_bootloader_bl006_retained_survey", path
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        report = module.survey()
        regions = [
            region
            for region in report["regions"]
            if region["start"] == f"0x{SPAN_START:08X}"
            or region["start"] == SPAN_START
        ]
        self.assertEqual(len(regions), 1)
        self.assertNotEqual(
            regions[0]["verdict"], "POSSIBLY_REACHABLE_NEEDS_REVIEW"
        )
        self.assertEqual(report["needs_review_count"], 0)


if __name__ == "__main__":
    unittest.main()
