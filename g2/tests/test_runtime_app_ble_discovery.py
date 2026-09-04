from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/app_ble_discovery.c"
FIXTURES = ROOT / "tests/fixtures"


class RuntimeAppBleDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"app_ble_discovery{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURES / "app_ble_discovery_host.h"),
            str(SOURCE), str(FIXTURES / "app_ble_discovery_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_app_start_service_discovery.argtypes = [ctypes.c_uint8]
        cls.loaded.open_cfw_app_ble_server_disc_callback.argtypes = [
            ctypes.c_uint8, ctypes.c_uint8,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_discovery_reset()

    def u8(self, name: str, size: int):
        return (ctypes.c_uint8 * size).in_dll(self.loaded, name)

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def events(self):
        count = self.uint("open_cfw_test_discovery_event_count")
        values = (ctypes.c_uint * 32).in_dll(
            self.loaded, "open_cfw_test_discovery_events"
        )
        return list(values)[:count]

    def arguments(self):
        values = (ctypes.c_size_t * (32 * 6)).in_dll(
            self.loaded, "open_cfw_test_discovery_arguments"
        )
        return [list(values[index * 6:(index + 1) * 6]) for index in range(32)]

    def set_role(self, role: int) -> None:
        ctypes.c_uint8.in_dll(
            self.loaded, "open_cfw_test_discovery_role_value"
        ).value = role

    def callback(self, state: int, connection_id: int = 3) -> None:
        self.loaded.open_cfw_app_ble_server_disc_callback(connection_id, state)

    def test_start_resets_record_and_posts_exact_product_message(self) -> None:
        self.loaded.open_cfw_app_start_service_discovery(0x123)
        self.assertEqual(self.events(), [1, 2, 3, 4, 5, 6])
        args = self.arguments()
        self.assertNotEqual(args[0][0], 0)
        self.assertEqual(args[1][0], 0x23)
        self.assertEqual(args[4][0], 12)
        self.assertEqual(args[5][0], 9)
        message = self.u8("open_cfw_test_discovery_message", 12)
        self.assertEqual(list(message[:3]), [0x23, 0, 0xA5])

    def test_start_handles_missing_record_and_allocation_failure(self) -> None:
        ctypes.c_uint8.in_dll(
            self.loaded, "open_cfw_test_discovery_record_present"
        ).value = 0
        ctypes.c_uint8.in_dll(
            self.loaded, "open_cfw_test_discovery_allocate_success"
        ).value = 0
        self.loaded.open_cfw_app_start_service_discovery(7)
        self.assertEqual(self.events(), [1, 2, 5])

    def test_initialization_is_role_aware_and_resets_attempt(self) -> None:
        context = self.u8("open_cfw_test_discovery_context", 128)
        context[0x57] = 9
        self.callback(0)
        self.assertEqual(context[0x57], 0)
        self.assertEqual(self.events(), [7, 8])
        self.assertEqual(self.arguments()[1][1:], [5, ctypes.addressof(context), 0, 0, 0])
        self.loaded.open_cfw_test_discovery_reset()
        self.set_role(1)
        context = self.u8("open_cfw_test_discovery_context", 128)
        self.callback(0)
        self.assertEqual(self.arguments()[1][1], 8)
        self.assertEqual(self.arguments()[1][2], ctypes.addressof(context) + 0x2A)

    def test_failure_phone_ready_and_configure_states(self) -> None:
        self.callback(1, 4)
        self.assertEqual(self.events(), [9])
        self.loaded.open_cfw_test_discovery_reset()
        self.callback(2, 4)
        self.assertEqual(self.events(), [7, 10])
        self.loaded.open_cfw_test_discovery_reset()
        self.set_role(1)
        self.callback(2, 4)
        self.assertEqual(self.events(), [7])
        self.loaded.open_cfw_test_discovery_reset()
        context = self.u8("open_cfw_test_discovery_context", 128)
        context[0x57] = context[0x5A] = 8
        self.callback(3, 4)
        self.assertEqual(context[0x57], 0)
        self.assertEqual(context[0x5A], 0)
        self.assertEqual(self.events(), [7, 11])
        self.assertEqual(self.arguments()[1][1], 0x2020)

    def test_phone_phase_orders_database_hash_then_gatt(self) -> None:
        context = self.u8("open_cfw_test_discovery_context", 128)
        self.callback(4)
        self.assertEqual(context[0x57], 1)
        self.assertEqual(self.events(), [7, 14])
        self.assertEqual(self.arguments()[1][1], 0x2424)
        self.loaded.open_cfw_test_discovery_reset()
        context = self.u8("open_cfw_test_discovery_context", 128)
        context[0x57] = 1
        self.callback(4)
        self.assertEqual(context[0x57], 2)
        self.assertEqual(self.events(), [7, 12, 13])
        args = self.arguments()[2]
        self.assertEqual(args[:5], [3, 6, 2, 0x784DC0, 5])
        self.assertEqual(args[5], ctypes.addressof(context))

    def test_ring_phase_runs_optional_ancs_then_ring_service(self) -> None:
        self.set_role(1)
        context = self.u8("open_cfw_test_discovery_context", 128)
        context[0x5A] = 7
        self.callback(4)
        self.assertEqual(context[0x57], 1)
        self.assertEqual(self.events(), [7, 15])
        handles = (ctypes.c_uint16 * 5).in_dll(
            self.loaded, "open_cfw_test_discovery_ancs_handles"
        )
        self.assertEqual(self.arguments()[1][1], ctypes.addressof(handles))
        self.loaded.open_cfw_test_discovery_reset()
        self.set_role(1)
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_discovery_ancs_result"
        ).value = 0
        context = self.u8("open_cfw_test_discovery_context", 128)
        context[0x5A] = 7
        self.callback(4)
        self.assertEqual(context[0x57], 2)
        self.assertEqual(context[0x5A], 7)
        self.assertEqual(self.events(), [7, 15, 12, 13])
        args = self.arguments()[3]
        self.assertEqual(args[:5], [3, 6, 4, 0x75DAF0, 8])
        self.assertEqual(args[5], ctypes.addressof(context) + 0x2A)
        self.loaded.open_cfw_test_discovery_reset()
        self.set_role(1)
        context = self.u8("open_cfw_test_discovery_context", 128)
        context[0x57] = 1
        context[0x5A] = 9
        self.callback(4)
        self.assertEqual(context[0x5A], 0)
        self.assertEqual(self.events(), [7, 12, 13])

    def test_phase_failure_service_and_completion_paths(self) -> None:
        context = self.u8("open_cfw_test_discovery_context", 128)
        context[0x57] = 4
        self.callback(5)
        self.assertEqual(context[0x57], 6)
        self.assertEqual(self.events(), [])
        self.callback(6)
        self.assertEqual(self.events(), [7, 13])
        self.assertEqual(self.arguments()[1][:5], [3, 6, 2, 0x784DC0, 5])
        self.loaded.open_cfw_test_discovery_reset()
        self.callback(7)
        self.assertEqual(self.events(), [])
        self.callback(8)
        self.assertEqual(self.events(), [12, 7, 16])
        self.assertEqual(self.arguments()[0][:2], [3, 8])
        self.assertEqual(self.arguments()[2][0], 4)

    def test_ring_completion_reports_five_handles(self) -> None:
        self.set_role(1)
        reported = (ctypes.c_uint16 * 5).in_dll(
            self.loaded, "open_cfw_test_discovery_reported_handles"
        )
        self.callback(8)
        self.assertEqual(self.events(), [12, 7, 17])
        self.assertEqual(list(reported), [1, 2, 3, 4, 5])

    def test_target_compiles_with_two_global_text_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "app_ble_discovery.o"
            subprocess.run([
                "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(target),
            ], check=True, cwd=ROOT)
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            observed = {
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, {
                "open_cfw_app_start_service_discovery",
                "open_cfw_app_ble_server_disc_callback",
            })


if __name__ == "__main__":
    unittest.main()
