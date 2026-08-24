import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/service_nvdb_host.c"


class Defaults(ctypes.Structure):
    _fields_ = [("nodes", ctypes.c_void_p), ("count", ctypes.c_uint32)]


class ServiceNvdbCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name) / "service_nvdb.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-std=c11", "-Wall",
                        "-Wextra", "-Werror", str(FIXTURE), "-o", str(out)],
                       check=True)
        cls.lib = ctypes.CDLL(str(out))
        cls.lib.open_cfw_service_nvdb_init.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.lib.open_cfw_service_nvdb_init.restype = ctypes.c_int
        cls.lib.open_cfw_service_nvdb_defaults_get.argtypes = [ctypes.POINTER(Defaults)]
        cls.lib.host_system_data.restype = ctypes.POINTER(ctypes.c_uint8)

    def setUp(self):
        self.lib.host_reset()

    def test_wrappers_preserve_index_and_payload(self):
        value = ctypes.c_uint32()
        self.assertEqual(self.lib.open_cfw_service_nvdb_read(b"nvMagic", ctypes.byref(value), 4), 1)
        self.assertEqual(value.value, 0x55550022)
        self.assertEqual(self.lib.open_cfw_service_nvdb_write(b"x", ctypes.byref(value), 4), 1)

    def test_default_descriptor(self):
        defaults = Defaults()
        self.lib.open_cfw_service_nvdb_defaults_get(ctypes.byref(defaults))
        self.assertTrue(defaults.nodes)
        self.assertEqual(defaults.count, 9)

    def test_valid_mount_and_callbacks(self):
        self.assertEqual(self.lib.open_cfw_service_nvdb_init(1, 2), 0)
        self.assertEqual(self.lib.host_controls(), 2)
        self.assertEqual(self.lib.host_defaults_calls(), 0)
        self.assertEqual(self.lib.host_legacy_scans(), 1)
        data = bytes(self.lib.host_system_data()[i] for i in range(16))
        self.assertEqual(data, b"\0ABCDEFGHIJKLMN\0")

    def test_init_failure_is_reported(self):
        self.lib.host_set_init_result(3)
        self.assertEqual(self.lib.open_cfw_service_nvdb_init(None, None), 8)
        self.assertEqual(self.lib.host_controls(), 0)

    def test_magic_mismatch_is_non_destructive_by_default(self):
        self.lib.host_set_magic(0xDEADBEEF, 1)
        self.assertEqual(self.lib.open_cfw_service_nvdb_init(None, None), 9)
        self.assertEqual(self.lib.host_defaults_calls(), 0)
        self.lib.host_set_magic(0, 0)
        self.assertEqual(self.lib.open_cfw_service_nvdb_init(None, None), 9)
        self.assertEqual(self.lib.host_defaults_calls(), 0)


if __name__ == "__main__":
    unittest.main()
