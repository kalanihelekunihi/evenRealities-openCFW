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
SOURCE = COMPONENT_ROOT / "pwrctrl_mcu_switch_sequence.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_mcu_switch_sequence_host.c"
)


class PwrctrlMcuSwitchSequenceTests(unittest.TestCase):
    IRQ_DISABLE = 1
    SPOT_UPDATE = 2
    READ_MISC = 3
    WRITE_MISC = 4
    DELAY = 5
    DELAY_STATUS = 6
    READ_CLOCK = 7
    READ_PERFORMANCE = 8
    WRITE_PERFORMANCE = 9
    SPOT_POST = 10
    CURRENT_MODE_WRITE = 11
    IRQ_RESTORE = 12

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_mcu_switch_sequence.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_mcu_switch_sequence.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_mcu_switch_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.switch = cls.loaded.open_cfw_pwrctrl_mcu_switch_sequence
        cls.switch.argtypes = [ctypes.c_uint]
        cls.switch.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_mcu_switch_{name}",
        )

    @classmethod
    def signed_word(cls, name: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_mcu_switch_{name}",
        )

    def trace(self) -> list[tuple[int, int]]:
        count = self.word("trace_count").value
        event = (ctypes.c_uint * 256).in_dll(
            self.loaded,
            "open_cfw_test_mcu_switch_trace_event",
        )
        value = (ctypes.c_uint * 256).in_dll(
            self.loaded,
            "open_cfw_test_mcu_switch_trace_value",
        )
        return [(event[index], value[index]) for index in range(count)]

    def assert_primask_restored(self) -> None:
        self.assertEqual(
            self.word("restored_primask").value,
            self.word("primask").value,
        )
        self.assertEqual(self.trace()[0][0], self.IRQ_DISABLE)
        self.assertEqual(self.trace()[-1][0], self.IRQ_RESTORE)

    def test_hp_success_forces_waits_and_restores_hfrc2(self) -> None:
        self.word("misc").value = 0xA5000000
        self.word("performance").value = 0x5A5A00F1
        self.signed_word("ack_after_reads").value = 2
        self.word("primask").value = 1

        result = self.switch(2)

        self.assertEqual(result, 0)
        self.assertEqual(self.word("misc").value, 0xA5000000)
        self.assertEqual(self.word("performance").value, 0x5A5A00F2)
        self.assertEqual(self.word("current_mode").value, 2)
        self.assertEqual(self.word("hp_spot_calls").value, 1)
        self.assertEqual(self.word("lp_spot_calls").value, 0)
        self.assertEqual(self.word("post_calls").value, 1)
        self.assertEqual(self.word("delay_calls").value, 3)
        self.assertEqual(self.word("delay_total").value, 3)
        self.assertEqual(self.word("delay_status_calls").value, 1)
        self.assertEqual(self.word("delay_status_maximum").value, 15)
        self.assertEqual(
            self.word("delay_status_address").value,
            0x40004030,
        )
        self.assertEqual(self.word("delay_status_mask").value, 0x01000000)
        self.assertEqual(
            self.word("delay_status_expected").value,
            0x01000000,
        )
        self.assertEqual(self.word("ack_reads").value, 3)
        self.assert_primask_restored()

        events = [event for event, _ in self.trace()]
        self.assertEqual(
            events,
            [
                self.IRQ_DISABLE,
                self.SPOT_UPDATE,
                self.READ_MISC,
                self.WRITE_MISC,
                self.DELAY,
                self.DELAY_STATUS,
                self.READ_CLOCK,
                self.READ_PERFORMANCE,
                self.WRITE_PERFORMANCE,
                self.READ_PERFORMANCE,
                self.DELAY,
                self.READ_PERFORMANCE,
                self.DELAY,
                self.READ_PERFORMANCE,
                self.READ_MISC,
                self.WRITE_MISC,
                self.SPOT_POST,
                self.CURRENT_MODE_WRITE,
                self.IRQ_RESTORE,
            ],
        )

    def test_hp_already_forced_skips_force_wait_and_clear(self) -> None:
        self.word("misc").value = 0x12340020

        result = self.switch(0x102)

        self.assertEqual(result, 0)
        self.assertEqual(self.word("misc").value, 0x12340020)
        self.assertEqual(self.word("delay_status_calls").value, 0)
        self.assertEqual(self.word("delay_calls").value, 0)
        self.assertEqual(self.word("current_mode").value, 2)
        self.assertEqual(self.word("performance").value & 3, 2)
        self.assertEqual(
            [event for event, _ in self.trace()].count(self.WRITE_MISC),
            0,
        )
        self.assert_primask_restored()

    def test_hp_spot_rejection_has_no_register_or_post_effects(self) -> None:
        self.word("hp_spot_status").value = 9
        initial_performance = self.word("performance").value

        result = self.switch(2)

        self.assertEqual(result, 9)
        self.assertEqual(self.word("performance").value, initial_performance)
        self.assertEqual(self.word("performance_writes").value, 0)
        self.assertEqual(self.word("current_mode_writes").value, 0)
        self.assertEqual(self.word("post_calls").value, 0)
        self.assertEqual(self.word("hp_spot_calls").value, 1)
        self.assertEqual(self.word("lp_spot_calls").value, 1)
        self.assertEqual(
            [event for event, _ in self.trace()],
            [
                self.IRQ_DISABLE,
                self.SPOT_UPDATE,
                self.SPOT_UPDATE,
                self.IRQ_RESTORE,
            ],
        )
        self.assert_primask_restored()

    def test_hp_readiness_failure_reverts_force_posts_and_rolls_back(
        self,
    ) -> None:
        self.word("clock_status").value = 0
        self.word("misc").value = 0x80000000
        self.word("lp_spot_status").value = 0xDEADBEEF

        result = self.switch(2)

        self.assertEqual(result, 1)
        self.assertEqual(self.word("misc").value, 0x80000000)
        self.assertEqual(self.word("performance_writes").value, 0)
        self.assertEqual(self.word("current_mode_writes").value, 0)
        self.assertEqual(self.word("hp_spot_calls").value, 1)
        self.assertEqual(self.word("lp_spot_calls").value, 1)
        self.assertEqual(self.word("post_calls").value, 1)
        self.assertEqual(self.word("delay_status_calls").value, 1)
        self.assert_primask_restored()

    def test_hp_ack_timeout_delays_twenty_times_and_rolls_back(self) -> None:
        self.word("misc").value = 0x20
        self.signed_word("ack_after_reads").value = -1
        self.word("lp_spot_status").value = 0

        result = self.switch(2)

        self.assertEqual(result, 4)
        self.assertEqual(self.word("ack_reads").value, 20)
        self.assertEqual(self.word("delay_calls").value, 20)
        self.assertEqual(self.word("delay_total").value, 20)
        self.assertEqual(self.word("current_mode_writes").value, 0)
        self.assertEqual(self.word("hp_spot_calls").value, 1)
        self.assertEqual(self.word("lp_spot_calls").value, 1)
        self.assertEqual(self.word("post_calls").value, 1)
        self.assert_primask_restored()

    def test_lp_success_updates_cache_then_propagates_spot_result(self) -> None:
        self.word("performance").value = 0xF0F000FF
        self.signed_word("ack_after_reads").value = 3
        self.word("lp_spot_status").value = 7

        result = self.switch(1)

        self.assertEqual(result, 7)
        self.assertEqual(self.word("performance").value, 0xF0F000FD)
        self.assertEqual(self.word("ack_reads").value, 4)
        self.assertEqual(self.word("delay_calls").value, 3)
        self.assertEqual(self.word("current_mode").value, 1)
        self.assertEqual(self.word("current_mode_writes").value, 1)
        self.assertEqual(self.word("hp_spot_calls").value, 0)
        self.assertEqual(self.word("lp_spot_calls").value, 1)
        self.assertEqual(self.word("post_calls").value, 0)
        self.assert_primask_restored()

    def test_lp_timeout_preserves_current_mode_and_skips_spot(self) -> None:
        self.signed_word("ack_after_reads").value = -1

        result = self.switch(1)

        self.assertEqual(result, 4)
        self.assertEqual(self.word("ack_reads").value, 20)
        self.assertEqual(self.word("delay_calls").value, 20)
        self.assertEqual(self.word("current_mode_writes").value, 0)
        self.assertEqual(self.word("spot_calls").value, 0)
        self.assert_primask_restored()

    def test_deterministic_randomized_stock_model(self) -> None:
        generator = random.Random(0x0047EF74)
        for _ in range(1000):
            self.reset_fixture()
            requested = generator.getrandbits(32)
            mode = requested & 0xFF
            misc = generator.getrandbits(32)
            performance = generator.getrandbits(32)
            ready = bool(generator.getrandbits(1))
            ack_after = generator.randrange(-1, 23)
            hp_status = generator.getrandbits(3)
            lp_status = generator.getrandbits(3)
            primask = generator.getrandbits(1)

            self.word("misc").value = misc
            self.word("performance").value = performance
            self.word("clock_status").value = (
                0x01000000 if ready else 0
            )
            self.signed_word("ack_after_reads").value = ack_after
            self.word("hp_spot_status").value = hp_status
            self.word("lp_spot_status").value = lp_status
            self.word("primask").value = primask

            result = self.switch(requested)

            status: int
            expected_hp_calls = 0
            expected_lp_calls = 0
            expected_post_calls = 0
            expected_writes = 0
            expected_ack_reads = 0
            expected_delay_calls = 0
            expected_current_writes = 0
            expected_current = 0xFF
            expected_performance = performance

            if mode == 2:
                expected_hp_calls = 1
                status = hp_status
                if status == 0:
                    expected_post_calls = 1
                    if ready:
                        expected_writes = 1
                        expected_performance = (
                            performance & ~3
                        ) | (mode & 3)
                        if 0 <= ack_after < 20:
                            status = 0
                            expected_ack_reads = ack_after + 1
                            expected_delay_calls = ack_after
                        else:
                            status = 4
                            expected_ack_reads = 20
                            expected_delay_calls = 20
                    else:
                        status = 1
                if status == 0:
                    expected_current = mode
                    expected_current_writes = 1
                else:
                    expected_lp_calls = 1
            else:
                expected_writes = 1
                expected_performance = (
                    performance & ~3
                ) | (mode & 3)
                if 0 <= ack_after < 20:
                    expected_ack_reads = ack_after + 1
                    expected_delay_calls = ack_after
                    expected_current = mode
                    expected_current_writes = 1
                    expected_lp_calls = 1
                    status = lp_status
                else:
                    expected_ack_reads = 20
                    expected_delay_calls = 20
                    status = 4

            if mode == 2 and hp_status == 0 and (misc & 0x20) == 0:
                expected_delay_calls += 1

            self.assertEqual(result, status)
            self.assertEqual(
                self.word("hp_spot_calls").value,
                expected_hp_calls,
            )
            self.assertEqual(
                self.word("lp_spot_calls").value,
                expected_lp_calls,
            )
            self.assertEqual(
                self.word("post_calls").value,
                expected_post_calls,
            )
            self.assertEqual(
                self.word("performance_writes").value,
                expected_writes,
            )
            self.assertEqual(
                self.word("ack_reads").value,
                expected_ack_reads,
            )
            self.assertEqual(
                self.word("delay_calls").value,
                expected_delay_calls,
            )
            self.assertEqual(
                self.word("performance").value,
                expected_performance,
            )
            self.assertEqual(
                self.word("current_mode_writes").value,
                expected_current_writes,
            )
            self.assertEqual(
                self.word("current_mode").value,
                expected_current,
            )
            self.assertEqual(self.word("misc").value, misc)
            self.assertEqual(self.word("restored_primask").value, primask)

    def test_source_and_fixture_are_pinned(self) -> None:
        expected = {
            SOURCE: "f875967a29219eb366a28d4fe9d7cac3464ffa71678105db5b2a07fb2fcb8b24",
            FIXTURE: "56f7fa49057b0bb932d2935466b8de8c58ef144650d01354901ace7f342b3670",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                digest,
            )


if __name__ == "__main__":
    unittest.main()
