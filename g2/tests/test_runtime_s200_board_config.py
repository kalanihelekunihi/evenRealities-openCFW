"""Runtime and target-compile tests for the S200 board configuration policy."""

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/s200_board_config.c"
FIXTURE = ROOT / "tests/fixtures"


class S200BoardConfigRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temporary.name) / f"s200_board_config{suffix}"
        subprocess.run([
            "clang", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra",
            "-Werror", "-include", str(FIXTURE / "s200_board_config_host.h"),
            str(SOURCE), str(FIXTURE / "s200_board_config_host.c"),
            "-o", str(library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_s200_board_reset.argtypes = [
            ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ushort,
        ]
        cls.lib.open_cfw_s200_board_config_initialize.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def value(self, name):
        return ctypes.c_uint.in_dll(self.lib, name).value

    def run_family(self, family):
        self.lib.open_cfw_test_s200_board_reset(family, 7, 0x1234)
        self.assertEqual(self.lib.open_cfw_s200_board_config_initialize(), 0)
        self.assertEqual(self.value("open_cfw_test_s200_selector_calls"), 1)
        self.assertEqual(self.value("open_cfw_test_s200_selector_argument"), 3)

    def test_npmx_family(self):
        self.run_family(1)
        self.assertEqual(self.value("open_cfw_test_s200_npmx_calls"), 1)
        self.assertEqual(self.value("open_cfw_test_s200_bq25180_calls"), 0)
        self.assertEqual(self.value("open_cfw_test_s200_bq27427_calls"), 0)

    def test_discrete_charger_family(self):
        self.run_family(2)
        self.assertEqual(self.value("open_cfw_test_s200_npmx_calls"), 0)
        self.assertEqual(self.value("open_cfw_test_s200_bq25180_calls"), 1)
        self.assertEqual(self.value("open_cfw_test_s200_bq27427_calls"), 1)

    def test_unknown_families_are_noop(self):
        for family in (0, 3, 255):
            with self.subTest(family=family):
                self.run_family(family)
                self.assertEqual(self.value("open_cfw_test_s200_npmx_calls"), 0)
                self.assertEqual(self.value("open_cfw_test_s200_bq25180_calls"), 0)
                self.assertEqual(self.value("open_cfw_test_s200_bq27427_calls"), 0)

    def test_target_compiles_as_freestanding_c(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "s200_board_config.o"
            subprocess.run([
                "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
                "-fno-jump-tables", "-fomit-frame-pointer",
                "-mno-unaligned-access", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-mllvm", "-enable-machine-outliner=never",
                "-c", str(SOURCE), "-o", str(output),
            ], check=True)
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
