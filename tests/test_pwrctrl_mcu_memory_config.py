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
SOURCE = COMPONENT_ROOT / "pwrctrl_mcu_memory_config.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_mcu_memory_config_host.c"
)


class PwrctrlMcuMemoryConfigTests(unittest.TestCase):
    ROM_WRITE = 1
    READ_STATUS = 2
    READ_FORCE = 3
    WRITE_FORCE = 4
    READ_ENABLE = 5
    WRITE_ENABLE = 6
    DELAY_STATUS = 7
    SPOT_UPDATE = 8
    READ_DEVICE_STATUS = 9
    READ_DEVICE_ENABLE = 10
    READ_RETENTION = 11
    WRITE_RETENTION = 12

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_mcu_memory_config.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_mcu_memory_config.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_memory_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.configure = cls.loaded.open_cfw_pwrctrl_mcu_memory_config
        cls.configure.argtypes = [ctypes.c_void_p]
        cls.configure.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_memory_{name}",
        )

    @classmethod
    def word_array(cls, name: str, count: int = 2) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_memory_{name}",
        )

    @staticmethod
    def config(
        rom: int,
        tcm: int,
        retain_tcm: int,
        nvm: int,
        keep_nvm: int,
    ) -> ctypes.Array:
        return (ctypes.c_ubyte * 5)(
            rom,
            tcm,
            retain_tcm,
            nvm,
            keep_nvm,
        )

    def trace(self) -> list[tuple[int, int]]:
        count = self.word("trace_count").value
        events = self.word_array("trace_event", 64)
        values = self.word_array("trace_value", 64)
        return [(events[index], values[index]) for index in range(count)]

    def test_already_selected_updates_only_cache_and_retention(self) -> None:
        configuration = self.config(0, 7, 0, 3, 0)
        self.word("status").value = 0xCF
        self.word("enable").value = 0xFFFFFFFF
        self.word("retention").value = 0xA5

        result = self.configure(configuration)

        self.assertEqual(result, 0)
        self.assertEqual(self.word("current_rom_mode").value, 0)
        self.assertEqual(self.word("delay_calls").value, 0)
        self.assertEqual(self.word("spot_calls").value, 0)
        self.assertEqual(self.word("enable").value, 0xFFFFFFFF)
        self.assertEqual(self.word("retention").value, 0xA6)
        self.assertEqual(
            self.trace(),
            [
                (self.ROM_WRITE, 0),
                (self.READ_STATUS, 0xCF),
                (self.READ_STATUS, 0xCF),
                (self.READ_RETENTION, 0xA5),
                (self.WRITE_RETENTION, 0xA7),
                (self.READ_RETENTION, 0xA7),
                (self.WRITE_RETENTION, 0xA6),
            ],
        )

    def test_transition_uses_exact_disable_spot_enable_sequence(self) -> None:
        configuration = self.config(1, 3, 1, 1, 1)
        self.word("status").value = 0x08
        self.word("enable").value = 0xFFFFFFF8
        self.word("retention").value = 0xA5
        self.word("device_status").value = 1 << 27
        self.word("device_enable").value = 1 << 27

        result = self.configure(configuration)

        self.assertEqual(result, 0)
        self.assertEqual(self.word("current_rom_mode").value, 1)
        self.assertEqual(self.word("enable").value, 0x0B)
        self.assertEqual(self.word("status").value, 0x0B)
        self.assertEqual(self.word("retention").value, 0xA5)
        self.assertEqual(self.word("delay_calls").value, 2)
        self.assertEqual(list(self.word_array("delay_maximum")), [5, 5])
        self.assertEqual(
            list(self.word_array("delay_address")),
            [0x40021018, 0x40021018],
        )
        self.assertEqual(list(self.word_array("delay_mask")), [0xCF, 0xCF])
        self.assertEqual(
            list(self.word_array("delay_expected")),
            [0x08, 0x0B],
        )
        self.assertEqual(list(self.word_array("delay_wait")), [1, 1])
        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word("spot_stimulus").value, 5)
        self.assertEqual(self.word("spot_enabled").value, 1)
        self.assertEqual(self.word("spot_value").value, 0x0B)
        self.assertEqual(
            self.trace()[:10],
            [
                (self.ROM_WRITE, 1),
                (self.READ_STATUS, 0x08),
                (self.READ_STATUS, 0x08),
                (self.READ_ENABLE, 0xFFFFFFF8),
                (self.WRITE_ENABLE, 0x08),
                (self.DELAY_STATUS, 0x08),
                (self.SPOT_UPDATE, 0x0B),
                (self.WRITE_ENABLE, 0x0B),
                (self.DELAY_STATUS, 0x0B),
                (self.READ_STATUS, 0x0B),
            ],
        )
        events = [event for event, _ in self.trace()]
        self.assertEqual(events[-4:], [
            self.READ_RETENTION,
            self.WRITE_RETENTION,
            self.READ_RETENTION,
            self.WRITE_RETENTION,
        ])

    def test_nvm1_transition_forces_and_then_restores_axi_clock(
        self,
    ) -> None:
        configuration = self.config(1, 7, 0, 3, 0)
        self.word("status").value = 0x0F
        self.word("enable").value = 0x0F
        self.word("force_axi_clock").value = 0xA4

        self.assertEqual(self.configure(configuration), 0)

        self.assertEqual(self.word("force_axi_clock").value, 0xA4)
        self.assertEqual(self.word("enable").value, 0x1F)
        self.assertEqual(self.word("status").value, 0x4F)
        self.assertEqual(
            [
                item
                for item in self.trace()
                if item[0] in (
                    self.READ_FORCE,
                    self.WRITE_FORCE,
                    self.DELAY_STATUS,
                )
            ],
            [
                (self.READ_FORCE, 0xA4),
                (self.WRITE_FORCE, 0xA5),
                (self.DELAY_STATUS, 0x0F),
                (self.DELAY_STATUS, 0x4F),
                (self.READ_FORCE, 0xA5),
                (self.WRITE_FORCE, 0xA4),
            ],
        )

    def test_first_timeout_preserves_stock_forced_axi_leak(self) -> None:
        configuration = self.config(1, 7, 0, 3, 0)
        self.word("status").value = 0x08
        self.word("enable").value = 0x1F
        self.word_array("delay_result")[0] = 9

        self.assertEqual(self.configure(configuration), 9)

        self.assertEqual(self.word("current_rom_mode").value, 1)
        self.assertEqual(self.word("force_axi_clock").value, 1)
        self.assertEqual(self.word("delay_calls").value, 1)
        self.assertEqual(self.word("spot_calls").value, 0)
        self.assertNotIn(
            self.READ_RETENTION,
            [event for event, _ in self.trace()],
        )

    def test_second_timeout_clears_forced_axi_before_return(self) -> None:
        configuration = self.config(1, 7, 0, 3, 0)
        self.word("status").value = 0x08
        self.word("enable").value = 0x1F
        self.word_array("delay_result")[1] = 7

        self.assertEqual(self.configure(configuration), 7)

        self.assertEqual(self.word("force_axi_clock").value, 0)
        self.assertEqual(self.word("delay_calls").value, 2)
        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertNotIn(
            self.READ_RETENTION,
            [event for event, _ in self.trace()],
        )

    def test_spot_error_is_deliberately_ignored(self) -> None:
        configuration = self.config(1, 1, 0, 1, 0)
        self.word("status").value = 0
        self.word("enable").value = 0
        self.word("spot_result").value = 0xDEADBEEF

        self.assertEqual(self.configure(configuration), 0)
        self.assertEqual(self.word("spot_calls").value, 1)
        self.assertEqual(self.word("enable").value, 0x09)

    def test_post_transition_hardware_mismatch_returns_failure(self) -> None:
        configuration = self.config(1, 3, 0, 1, 0)
        self.word("status").value = 0x08
        self.word("enable").value = 0x08
        self.word("delay_updates_status").value = 0

        self.assertEqual(self.configure(configuration), 1)

        self.assertEqual(self.word("delay_calls").value, 2)
        self.assertEqual(self.word("retention").value, 0)
        self.assertNotIn(
            self.WRITE_RETENTION,
            [event for event, _ in self.trace()],
        )

    def test_invalid_retain_tcm_returns_five_after_nvm_retention(
        self,
    ) -> None:
        configuration = self.config(1, 0, 2, 0, 1)
        self.word("status").value = 0
        self.word("retention").value = 0xFFFFFFFF

        self.assertEqual(self.configure(configuration), 5)

        self.assertEqual(self.word("retention").value, 0xFFFFFFFD)
        self.assertEqual(
            [
                item
                for item in self.trace()
                if item[0] in (
                    self.READ_RETENTION,
                    self.WRITE_RETENTION,
                )
            ],
            [
                (self.READ_RETENTION, 0xFFFFFFFF),
                (self.WRITE_RETENTION, 0xFFFFFFFD),
            ],
        )

    def test_invalid_rom_and_nvm_are_ignored_and_tcm_is_masked(
        self,
    ) -> None:
        configuration = self.config(0xFE, 0xFF, 0, 2, 0xFF)
        self.word("status").value = 7
        self.word("retention").value = 3

        self.assertEqual(self.configure(configuration), 0)

        self.assertEqual(self.word("current_rom_mode").value, 0xFE)
        self.assertEqual(self.word("delay_calls").value, 0)
        self.assertEqual(self.word("retention").value, 0)

    def test_randomized_stock_model(self) -> None:
        randomizer = random.Random(0x47F204)

        for _ in range(1000):
            self.reset_fixture()
            values = [randomizer.randrange(0, 256) for _ in range(5)]
            configuration = self.config(*values)
            rom, tcm, retain_tcm, nvm, keep_nvm = values
            initial_status = randomizer.randrange(0, 256)
            initial_enable = randomizer.randrange(0, 256)
            initial_retention = randomizer.randrange(0, 1 << 32)
            initial_force = randomizer.randrange(0, 1 << 32)
            device_enable = randomizer.randrange(0, 2) << 27
            device_status = randomizer.randrange(0, 2) << 27
            first_result = randomizer.randrange(0, 4)
            second_result = randomizer.randrange(0, 4)
            self.word("status").value = initial_status
            self.word("enable").value = initial_enable
            self.word("retention").value = initial_retention
            self.word("force_axi_clock").value = initial_force
            self.word("device_enable").value = device_enable
            self.word("device_status").value = device_status
            self.word_array("delay_result")[0] = first_result
            self.word_array("delay_result")[1] = second_result

            desired_enable = tcm & 7
            desired_status = tcm & 7
            if rom == 0:
                desired_enable |= 0x20
                desired_status |= 0x80
            if nvm == 1:
                desired_enable |= 0x08
                desired_status |= 0x08
            elif nvm == 3:
                desired_enable |= 0x18
                desired_status |= 0x48
            forced = nvm == 3 and (initial_status & 0x48) == 0x08
            transition = desired_status != initial_status

            if transition and first_result != 0:
                expected_result = first_result
                expected_status = initial_status
                expected_enable = initial_enable & desired_enable
                expected_force = (
                    initial_force | 1
                    if forced
                    else initial_force
                )
                expected_retention = initial_retention
            elif transition and second_result != 0:
                expected_result = second_result
                expected_status = initial_status & desired_status
                expected_enable = desired_enable
                expected_force = initial_force & ~1 if forced else initial_force
                expected_retention = initial_retention
            elif transition and device_enable != device_status:
                expected_result = 1
                expected_status = desired_status
                expected_enable = desired_enable
                expected_force = initial_force & ~1 if forced else initial_force
                expected_retention = initial_retention
            else:
                expected_status = (
                    desired_status if transition else initial_status
                )
                expected_enable = (
                    desired_enable if transition else initial_enable
                )
                expected_force = (
                    initial_force & ~1 if transition and forced
                    else initial_force
                )
                expected_retention = (
                    initial_retention & ~2
                    if keep_nvm != 0
                    else initial_retention | 2
                )
                if retain_tcm == 1:
                    expected_retention |= 1
                    expected_result = 0
                elif retain_tcm == 0:
                    expected_retention &= ~1
                    expected_result = 0
                else:
                    expected_result = 5

            self.assertEqual(
                self.configure(configuration),
                expected_result,
            )
            self.assertEqual(self.word("current_rom_mode").value, rom)
            self.assertEqual(
                self.word("status").value,
                expected_status & 0xFFFFFFFF,
            )
            self.assertEqual(
                self.word("enable").value,
                expected_enable & 0xFFFFFFFF,
            )
            self.assertEqual(
                self.word("force_axi_clock").value,
                expected_force & 0xFFFFFFFF,
            )
            self.assertEqual(
                self.word("retention").value,
                expected_retention & 0xFFFFFFFF,
            )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "7943699808079a9399e1fdd511ef6653d4db8685ffd78967197340f79e16d098",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "6d54365cef4f2eb6bd8f3ef5c268b8cb9b62027f44af1ad95fd512f00e99a380",
        )


if __name__ == "__main__":
    unittest.main()
