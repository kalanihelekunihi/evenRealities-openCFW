#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_mspi_interrupt_clear.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_mspi_interrupt_clear",
        ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load MSPI interrupt-clear analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MspiInterruptClearAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_authenticated_cross_image_boundary(self) -> None:
        result = self.analyzer.run_audit()

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["read_only"])
        self.assertTrue(result["cross_image"]["byte_identical"])
        self.assertEqual(
            result["cross_image"]["function_sha256"],
            "4b01a25a8075cf158eb59da277f8730e"
            "36c751ee01c67bae86bc172ec877bd48",
        )
        self.assertEqual(
            [item["address"] for item in result["images"]["boot"]["direct_callers"]],
            [0x0041FE1A, 0x004203CC],
        )
        self.assertEqual(
            [item["address"] for item in result["images"]["main"]["direct_callers"]],
            [
                0x0046F4FE,
                0x0046FD4A,
                0x00592672,
                0x0059CE4C,
                0x0059D0D8,
                0x005BBD62,
            ],
        )
        for image in result["images"].values():
            self.assertEqual(image["function"]["size"], 48)
            self.assertEqual(
                image["literal_evidence"]["combined_initialized_handle_word"],
                0x01BEBEBE,
            )
            self.assertEqual(
                image["literal_evidence"]["mspi_register_base"],
                0x40060000,
            )
            self.assertEqual(image["stored_entry_addresses"]["even"], [])
            self.assertEqual(image["stored_entry_addresses"]["thumb"], [])

    def test_json_cli_is_read_only_and_machine_readable(self) -> None:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["read_only"])
        self.assertEqual(
            result["upstream"]["function"],
            "am_hal_mspi_interrupt_clear",
        )
        self.assertTrue(result["reuse_assessment"]["safe_candidate"])


if __name__ == "__main__":
    unittest.main()
