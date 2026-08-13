#!/usr/bin/env python3
"""Fail-closed tests for the G2 touch I2C protocol audit."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_touch_i2c_protocol as proto  # noqa: E402

BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_touch.bin"


def tamper(data: bytes, offset: int, xor: int = 0x01) -> bytes:
    buf = bytearray(data)
    buf[offset] ^= xor
    return bytes(buf)


class TestProtocolAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = BLOB.read_bytes()

    def test_full_audit_passes(self):
        report = proto.audit(self.blob)
        self.assertEqual(len(report["checks"]), 6)
        self.assertTrue(all(c["result"] == "pass" for c in report["checks"]))

    def test_span_tamper_fails(self):
        # one byte inside each pinned protocol span (payload-relative)
        for off in (0x0380, 0x0446, 0x04C8, 0x052C, 0x0900, 0x37C8,
                    0x4B18, 0x67D8, 0x7050, 0x0BE0, 0x06FC, 0x02F4):
            with self.subTest(payload_offset=off):
                with self.assertRaises(proto.AuditError):
                    proto.audit(tamper(self.blob, 0x20 + off))

    def test_pool_tamper_fails(self):
        for off, _value, _role in proto.POOLS[:6]:
            with self.subTest(pool=off):
                with self.assertRaises(proto.AuditError):
                    proto.audit(tamper(self.blob, 0x20 + off))

    def test_resident_ref_tamper_fails(self):
        for off, _value, _role in proto.RESIDENT_REFS:
            with self.subTest(resident_ref=off):
                with self.assertRaises(proto.AuditError):
                    proto.audit(tamper(self.blob, 0x20 + off))

    def test_dispatch_site_tamper_fails(self):
        for off in (0x42C, 0x43A, 0x444):
            with self.subTest(dispatch=off):
                with self.assertRaises(proto.AuditError):
                    proto.audit(tamper(self.blob, 0x20 + off))

    def test_truncated_blob_fails(self):
        with self.assertRaises(proto.AuditError):
            proto.audit(self.blob[:-1])

    def test_dispatch_constants(self):
        # rx length rule [1,16] and command slot bound 8 are structural
        self.assertEqual(proto.DISPATCH_HALFWORDS[1], 0x1E43)   # subs r3,r0,#1
        self.assertEqual(proto.DISPATCH_HALFWORDS[3], 0x2B0F)   # cmp r3,#0xf
        self.assertEqual(proto.DISPATCH_HALFWORDS[7], 0x2B08)   # cmp r3,#8
        self.assertEqual(proto.DISPATCH_HALFWORDS[12], 0x469F)  # mov pc,r3

    def test_call_count_semantics(self):
        self.assertEqual(proto.CALL_COUNTS[0x0BE0], 38)
        self.assertEqual(proto.CALL_COUNTS[0x4B30], 1)
        self.assertEqual(proto.CALL_COUNTS[0x0400], 0)

    def test_command_map_covers_slots(self):
        slots = [c[0] for c in proto.COMMANDS]
        self.assertEqual(slots, list(range(9)))
        bodies = [c[1] for c in proto.COMMANDS if c[1] is not None]
        self.assertEqual(len(bodies), 7)
        for entry in bodies:
            self.assertTrue(0x400 <= entry < 0x5A0)


class TestManifestOutput(unittest.TestCase):
    def test_manifests_written(self):
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            rc = proto.main()
        self.assertEqual(rc, 0)
        for name in ("g2-touch-i2c-command-map.tsv",
                     "g2-touch-i2c-span-map.tsv",
                     "g2-touch-i2c-protocol-map.json"):
            path = ROOT / "tools/manifests" / name
            self.assertTrue(path.is_file(), name)
            self.assertGreater(path.stat().st_size, 0, name)

    def test_protocol_json_structure(self):
        import json
        data = json.loads((ROOT / "tools/manifests/g2-touch-i2c-protocol-map.json").read_text())
        self.assertEqual(data["component"], "g2-touch")
        self.assertEqual(data["transport"]["irq"]["number"], 7)
        self.assertEqual(data["transport"]["rx_buffer"]["address"], "0x200009A0")
        self.assertEqual(data["transport"]["attention_line"]["port"], "GPIO_PRT4")
        self.assertEqual(len(data["commands"]), 9)
        self.assertEqual(data["dfu_handoff"]["mailbox"], "0x20000000 (SRAM base, preserved across reset)")
        self.assertIn("shipped prefix", data["resident_dependency"]["model"])


if __name__ == "__main__":
    unittest.main()
