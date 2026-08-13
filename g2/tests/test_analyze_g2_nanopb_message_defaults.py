from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_nanopb_message_defaults as audit  # noqa: E402


class NanopbMessageDefaultsAuditTests(unittest.TestCase):
    def test_authenticated_boundary_and_dependency_closure(self) -> None:
        report = audit.analyze()
        self.assertEqual(report["stock"]["size"], 166)
        self.assertEqual(report["stock"]["sha256"], audit.STOCK_SHA256)
        self.assertEqual(len(report["ingress"]["direct"]["bl"]), 4)
        self.assertFalse(report["ingress"]["interior"])
        self.assertFalse(report["ingress"]["stored_patterns"])
        self.assertEqual(len(report["outgoing"]), 7)
        self.assertEqual(
            [item["function"] for item in report["outgoing"]],
            [item[3] for item in audit.EXPECTED_CALLS],
        )
        self.assertEqual(report["decision"]["source_owned_call_sites"], 4)
        self.assertEqual(report["decision"]["fixed_stock_call_sites"], 3)
        self.assertEqual(report["decision"]["fixed_stock_helper_families"], 3)
        self.assertTrue(report["decision"]["production_integrated"])
        self.assertEqual(report["decision"]["source_recreation_percent"], 100)
        self.assertEqual(report["decision"]["production_fixed_stock_call_sites"], 1)
        self.assertTrue(report["decision"]["production_candidate"])

    def test_mutated_stock_body_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        blob[audit.START - audit.shared.LOAD_BASE + 8] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.bin"
            path.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(path)

    def test_mutated_caller_context_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        address = audit.EXPECTED_CALLERS[0][0]
        blob[address - audit.shared.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.bin"
            path.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(path)


if __name__ == "__main__":
    unittest.main()
