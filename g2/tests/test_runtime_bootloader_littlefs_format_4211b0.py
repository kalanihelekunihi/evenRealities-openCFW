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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_littlefs_format_4211b0.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_littlefs_format_host.c"


class LittlefsFormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "littlefs-format.dylib" if sys.platform == "darwin" else "littlefs-format.so"
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
        cls.lib.open_cfw_littlefs_format_fixture_config.argtypes = [
            ctypes.c_uint32, ctypes.c_int32
        ]
        cls.lib.open_cfw_littlefs_format_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_littlefs_format_fixture_value.restype = ctypes.c_int32
        cls.lib.open_cfw_littlefs_bootloader_format_4211b0.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_littlefs_format_fixture_reset()

    def config(self, operation: int, result: int) -> None:
        self.lib.open_cfw_littlefs_format_fixture_config(operation, result)

    def events(self) -> tuple[tuple[int, int], ...]:
        count = self.lib.open_cfw_littlefs_format_fixture_value(16)
        raw = [self.lib.open_cfw_littlefs_format_fixture_value(i) for i in range(count)]
        return tuple((raw[i], raw[i + 1]) for i in range(0, len(raw), 2))

    def test_authenticated_body_successor_calls_literals_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x111B0:0x11210]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (96, "9c3d0c94a411e7e0a666d918d23a0c8f4eefecd2d5a32761767786bf1f47bc08"),
        )
        successor = blob[0x11210:0x112D8]
        self.assertEqual(
            (len(successor), hashlib.sha256(successor).hexdigest()),
            (200, "07d8267cfa9725c9ac0ee613334d09968b780b890c4680f612546239bff1adf8"),
        )
        self.assertEqual(blob[0x1126E:0x11272].hex(), "fff79fff")
        self.assertEqual(
            tuple(blob[offset:offset + 4].hex() for offset in
                (0x111B8, 0x111C2, 0x111CA, 0x111E4, 0x111EC, 0x11204)),
            ("f3f7c0ff", "f3f7b1ff", "f3f7b2ff", "f6f773fa", "fff76cff", "f6f763fa"),
        )
        self.assertEqual(
            tuple(int.from_bytes(blob[offset:offset + 4], "little") for offset in
                (0x1138C, 0x1139C, 0x113A0, 0x113A4, 0x113A8)),
            (0x20026878, 0x00431070, 0x00433964, 0x00433E28, 0x00433000),
        )

    def test_success_ignores_unmount_and_format_results(self) -> None:
        self.config(0, -5)
        self.config(1, -17)
        self.assertEqual(self.lib.open_cfw_littlefs_bootloader_format_4211b0(), 0)
        self.assertEqual(self.events(), ((1, -5), (2, -17), (3, 0), (4, 0)))

    def test_mount_failure_logs_maps_to_nine_and_stops(self) -> None:
        self.config(2, -84)
        self.assertEqual(self.lib.open_cfw_littlefs_bootloader_format_4211b0(), 9)
        self.assertEqual(self.events(), ((1, 0), (2, 0), (3, -84), (11, -84)))

    def test_directory_failure_logs_and_maps_to_nine(self) -> None:
        self.config(3, -1)
        self.assertEqual(self.lib.open_cfw_littlefs_bootloader_format_4211b0(), 9)
        self.assertEqual(
            self.events(), ((1, 0), (2, 0), (3, 0), (4, -1), (12, -1))
        )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "littlefs-format-target.o"
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
