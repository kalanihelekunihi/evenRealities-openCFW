from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AnalyzeBootloaderNumericTests(unittest.TestCase):
    def test_fail_closed_audit(self) -> None:
        completed = subprocess.run(["python3", "tools/analyze_g2_bootloader_numeric.py", "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "implemented-in-source / hardware-validation-deferred-by-project-direction")
        self.assertEqual(report["software_gap_count"], 0)
        self.assertEqual(report["stock"]["function_count"], 113)
        self.assertEqual(report["stock"]["direct_caller_count"], 428)
        self.assertEqual(report["stock"]["registered_pointer_ingress_count"], 3)
        self.assertEqual(report["source"]["compiled_bytes"], 8202)
        self.assertEqual(report["source"]["relocation_count"], 187)
        self.assertEqual(
            report["provider"]["source_owned_bytes"]
            + report["provider"]["retained_official_bytes"],
            147_296,
        )
        self.assertFalse(report["hardware_block"]["physical_evidence_available"])


if __name__ == "__main__":
    unittest.main()
