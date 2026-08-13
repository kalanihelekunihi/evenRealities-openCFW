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
SOURCE = COMPONENT_ROOT / "pwrctrl_info1_populate.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_info1_populate_host.c"
)

EXPECTED_CALLS = [
    (5, 0x480, 2),
    (1, 0x204, 1),
    (1, 0x206, 1),
    (3, 0x208, 8),
    (1, 0x210, 1),
    (1, 0x240, 3),
    (1, 0x24A, 2),
    (1, 0x250, 12),
    (1, 0x245, 1),
]

DESTINATIONS = [
    (1, 2),
    (3,),
    (4,),
    tuple(range(5, 13)),
    (13,),
    (14, 15, 16),
    (18, 19),
    tuple(range(20, 32)),
    (17,),
]


class PwrctrlInfo1PopulateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_info1_populate.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_info1_populate.so"
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
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset_fixture = cls.loaded.open_cfw_test_info1_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.populate = cls.loaded.open_cfw_pwrctrl_info1_populate
        cls.populate.argtypes = []
        cls.populate.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_info1_{name}",
        )

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_info1_{name}",
        )

    def assert_call_abi(self, count: int) -> None:
        observed = list(
            zip(
                self.words("call_info_space", 9)[:count],
                self.words("call_word_offset", 9)[:count],
                self.words("call_word_count", 9)[:count],
            )
        )
        self.assertEqual(observed, EXPECTED_CALLS[:count])

    def expected_success_registers(self) -> list[int]:
        expected = [0xCC000000 | index for index in range(32)]
        for call, destinations in enumerate(DESTINATIONS):
            for value_index, destination in enumerate(destinations):
                expected[destination] = (
                    0xA0000000 | (call << 16) | value_index
                )
        expected[0] = 0x1F01600D
        return expected

    def test_invalid_shadow_short_circuits_without_power_or_info1_read(
        self,
    ) -> None:
        before = list(self.words("registers", 32))
        self.word("shadow_valid").value = 0

        self.assertEqual(self.populate(), 7)
        self.assertEqual(self.word("shadow_reads").value, 1)
        self.assertEqual(self.word("power_reads").value, 0)
        self.assertEqual(self.word("call_count").value, 0)
        self.assertEqual(list(self.words("registers", 32)), before)

    def test_powered_off_otp_rejects_without_info1_read(self) -> None:
        before = list(self.words("registers", 32))
        self.word("power_status").value = 0

        self.assertEqual(self.populate(), 7)
        self.assertEqual(self.word("shadow_reads").value, 1)
        self.assertEqual(self.word("power_reads").value, 1)
        self.assertEqual(self.word("call_count").value, 0)
        self.assertEqual(list(self.words("registers", 32)), before)

    def test_preconditions_use_only_the_reviewed_status_bits(self) -> None:
        self.word("shadow_valid").value = 0xFFFFFFF7
        self.word("power_status").value = 0xFFFFFFFF
        self.assertEqual(self.populate(), 7)

        self.reset_fixture()
        self.word("shadow_valid").value = 0xFFFFFFFF
        self.word("power_status").value = 0xF7FFFFFF
        self.assertEqual(self.populate(), 7)

        self.reset_fixture()
        self.word("shadow_valid").value = 0xA5A5A5AD
        self.word("power_status").value = 0x5A5A5A5A
        self.assertEqual(self.populate(), 0)

    def test_success_uses_stock_call_order_and_register_mapping(self) -> None:
        self.assertEqual(self.populate(), 0)
        self.assertEqual(self.word("shadow_reads").value, 1)
        self.assertEqual(self.word("power_reads").value, 1)
        self.assertEqual(self.word("call_count").value, 9)
        self.assert_call_abi(9)
        self.assertEqual(
            list(self.words("registers", 32)),
            self.expected_success_registers(),
        )

    def test_each_read_failure_returns_immediately_after_partial_commit(
        self,
    ) -> None:
        for fail_call in range(9):
            with self.subTest(fail_call=fail_call):
                self.reset_fixture()
                self.word("fail_call").value = fail_call
                self.word("fail_status").value = 0x80 + fail_call

                self.assertEqual(self.populate(), 0x80 + fail_call)
                self.assertEqual(
                    self.word("call_count").value,
                    fail_call + 1,
                )
                self.assert_call_abi(fail_call + 1)

                expected = [
                    0xCC000000 | index for index in range(32)
                ]
                for call in range(fail_call):
                    for value_index, destination in enumerate(
                        DESTINATIONS[call]
                    ):
                        expected[destination] = (
                            0xA0000000
                            | (call << 16)
                            | value_index
                        )
                self.assertEqual(
                    list(self.words("registers", 32)),
                    expected,
                )

    def test_valid_marker_is_preserved_on_failure_and_set_on_success(
        self,
    ) -> None:
        registers = self.words("registers", 32)
        registers[0] = 0x12345678
        self.word("fail_call").value = 8

        self.assertEqual(self.populate(), 0x55)
        self.assertEqual(registers[0], 0x12345678)

        self.reset_fixture()
        registers = self.words("registers", 32)
        registers[0] = 0
        self.assertEqual(self.populate(), 0)
        self.assertEqual(registers[0], 0x1F01600D)

    def test_sources_are_pinned(self) -> None:
        expected = {
            SOURCE:
                "1c7e30a4405aefd23c8d088e5166c4d9"
                "b4c7baad7f92a197505c8544867616a6",
            FIXTURE:
                "a9af226674561396cd6b5693cbafcc8af"
                "1049a8ea5a4a279b19c4e975a1629a2",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                digest,
            )


if __name__ == "__main__":
    unittest.main()
