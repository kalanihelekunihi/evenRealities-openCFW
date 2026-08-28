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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_littlefs_sync_4213d4.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_littlefs_sync_host.c"


class LittlefsSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "littlefs-sync.dylib" if sys.platform == "darwin" else "littlefs-sync.so"
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
        cls.lib.open_cfw_bootloader_littlefs_sync_4213d4.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_bootloader_littlefs_sync_4213d4.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_body_and_configuration_binding(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x113D4:0x113D8]
        self.assertEqual(
            (body.hex(), hashlib.sha256(body).hexdigest()),
            ("00207047", "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"),
        )
        config = blob[0x21070:0x210A0]
        self.assertEqual(int.from_bytes(config[16:20], "little"), 0x004213D5)

    def test_sync_is_a_constant_success_noop(self) -> None:
        self.assertEqual(
            self.lib.open_cfw_bootloader_littlefs_sync_4213d4(None),
            0,
        )
        self.assertEqual(
            self.lib.open_cfw_bootloader_littlefs_sync_4213d4(
                ctypes.c_void_p(0x12345678)
            ),
            0,
        )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "littlefs-sync-target.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Oz", "-ffreestanding", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True,
        )
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
