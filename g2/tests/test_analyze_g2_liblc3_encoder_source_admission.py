from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_g2_liblc3_encoder_source_admission.py"
SPEC = importlib.util.spec_from_file_location("liblc3_encoder_admission", TOOL)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Liblc3EncoderSourceAdmissionTests(unittest.TestCase):
    def test_complete_admission_reconciles_source_and_blockers(self) -> None:
        report = MODULE.run_audit()
        self.assertEqual(report["status"], "liblc3-encoder-source-admission")
        self.assertEqual(
            report["g2_0x59_source_attribution"],
            {
                "functions": 41,
                "official_opaque_bytes": 16_128,
                "high_confidence": 15,
                "medium_confidence": 9,
                "low_confidence": 17,
                "investigation_required_non_liblc3_functions": 31,
                "investigation_required_non_liblc3_bytes": 3_440,
            },
        )
        self.assertEqual(report["upstream"]["authenticated_encoder_sources"], 11)
        self.assertTrue(report["production_capable_source"])
        self.assertFalse(report["overlay_routed"])
        self.assertEqual(len(report["software_integration_blockers"]), 4)
        self.assertEqual(len(report["physical_evidence_blockers"]), 1)
        self.assertFalse(report["hardware_operations"])

    def test_provider_hash_or_exact_source_overclaim_fails_closed(self) -> None:
        admission = json.loads(MODULE.ADMISSION.read_text())
        bad_hash = copy.deepcopy(admission)
        bad_hash["provider_source_sha256"] = "0" * 64
        with mock.patch.object(
            MODULE.json, "loads", side_effect=[bad_hash,
                json.loads(MODULE.PROVENANCE.read_text())]
        ):
            with self.assertRaisesRegex(MODULE.AdmissionError,
                                        "provider source hash drift"):
                MODULE.run_audit()

        bad_claim = copy.deepcopy(admission)
        bad_claim["exact_generating_checkout_proven"] = True
        with mock.patch.object(
            MODULE.json, "loads", side_effect=[bad_claim,
                json.loads(MODULE.PROVENANCE.read_text())]
        ):
            with self.assertRaisesRegex(MODULE.AdmissionError,
                                        "over-promoted to exact source"):
                MODULE.run_audit()

    def test_runtime_relocation_allowlist_fails_closed(self) -> None:
        admission = json.loads(MODULE.ADMISSION.read_text())
        admission["allowed_external_runtime_relocations"].append("mystery")
        with mock.patch.object(
            MODULE.json, "loads", side_effect=[admission,
                json.loads(MODULE.PROVENANCE.read_text())]
        ):
            with self.assertRaisesRegex(MODULE.AdmissionError,
                                        "external-runtime seam drift"):
                MODULE.run_audit()


if __name__ == "__main__":
    unittest.main()
