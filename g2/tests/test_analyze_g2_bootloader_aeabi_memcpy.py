from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AnalyzeBootloaderAeabiMemcpyTests(unittest.TestCase):
    def test_fail_closed_audit(self) -> None:
        completed = subprocess.run(
            ["python3", "tools/analyze_g2_bootloader_aeabi_memcpy.py", "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "implemented-in-source / hardware-validation-blocked")
        self.assertEqual(report["software_gap_count"], 0)
        self.assertEqual(report["stock"]["whole_image_callers"], 33)
        self.assertEqual(report["source"]["size"], 16)
        self.assertEqual(report["source"]["relocations"], 0)
        self.assertEqual(report["provider"]["retained_official_bytes"], 146201)
        self.assertFalse(report["hardware_block"]["physical_evidence_available"])


if __name__ == "__main__":
    unittest.main()
