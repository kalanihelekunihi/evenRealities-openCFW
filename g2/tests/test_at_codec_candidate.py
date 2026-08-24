import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/at_codec.c"
FIXTURE = ROOT / "tests/fixtures/at_codec_host.c"
HEADER = ROOT / "tests/fixtures/at_codec_host.h"


class AtCodecCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "at-codec.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_at_codec_audio_control.argtypes = [ctypes.c_char_p]
        cls.lib.open_cfw_at_codec_audio_control.restype = ctypes.c_int32
        cls.lib.host_at_codec_reset.restype = None

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.lib.host_at_codec_reset()

    def value(self, name):
        return ctypes.c_uint32.in_dll(self.lib, name).value

    def call(self, parameter):
        result = self.lib.open_cfw_at_codec_audio_control(parameter)
        self.assertEqual(result, 1)
        self.assertEqual(self.value("host_at_codec_output_calls"), 1)
        output = ctypes.c_char_p.in_dll(self.lib, "host_at_codec_last_output").value
        self.assertEqual(output, b"AUD_AUDIO+OK\r\n")

    def test_enable_uses_audio_application_seven(self):
        self.call(b"1anything")
        self.assertEqual((self.value("host_at_codec_acquire_calls"),
                          self.value("host_at_codec_release_calls"),
                          self.value("host_at_codec_last_application")), (1, 0, 7))

    def test_disable_uses_audio_application_seven(self):
        self.call(b"0")
        self.assertEqual((self.value("host_at_codec_acquire_calls"),
                          self.value("host_at_codec_release_calls"),
                          self.value("host_at_codec_last_application")), (0, 1, 7))

    def test_other_and_null_only_acknowledge(self):
        for value in (b"2", b"", None):
            self.setUp()
            self.call(value)
            self.assertEqual((self.value("host_at_codec_acquire_calls"),
                              self.value("host_at_codec_release_calls")), (0, 0))

    def test_strict_cortex_m55_compile(self):
        output = Path(self.temp.name) / "at-codec.o"
        subprocess.run([
            "/usr/bin/clang", "-target", "arm-none-eabi", "-mthumb",
            "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
            "-fno-builtin", "-fropi", "-ffunction-sections", "-fdata-sections",
            "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output),
        ], check=True)


if __name__ == "__main__":
    unittest.main()
