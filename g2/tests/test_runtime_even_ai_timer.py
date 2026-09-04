#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeEvenAiTimerTests(unittest.TestCase):
    def test_tick_wrap_role_and_timeout_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "even-ai-timer-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/even_ai_timer_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
