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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_fs_directories_4210c8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_fs_directories_host.c"


class FsDirectoriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fs-directories.dylib" if sys.platform == "darwin" else "fs-directories.so"
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
        cls.lib.open_cfw_fs_directories_fixture_config.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32
        ]
        cls.lib.open_cfw_fs_directories_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_fs_directories_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_check_and_create_directories_4210c8.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_fs_directories_fixture_reset()

    def config(self, operation: int, index: int, result: int) -> None:
        self.lib.open_cfw_fs_directories_fixture_config(operation, index, result)

    def events(self) -> tuple[tuple[int, int, int], ...]:
        count = self.lib.open_cfw_fs_directories_fixture_value(64)
        raw = [self.lib.open_cfw_fs_directories_fixture_value(i) for i in range(count)]
        return tuple(
            (raw[i], raw[i + 1], ctypes.c_int32(raw[i + 2]).value)
            for i in range(0, len(raw), 3)
        )

    def test_authenticated_stock_body_literals_successor_and_callers(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x110C8:0x111B0]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (232, "f4f1aea508ed9f9a63a310c36cf80053a49b45324d8872cd5507116db495be8c"),
        )
        self.assertEqual(
            (len(blob[0x10FF2:0x110C8]), hashlib.sha256(blob[0x10FF2:0x110C8]).hexdigest()),
            (214, "21ac43cfda25ec0bc55b6df8e70c3341923392c939cf989b96f0945e7b151ba3"),
        )
        self.assertEqual(
            (len(blob[0x111B0:0x11210]), hashlib.sha256(blob[0x111B0:0x11210]).hexdigest()),
            (96, "9c3d0c94a411e7e0a666d918d23a0c8f4eefecd2d5a32761767786bf1f47bc08"),
        )
        self.assertEqual(blob[0x111EC:0x111F0].hex(), "fff76cff")
        self.assertEqual(blob[0x11252:0x11256].hex(), "fff739ff")
        pointers = [
            int.from_bytes(blob[0x23E58 + i:0x23E5C + i], "little")
            for i in range(0, 16, 4)
        ]
        self.assertEqual(pointers, [0x00433FB0, 0x00434104, 0x0043410C, 0x00434114])
        self.assertEqual(
            tuple(blob[p - 0x410000:blob.index(0, p - 0x410000)].decode() for p in pointers),
            ("/firmware", "/ota", "/user", "/log"),
        )

    def test_existing_directories_are_closed_and_logged(self) -> None:
        self.config(3, 2, -5)
        self.assertEqual(
            self.lib.open_cfw_bootloader_check_and_create_directories_4210c8(), 0
        )
        expected = []
        for index in range(4):
            expected.extend(((1, index, 0), (3, index, -5 if index == 2 else 0), (12, index, 0)))
        self.assertEqual(self.events(), tuple(expected))

    def test_missing_directories_cover_create_race_and_nonfatal_failure(self) -> None:
        for index in range(4):
            self.config(1, index, -2)
        self.config(2, 0, 0)
        self.config(2, 1, -17)
        self.config(2, 2, -5)
        self.config(2, 3, 0)
        self.assertEqual(
            self.lib.open_cfw_bootloader_check_and_create_directories_4210c8(), 0
        )
        self.assertEqual(
            self.events(),
            (
                (1, 0, -2), (2, 0, 0), (11, 0, 0),
                (1, 1, -2), (2, 1, -17), (13, 1, -17),
                (1, 2, -2), (2, 2, -5), (14, 2, -5),
                (1, 3, -2), (2, 3, 0), (11, 3, 0),
            ),
        )

    def test_unexpected_check_failure_is_fatal_and_stops_iteration(self) -> None:
        self.config(1, 1, -5)
        self.assertEqual(
            self.lib.open_cfw_bootloader_check_and_create_directories_4210c8(), -1
        )
        self.assertEqual(
            self.events(),
            ((1, 0, 0), (3, 0, 0), (12, 0, 0), (1, 1, -5), (15, 1, -5)),
        )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "fs-directories-target.o"
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
