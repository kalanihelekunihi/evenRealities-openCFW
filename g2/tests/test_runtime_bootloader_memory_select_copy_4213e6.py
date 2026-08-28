from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memory_select_copy_4213e6.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_memory_select_copy_host.c"


class MemorySelectCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "memory-select.dylib" if sys.platform == "darwin" else "memory-select.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
            *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
            "-o", str(cls.library),
        ], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_memory_select_fixture_reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_memory_select_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_memory_select_fixture_value.restype = ctypes.c_size_t
        for name in (
            "open_cfw_bootloader_memory_select_copy_4213e6",
            "open_cfw_bootloader_memory_select_odd_421548",
        ):
            fn = getattr(cls.lib, name)
            fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
            fn.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def invoke(self, kind: int, offset: int, size: int, control: int = 0, security: int = 0) -> tuple[int, tuple[int, ...]]:
        self.lib.open_cfw_memory_select_fixture_reset(control, security)
        status = self.lib.open_cfw_bootloader_memory_select_copy_4213e6(
            kind, offset, size, ctypes.c_void_p(0x1234)
        )
        values = tuple(self.lib.open_cfw_memory_select_fixture_value(i) for i in range(4))
        return status, values

    def test_authenticated_bodies_literal_pool_and_calls(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x113E6:0x11548]
        wrapper = blob[0x11548:0x1156E]
        pool = blob[0x1156E:0x11584]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (354, "989242545e69349bd0ff976d0bdd47f5800523263ad0f2c35fa06c0a68ea5127"))
        self.assertEqual((len(wrapper), hashlib.sha256(wrapper).hexdigest()), (38, "3b5bbbf5927b1c40733445a47ac8ddcec46ba52837fd94cf3ee0dc20c28d9e72"))
        self.assertEqual(pool.hex(), "0000bc01024008100240004000420060004200200042")
        self.assertEqual(blob[0x1153E:0x11542].hex(), "fbf7a4fe")
        self.assertEqual(blob[0x11568:0x1156C].hex(), "fff73dff")

    def test_validation_capacities_and_wrapping_sum(self) -> None:
        self.assertEqual(self.lib.open_cfw_bootloader_memory_select_copy_4213e6(0, 0, 0, None), 6)
        self.assertEqual(self.invoke(6, 0, 0)[0], 6)
        for kind, capacity in ((0, 0x200), (1, 0x600), (2, 0x40), (3, 0x2C0), (4, 0x200), (5, 0x600)):
            security = 1 << 27 if kind in (2, 3) else 0
            self.assertEqual(self.invoke(kind, capacity, 0, security=security)[0], 0)
            self.assertEqual(self.invoke(kind, capacity, 1, security=security)[0], 5)
        self.assertEqual(self.invoke(4, 0xFFFFFFFF, 1)[0], 0)

    def test_all_source_mappings_and_unavailable_paths(self) -> None:
        cases = (
            (0, 3, 4, 0, 0, 0x4200000C),
            (0, 3, 4, 1 << 4, 1 << 27, 0x4200400C),
            (1, 0x1FF, 4, 0, 0, 0x420027FC),
            (1, 0x200, 4, 0, 0, 0x42003200),
            (1, 3, 4, 1 << 3, 1 << 27, 0x4200600C),
            (2, 3, 4, 0, 1 << 27, 0x4200400C),
            (3, 3, 4, 0, 1 << 27, 0x4200600C),
            (4, 3, 4, 0, 0, 0x4200000C),
            (5, 3, 4, 0, 0, 0x4200200C),
        )
        for kind, offset, size, control, security, source in cases:
            with self.subTest(kind=kind, offset=offset):
                status, values = self.invoke(kind, offset, size, control, security)
                self.assertEqual((status, values), (0, (source, 0x1234, size, 1)))
        for kind, control in ((0, 1 << 4), (1, 1 << 3), (2, 0), (3, 0)):
            self.assertEqual(self.invoke(kind, 0, 0, control, 0), (9, (0, 0, 0, 0)))

    def test_odd_wrapper_filters_and_forwards(self) -> None:
        odd = self.lib.open_cfw_bootloader_memory_select_odd_421548
        for kind in (0, 2, 4, 6):
            self.lib.open_cfw_memory_select_fixture_reset(0, 1 << 27)
            self.assertEqual(odd(kind, 0, 0, ctypes.c_void_p(0x1234)), 6)
        for kind in (1, 3, 5):
            self.lib.open_cfw_memory_select_fixture_reset(0, 1 << 27)
            self.assertEqual(odd(kind, 0, 0, ctypes.c_void_p(0x1234)), 0)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "memory-select-target.o"
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "--target=arm-none-eabi",
            "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
            "-fno-builtin", "-ffunction-sections", "-Wall", "-Wextra", "-Werror",
            "-c", str(SOURCE), "-o", str(output),
        ], check=True, capture_output=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
