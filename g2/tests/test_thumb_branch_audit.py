from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import thumb_branch_audit as audit  # noqa: E402


def movw(register: int, immediate: int) -> bytes:
    """Encode `movw <register>, #<immediate>` (Thumb-2 T3)."""
    imm4 = (immediate >> 12) & 0xF
    i = (immediate >> 11) & 1
    imm3 = (immediate >> 8) & 7
    imm8 = immediate & 0xFF
    first = 0xF240 | (i << 10) | imm4
    second = (imm3 << 12) | (register << 8) | imm8
    return bytes([first & 0xFF, first >> 8, second & 0xFF, second >> 8])


def movt(register: int, immediate: int) -> bytes:
    """Encode `movt <register>, #<immediate>` (Thumb-2 T1)."""
    imm4 = (immediate >> 12) & 0xF
    i = (immediate >> 11) & 1
    imm3 = (immediate >> 8) & 7
    imm8 = immediate & 0xFF
    first = 0xF2C0 | (i << 10) | imm4
    second = (imm3 << 12) | (register << 8) | imm8
    return bytes([first & 0xFF, first >> 8, second & 0xFF, second >> 8])


def bx(register: int) -> bytes:
    """Encode `bx <register>` (Thumb T1)."""
    value = 0x4700 | (register << 3)
    return bytes([value & 0xFF, value >> 8])


def blx(register: int) -> bytes:
    """Encode `blx <register>` (Thumb T1)."""
    value = 0x4780 | (register << 3)
    return bytes([value & 0xFF, value >> 8])


def materialize(register: int, target: int) -> bytes:
    """Encode the full `movw / movt / bx` constant-branch idiom."""
    return (
        movw(register, target & 0xFFFF)
        + movt(register, (target >> 16) & 0xFFFF)
        + bx(register)
    )


NOP = bytes([0x00, 0xBF])


# --- Pinned real-world evidence -------------------------------------------
#
# `faceclaw_evenai_display_entry` exactly as it exists in the shipped image
#
#   SybilSight CFW (2.2.6.11)
#   sha256 d2fb5dcef485b1bb14818b8dc56811b9d278d6fc2b81e56c496c53b72aaa1e86
#   4,320,415 bytes, base Even Realities G2 stock s200_v2.2.6.10
#
# extracted from file offset 4,305,215, which the appended CFW blob loads at
# MRAM 0x007952B8. The B.W installed over `even_ai_display_ctrl`'s prologue at
# 0x004E1FD2 (stock `7f b5 06 00`) branches here.
#
# The trailing `bx ip` returns to the stock function body at 0x004E1FD6 with
# bit 0 clear, which requests ARM state. The Apollo510 (Cortex-M55) has no ARM
# state, so this raises a UsageFault with INVSTATE set. The shipped image
# installs no MemManage/BusFault/UsageFault vectors, so it escalates to
# HardFault, which captures /log/hardfault.txt and then spins until the
# external watchdog resets the temple.
SHIPPED_CFW_SHA256 = (
    "d2fb5dcef485b1bb14818b8dc56811b9d278d6fc2b81e56c496c53b72aaa1e86"
)
SHIPPED_TRAMPOLINE_BASE = 0x007952B8
SHIPPED_TRAMPOLINE_FILE_OFFSET = 4_305_215
SHIPPED_TRAMPOLINE = bytes.fromhex(
    "7fb5"          # push {r0-r6, lr}
    "0646"          # mov  r6, r0
    "0028"          # cmp  r0, #0
    "06d1"          # bne  +0xc            -> resume stock (op != START)
    "fff760fc"      # bl   cfw_wake_lease_active
    "0028"          # cmp  r0, #0
    "07d1"          # bne  +0xe            -> suppress (lease held)
    "9de80f00"      # ldm.w sp, {r0-r3}
    "0646"          # mov  r6, r0
    "41f6d67c"      # movw ip, #0x1fd6     <-- Thumb bit missing
    "c0f24e0c"      # movt ip, #0x4e
    "6047"          # bx   ip              <-- INVSTATE UsageFault
    "7fbd"          # pop  {r0-r6, pc}
)
# Offset of the `movw` half of the defective pair inside the trampoline.
SHIPPED_MOVW_OFFSET = 22
SHIPPED_BRANCH_ADDRESS = SHIPPED_TRAMPOLINE_BASE + SHIPPED_MOVW_OFFSET
SHIPPED_TARGET = 0x004E1FD6

