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
SOURCE = COMPONENT_ROOT / "mram_program_bytes.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mram_program_bytes_host.c"
)


class MramProgramBytesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_program_bytes.dylib"
            if sys.platform == "darwin"
            else "mram_program_bytes.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_program_bytes_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.program = cls.loaded.open_cfw_mram_program_bytes
        cls.program.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint,
        ]
        cls.program.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def address(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.loaded, name)

    def test_disables_programs_and_restores_in_stock_order(self) -> None:
        source = (ctypes.c_ubyte * 8)(*range(8))
        destination = (ctypes.c_ubyte * 8)()
        self.word(
            "open_cfw_test_mram_program_bytes_disable_result"
        ).value = 0xA5A55A5A

        self.program(destination, source, 5)

        count = self.word(
            "open_cfw_test_mram_program_bytes_order_count"
        ).value
        order = (ctypes.c_uint * 8).in_dll(
            self.loaded,
            "open_cfw_test_mram_program_bytes_order",
        )
        self.assertEqual(list(order[:count]), [1, 2, 3])
        self.assertEqual(
            self.word("open_cfw_test_mram_program_bytes_key").value,
            0x12344321,
        )
        self.assertEqual(
            self.address("open_cfw_test_mram_program_bytes_source").value,
            ctypes.addressof(source),
        )
        self.assertEqual(
            self.address(
                "open_cfw_test_mram_program_bytes_destination"
            ).value,
            ctypes.addressof(destination),
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_program_bytes_words").value,
            2,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_program_bytes_restored_primask"
            ).value,
            0xA5A55A5A,
        )

    def test_word_count_rounds_up_with_unsigned_wrap(self) -> None:
        cases = {
            0: 0,
            1: 1,
            3: 1,
            4: 1,
            5: 2,
            0xFFFFFFFC: 0x3FFFFFFF,
            0xFFFFFFFD: 0,
            0xFFFFFFFF: 0,
        }
        for size, expected in cases.items():
            with self.subTest(size=size):
                self.reset()
                self.program(None, None, size)
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_program_bytes_words"
                    ).value,
                    expected,
                )

    def test_program_result_is_ignored_and_restore_is_unconditional(
        self,
    ) -> None:
        for result in (0, 1, 0xFFFFFFFF):
            with self.subTest(result=result):
                self.reset()
                self.word(
                    "open_cfw_test_mram_program_bytes_program_result"
                ).value = result
                self.word(
                    "open_cfw_test_mram_program_bytes_disable_result"
                ).value = 1

                self.program(None, None, 16)

                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_program_bytes_program_count"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_program_bytes_restore_count"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_program_bytes_restored_primask"
                    ).value,
                    1,
                )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ad454bf74cbef1c60ee0056e048b23cffed92c3547281fde8e9d91243645af29",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "e719330de2828d03c411cca77f339bc4ab553a4657ead8c5ef1c754649b70817",
        )


if __name__ == "__main__":
    unittest.main()
