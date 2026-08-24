import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/service_codec_porting.c"
FIXTURE = ROOT / "tests/fixtures/service_codec_porting_host.c"
HEADER = ROOT / "tests/fixtures/service_codec_porting_host.h"


class ServiceCodecPortingCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.libs = {}
        for selector in (1, 2):
            output = Path(cls.temp.name) / f"codec-{selector}.so"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
                f"-DOPEN_CFW_SELECTOR={selector}", str(SOURCE), str(FIXTURE),
                "-o", str(output),
            ], check=True)
            cls.libs[selector] = ctypes.CDLL(str(output))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def word(lib, name):
        return ctypes.c_uint32.in_dll(lib, name)

    @staticmethod
    def byte(lib, name):
        return ctypes.c_uint8.in_dll(lib, name)

    def test_first_init_configures_ring_callback_and_resumes_uart3(self):
        lib = self.libs[1]
        self.byte(lib, "host_codec_init_flag").value = 0
        self.byte(lib, "host_codec_active_flag").value = 0
        lib.open_cfw_codec_uart_init.restype = ctypes.c_int32
        self.assertEqual(lib.open_cfw_codec_uart_init(), 0)
        self.assertEqual((self.byte(lib, "host_codec_init_flag").value,
                          self.byte(lib, "host_codec_active_flag").value), (1, 1))
        self.assertEqual((self.word(lib, "host_codec_ring_init_calls").value,
                          self.word(lib, "host_codec_callback_calls").value,
                          self.word(lib, "host_codec_resume_calls").value), (1, 1, 1))
        self.assertEqual(self.word(lib, "host_codec_last_port").value, 3)
        self.assertEqual(ctypes.c_size_t.in_dll(lib, "host_codec_last_ring_size").value, 64)

    def test_init_is_idempotent_and_resume_failure_keeps_inactive(self):
        lib = self.libs[1]
        self.byte(lib, "host_codec_init_flag").value = 1
        self.byte(lib, "host_codec_active_flag").value = 1
        before = self.word(lib, "host_codec_resume_calls").value
        self.assertEqual(lib.open_cfw_codec_uart_init(), 0)
        self.assertEqual(self.word(lib, "host_codec_resume_calls").value, before)
        self.byte(lib, "host_codec_active_flag").value = 0
        ctypes.c_int32.in_dll(lib, "host_codec_resume_result").value = 9
        self.assertEqual(lib.open_cfw_codec_uart_init(), -1)
        self.assertEqual(self.byte(lib, "host_codec_active_flag").value, 0)

    def test_close_is_idempotent_and_only_clears_after_success(self):
        lib = self.libs[2]
        lib.open_cfw_codec_uart_close.restype = ctypes.c_int32
        self.byte(lib, "host_codec_active_flag").value = 0
        before = self.word(lib, "host_codec_suspend_calls").value
        self.assertEqual(lib.open_cfw_codec_uart_close(), 0)
        self.assertEqual(self.word(lib, "host_codec_suspend_calls").value, before)
        self.byte(lib, "host_codec_active_flag").value = 1
        ctypes.c_int32.in_dll(lib, "host_codec_suspend_result").value = 7
        self.assertEqual(lib.open_cfw_codec_uart_close(), -1)
        self.assertEqual(self.byte(lib, "host_codec_active_flag").value, 1)
        ctypes.c_int32.in_dll(lib, "host_codec_suspend_result").value = 0
        self.assertEqual(lib.open_cfw_codec_uart_close(), 0)
        self.assertEqual(self.byte(lib, "host_codec_active_flag").value, 0)

    def test_all_target_selectors_compile_strictly(self):
        for selector in (1, 2):
            output = Path(self.temp.name) / f"codec-{selector}.o"
            subprocess.run([
                "/usr/bin/clang", "-target", "arm-none-eabi", "-mthumb",
                "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                "-fno-builtin", "-fropi", "-Wall", "-Wextra", "-Werror",
                f"-DOPEN_CFW_SELECTOR={selector}", "-c", str(SOURCE),
                "-o", str(output),
            ], check=True)


if __name__ == "__main__":
    unittest.main()