# Every `movw/movt -> bx|blx` site in the shipped 19,188-byte CFW blob, which
# the image loads at MRAM 0x00794324. The audited blob spans file offsets
# 4,301,227..4,320,415.
#
# Eight of the nine materialize a stock entry point with the Thumb bit set --
# including 0x0045A569 (the lens-side accessor the CFW spells `FW_SIDE_ID`) and
# 0x00475B15 (`FW_SEND`), both written as odd constants in C. Only the Even AI
# trampoline, whose destination is spelled as a bare `movw`/`movt` immediate
# pair inside inline assembly, is even. That contrast is the whole finding:
# the same author got this right eight times in the same translation unit.
SHIPPED_BLOB_BASE = 0x00794324
SHIPPED_BLOB_FILE_OFFSET = 4_301_227
SHIPPED_BLOB_SITES = {
    0x00794328: 0x00474CD3,
    0x00794336: 0x00474D17,
    0x00794C88: 0x004494D9,
    0x00794D1C: 0x0045A569,
    0x007951B6: 0x004494D9,
    0x007952CE: 0x004E1FD6,
    0x007953C6: 0x00475B15,
    0x00795CE0: 0x00502AC5,
    0x007987EC: 0x005BEA87,
}


class ImmediateDecodingTests(unittest.TestCase):
    def test_decodes_every_immediate_bit_position(self) -> None:
        for bit in range(16):
            immediate = 1 << bit
            encoded = movw(3, immediate)
            first = encoded[0] | (encoded[1] << 8)
            second = encoded[2] | (encoded[3] << 8)
            self.assertEqual(
                audit.decode_movw_movt_immediate(first, second), immediate
            )

    def test_decodes_boundary_immediates(self) -> None:
        for immediate in (0x0000, 0x0001, 0x00FF, 0x0100, 0x07FF, 0x0800,
                          0x0FFF, 0x1000, 0xFFFE, 0xFFFF):
            encoded = movt(9, immediate)
            first = encoded[0] | (encoded[1] << 8)
            second = encoded[2] | (encoded[3] << 8)
            self.assertEqual(
                audit.decode_movw_movt_immediate(first, second), immediate
            )


