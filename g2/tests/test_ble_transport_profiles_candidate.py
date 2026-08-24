from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/ble_transport_profiles.c"
HOST = ROOT / "tests/fixtures/ble_transport_profiles_host.c"


class Message(ctypes.Structure):
    _fields_ = [
        ("parameter", ctypes.c_uint16),
        ("event", ctypes.c_uint8),
        ("status", ctypes.c_uint8),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("length", ctypes.c_uint16),
        ("reserved", ctypes.c_uint16),
    ]


class CccMessage(ctypes.Structure):
    _fields_ = [
        ("parameter", ctypes.c_uint16),
        ("event", ctypes.c_uint8),
        ("status", ctypes.c_uint8),
        ("handle", ctypes.c_uint16),
        ("value", ctypes.c_uint16),
        ("index", ctypes.c_uint8),
    ]


class BleTransportProfilesCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "ble_transport_profiles.so"
        subprocess.run(
            ["clang", "-std=c11", "-shared", "-fPIC", "-Wall", "-Wextra", "-Werror", str(HOST), "-o", str(library)],
            check=True,
            cwd=ROOT,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_ble_profile_word.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ble_profile_control.restype = ctypes.c_uint8
        cls.lib.open_cfw_test_ble_profile_message_word.restype = ctypes.c_uint32
        for module in ("eus", "ess", "efs", "nus"):
            getattr(cls.lib, f"open_cfw_ble_{module}_process_ccc").argtypes = [ctypes.POINTER(Message)]
            getattr(cls.lib, f"open_cfw_ble_{module}_process_message").argtypes = [ctypes.POINTER(Message)]
            getattr(cls.lib, f"open_cfw_ble_{module}_public_process_message").argtypes = [ctypes.c_uint32, ctypes.POINTER(Message)]
            getattr(cls.lib, f"open_cfw_ble_{module}_send_data").argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16]
            getattr(cls.lib, f"open_cfw_ble_{module}_send_data").restype = ctypes.c_uint8
            callback = getattr(cls.lib, f"open_cfw_ble_{module}_write_callback")
            callback.argtypes = [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8), ctypes.c_void_p]
            callback.restype = ctypes.c_uint8
        cls.lib.open_cfw_ble_eus_direct_send_data.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16]
        cls.lib.open_cfw_ble_eus_direct_send_data.restype = ctypes.c_uint8

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.lib.open_cfw_test_ble_profile_reset()

    def word(self, index):
        return self.lib.open_cfw_test_ble_profile_word(index)

    def control(self, module, index):
        return self.lib.open_cfw_test_ble_profile_control(module, index)

    def test_ccc_indices_init_connection_and_close_role(self):
        modules = (("eus", 0, 2), ("ess", 1, 3), ("efs", 2, 4), ("nus", 3, 5))
        for ordinal, (name, module, index) in enumerate(modules, 7):
            self.lib.open_cfw_test_ble_profile_reset()
            getattr(self.lib, f"open_cfw_ble_{name}_handler_init")(ordinal)
            self.assertEqual(tuple(self.control(module, i) for i in range(4)), (0, ordinal, 0, 0))
            wrong = CccMessage(2, 0x14, 0, 0x20, 1, index + 1)
            getattr(self.lib, f"open_cfw_ble_{name}_process_ccc")(ctypes.cast(ctypes.byref(wrong), ctypes.POINTER(Message)))
            self.assertEqual((self.control(module, 0), self.control(module, 2)), (0, 0))
            ccc = CccMessage(2, 0x14, 0, 0x20, 1, index)
            getattr(self.lib, f"open_cfw_ble_{name}_process_ccc")(ctypes.cast(ctypes.byref(ccc), ctypes.POINTER(Message)))
            self.assertEqual((self.control(module, 0), self.control(module, 2)), (2, 1))
            opened = Message(2, 0x12, 0, None, 0, 0)
            getattr(self.lib, f"open_cfw_ble_{name}_process_message")(ctypes.byref(opened))
            self.assertEqual(self.control(module, 3), 1)
            self.lib.open_cfw_test_ble_profile_set_role(2, 1)
            closed = Message(2, 0x28, 0, None, 0, 0)
            getattr(self.lib, f"open_cfw_ble_{name}_process_message")(ctypes.byref(closed))
            self.assertEqual(self.control(module, 0), 0)

    def test_send_queue_and_provider_dispatch(self):
        data = (ctypes.c_uint8 * 2)(0x45, 0x46)
        modules = (("eus", 0, 2, 0xA8, 0x844), ("ess", 1, 3, 0xA9, 0x864), ("efs", 2, 4, 0xAA, 0x884), ("nus", 3, 5, 0xAB, 0x8A4))
        for name, module, index, event, handle in modules:
            self.lib.open_cfw_test_ble_profile_reset()
            getattr(self.lib, f"open_cfw_ble_{name}_handler_init")(9)
            ccc = CccMessage(2, 0x14, 0, 0x20, 1, index)
            getattr(self.lib, f"open_cfw_ble_{name}_process_ccc")(ctypes.cast(ctypes.byref(ccc), ctypes.POINTER(Message)))
            self.assertEqual(getattr(self.lib, f"open_cfw_ble_{name}_send_data")(data, 2), 0)
            self.assertEqual((self.word(0), self.word(1), self.word(2), self.word(3)), (1, 12, 1, 9))
            self.assertEqual(tuple(self.lib.open_cfw_test_ble_profile_message_word(i) for i in range(4)), (2, event, 2, 0x45))
            message = Message(2, event, 0, data, 2, 0)
            getattr(self.lib, f"open_cfw_ble_{name}_public_process_message")(0, ctypes.byref(message))
            self.assertEqual((self.word(4), self.word(5), self.word(6), self.word(7), self.word(8)), (1, 2, handle, 2, 0x45))
            self.assertEqual(self.control(module, 3), 0)

    def test_ota_gates_and_tx_release_paths(self):
        data = (ctypes.c_uint8 * 1)(0x61)
        self.lib.open_cfw_test_ble_profile_set_ota(1)
        for name in ("eus", "ess", "nus"):
            self.assertEqual(getattr(self.lib, f"open_cfw_ble_{name}_send_data")(data, 1), 0)
        self.assertEqual(self.word(0), 0)
        self.assertEqual(self.word(10), 1)  # ESS releases its completion semaphore.
        self.lib.open_cfw_test_ble_profile_reset()
        self.lib.open_cfw_ble_eus_handler_init(4)
        ccc = CccMessage(1, 0x14, 0, 0, 1, 2)
        self.lib.open_cfw_ble_eus_process_ccc(ctypes.cast(ctypes.byref(ccc), ctypes.POINTER(Message)))
        self.lib.open_cfw_test_ble_profile_set_alloc_fail(1)
        self.lib.open_cfw_ble_eus_send_data(data, 1)
        self.assertEqual((self.word(9), self.word(10), self.word(2)), (1, 1, 0))
        self.lib.open_cfw_test_ble_profile_reset()
        self.lib.open_cfw_ble_ess_handler_init(5)
        self.lib.open_cfw_ble_ess_send_data(data, 1)
        self.assertEqual((self.word(9), self.word(10)), (0, 1))

    def test_eus_direct_send_does_not_take_or_release_tx_semaphore(self):
        data = (ctypes.c_uint8 * 1)(0x70)
        self.lib.open_cfw_ble_eus_handler_init(6)
        ccc = CccMessage(3, 0x14, 0, 0, 1, 2)
        self.lib.open_cfw_ble_eus_process_ccc(ctypes.cast(ctypes.byref(ccc), ctypes.POINTER(Message)))
        self.lib.open_cfw_ble_eus_direct_send_data(data, 1)
        self.assertEqual((self.word(9), self.word(10), self.word(2)), (0, 0, 1))

    def test_all_four_registered_write_callbacks(self):
        data = (ctypes.c_uint8 * 2)(0x91, 0x92)
        self.assertEqual(self.lib.open_cfw_ble_eus_write_callback(1, 2, 3, 4, 2, data, None), 0)
        self.assertEqual((self.word(13), self.word(14), self.word(15), self.word(16), self.word(11), self.word(12)), (1, 0, 2, 0x91, 1, 1))
        self.lib.open_cfw_test_ble_profile_reset()
        self.assertEqual(self.lib.open_cfw_ble_efs_write_callback(1, 2, 3, 4, 2, data, None), 0)
        self.assertEqual((self.word(17), self.word(18), self.word(19), self.word(11)), (1, 2, 0x91, 1))
        self.lib.open_cfw_test_ble_profile_reset()
        self.lib.open_cfw_test_ble_profile_set_ota(1)
        self.lib.open_cfw_ble_efs_write_callback(1, 2, 3, 4, 2, data, None)
        self.assertEqual((self.word(17), self.word(11)), (0, 0))
        self.lib.open_cfw_test_ble_profile_reset()
        self.lib.open_cfw_ble_nus_write_callback(1, 2, 3, 4, 2, data, None)
        self.assertEqual((self.word(20), self.word(21), self.word(22), self.word(11)), (1, 2, 0x91, 1))
        self.lib.open_cfw_test_ble_profile_reset()
        self.lib.open_cfw_ble_ess_handler_init(8)
        ccc = CccMessage(1, 0x14, 0, 0, 1, 3)
        self.lib.open_cfw_ble_ess_process_ccc(ctypes.cast(ctypes.byref(ccc), ctypes.POINTER(Message)))
        self.lib.open_cfw_ble_ess_write_callback(1, 2, 3, 4, 2, data, None)
        self.assertEqual((self.word(2), self.lib.open_cfw_test_ble_profile_message_word(1)), (1, 0xA9))

    def test_all_25_cortex_m55_selectors_compile_to_one_global_leaf(self):
        selectors = {
            "EUS_CCC": "open_cfw_ble_eus_process_ccc", "EUS_PROCESS": "open_cfw_ble_eus_process_message", "EUS_WRITE": "open_cfw_ble_eus_write_callback", "EUS_INIT": "open_cfw_ble_eus_handler_init", "EUS_PUBLIC": "open_cfw_ble_eus_public_process_message", "EUS_SEND": "open_cfw_ble_eus_send_data", "EUS_DIRECT_SEND": "open_cfw_ble_eus_direct_send_data",
            "ESS_CCC": "open_cfw_ble_ess_process_ccc", "ESS_PROCESS": "open_cfw_ble_ess_process_message", "ESS_WRITE": "open_cfw_ble_ess_write_callback", "ESS_INIT": "open_cfw_ble_ess_handler_init", "ESS_PUBLIC": "open_cfw_ble_ess_public_process_message", "ESS_SEND": "open_cfw_ble_ess_send_data",
            "EFS_CCC": "open_cfw_ble_efs_process_ccc", "EFS_PROCESS": "open_cfw_ble_efs_process_message", "EFS_WRITE": "open_cfw_ble_efs_write_callback", "EFS_INIT": "open_cfw_ble_efs_handler_init", "EFS_PUBLIC": "open_cfw_ble_efs_public_process_message", "EFS_SEND": "open_cfw_ble_efs_send_data",
            "NUS_CCC": "open_cfw_ble_nus_process_ccc", "NUS_PROCESS": "open_cfw_ble_nus_process_message", "NUS_WRITE": "open_cfw_ble_nus_write_callback", "NUS_INIT": "open_cfw_ble_nus_handler_init", "NUS_PUBLIC": "open_cfw_ble_nus_public_process_message", "NUS_SEND": "open_cfw_ble_nus_send_data",
        }
        flags = ["-target", "thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        with tempfile.TemporaryDirectory() as directory:
            for selector, symbol in selectors.items():
                obj = Path(directory) / f"{selector}.o"
                subprocess.run(["clang", *flags, f"-DOPEN_CFW_BLE_{selector}_ONLY=1", "-c", str(SOURCE), "-o", str(obj)], check=True, cwd=ROOT)
                output = subprocess.run(["nm", str(obj)], check=True, capture_output=True, text=True).stdout
                globals_found = {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(globals_found, {symbol}, selector)


if __name__ == "__main__":
    unittest.main()
