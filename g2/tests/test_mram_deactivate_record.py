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
SOURCE = COMPONENT_ROOT / "mram_deactivate_record.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mram_deactivate_record_host.c"
)


class MramDeactivateRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_deactivate_record.dylib"
            if sys.platform == "darwin"
            else "mram_deactivate_record.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_deactivate_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.deactivate = cls.loaded.open_cfw_mram_deactivate_record
        cls.deactivate.argtypes = [ctypes.c_void_p]
        cls.deactivate.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.loaded, name)

    def test_clears_both_flags_then_updates_and_verifies_same_record(
        self,
    ) -> None:
        self.reset()
        record = (ctypes.c_ubyte * 200)()
        record[0x2F] = 0xA5
        record[0x30] = 0x5A
        self.word(
            "open_cfw_test_mram_deactivate_update_result"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_deactivate_verify_result"
        ).value = 0x12345678

        result = self.deactivate(record)

        self.assertEqual(result, 0x12345678)
        order = (ctypes.c_uint * 4).in_dll(
            self.loaded,
            "open_cfw_test_mram_deactivate_order",
        )
        self.assertEqual((record[0x2F], record[0x30]), (0, 0))
        self.assertEqual(
            list(order)[:self.word(
                "open_cfw_test_mram_deactivate_order_count"
            ).value],
            [1, 2],
        )
        self.assertEqual(
            (
                self.pointer(
                    "open_cfw_test_mram_deactivate_update_record"
                ).value,
                self.pointer(
                    "open_cfw_test_mram_deactivate_verify_record"
                ).value,
            ),
            (ctypes.addressof(record), ctypes.addressof(record)),
        )
        self.assertEqual(
            (
                self.word(
                    "open_cfw_test_mram_deactivate_update_flags"
                ).value,
                self.word(
                    "open_cfw_test_mram_deactivate_verify_flags"
                ).value,
            ),
            (0, 0),
        )

    def test_source_and_fixture_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0a1f95e1679740243791520e605a87846731dc5c2a2afe033e308a4bdb5bf2d0",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "96404b4c6ec049bf9419534e9dad9fbeb40b4086b6cc9875ca8bd8a523278555",
        )


if __name__ == "__main__":
    unittest.main()