class ConstantBranchDetectionTests(unittest.TestCase):
    def test_flags_bx_to_even_target(self) -> None:
        findings = audit.audit(materialize(12, 0x004E1FD6))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].register, 12)
        self.assertEqual(findings[0].target, 0x004E1FD6)
        self.assertFalse(findings[0].is_thumb)

    def test_accepts_bx_to_odd_target(self) -> None:
        self.assertEqual(audit.audit(materialize(12, 0x004E1FD7)), [])

    def test_flags_blx_to_even_target(self) -> None:
        blob = movw(4, 0x1FD6) + movt(4, 0x004E) + blx(4)
        findings = audit.audit(blob)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].mnemonic, "blx")

    def test_accepts_blx_to_odd_target(self) -> None:
        self.assertEqual(audit.audit(movw(4, 0x1FD7) + movt(4, 0x004E) + blx(4)), [])

    def test_ignores_movt_targeting_another_register(self) -> None:
        blob = movw(1, 0x1FD6) + movt(2, 0x004E) + bx(1)
        self.assertEqual(audit.audit(blob), [])

    def test_ignores_branch_through_another_register(self) -> None:
        blob = movw(1, 0x1FD6) + movt(1, 0x004E) + bx(3)
        self.assertEqual(audit.audit(blob), [])

    def test_ignores_non_adjacent_sequence(self) -> None:
        """An intervening instruction may set the Thumb bit, so do not guess."""
        blob = movw(12, 0x1FD6) + movt(12, 0x004E) + NOP + bx(12)
        self.assertEqual(audit.audit(blob), [])

    def test_ignores_movw_movt_without_a_branch(self) -> None:
        self.assertEqual(audit.audit(movw(12, 0x1FD6) + movt(12, 0x004E) + NOP), [])

    def test_ignores_bare_bx(self) -> None:
        self.assertEqual(audit.audit(bx(14) * 8), [])

    def test_tolerates_truncated_blob(self) -> None:
        """A sequence cut short is incomplete evidence, never a finding."""
        blob = materialize(12, 0x004E1FD6)
        for length in range(len(blob)):
            self.assertEqual(audit.audit(blob[:length]), [], f"length {length}")
        self.assertEqual(len(audit.audit(blob)), 1)

    def test_tolerates_empty_blob(self) -> None:
        self.assertEqual(audit.audit(b""), [])

    def test_finds_every_defect_in_a_blob(self) -> None:
        blob = (
            materialize(1, 0x00474CD3)
            + materialize(12, 0x004E1FD6)
            + materialize(12, 0x00475B15)
            + materialize(3, 0x00123456)
        )
        findings = audit.audit(blob)
        self.assertEqual(
            [finding.target for finding in findings],
            [0x004E1FD6, 0x00123456],
        )


class AddressReportingTests(unittest.TestCase):
    def test_reports_blob_relative_offsets_by_default(self) -> None:
        blob = NOP + materialize(12, 0x004E1FD6)
        finding = audit.audit(blob)[0]
        self.assertEqual(finding.offset, 2)
        self.assertEqual(finding.address, 2)

    def test_reports_addresses_relative_to_base(self) -> None:
        blob = NOP + materialize(12, 0x004E1FD6)
        finding = audit.audit(blob, base_address=SHIPPED_BLOB_BASE)[0]
        self.assertEqual(finding.offset, 2)
        self.assertEqual(finding.address, SHIPPED_BLOB_BASE + 2)


class ShippedCustomFirmwareTests(unittest.TestCase):
    """Regression evidence pinned from the image customers are running."""

    def test_trampoline_fixture_is_the_documented_length(self) -> None:
        self.assertEqual(len(SHIPPED_TRAMPOLINE), 34)

    def test_audit_detects_the_shipped_even_ai_defect(self) -> None:
        findings = audit.audit(
            SHIPPED_TRAMPOLINE, base_address=SHIPPED_TRAMPOLINE_BASE
        )
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.address, SHIPPED_BRANCH_ADDRESS)
        self.assertEqual(finding.register, 12)
        self.assertEqual(finding.target, SHIPPED_TARGET)
        self.assertEqual(finding.mnemonic, "bx")
        self.assertFalse(finding.is_thumb)

    def test_one_byte_restores_the_thumb_bit(self) -> None:
        """The reviewed fix is `movw ip, #0x1fd7`: a single immediate byte."""
        fixed = bytearray(SHIPPED_TRAMPOLINE)
        fixed[SHIPPED_MOVW_OFFSET + 2] |= 0x01
        differing = [
            index
            for index, (before, after) in enumerate(
                zip(SHIPPED_TRAMPOLINE, fixed)
            )
            if before != after
        ]
        self.assertEqual(differing, [SHIPPED_MOVW_OFFSET + 2])
        self.assertEqual(
            audit.audit(bytes(fixed), base_address=SHIPPED_TRAMPOLINE_BASE), []
        )

    def test_fixed_trampoline_targets_the_stock_resume_point(self) -> None:
        fixed = bytearray(SHIPPED_TRAMPOLINE)
        fixed[SHIPPED_MOVW_OFFSET + 2] |= 0x01
        branches = audit.find_constant_branches(
            bytes(fixed), base_address=SHIPPED_TRAMPOLINE_BASE
        )
        self.assertEqual(len(branches), 1)
        self.assertEqual(branches[0].target, SHIPPED_TARGET | 1)
        self.assertTrue(branches[0].is_thumb)
        self.assertEqual(branches[0].target & ~1, SHIPPED_TARGET)


