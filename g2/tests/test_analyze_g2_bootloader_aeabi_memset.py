from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AnalyzeBootloaderAeabiMemsetTests(unittest.TestCase):
    def test_fail_closed_audit(self) -> None:
        completed = subprocess.run(
            ["python3", "tools/analyze_g2_bootloader_aeabi_memset.py", "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence")
        self.assertEqual(report["software_gap_count"], 0)
        self.assertEqual(report["stock"]["whole_image_callers"], 20)
        self.assertEqual(report["source"]["size"], 12)
        self.assertEqual(report["source"]["relocations"], 0)
        self.assertEqual(
            report["provider"]["source_owned_bytes"]
            + report["provider"]["retained_official_bytes"],
            147_350,
        )
        self.assertFalse(report["hardware_block"]["physical_evidence_available"])
        self.assertEqual(
            report["hardware_block"]["required_evidence"],
            "authorized G2 hardware demonstrating boot progression through "
            "all byte-fill callers",
        )
        self.assertEqual(report["safety"]["hardware_operations"], [])


if __name__ == "__main__":
    unittest.main()
