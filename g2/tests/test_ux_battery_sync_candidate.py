import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/ux_battery_sync.c"
FIXTURE = ROOT / "tests/fixtures/ux_battery_sync_host.c"
HEADER = ROOT / "tests/fixtures/ux_battery_sync_host.h"


class Message(ctypes.Structure):
    _fields_ = [
        ("message_id", ctypes.c_uint8), ("payload_length", ctypes.c_uint8),
        ("source_role", ctypes.c_uint8), ("destination_role", ctypes.c_uint8),
        ("battery_level", ctypes.c_int32), ("is_charging", ctypes.c_int8),
        ("reserved", ctypes.c_uint8 * 3),
    ]


class UxBatterySyncCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "libux_battery_sync.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.handler = cls.lib.open_cfw_ux_battery_sync_handler
        cls.handler.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint16]
        cls.handler.restype = ctypes.c_int32
        cls.lib.host_reset()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.lib.host_reset()

    def dispatch(self, message):
        return self.handler(None, ctypes.byref(message), ctypes.sizeof(message))

    def value(self, name, kind=ctypes.c_uint32):
        return kind.in_dll(self.lib, name).value

    def test_validation_and_unknown_id(self):
        self.assertEqual(self.handler(None, None, 12), -1)
        message = Message(message_id=1)
        self.assertEqual(self.handler(None, ctypes.byref(message), 11), -1)
        message.message_id = 0
        self.assertEqual(self.dispatch(message), -1)
        message.message_id = 7
        self.assertEqual(self.dispatch(message), -1)

    def test_charger_request_response_and_notification_routes(self):
        message = Message(message_id=1)
        self.assertEqual(self.dispatch(message), 0)
        self.assertEqual(self.value("host_sent_id", ctypes.c_uint8), 2)
        message.message_id = 4
        self.assertEqual(self.dispatch(message), 0)
        self.assertEqual(self.value("host_sent_id", ctypes.c_uint8), 3)
        for message_id in (2, 3):
            message.message_id = message_id
            self.assertEqual(self.dispatch(message), 0)
            self.assertEqual(
                self.value("host_received", ctypes.c_void_p),
                ctypes.addressof(message),
            )

    def test_ring_import_clamps_normalizes_and_notifies_changes(self):
        ctypes.c_uint8.in_dll(self.lib, "host_level").value = 50
        message = Message(message_id=5, battery_level=-9, is_charging=-3)
        self.assertEqual(self.dispatch(message), 0)
        self.assertEqual(self.value("host_level", ctypes.c_uint8), 0)
        self.assertEqual(self.value("host_charging", ctypes.c_uint8), 1)
        self.assertEqual(self.value("host_notification_count"), 2)
        notes = (ctypes.c_uint32 * 4).in_dll(self.lib, "host_notifications")
        self.assertEqual(list(notes), [0, 0, 1, 1])
        self.assertEqual(self.dispatch(message), 0)
        self.assertEqual(self.value("host_notification_count"), 2)
        message.battery_level = 101
        self.assertEqual(self.dispatch(message), 0)
        self.assertEqual(self.value("host_level", ctypes.c_uint8), 100)

    def test_ring_export_uses_cached_state(self):
        ctypes.c_uint8.in_dll(self.lib, "host_level").value = 73
        ctypes.c_uint8.in_dll(self.lib, "host_charging").value = 1
        self.assertEqual(self.dispatch(Message(message_id=6)), 0)
        self.assertEqual(self.value("host_update_count"), 1)
        self.assertEqual(self.value("host_update_level", ctypes.c_uint8), 73)
        self.assertEqual(self.value("host_update_charging", ctypes.c_uint8), 1)


if __name__ == "__main__":
    unittest.main()