@unittest.skipUnless(
    os.environ.get("SYBILSIGHT_G2_CFW_IMAGE"),
    "set SYBILSIGHT_G2_CFW_IMAGE to the reviewed CFW bundle to audit it whole",
)
class ShippedImageAuditTests(unittest.TestCase):
    """Whole-image audit, opt-in because the bundle is not vendored here."""

    @classmethod
    def setUpClass(cls) -> None:
        path = Path(os.environ["SYBILSIGHT_G2_CFW_IMAGE"]).expanduser()
        cls.image = path.read_bytes()
        cls.digest = hashlib.sha256(cls.image).hexdigest()

    def test_image_is_the_pinned_reviewed_build(self) -> None:
        self.assertEqual(self.digest, SHIPPED_CFW_SHA256)
        self.assertEqual(len(self.image), 4_320_415)

    def test_trampoline_fixture_matches_the_image(self) -> None:
        start = SHIPPED_TRAMPOLINE_FILE_OFFSET
        self.assertEqual(
            self.image[start:start + len(SHIPPED_TRAMPOLINE)],
            SHIPPED_TRAMPOLINE,
        )

    def test_even_ai_hook_is_installed_over_the_stock_prologue(self) -> None:
        installed = self.image[1_474_137:1_474_141]
        self.assertEqual(installed, bytes.fromhex("b3f271b9"))
        self.assertNotEqual(installed, bytes.fromhex("7fb50600"))

    def test_only_the_even_ai_trampoline_is_defective(self) -> None:
        blob = self.image[SHIPPED_BLOB_FILE_OFFSET:]
        branches = audit.find_constant_branches(
            blob, base_address=SHIPPED_BLOB_BASE
        )
        self.assertEqual(
            {branch.address: branch.target for branch in branches},
            SHIPPED_BLOB_SITES,
        )
        findings = audit.audit(blob, base_address=SHIPPED_BLOB_BASE)
        self.assertEqual([finding.address for finding in findings], [0x007952CE])


class CommandLineTests(unittest.TestCase):
    TOOL = OPENCFW_ROOT / "tools" / "thumb_branch_audit.py"

    def run_tool(self, blob: bytes, *arguments: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blob.bin"
            path.write_bytes(blob)
            return subprocess.run(
                [sys.executable, str(self.TOOL), str(path), *arguments],
                capture_output=True,
                text=True,
            )

    def test_exits_zero_on_a_clean_blob(self) -> None:
        result = self.run_tool(materialize(12, 0x004E1FD7))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_exits_nonzero_and_names_the_defect(self) -> None:
        result = self.run_tool(
            SHIPPED_TRAMPOLINE, "--base", hex(SHIPPED_TRAMPOLINE_BASE)
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("007952ce", result.stdout.lower())
        self.assertIn("004e1fd6", result.stdout.lower())

    def test_emits_machine_readable_findings(self) -> None:
        result = self.run_tool(
            SHIPPED_TRAMPOLINE, "--base", hex(SHIPPED_TRAMPOLINE_BASE), "--json"
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["scanned_bytes"], len(SHIPPED_TRAMPOLINE))
        self.assertEqual(len(payload["findings"]), 1)
        self.assertEqual(payload["findings"][0]["target"], SHIPPED_TARGET)
        self.assertEqual(payload["findings"][0]["address"], SHIPPED_BRANCH_ADDRESS)


if __name__ == "__main__":
    unittest.main()
