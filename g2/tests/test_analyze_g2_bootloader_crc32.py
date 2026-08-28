from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AnalyzeBootloaderCrc32Tests(unittest.TestCase):
    def test_fail_closed_audit(self) -> None:
        completed = subprocess.run(["python3", "tools/analyze_g2_bootloader_crc32.py", "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "implemented-in-source / hardware-validation-deferred-by-project-direction")
        self.assertEqual(report["software_gap_count"], 0)
        self.assertEqual(report["stock"]["whole_image_callers"], 6)
        self.assertEqual(report["stock"]["table_polynomial"], "0xEDB88320")
        self.assertEqual(report["source"]["size"], 44)
        self.assertEqual(report["source"]["relocations"], 0)
        self.assertEqual(
            report["provider"]["source_owned_bytes"]
            + report["provider"]["retained_official_bytes"],
            147_296,
        )
        self.assertFalse(report["hardware_block"]["physical_evidence_available"])


if __name__ == "__main__":
    unittest.main()
