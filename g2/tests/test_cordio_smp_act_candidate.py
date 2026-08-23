#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_act.c"
FIXTURE = ROOT / "tests/fixtures/cordio_smp_act_host.c"
HEADER = ROOT / "tests/fixtures/cordio_smp_act_host.h"


class CordioSmpActCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        output = Path(cls.temp.name) / "libsmp_act.so"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
                str(SOURCE), str(FIXTURE), "-o", str(output),
            ],
            check=True,
        )
        cls.lib = ctypes.CDLL(str(output))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def check(self, name: str) -> None:
        function = getattr(self.lib, name)
        function.restype = ctypes.c_int
        self.assertEqual(function(), 0)

    def test_timer_and_cleanup(self) -> None:
        self.check("open_cfw_test_smp_act_timer_cleanup_contract")

    def test_failure_and_security_timeout(self) -> None:
        self.check("open_cfw_test_smp_act_failure_contract")

    def test_pairing_and_authentication(self) -> None:
        self.check("open_cfw_test_smp_act_pairing_auth_contract")

    def test_legacy_confirm_path(self) -> None:
        self.check("open_cfw_test_smp_act_confirm_contract")

    def test_key_distribution(self) -> None:
        self.check("open_cfw_test_smp_act_key_contract")

    def test_attempts_and_completion(self) -> None:
        self.check("open_cfw_test_smp_act_attempts_execute_contract")


if __name__ == "__main__":
    unittest.main()
