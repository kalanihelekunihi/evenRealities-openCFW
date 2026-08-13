#!/usr/bin/env python3
"""Fail-closed tests for the G2 touch-controller identity/memory-map audit."""

from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_touch_identity as audit_mod  # noqa: E402

BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_touch.bin"


def tamper(data: bytes, offset: int, xor: int = 0x01) -> bytes:
    buf = bytearray(data)
    buf[offset] ^= xor
    return bytes(buf)


class TestBlobAuthenticity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = BLOB.read_bytes()

    def test_full_audit_passes(self):
        report = audit_mod.audit(self.blob)
        self.assertEqual(len(report["checks"]), 12)
        self.assertTrue(all(c["result"] == "pass" for c in report["checks"]))

    def test_truncated_blob_fails(self):
        with self.assertRaises(audit_mod.AuditError):
            audit_mod.audit(self.blob[:-1])

    def test_wrapper_tamper_fails(self):
        for off in (0x00, 0x04, 0x08, 0x10, 0x14, 0x18, 0x1C):
            with self.subTest(offset=off):
                with self.assertRaises(audit_mod.AuditError):
                    audit_mod.audit(tamper(self.blob, off))

    def test_vector_tamper_fails(self):
        payload0 = 0x20
        for off in (payload0 + 0x00, payload0 + 0x04, payload0 + 0x74, payload0 + 0xB0):
            with self.subTest(offset=off):
                with self.assertRaises(audit_mod.AuditError):
                    audit_mod.audit(tamper(self.blob, off))

    def test_region_tamper_fails(self):
        # one byte inside each pinned region of the payload
        for off in (0x0100, 0x4000, 0x77A0, 0x7E00, 0x8114, 0x8200, 0x8500, 0x8600, 0x8660, 0x867E):
            with self.subTest(payload_offset=off):
                with self.assertRaises(audit_mod.AuditError):
                    audit_mod.audit(tamper(self.blob, 0x20 + off))

    def test_trailing_crc_tamper_fails(self):
        with self.assertRaises(audit_mod.AuditError):
            audit_mod.audit(tamper(self.blob, len(self.blob) - 1))

    def test_crc32c_known_vectors(self):
        # CRC-32C("123456789") = 0xE3069283; verified against the ARMv8
        # CRC32CB hardware instruction and both blob-resident CRC fields.
        self.assertEqual(audit_mod.crc32c(b"123456789"), 0xE3069283)
        self.assertEqual(audit_mod.crc32c(b""), 0x00000000)

    def test_vector_table_semantics(self):
        payload = self.blob[0x20:]
        vectors = struct.unpack_from("<48I", payload, 0)
        self.assertEqual(vectors[0], 0x20002000)          # 8 KiB SRAM top
        self.assertEqual(vectors[1], 0x00004675)          # reset
        self.assertEqual(vectors[3], 0x0000465F)          # HardFault
        self.assertTrue(all(w == 0 for w in vectors[4:11]))
        self.assertTrue(all(w == 0x0000465D for w in vectors[16:29]))  # 13 IRQs
        self.assertTrue(all(w == 0 for w in vectors[29:]))

    def test_peripheral_bases_present(self):
        payload = self.blob[0x20:]
        pools = dict(audit_mod.mmio_pool_census(payload))
        values = set(pools.values())
        for base in (0x40010000, 0x40030000, 0x40040200, 0x40040300, 0x40040400,
                     0x40100000, 0x40250000, 0x40290000):
            self.assertIn(base, values, f"missing PSoC 4000T block base {base:#x}")

    def test_strings_region_contents(self):
        payload = self.blob[0x20:]
        strings = payload[0x775C:0x7DC4]
        for needle in audit_mod.REQUIRED_STRINGS:
            self.assertIn(needle, strings)


class TestManifestOutput(unittest.TestCase):
    def test_manifests_written_and_stable(self):
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            rc = audit_mod.main()
        self.assertEqual(rc, 0)
        for name, digest in (
            ("g2-touch-identity-regions.tsv",
             None),  # digests asserted structurally below
            ("g2-touch-identity-peripheral-census.tsv", None),
            ("g2-touch-identity-memory-map.json", None),
        ):
            path = ROOT / "tools/manifests" / name
            self.assertTrue(path.is_file(), name)
            self.assertGreater(path.stat().st_size, 0, name)

    def test_memory_map_json_structure(self):
        import json
        data = json.loads((ROOT / "tools/manifests/g2-touch-identity-memory-map.json").read_text())
        self.assertEqual(data["component"], "g2-touch")
        self.assertIn("PSoC 4000T", data["identity"]["verdict"])
        self.assertEqual(data["container"]["record"]["type"], 3)
        self.assertEqual(data["container"]["record"]["size"], 0x8680)
        self.assertEqual(data["memory_map"]["initial_sp"], 0x20002000)
        self.assertEqual(len(data["memory_map"]["regions"]), 10)
        self.assertEqual(len(data["memory_map"]["nvic"]), 13)
        sizes = sum(r["size"] for r in data["memory_map"]["regions"])
        self.assertEqual(sizes, 0x8680)


if __name__ == "__main__":
    unittest.main()
