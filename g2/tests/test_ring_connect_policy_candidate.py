import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/ring_connect_policy.c"
FIXTURE = ROOT / "tests/fixtures/ring_connect_policy_host.c"
HEADER = ROOT / "tests/fixtures/ring_connect_policy_host.h"


class State(ctypes.Structure):
    _fields_ = [
        ("mode", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
        ("started_at", ctypes.c_uint32),
        ("processed", ctypes.c_uint8),
    ]


class RingConnectPolicyCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "ring-connect-policy.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.output),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.output))
        cls.lib.open_cfw_ring_policy_on_dominant_hand.restype = ctypes.c_uint32
        cls.lib.open_cfw_ring_policy_should_block_connect_info.restype = ctypes.c_uint32
        cls.state = State.in_dll(cls.lib, "host_ring_policy_state")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        ctypes.memset(ctypes.addressof(self.state), 0, ctypes.sizeof(self.state))
        for name in (
            "host_ring_policy_tick", "host_ring_policy_throttle_tick",
            "host_ring_policy_owner", "host_ring_policy_notify_value",
            "host_ring_policy_notify_count", "host_ring_policy_remove_count",
            "host_ring_policy_push_count", "host_ring_policy_delay",
            "host_ring_policy_argument", "host_ring_policy_last_removed",
            "host_ring_policy_last_pushed",
        ):
            value = ctypes.c_uint32.in_dll(self.lib, name)
            value.value = 0
        ctypes.c_uint8.in_dll(self.lib, "host_ring_policy_pending").value = 0

    def tick(self, value):
        ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_tick").value = value

    def test_state_windows_and_dominant_hand_decisions(self):
        self.tick(100)
        self.assertEqual(self.lib.open_cfw_ring_policy_on_dominant_hand(1, 2), 0)
        self.assertEqual((self.state.mode, self.state.started_at), (1, 100))
        self.assertEqual(self.lib.open_cfw_ring_policy_on_dominant_hand(1, 2), 2)
        self.tick(20100)
        self.assertEqual(self.lib.open_cfw_ring_policy_get_state(), 0)
        self.assertEqual(self.lib.open_cfw_ring_policy_on_dominant_hand(2, 2), 1)
        self.assertEqual(self.state.mode, 2)
        self.tick(23100)
        self.assertEqual(self.lib.open_cfw_ring_policy_get_state(), 0)

    def test_connect_info_throttle_matches_switch_and_global_windows(self):
        self.tick(500)
        self.lib.open_cfw_ring_policy_enter_state(1)
        self.assertEqual(self.lib.open_cfw_ring_policy_should_block_connect_info(1), 0)
        self.lib.open_cfw_ring_policy_mark_connect_info_processed(1)
        self.assertEqual(self.state.processed, 1)
        self.assertEqual(self.lib.open_cfw_ring_policy_should_block_connect_info(1), 1)
        self.lib.open_cfw_ring_policy_enter_state(0)
        self.assertEqual(self.lib.open_cfw_ring_policy_should_block_connect_info(1), 1)
        self.tick(20500)
        self.assertEqual(self.lib.open_cfw_ring_policy_should_block_connect_info(1), 0)
        self.assertEqual(self.lib.open_cfw_ring_policy_should_block_connect_info(0), 0)

    def test_timeout_scheduling_is_idempotent_and_failure_is_bounded(self):
        self.lib.open_cfw_ring_policy_schedule_connect_timeout()
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_remove_count").value, 1)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_push_count").value, 1)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_delay").value, 20000)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_argument").value, 0x5A)
        self.lib.open_cfw_ring_policy_schedule_reconnect_timeout()
        self.lib.open_cfw_ring_policy_schedule_reconnect_timeout()
        self.assertEqual(ctypes.c_uint8.in_dll(self.lib, "host_ring_policy_pending").value, 1)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_push_count").value, 2)
        self.lib.open_cfw_ring_policy_reconnect_timeout_fire(None)
        self.assertEqual(ctypes.c_uint8.in_dll(self.lib, "host_ring_policy_pending").value, 0)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_notify_value").value, 0x5A)

    def test_success_owner_gate_cancel_and_reset_scopes(self):
        ctypes.c_uint8.in_dll(self.lib, "host_ring_policy_pending").value = 1
        ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_owner").value = 0
        self.lib.open_cfw_ring_policy_notify_connect_success_soon()
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_push_count").value, 0)
        ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_owner").value = 1
        self.lib.open_cfw_ring_policy_notify_connect_success_soon()
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_delay").value, 200)
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_argument").value, 0)
        self.tick(99)
        self.lib.open_cfw_ring_policy_enter_state(1)
        ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_throttle_tick").value = 77
        ctypes.c_uint8.in_dll(self.lib, "host_ring_policy_pending").value = 1
        self.lib.open_cfw_ring_policy_reset()
        self.assertEqual((self.state.mode, self.state.started_at), (0, 0))
        self.assertEqual(ctypes.c_uint32.in_dll(self.lib, "host_ring_policy_throttle_tick").value, 0)
        self.assertEqual(ctypes.c_uint8.in_dll(self.lib, "host_ring_policy_pending").value, 0)

    def test_all_target_selectors_compile_strictly(self):
        for selector in range(1, 16):
            output = Path(self.temp.name) / f"selector-{selector}.o"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-Os", "-ffreestanding",
                "-fno-builtin", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Wall", "-Wextra", "-Werror",
                f"-DOPEN_CFW_RING_POLICY_SELECTOR={selector}",
                "-c", str(SOURCE), "-o", str(output),
            ], check=True)


if __name__ == "__main__":
    unittest.main()
