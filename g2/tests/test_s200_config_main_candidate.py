import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/s200_config_main.c"
FIXTURE = ROOT / "tests/fixtures/s200_config_main_host.c"
HEADER = ROOT / "tests/fixtures/s200_config_main_host.h"


class Event(ctypes.Structure):
    _fields_ = [("target", ctypes.c_void_p), ("code", ctypes.c_uint32)]


class S200ConfigMainCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "libs200_config_main.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.host_s200_object.restype = ctypes.c_void_p
        cls.lib.host_s200_object_parent.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.host_s200_object_value.argtypes = [ctypes.c_uint32, ctypes.c_int32]
        cls.lib.host_s200_object_extent.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32]
        cls.lib.host_s200_object_flags.argtypes = [ctypes.c_uint32, ctypes.c_uint8]
        cls.lib.open_cfw_s200_main_class_event.argtypes = [ctypes.c_void_p, ctypes.POINTER(Event)]
        cls.lib.open_cfw_s200_main_input_event.argtypes = [ctypes.POINTER(Event)]
        cls.lib.open_cfw_s200_main_widget_init.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.lib.open_cfw_s200_main_report_reset.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.lib.host_s200_reset()

    def u32(self, name):
        return ctypes.c_uint32.in_dll(self.lib, name)

    def test_class_event_reapplies_current_value(self):
        target = self.lib.host_s200_object(0)
        self.lib.host_s200_object_value(0, 37)
        event = Event(target, 0x31)
        self.lib.open_cfw_s200_main_class_event(None, ctypes.byref(event))
        self.assertEqual(self.u32("host_s200_set_count").value, 1)
        self.assertEqual(self.lib.host_s200_object_value_get(0), 37)

    def test_input_event_updates_value_and_emits_change(self):
        self.lib.host_s200_object_parent(0, 1)
        self.lib.host_s200_object_extent(0, 100, 80)
        self.lib.host_s200_object_flags(1, 0x0C)
        self.lib.host_s200_object_value(1, 0)
        self.u32("host_s200_direction").value = 1
        points = (ctypes.c_int32 * 2).in_dll(self.lib, "host_s200_point")
        points[:] = (-50, 0)
        event = Event(self.lib.host_s200_object(0), 0x0E)
        self.lib.open_cfw_s200_main_input_event(ctypes.byref(event))
        self.assertEqual(self.lib.host_s200_object_value_get(1), 1)
        self.assertEqual(self.u32("host_s200_event_count").value, 1)

    def test_widget_initialization_preserves_geometry(self):
        self.lib.host_s200_object_parent(0, 1)
        self.lib.host_s200_object_extent(1, 240, 80)
        self.lib.open_cfw_s200_main_widget_init(None, self.lib.host_s200_object(0))
        self.assertEqual(self.u32("host_s200_created_count").value, 2)
        self.assertEqual(self.lib.host_s200_object_value_get(3), 100)

    def test_platform_initialization_and_result(self):
        result = self.lib.open_cfw_s200_main_platform_init()
        self.assertEqual(result, -7)
        self.assertEqual(self.u32("host_s200_init_mask").value, 0x3FF)
        self.assertEqual(self.u32("host_s200_release_count").value, 1)

    def test_reset_priority_and_brownout_side_effect(self):
        reset = (ctypes.c_uint8 * 16).in_dll(self.lib, "host_s200_reset_storage")
        reset[4] = 1
        reset[8] = 1
        self.assertEqual(self.lib.open_cfw_s200_main_report_reset(), 3)
        self.assertEqual(self.u32("host_s200_reset_clear_count").value, 1)
        reset[2] = 1
        self.assertEqual(self.lib.open_cfw_s200_main_report_reset(), 1)
        self.assertEqual(self.u32("host_s200_reset_clear_count").value, 1)

    def test_all_isolated_cortex_m55_entries_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            for selector in range(1, 7):
                subprocess.run([
                    "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    f"-DOPEN_CFW_S200_MAIN_SELECTOR={selector}",
                    "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                ], check=True)


if __name__ == "__main__":
    unittest.main()
