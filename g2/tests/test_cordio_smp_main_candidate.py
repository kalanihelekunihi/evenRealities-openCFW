#!/usr/bin/env python3
"""Exercise the production Cordio SMP-main adapter on the host."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_main.c"
FIXTURE = ROOT / "tests/fixtures"


class CordioSmpMainCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "cordio_smp_main.so"
        subprocess.run(
            [
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-fPIC", "-shared", "-include",
                str(FIXTURE / "cordio_smp_main_host.h"),
                str(SOURCE), str(FIXTURE / "cordio_smp_main_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def check_contract(self, name: str) -> None:
        function = getattr(self.loaded, name)
        function.restype = ctypes.c_int
        self.assertEqual(function(), 0)

    def test_lookup_and_initialization(self) -> None:
        self.check_contract("open_cfw_test_smp_main_lookup_and_init")

    def test_connection_lifecycle_and_attempt_resume(self) -> None:
        self.check_contract("open_cfw_test_smp_main_connection_lifecycle")

    def test_l2cap_validation_flow_and_queueing(self) -> None:
        self.check_contract("open_cfw_test_smp_main_l2cap_and_queueing")

    def test_legacy_crypto_inputs_and_failure(self) -> None:
        self.check_contract("open_cfw_test_smp_main_legacy_crypto")

    def test_ltk_generation_and_key_accessors(self) -> None:
        self.check_contract("open_cfw_test_smp_main_keys")

    def test_messages_handler_and_stale_aes_cleanup(self) -> None:
        self.check_contract("open_cfw_test_smp_main_handler")


if __name__ == "__main__":
    unittest.main()
