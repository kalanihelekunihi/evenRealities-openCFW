from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/app_ble_peer_manager.c"
FIXTURES = ROOT / "tests/fixtures"


class RuntimeAppBlePeerManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"app_ble_peer_manager{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURES / "app_ble_peer_manager_host.h"),
            str(SOURCE), str(FIXTURES / "app_ble_peer_manager_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_app_ble_peer_manager_find_conn_id_by_addr.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
        ]
        cls.loaded.open_cfw_app_ble_peer_manager_find_conn_id_by_addr.restype = (
            ctypes.c_uint8
        )
        cls.loaded.open_cfw_app_master_sec_get_addr.restype = ctypes.c_void_p
        cls.loaded.open_cfw_app_ble_master_peer_mgr_unpair_dev.argtypes = [
            ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8),
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_peer_reset()

    def u8_array(self, name: str, size: int):
        return (ctypes.c_uint8 * size).in_dll(self.loaded, name)

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def uint_array(self, name: str, size: int):
        return (ctypes.c_uint * size).in_dll(self.loaded, name)

    def test_find_scans_three_records_and_returns_matching_conn_id(self) -> None:
        records = self.u8_array("open_cfw_test_peer_records", 144)
        addresses = self.u8_array("open_cfw_test_peer_addresses", 256 * 6)
        valid = self.u8_array("open_cfw_test_peer_address_valid", 256)
        records[4] = 3
        records[48 + 4] = 7
        records[96 + 4] = 9
        valid[3] = valid[7] = valid[9] = 1
        addresses[3 * 6:3 * 6 + 6] = (10, 11, 12, 13, 14, 15)
        addresses[7 * 6:7 * 6 + 6] = (1, 2, 3, 4, 5, 6)
        addresses[9 * 6:9 * 6 + 6] = (20, 21, 22, 23, 24, 25)
        target = (ctypes.c_uint8 * 6)(1, 2, 3, 4, 5, 6)
        self.assertEqual(
            self.loaded.open_cfw_app_ble_peer_manager_find_conn_id_by_addr(
                target
            ),
            7,
        )
        self.assertEqual(self.uint("open_cfw_test_peer_find_calls"), 2)
        self.assertEqual(self.uint("open_cfw_test_peer_compare_calls"), 2)

    def test_find_handles_null_and_exhaustion(self) -> None:
        self.assertEqual(
            self.loaded.open_cfw_app_ble_peer_manager_find_conn_id_by_addr(None),
            0,
        )
        target = (ctypes.c_uint8 * 6)(1, 2, 3, 4, 5, 6)
        self.assertEqual(
            self.loaded.open_cfw_app_ble_peer_manager_find_conn_id_by_addr(
                target
            ),
            0,
        )
        self.assertEqual(self.uint("open_cfw_test_peer_find_calls"), 0)

    def test_clear_and_get_expose_the_exact_pending_tuple(self) -> None:
        pending = self.u8_array("open_cfw_test_peer_pending", 7)
        pending[:] = (1, 2, 3, 4, 5, 6, 7)
        self.loaded.open_cfw_app_master_sec_clear_addr()
        self.assertEqual(list(pending), [0, 0, 0, 0, 0, 0, 255])
        self.assertEqual(
            self.loaded.open_cfw_app_master_sec_get_addr(),
            ctypes.addressof(pending),
        )

    def test_null_unpair_is_a_strict_noop(self) -> None:
        pending = self.u8_array("open_cfw_test_peer_pending", 7)
        pending[:] = (8, 7, 6, 5, 4, 3, 2)
        self.loaded.open_cfw_app_ble_master_peer_mgr_unpair_dev(1, None)
        self.assertEqual(list(pending), [8, 7, 6, 5, 4, 3, 2])
        self.assertEqual(self.uint("open_cfw_test_peer_event_count"), 0)

    def test_active_connection_closes_before_deferred_unpair(self) -> None:
        active = ctypes.c_uint8.in_dll(
            self.loaded, "open_cfw_test_peer_active_connection"
        )
        active.value = 12
        address = (ctypes.c_uint8 * 6)(6, 5, 4, 3, 2, 1)
        self.loaded.open_cfw_app_ble_master_peer_mgr_unpair_dev(2, address)
        self.assertEqual(
            list(self.u8_array("open_cfw_test_peer_pending", 7)),
            [6, 5, 4, 3, 2, 1, 2],
        )
        self.assertEqual(self.uint("open_cfw_test_peer_find_calls"), 0)
        self.assertEqual(
            list(self.uint_array("open_cfw_test_peer_events", 8))[:3],
            [2, 3, 6],
        )
        self.assertEqual(
            self.u8_array("open_cfw_test_peer_unpair_connection", 1)[0], 12
        )
        removed = (ctypes.c_size_t * 2).in_dll(
            self.loaded, "open_cfw_test_peer_removed_callbacks"
        )
        self.assertEqual(removed[0], 0x1111)

    def test_record_lookup_also_closes_before_deferred_unpair(self) -> None:
        records = self.u8_array("open_cfw_test_peer_records", 144)
        addresses = self.u8_array("open_cfw_test_peer_addresses", 256 * 6)
        valid = self.u8_array("open_cfw_test_peer_address_valid", 256)
        records[96 + 4] = 17
        valid[17] = 1
        addresses[17 * 6:17 * 6 + 6] = (1, 3, 5, 7, 9, 11)
        address = (ctypes.c_uint8 * 6)(1, 3, 5, 7, 9, 11)
        self.loaded.open_cfw_app_ble_master_peer_mgr_unpair_dev(4, address)
        self.assertEqual(self.uint("open_cfw_test_peer_find_calls"), 1)
        self.assertEqual(
            self.u8_array("open_cfw_test_peer_unpair_connection", 1)[0], 17
        )
        self.assertEqual(
            list(self.uint_array("open_cfw_test_peer_events", 8))[:3],
            [2, 3, 6],
        )

    def test_disconnected_peer_unpairs_immediately_in_stock_order(self) -> None:
        address = (ctypes.c_uint8 * 6)(9, 8, 7, 6, 5, 4)
        self.loaded.open_cfw_app_ble_master_peer_mgr_unpair_dev(3, address)
        self.assertEqual(
            list(self.uint_array("open_cfw_test_peer_events", 8))[:6],
            [1, 2, 3, 3, 4, 5],
        )
        self.assertEqual(
            list(self.u8_array("open_cfw_test_peer_target", 8)),
            [255, 255, 255, 255, 255, 255, 0, 0],
        )
        self.assertEqual(
            self.u8_array("open_cfw_test_peer_target_connect", 1)[0], 0
        )
        self.assertEqual(
            list(self.u8_array("open_cfw_test_peer_unpair_address", 7)),
            [9, 8, 7, 6, 5, 4, 3],
        )
        removed = (ctypes.c_size_t * 2).in_dll(
            self.loaded, "open_cfw_test_peer_removed_callbacks"
        )
        self.assertEqual(list(removed), [0x1111, 0x2222])

    def test_target_compiles_with_four_global_text_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "app_ble_peer_manager.o"
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
                "open_cfw_app_ble_peer_manager_find_conn_id_by_addr",
                "open_cfw_app_master_sec_clear_addr",
                "open_cfw_app_master_sec_get_addr",
                "open_cfw_app_ble_master_peer_mgr_unpair_dev",
            })


if __name__ == "__main__":
    unittest.main()
