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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_address_map_4213d8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_address_map_host.c"


class AddressMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "address-map.dylib" if sys.platform == "darwin" else "address-map.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        for name in (
            "open_cfw_bootloader_address_identity_4213d8",
            "open_cfw_bootloader_address_map_4213da",
        ):
            function = getattr(cls.lib, name)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_bodies_and_callers(self) -> None:
        blob = OFFICIAL.read_bytes()
        identity = blob[0x113D8:0x113DA]
        mapping = blob[0x113DA:0x113E6]
        self.assertEqual(
            (identity.hex(), hashlib.sha256(identity).hexdigest()),
            ("7047", "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
        )
        self.assertEqual(
            (mapping.hex(), hashlib.sha256(mapping).hexdigest()),
            ("b0f5007f01d310f520707047", "742c0902623d3c2df2a28eaa1cde52792f9cf28dccd447d513720eb408f5392a"),
        )
        self.assertEqual(blob[0x114BE:0x114C2].hex(), "fff78bff")
        self.assertEqual(blob[0x114E8:0x114EC].hex(), "fff777ff")

    def test_identity_and_threshold_mapping_contract(self) -> None:
        identity = self.lib.open_cfw_bootloader_address_identity_4213d8
        mapping = self.lib.open_cfw_bootloader_address_map_4213da
        for value in (0, 1, 0x1FF, 0x200, 0xFFFFFFFF):
            self.assertEqual(identity(value), value)
        self.assertEqual(mapping(0), 0)
        self.assertEqual(mapping(0x1FF), 0x1FF)
        self.assertEqual(mapping(0x200), 0x480)
        self.assertEqual(mapping(0xFFFFFFFF), 0x27F)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "address-map-target.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                "-Wall", "-Wextra", "-Werror",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True,
        )
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
