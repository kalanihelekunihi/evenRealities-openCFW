import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/opt3007_registers_host.c"
SOURCE = ROOT / "components/apollo_main/core_overlay/opt3007_registers.c"

EXPECTED = bytes(value for triple in (
    (11, 0, 0), (15, 12, 0), (15, 12, 1), (11, 11, 1),
    (10, 9, 1), (8, 8, 1), (7, 7, 1), (6, 6, 1), (5, 5, 1),
    (4, 4, 1), (3, 3, 1), (2, 2, 1), (1, 0, 1), (15, 12, 2),
    (11, 0, 2), (15, 12, 3), (11, 0, 3), (15, 0, 0x7E),
    (15, 0, 0x7F),
) for value in triple)


class Opt3007RegistersCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "opt3007.so"
        subprocess.run([
            "clang", "-shared", "-fPIC", "-std=c11", "-Wall", "-Wextra",
            "-Werror", str(FIXTURE), "-o", str(library),
        ], check=True)
        cls.module = ctypes.CDLL(str(library))
        cls.module.host_opt3007_fill.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        cls.module.host_opt3007_fill.restype = ctypes.c_uint32

    def test_exact_sbos864_descriptor_bytes(self):
        output = (ctypes.c_uint8 * 57)()
        self.module.host_opt3007_fill(output)
        self.assertEqual(bytes(output), EXPECTED)

    def test_null_destination_is_safe(self):
        self.module.host_opt3007_null()

    def test_strict_cortex_m55_selector_compiles(self):
        output = Path(self.temporary.name) / "opt3007.o"
        subprocess.run([
            "/usr/bin/clang", "--target=thumbv7em-none-eabi", "-mthumb",
            "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-builtin",
            "-fno-jump-tables", "-fomit-frame-pointer",
            "-mno-unaligned-access", "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables", "-fropi",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
            "-Werror", "-mllvm", "-enable-machine-outliner=never",
            "-DOPEN_CFW_SELECTOR=1", "-c", str(SOURCE), "-o", str(output),
        ], check=True)


if __name__ == "__main__":
    unittest.main()
