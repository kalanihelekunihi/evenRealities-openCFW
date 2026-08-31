import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/charger_common.c"
FIXTURE = ROOT / "tests/fixtures"
SOURCE_SHA256 = "e1ef461fd86a8476a7c240cba1b46ba4d5210f8f2464cac0f4d4de82ea3009ac"
EXPECTED_SYMBOLS = {
    "open_cfw_charger_compare_and_update_is_charging",
    "open_cfw_charger_compare_and_update_soc",
    "open_cfw_charger_deinit_battery_sync",
    "open_cfw_charger_get_is_charging",
    "open_cfw_charger_get_local_battery_info",
    "open_cfw_charger_get_soc",
    "open_cfw_charger_init_battery_sync",
    "open_cfw_charger_on_battery_level_changed",
    "open_cfw_charger_receive_battery_info_from_peer",
    "open_cfw_charger_request_notify_battery_info_from_peer",
    "open_cfw_charger_send_battery_info",
}


class BatteryInfo(ctypes.Structure):
    _fields_ = [("soc", ctypes.c_int32), ("is_charging", ctypes.c_uint8),
                ("reserved", ctypes.c_uint8 * 3)]


class SyncMessage(ctypes.Structure):
    _fields_ = [("message_id", ctypes.c_uint8), ("payload_length", ctypes.c_uint8),
                ("source_role", ctypes.c_uint8), ("destination_role", ctypes.c_uint8),
                ("battery", BatteryInfo)]


class ChargerCommonCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"charger_common{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURE / "charger_common_host.h"),
            str(SOURCE), str(FIXTURE / "charger_common_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_charger_get_local_battery_info.argtypes = [
            ctypes.POINTER(BatteryInfo)
        ]
        cls.loaded.open_cfw_charger_get_local_battery_info.restype = ctypes.c_int
        cls.loaded.open_cfw_charger_receive_battery_info_from_peer.argtypes = [
            ctypes.POINTER(SyncMessage)
        ]
        cls.loaded.open_cfw_charger_get_soc.restype = ctypes.c_int32
        cls.loaded.open_cfw_charger_get_is_charging.restype = ctypes.c_uint8

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_charger_reset()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def byte(self, name: str) -> int:
        return ctypes.c_uint8.in_dll(self.loaded, name).value

    def driver_bytes(self):
        return (ctypes.c_uint8 * 22).in_dll(self.loaded, "open_cfw_test_charger_driver")

    def runtime_bytes(self):
        return (ctypes.c_uint8 * 24).in_dll(self.loaded, "open_cfw_test_charger_runtime")

    def set_driver(self, soc: int, current: int, charge_state: int) -> None:
        raw = self.driver_bytes()
        raw[4:8] = struct.pack("<i", soc)
        raw[12:16] = struct.pack("<i", current)
        raw[21] = charge_state

    def test_local_battery_soc_compensation_and_current_sign(self) -> None:
        for soc, state, expected in (
            (92, 1, 92), (93, 0, 93), (93, 1, 94),
            (94, 0, 95), (94, 1, 96), (95, 0, 97),
            (95, 1, 98), (96, 0, 99), (97, 0, 100),
        ):
            self.set_driver(soc, -1, state)
            info = BatteryInfo()
            self.assertEqual(
                self.loaded.open_cfw_charger_get_local_battery_info(ctypes.byref(info)), 0
            )
            self.assertEqual((info.soc, info.is_charging), (expected, 1))
        self.assertEqual(self.loaded.open_cfw_charger_get_local_battery_info(None), -1)

    def test_init_and_deinit_own_mutex_timer_and_sentinels(self) -> None:
        self.loaded.open_cfw_charger_init_battery_sync()
        self.assertEqual(self.uint("open_cfw_test_charger_create_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_charger_start_count"), 1)
        self.assertEqual(struct.unpack_from("<i", self.runtime_bytes(), 0x10)[0], -1)
        local = (ctypes.c_uint8 * 8).in_dll(self.loaded, "open_cfw_test_charger_local_info")
        self.assertEqual(struct.unpack_from("<i", local, 0)[0], -1)
        self.loaded.open_cfw_charger_deinit_battery_sync()
        self.assertEqual(self.uint("open_cfw_test_charger_delete_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_charger_stop_count"), 1)

    def test_send_and_request_use_exact_twelve_byte_wire_layout(self) -> None:
        self.loaded.open_cfw_charger_init_battery_sync()
        local = (ctypes.c_uint8 * 8).in_dll(self.loaded, "open_cfw_test_charger_local_info")
        local[:] = struct.pack("<iB3x", 77, 1)
        ctypes.c_uint8.in_dll(self.loaded, "open_cfw_test_charger_role_value").value = 1
        self.loaded.open_cfw_charger_send_battery_info(3)
        message = bytes((ctypes.c_uint8 * 12).in_dll(
            self.loaded, "open_cfw_test_charger_last_message"
        ))
        self.assertEqual(message, struct.pack("<BBBBiB3x", 3, 8, 1, 2, 77, 1))
        self.assertEqual(self.uint("open_cfw_test_charger_last_service"), 0x105)
        self.loaded.open_cfw_charger_request_notify_battery_info_from_peer()
        message = bytes((ctypes.c_uint8 * 12).in_dll(
            self.loaded, "open_cfw_test_charger_last_message"
        ))
        self.assertEqual(message, struct.pack("<BBBB8x", 4, 0, 1, 2))

    def test_peer_notify_updates_aggregate_and_replies(self) -> None:
        self.loaded.open_cfw_charger_init_battery_sync()
        local = (ctypes.c_uint8 * 8).in_dll(self.loaded, "open_cfw_test_charger_local_info")
        local[:] = struct.pack("<iB3x", 80, 1)
        message = SyncMessage(3, 8, 2, 1, BatteryInfo(75, 1, (ctypes.c_uint8 * 3)()))
        self.loaded.open_cfw_charger_receive_battery_info_from_peer(ctypes.byref(message))
        self.assertEqual(self.loaded.open_cfw_charger_get_soc(), 75)
        self.assertEqual(self.loaded.open_cfw_charger_get_is_charging(), 1)
        self.assertEqual(self.uint("open_cfw_test_charger_send_count"), 1)
        reply = bytes((ctypes.c_uint8 * 12).in_dll(
            self.loaded, "open_cfw_test_charger_last_message"
        ))
        self.assertEqual(reply[0], 2)
        self.assertEqual(self.uint("open_cfw_test_charger_publish_count"), 2)

    def test_on_change_debounces_charging_only_near_full(self) -> None:
        self.loaded.open_cfw_charger_init_battery_sync()
        self.runtime_bytes()[0x10:0x14] = struct.pack("<i", 50)
        self.set_driver(99, -1, 0)
        for expected_sends in (1, 1, 1):
            self.loaded.open_cfw_charger_on_battery_level_changed()
            self.assertEqual(self.uint("open_cfw_test_charger_send_count"), expected_sends)
        self.loaded.open_cfw_charger_on_battery_level_changed()
        self.assertEqual(self.uint("open_cfw_test_charger_send_count"), 2)

    def test_thumb_compile_and_source_pin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "charger_common.o"
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
                fields[2]
                for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, EXPECTED_SYMBOLS)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
