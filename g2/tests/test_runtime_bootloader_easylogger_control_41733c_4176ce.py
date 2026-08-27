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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_easylogger_control_41733c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_easylogger_control_host.c"

STOCK = (
    (0x733C, 0x7392, "3d6da1a7bb77911823a8999d787e232aaf5134a06301a6566a1c6988f91ed13e"),
    (0x7392, 0x73CA, "68431e6fc495d8a35461500b6fdea63ecd39f98410a5a58a84fd6b988117604f"),
    (0x73CA, 0x7438, "337a2732ea67532c2f52e83af3905e873d942b8fe36058f2f3c2b34f00a734d8"),
    (0x7438, 0x74A6, "63e8094bcde827d2a3fd91cf64ec9c7b7c198ef11d3a6265719158f5b580e40c"),
    (0x74A6, 0x7510, "258488405b3f448615643b67d5d2a27c809ce9bf52d2f1d13368403bbd5ca917"),
    (0x7510, 0x7570, "35b3f3bb54bfab028302318966661d8e748ca1c27f46e3a164a105d105d8d205"),
    (0x7570, 0x7592, "392ca1002e32da529cfb530d17637089baa8e00c9b50bff1e6aca25def797668"),
    (0x7592, 0x75B4, "8d48f5842013881552033a3a4870589623c0f4fde269e0f567aec8c80e8e6ef5"),
    (0x75B4, 0x760A, "cc5f546238ab928d2487cf2fb564adbbfc0ba3d8bdda72d224ff74a888b68224"),
    (0x760A, 0x76CE, "fffecb363fe65341db8ea23a28a506f03d5dd06d8b2829cf0f3ea4fd9b62e709"),
)


class BootloaderEasyloggerControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / (
            "easylogger_control.dylib" if sys.platform == "darwin"
            else "easylogger_control.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.cases = {}
        for name in ("init", "start_and_setters", "locking", "tag_levels"):
            function = getattr(cls.lib, f"open_cfw_test_easylogger_control_{name}")
            function.restype = ctypes.c_uint
            cls.cases[name] = function

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_authenticated_complete_entries(self):
        image = OFFICIAL.read_bytes()
        for start, end, digest in STOCK:
            body = image[start:end]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

    def test_initialize_and_idempotence(self):
        self.assertEqual(self.cases["init"](), 1)

    def test_start_setters_and_assert_metadata(self):
        self.assertEqual(self.cases["start_and_setters"](), 1)

    def test_lock_transition_contract(self):
        self.assertEqual(self.cases["locking"](), 1)

    def test_tag_level_reset_and_query(self):
        self.assertEqual(self.cases["tag_levels"](), 1)

    def test_freestanding_target_compile_and_recovered_constants(self):
        text = SOURCE.read_text()
        for token in (
            "0x200270E4U", "0x0041A685U", "0x00417B7DU",
            "0x0041A69BU", "0x0041A6A3U", "0x0041B0F5U",
            "278U", "290U", "321U", "347U", "481U",
        ):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "easylogger_control.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-fropi",
                "-Wall", "-Wextra", "-Werror",
                "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE=OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
