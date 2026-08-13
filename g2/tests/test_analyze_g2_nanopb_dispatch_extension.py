from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_nanopb_dispatch_extension as audit  # noqa: E402


class NanopbDispatchExtensionAuditTests(unittest.TestCase):
    def test_authenticated_boundaries_source_and_topology(self) -> None:
        report = audit.analyze()
        self.assertEqual(report["stock"]["size"], 254)
        self.assertEqual(report["stock"]["sha256"], audit.STOCK_SHA256)
        self.assertEqual(
            [item["name"] for item in report["stock"]["segments"]],
            [item[0] for item in audit.SEGMENTS],
        )
        self.assertFalse(report["topology"]["interior_bl"])
        self.assertFalse(report["topology"]["alternate"])
        self.assertFalse(report["topology"]["stored_pointers"])
        self.assertEqual(len(report["outgoing"]), 6)
        self.assertEqual(report["dynamic_callback"]["site"], 0x0048_FCB8)
        self.assertEqual(len(report["diagnostics"]), 2)
        self.assertEqual(len(report["upstream"]["definitions"]), 3)
        self.assertEqual(report["upstream"]["exact_definition_range"], "0.4.4--0.4.9.1")
        self.assertEqual(report["decision"]["source_identification_percent"], 100)
        self.assertEqual(report["decision"]["source_recreation_percent"], 100)
        self.assertTrue(report["decision"]["production_integrated"])
        self.assertEqual(len(report["production"]["functions"]), 3)
        self.assertEqual(
            report["decision"]["address_correction"]["decode_extension"],
            0x0048_FC88,
        )

    def test_mutated_dispatch_body_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        blob[audit.START - audit.shared.LOAD_BASE + 8] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.bin"
            path.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(path)

    def test_mutated_extension_caller_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        address = audit.EXPECTED_CALLERS[0x0048_FC88][0][0]
        blob[address - audit.shared.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.bin"
            path.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(path)


if __name__ == "__main__":
    unittest.main()
