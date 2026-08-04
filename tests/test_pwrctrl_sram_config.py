from __future__ import annotations

import os

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "pwrctrl_sram_config.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_sram_config_host.c"


class PwrctrlSramConfigTests(unittest.TestCase):
    READ = 1
    WRITE = 2
    SPOT = 3
    STATUS_CHECK = 4

    ENABLE = 0x40021024
    STATUS = 0x40021028
    RETENTION = 0x4002102C
    OVERRIDE = 0x40021040

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_sram_config.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_sram_config.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_sram_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.configure = cls.loaded.open_cfw_pwrctrl_sram_config
        cls.configure.argtypes = [ctypes.c_void_p]
        cls.configure.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, f"open_cfw_test_sram_{name}")

    @classmethod
    def word_array(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_sram_{name}",
        )

    @staticmethod
    def config(*values: int) -> ctypes.Array:
        return (ctypes.c_ubyte * 5)(*values)

    def trace(self) -> list[tuple[int, int, int]]:
        count = min(self.word("trace_count").value, 128)
        events = self.word_array("trace_event", 128)
        addresses = self.word_array("trace_address", 128)
        values = self.word_array("trace_value", 128)
        return [
            (events[index], addresses[index], values[index])
            for index in range(count)
        ]

    def test_unchanged_bank_count_skips_power_transition(self) -> None:
        self.word("power_status").value = 0xABCD0003
        self.word("power_enable").value = 0x12340003
        self.word("retention").value = 0xFFFF8000
        self.word("override").value = 0xFFFFFFFF
        config = self.config(3, 1, 2, 4, 7)

        self.assertEqual(self.configure(config), 0)

        self.assertEqual(self.word("power_enable").value, 0x12340003)
        self.assertEqual(self.word("status_check_calls").value, 0)
        self.assertEqual(self.word("spot_calls").value, 0)
        self.assertEqual(
            self.word("retention").value,
            (0xFFFF8000 & ~0x7E38) | (1 << 3) | (2 << 9) | (4 << 12),
        )
        self.assertEqual(self.word("override").value, 0xFFFFC0FF)

    def test_growth_notifies_before_power_write_and_ignores_spot_error(
        self,
    ) -> None:
        self.word("power_status").value = 0xA0000001
        self.word("power_enable").value = 0xB0000041
        self.word("spot_result").value = 0xDEADBEEF
        config = self.config(3, 0, 0, 0, 0)

        self.assertEqual(self.configure(config), 0)

        self.assertEqual(self.word("power_enable").value, 0xB0000043)
        self.assertEqual(self.word("power_status").value, 0xA0000003)
        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word_array("spot_stimulus", 4)[0], 6)
        self.assertEqual(self.word_array("spot_enabled", 4)[0], 1)
        self.assertEqual(self.word_array("spot_is_null", 4)[0], 0)
        self.assertEqual(self.word_array("spot_value", 4)[0], 3)
        self.assertEqual(
            self.trace()[:6],
            [
                (self.READ, self.STATUS, 0xA0000001),
                (self.SPOT, 6, 1),
                (self.READ, self.ENABLE, 0xB0000041),
                (self.WRITE, self.ENABLE, 0xB0000043),
                (self.READ, self.ENABLE, 0xB0000043),
                (self.STATUS_CHECK, self.STATUS, 0xB0000043),
            ],
        )

    def test_shrink_notifies_only_after_successful_verification(self) -> None:
        self.word("power_status").value = 7
        self.word("power_enable").value = 0xFFFFFFF7
        self.word("spot_result").value = 9
        config = self.config(1, 0, 0, 0, 7)

        self.assertEqual(self.configure(config), 0)

        self.assertEqual(self.word("power_enable").value, 0xFFFFFFF1)
        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word_array("spot_enabled", 4)[0], 0)
        self.assertEqual(self.word_array("spot_is_null", 4)[0], 1)
        events = [event for event, _, _ in self.trace()]
        self.assertGreater(events.index(self.SPOT), events.index(self.STATUS_CHECK))

    def test_status_check_arguments_and_error_propagation_are_exact(
        self,
    ) -> None:
        self.word("power_status").value = 0
        self.word("power_enable").value = 0xCAFEBAF8
        self.word("status_check_result").value = 0x12345678
        config = self.config(2, 7, 7, 7, 0)

        self.assertEqual(self.configure(config), 0x12345678)

        self.assertEqual(self.word("status_check_calls").value, 1)
        self.assertEqual(self.word("status_check_wait").value, 5)
        self.assertEqual(self.word("status_check_address").value, self.STATUS)
        self.assertEqual(self.word("status_check_mask").value, 7)
        self.assertEqual(self.word("status_check_expected").value, 0xCAFEBAFA)
        self.assertEqual(self.word("status_check_equal").value, 1)
        self.assertEqual(self.word("retention").value, 0)
        self.assertEqual(self.word("override").value, 0)

    def test_hardware_mismatch_returns_failure_before_shrink_spot(self) -> None:
        self.word("power_status").value = 7
        self.word("power_enable").value = 7
        self.word("status_check_applies_expected").value = 0
        config = self.config(1, 1, 1, 1, 1)

        self.assertEqual(self.configure(config), 1)

        self.assertEqual(self.word("spot_calls").value, 0)
        self.assertEqual(self.word("retention").value, 0)
        self.assertEqual(self.word("override").value, 0)

    def test_active_and_retention_fields_preserve_unrelated_bits(self) -> None:
        self.word("power_status").value = 3
        self.word("retention").value = 0xA5A58005
        self.word("override").value = 0x5A5A7FFF

        expected_low = {0: 7, 1: 6, 3: 4, 7: 0, 2: 5}
        for retain, low in expected_low.items():
            with self.subTest(retain=retain):
                self.word("retention").value = 0xA5A58005
                self.word("override").value = 0x5A5A7FFF
                config = self.config(3, 0xF9, 0xFA, 0xFC, retain)

                self.assertEqual(self.configure(config), 0)

                expected = (
                    (0xA5A58005 & ~0x7E3F)
                    | (1 << 3)
                    | (2 << 9)
                    | (4 << 12)
                    | low
                )
                self.assertEqual(self.word("retention").value, expected)
                self.assertEqual(self.word("override").value, 0x5A5A40FF)

    def test_high_target_bits_affect_comparison_but_not_enable_field(self) -> None:
        self.word("power_status").value = 7
        self.word("power_enable").value = 0x12345670
        config = self.config(0x83, 0, 0, 0, 7)

        self.assertEqual(self.configure(config), 0)

        self.assertEqual(self.word("power_enable").value, 0x12345673)
        self.assertEqual(self.word_array("spot_value", 4)[0], 0x83)
        self.assertEqual(self.word_array("spot_enabled", 4)[0], 1)

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x47F46A)

        for _ in range(1000):
            self.reset_fixture()
            values = [generator.randrange(256) for _ in range(5)]
            power_enable = generator.getrandbits(32)
            power_status = generator.getrandbits(32)
            retention = generator.getrandbits(32)
            override = generator.getrandbits(32)
            status_result = generator.randrange(5)
            apply_expected = generator.randrange(2)
            self.word("power_enable").value = power_enable
            self.word("power_status").value = power_status
            self.word("retention").value = retention
            self.word("override").value = override
            self.word("status_check_result").value = status_result
            self.word("status_check_applies_expected").value = apply_expected
            config = self.config(*values)

            result = self.configure(config)
            current = power_status & 7
            target = values[0]

            if target != current:
                expected_enable = (power_enable & ~7) | (target & 7)
                self.assertEqual(self.word("power_enable").value, expected_enable)
                if status_result != 0:
                    self.assertEqual(result, status_result)
                    self.assertEqual(self.word("retention").value, retention)
                    continue
                observed = (
                    (power_status & ~7) | (expected_enable & 7)
                    if apply_expected
                    else power_status
                )
                if (observed & 7) != (expected_enable & 7):
                    self.assertEqual(result, 1)
                    self.assertEqual(self.word("retention").value, retention)
                    continue

            self.assertEqual(result, 0)
            expected_retention = retention
            expected_retention = (
                expected_retention & ~0x38
            ) | ((values[1] & 7) << 3)
            expected_retention = (
                expected_retention & ~0xE00
            ) | ((values[2] & 7) << 9)
            expected_retention = (
                expected_retention & ~0x7000
            ) | ((values[3] & 7) << 12)
            retain_bits = {0: 7, 1: 6, 3: 4, 7: 0}
            if values[4] in retain_bits:
                expected_retention = (
                    expected_retention & ~7
                ) | retain_bits[values[4]]
            self.assertEqual(
                self.word("retention").value,
                expected_retention,
            )
            self.assertEqual(
                self.word("override").value,
                override & ~0x3F00,
            )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "34dfb5c2f55bb5ad6c740eda303334707116eead34e8a8c858275d2243d01d64",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "ee220dbfc091917eaa08c1fe34fb66ca7cb5a080bc4240aa772b8257aba85ca4",
        )


if __name__ == "__main__":
    unittest.main()
