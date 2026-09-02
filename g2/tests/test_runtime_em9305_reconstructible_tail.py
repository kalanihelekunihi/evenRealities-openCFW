#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/em9305/source_overlay/runtime_reconstructible_tail.c"
FIXTURE = ROOT / "tests/fixtures/em9305_reconstructible_tail_host.c"


class EM9305ReconstructibleTailRuntimeTests(unittest.TestCase):
    def test_host_semantics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-em9305-tail-") as directory:
            executable = Path(directory) / "em9305-tail"
            subprocess.run(
                [
                    "/usr/bin/clang",
                    "-std=c11",
                    "-O2",
                    "-DOPEN_CFW_EM9305_HOST_TEST",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    str(SOURCE),
                    str(FIXTURE),
                    "-o",
                    str(executable),
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([str(executable)], cwd=ROOT, check=True)

    def test_runtime_is_reviewable_c_without_raw_target_encodings(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("OPEN_CFW_EM9305_HOST_TEST", source)
        self.assertIn("UINT32_C(1) << 23", source)
        self.assertIn("base[23]", source)
        self.assertNotIn(".byte", source)
        self.assertNotIn(".short", source)


if __name__ == "__main__":
    unittest.main()
