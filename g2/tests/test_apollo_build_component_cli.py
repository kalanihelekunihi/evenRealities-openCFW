from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "build_component.py"
)


class ApolloBuildComponentCliTests(unittest.TestCase):
    def test_help_honors_cli_without_starting_a_build(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "must-not-exist"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--output-dir",
                    str(output),
                    "--help",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--toolchain-profile", completed.stdout)
        self.assertIn("--record-profile", completed.stdout)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
