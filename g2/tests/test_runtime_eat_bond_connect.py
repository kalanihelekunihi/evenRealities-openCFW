from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/eat_bond_connect.c"
FIXTURES = ROOT / "tests/fixtures"


class RuntimeEatBondConnectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"eat_bond_connect{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURES / "eat_bond_connect_host.h"),
            str(SOURCE), str(FIXTURES / "eat_bond_connect_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_eat_reset()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def pointer(self, name: str) -> int | None:
        return ctypes.c_void_p.in_dll(self.loaded, name).value

    def array_address(self, name: str, size: int) -> int:
        return ctypes.addressof((ctypes.c_char * size).in_dll(self.loaded, name))

    def test_clean_bond_provider_response_and_return(self) -> None:
        self.assertEqual(self.loaded.open_cfw_eat_clean_bond_handler(), 0)
        self.assertEqual(self.uint("open_cfw_test_eat_clean_calls"), 1)
        self.assertEqual(self.uint("open_cfw_test_eat_keep_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_eat_output_calls"), 1)
        expected = self.array_address("open_cfw_test_eat_clean_response", 15)
        self.assertEqual(self.pointer("open_cfw_test_eat_written"), expected)
        self.assertEqual(ctypes.string_at(expected), b"CLEANBOND+OK\r\n")

    def test_keep_connect_provider_argument_response_and_return(self) -> None:
        self.assertEqual(self.loaded.open_cfw_eat_keep_connect_handler(), 0)
        self.assertEqual(self.uint("open_cfw_test_eat_clean_calls"), 0)
        self.assertEqual(self.uint("open_cfw_test_eat_keep_calls"), 1)
        self.assertEqual(
            ctypes.c_int.in_dll(
                self.loaded, "open_cfw_test_eat_keep_argument"
            ).value,
            1,
        )
        self.assertEqual(self.uint("open_cfw_test_eat_output_calls"), 1)
        expected = self.array_address("open_cfw_test_eat_keep_response", 21)
        self.assertEqual(self.pointer("open_cfw_test_eat_written"), expected)
        self.assertEqual(ctypes.string_at(expected), b"BLE_KEEPCONNECT+OK\r\n")

    def test_target_compiles_with_only_two_global_text_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "eat_bond_connect.o"
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
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, {
                "open_cfw_eat_clean_bond_handler",
                "open_cfw_eat_keep_connect_handler",
            })


if __name__ == "__main__":
    unittest.main()
