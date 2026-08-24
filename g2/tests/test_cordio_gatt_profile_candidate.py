from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_gatt_profile.c"
FIXTURE = ROOT / "tests/fixtures"


class Event(ctypes.Structure):
    _fields_ = [
        ("parameter", ctypes.c_uint16), ("event", ctypes.c_uint8),
        ("status", ctypes.c_uint8), ("value", ctypes.POINTER(ctypes.c_uint8)),
        ("value_length", ctypes.c_uint16), ("handle", ctypes.c_uint16),
        ("continuing", ctypes.c_uint8), ("reserved", ctypes.c_uint8),
        ("mtu", ctypes.c_uint16),
    ]


class Attribute(ctypes.Structure):
    _fields_ = [
        ("uuid", ctypes.POINTER(ctypes.c_uint8)),
        ("value", ctypes.POINTER(ctypes.c_uint8)),
        ("length", ctypes.POINTER(ctypes.c_uint16)),
        ("maximum_length", ctypes.c_uint16),
        ("settings", ctypes.c_uint8), ("permissions", ctypes.c_uint8),
    ]


class CordioGattProfileCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library_path = Path(cls.temp.name) / ("gatt" + suffix)
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1", "-Wall",
            "-Wextra", "-Werror", "-include",
            str(FIXTURE / "cordio_gatt_profile_host.h"), str(SOURCE),
            str(FIXTURE / "cordio_gatt_profile_host.c"), "-o",
            str(cls.library_path),
        ], check=True, cwd=ROOT)
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.lib.open_cfw_test_gatt_word.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_gatt_word.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_gatt_bytes.restype = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.open_cfw_gatt_value_update.argtypes = [
            ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(Event)
        ]
        cls.lib.open_cfw_gatt_read_callback.argtypes = [
            ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint8, ctypes.c_uint16,
            ctypes.POINTER(Attribute),
        ]
        cls.lib.open_cfw_gatt_write_callback.argtypes = [
            ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint8, ctypes.c_uint16,
            ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(Attribute),
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_test_gatt_reset()

    def word(self, index: int) -> int:
        return self.lib.open_cfw_test_gatt_word(index)

    def test_discovery_uses_recovered_g2_contract(self) -> None:
        handles = (ctypes.c_uint16 * 3)()
        self.lib.open_cfw_gatt_discover(2, handles)
        self.assertEqual((self.word(0), self.word(1), self.word(2)), (2, 2, 3))
        self.assertEqual(self.word(5), ctypes.addressof(handles) & 0xFFFFFFFF)
        self.assertNotEqual(self.word(3), 0)
        self.assertEqual(self.word(4), 0x12345678)

    def test_value_update_routes_only_service_changed_handle(self) -> None:
        handles = (ctypes.c_uint16 * 3)(0x2222, 0, 0)
        event = Event(handle=0x2222)
        self.assertEqual(self.lib.open_cfw_gatt_value_update(handles, ctypes.byref(event)), 0)
        self.assertEqual(self.word(6), 1)
        event.handle = 0x3333
        self.assertEqual(self.lib.open_cfw_gatt_value_update(handles, ctypes.byref(event)), 0x0A)
        self.assertEqual(self.word(6), 1)

    def test_service_changed_index_and_broadcast(self) -> None:
        self.lib.open_cfw_gatt_send_service_changed_indication(0, 0x1234, 0xABCD)
        self.assertEqual(self.word(8), 0)
        self.lib.open_cfw_gatt_set_service_changed_index(7)
        self.lib.open_cfw_test_gatt_set_ccc(1, 1)
        self.lib.open_cfw_test_gatt_set_ccc(3, 1)
        self.lib.open_cfw_gatt_send_service_changed_indication(0, 0x1234, 0xABCD)
        self.assertEqual((self.word(8), self.word(9), self.word(10)), (3, 7, 2))
        self.assertEqual((self.word(11), self.word(12)), (1, 3))
        self.assertEqual((self.word(15), self.word(16)), (0x12, 0x12))
        raw = self.lib.open_cfw_test_gatt_bytes()
        self.assertEqual(list(raw[:8]), [0x34, 0x12, 0xCD, 0xAB] * 2)

    def test_service_changed_specific_connection(self) -> None:
        self.lib.open_cfw_gatt_set_service_changed_index(4)
        self.lib.open_cfw_test_gatt_set_ccc(2, 1)
        self.lib.open_cfw_gatt_send_service_changed_indication(2, 1, 0xFFFF)
        self.assertEqual((self.word(8), self.word(9), self.word(10)), (1, 4, 1))
        self.assertEqual(self.word(11), 2)
        self.assertEqual(list(self.lib.open_cfw_test_gatt_bytes()[:4]), [1, 0, 0xFF, 0xFF])

    def test_read_and_write_callbacks(self) -> None:
        value = (ctypes.c_uint8 * 4)(0xEE, 0xEE, 0xEE, 0xEE)
        attribute = Attribute(value=value)
        self.lib.open_cfw_test_gatt_set_features(0x5A)
        self.assertEqual(self.lib.open_cfw_gatt_read_callback(3, 0x15, 9, 8, ctypes.byref(attribute)), 0)
        self.assertEqual((value[0], self.word(22), self.word(23), self.word(24)), (0x5A, 1, 3, 1))
        value[0] = 0xA5
        self.assertEqual(self.lib.open_cfw_gatt_read_callback(3, 0x14, 0, 0, ctypes.byref(attribute)), 0)
        self.assertEqual((value[0], self.word(22)), (0xA5, 1))
        self.lib.open_cfw_test_gatt_set_write_result(0x77)
        self.assertEqual(self.lib.open_cfw_gatt_write_callback(2, 0x15, 9, 4, 1, value, ctypes.byref(attribute)), 0x77)
        self.assertEqual(tuple(self.word(i) for i in range(25, 30)), (1, 2, 4, 1, 0xA5))
        self.assertEqual(self.lib.open_cfw_gatt_write_callback(2, 0x14, 0, 0, 1, value, ctypes.byref(attribute)), 0)
        self.assertEqual(self.word(25), 1)

    def test_each_selector_is_one_thumb_function(self) -> None:
        selectors = {
            "DISCOVER": "open_cfw_gatt_discover",
            "VALUE_UPDATE": "open_cfw_gatt_value_update",
            "SET_INDEX": "open_cfw_gatt_set_service_changed_index",
            "SEND_CHANGED": "open_cfw_gatt_send_service_changed_indication",
            "READ_CALLBACK": "open_cfw_gatt_read_callback",
            "WRITE_CALLBACK": "open_cfw_gatt_write_callback",
        }
        flags = [
            "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
            "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
            "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
            "-fdata-sections", "-Wall", "-Wextra", "-Werror",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector, expected in selectors.items():
                target = Path(directory) / (selector + ".o")
                subprocess.run([
                    "clang", *flags, f"-DOPEN_CFW_GATT_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(target),
                ], check=True, cwd=ROOT)
                symbols = subprocess.run(
                    ["nm", str(target)], check=True, capture_output=True,
                    text=True,
                ).stdout
                observed = {
                    fields[2] for line in symbols.splitlines()
                    if len(fields := line.split()) == 3 and fields[1] == "T"
                }
                self.assertEqual(observed, {expected})


if __name__ == "__main__":
    unittest.main()
