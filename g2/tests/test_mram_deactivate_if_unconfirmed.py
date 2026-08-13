from __future__ import annotations

import os

import ctypes
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "mram_deactivate_if_unconfirmed.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_deactivate_if_unconfirmed_host.c"
)


class MramDeactivateIfUnconfirmedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_deactivate_if_unconfirmed.dylib"
            if sys.platform == "darwin"
            else "mram_deactivate_if_unconfirmed.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = (
            cls.loaded.open_cfw_test_mram_deactivate_if_reset
        )
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.execute = (
            cls.loaded.open_cfw_mram_deactivate_if_unconfirmed
        )
        cls.execute.argtypes = [ctypes.c_void_p]
        cls.execute.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.loaded, name)

    def test_zero_confirmation_flag_deactivates_same_record(self) -> None:
        self.reset()
        record = (ctypes.c_ubyte * 200)()
        record[0x30] = 0
        self.word(
            "open_cfw_test_mram_deactivate_if_result"
        ).value = 0xDEADBEEF

        self.execute(record)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_deactivate_if_calls"
            ).value,
            1,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_deactivate_if_record"
            ).value,
            ctypes.addressof(record),
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_deactivate_if_flag"
            ).value,
            0,
        )

    def test_every_nonzero_confirmation_flag_suppresses_deactivation(
        self,
    ) -> None:
        for flag in (1, 2, 0x80, 0xFF):
            with self.subTest(flag=flag):
                self.reset()
                record = (ctypes.c_ubyte * 200)()
                record[0x30] = flag

                self.execute(record)

                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_deactivate_if_calls"
                    ).value,
                    0,
                )
                self.assertEqual(record[0x30], flag)

    def test_source_and_fixture_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "f2380679535b946e50a6d0006563d777e9240417fcb5c28ac451c7e52db3bda4",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "a56942ad97927374567f0a150f443b7b4f9d7d680e2035f99ae4dc16b9991efa",
        )


if __name__ == "__main__":
    unittest.main()
