#!/usr/bin/env python3
"""Exercise the production Cordio SMP database candidate on the host."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_db.c"
FIXTURE = ROOT / "tests/fixtures"


class CordioSmpDbCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "cordio_smp_db.so"
        subprocess.run(
            [
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-fPIC", "-shared", "-include",
                str(FIXTURE / "cordio_smp_db_host.h"),
                str(SOURCE), str(FIXTURE / "cordio_smp_db_host.c"),
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

    def test_init_contract(self) -> None:
        self.check_contract("open_cfw_test_smp_db_init_contract")

    def test_record_reuse_and_failure(self) -> None:
        self.check_contract("open_cfw_test_smp_db_record_reuse_and_failure")

    def test_full_database_falls_back_to_common_record(self) -> None:
        self.check_contract("open_cfw_test_smp_db_full_falls_back_to_common")

    def test_backoff_and_clamp(self) -> None:
        self.check_contract("open_cfw_test_smp_db_backoff_and_clamp")

    def test_service_and_pairing_failed(self) -> None:
        self.check_contract("open_cfw_test_smp_db_service_and_pairing_failed")


if __name__ == "__main__":
    unittest.main()
