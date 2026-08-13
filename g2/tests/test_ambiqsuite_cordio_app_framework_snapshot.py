#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "third_party/ambiqsuite-cordio-app-framework/verify_snapshot.py"


class AmbiqSuiteCordioAppFrameworkSnapshotTests(unittest.TestCase):
    def test_authenticated_snapshot(self) -> None:
        spec = importlib.util.spec_from_file_location("ambiqsuite_cordio_app_snapshot", VERIFIER)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        report = module.verify()
        self.assertEqual(report["source_files"], 9)
        self.assertEqual(report["selected_release"], "2.5.1")
        self.assertIsNone(report["historical_g2_generating_commit"])


if __name__ == "__main__":
    unittest.main()
