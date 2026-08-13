from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_nanopb_iterator_cluster as audit  # noqa: E402


class NanopbIteratorClusterAuditTests(unittest.TestCase):
    def test_authenticated_cluster_and_source_closure(self) -> None:
        report = audit.analyze()
        self.assertEqual(report["stock"]["size"], 948)
        self.assertEqual(report["stock"]["sha256"], audit.STOCK_SHA256)
        self.assertEqual(len(report["stock"]["segments"]), 11)
        self.assertFalse(report["topology"]["interior_bl"])
        self.assertFalse(report["topology"]["unexpected_alternate"])
        self.assertEqual(
            tuple(report["topology"]["classified_data_branch_collision"]),
            audit.CLASSIFIED_DATA_BRANCH_COLLISION,
        )
        self.assertEqual(tuple(report["topology"]["stored_pointers"]), audit.STORED_POINTERS)
        self.assertEqual(len(report["outgoing"]), 16)
        self.assertEqual(len(report["dynamic_callbacks"]), 2)
        self.assertEqual(
            report["upstream"]["exact_pb_common_release_range"],
            "0.4.4--0.4.9.1",
        )
        self.assertFalse(report["upstream"]["vendor_point_release_proven"])
        self.assertFalse(report["decision"]["production_candidate"])
        self.assertEqual(report["decision"]["source_identification_percent"], 100)
        self.assertEqual(report["decision"]["source_recreation_percent"], 100)
        self.assertEqual(report["decision"]["production_integration_percent"], 100)
        self.assertEqual(report["source_recreation"]["undefined_symbol_count"], 0)
        self.assertEqual(report["production_integration"]["relocated_leaf_count"], 9)
        self.assertEqual(report["production_integration"]["entry_patch_count"], 8)
        self.assertEqual(report["decision"]["fixed_stock_call_sites_after_recreation"], 0)

    def test_mutated_cluster_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        blob[audit.START - audit.shared.LOAD_BASE + 12] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.bin"
            path.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(path)

    def test_mutated_external_caller_fails_closed(self) -> None:
        blob = bytearray(audit.DEFAULT_IMAGE.read_bytes())
        address = audit.EXPECTED_CALLERS[0x004D_93D8][0][0]
        blob[address - audit.shared.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.bin"
            path.write_bytes(blob)
            with self.assertRaises(audit.AuditError):
                audit.analyze(path)


if __name__ == "__main__":
    unittest.main()
