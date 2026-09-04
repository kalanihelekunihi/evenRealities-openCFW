#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeThreadNotificationTests(unittest.TestCase):
    def test_queue_events_lifecycle_and_fail_stop_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "thread-notification-host"
            subprocess.run([
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                str(ROOT / "tests/fixtures/thread_notification_host.c"),
                "-o", str(binary),
            ], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
