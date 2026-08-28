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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_littlefs_init_421210.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_littlefs_init_host.c"


class LittlefsInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "littlefs-init.dylib" if sys.platform == "darwin" else "littlefs-init.so"
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
        cls.lib.open_cfw_littlefs_init_fixture_config.argtypes = [
            ctypes.c_uint32, ctypes.c_int32
        ]
        cls.lib.open_cfw_littlefs_init_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_littlefs_init_fixture_value.restype = ctypes.c_int32
        cls.lib.open_cfw_littlefs_bootloader_init_421210.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_littlefs_init_fixture_reset()

    def config(self, operation: int, value: int) -> None:
        self.lib.open_cfw_littlefs_init_fixture_config(operation, value)

    def value(self, index: int) -> int:
        return self.lib.open_cfw_littlefs_init_fixture_value(index)

    def events(self) -> tuple[tuple[int, int], ...]:
        count = self.value(48)
        raw = [self.value(i) for i in range(count)]
        return tuple((raw[i], raw[i + 1]) for i in range(0, len(raw), 2))

    def test_authenticated_body_calls_literals_successor_and_sole_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x11210:0x112D8]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (200, "07d8267cfa9725c9ac0ee613334d09968b780b890c4680f612546239bff1adf8"),
        )
        successor = blob[0x112D8:0x11310]
        self.assertEqual(
            (len(successor), hashlib.sha256(successor).hexdigest()),
            (56, "26e2b4b9fe7f3389d15261fe01621eb3b37bfc4b9923ebfac70609216ac92a90"),
        )
        self.assertEqual(blob[0xB8A6:0xB8AA].hex(), "05f0b3fc")
        self.assertEqual(
            tuple(blob[offset:offset + 4].hex() for offset in
                (0x1121C, 0x11228, 0x11230, 0x1124A, 0x11252, 0x1126A,
                 0x1126E, 0x11288, 0x11294, 0x112A2, 0x112AE, 0x112B6,
                 0x112CE)),
            ("f3f789ff", "f3f77eff", "f3f77fff", "f6f740fa",
             "fff739ff", "f6f730fa", "fff79fff", "f3f75dff",
             "f3f794ff", "f3f7e7ff", "f3f7a5ff", "f3f763ff",
             "f6f7fef9"),
        )
        self.assertEqual(
            tuple(int.from_bytes(blob[offset:offset + 4], "little") for offset in
                range(0x113AC, 0x113C8, 4)),
            (0x0043397C, 0x00433E38, 0x0043178C, 0x2002711C,
             0x20026C0C, 0x00433FC8, 0x00433E48),
        )

    def test_mounted_path_publishes_ready_and_updates_boot_count(self) -> None:
        self.config(10, 41)
        self.assertEqual(self.lib.open_cfw_littlefs_bootloader_init_421210(), 0)
        self.assertEqual(self.value(49), 1)
        self.assertEqual(self.value(50), 42)
        self.assertEqual(self.value(51), 0x103)
        self.assertEqual(
            self.events(),
            ((1, 0), (3, 0), (5, 1), (6, 0), (7, 0), (8, 0),
             (9, 0), (10, 0), (13, 42)),
        )

    def test_mount_failure_formats_retries_and_then_completes(self) -> None:
        self.config(0, -84)
        self.config(1, 0)
        self.config(2, -17)
        self.assertEqual(self.lib.open_cfw_littlefs_bootloader_init_421210(), 0)
        self.assertEqual(self.events()[:4], ((1, -84), (2, -17), (1, 0), (3, 0)))
        self.assertEqual(self.value(52), 2)

    def test_second_mount_failure_logs_maps_to_nine_and_stops(self) -> None:
        self.config(0, -84)
        self.config(1, -5)
        self.assertEqual(self.lib.open_cfw_littlefs_bootloader_init_421210(), 9)
        self.assertEqual(
            self.events(), ((1, -84), (2, 0), (1, -5), (11, -5))
        )
        self.assertEqual(self.value(49), 0)

    def test_directory_failure_repairs_and_ignores_repair_and_io_statuses(self) -> None:
        self.config(3, -1)
        self.config(4, 9)
        for operation in range(5, 10):
            self.config(operation, -operation)
        self.config(10, 7)
        self.assertEqual(self.lib.open_cfw_littlefs_bootloader_init_421210(), 0)
        self.assertEqual(
            self.events(),
            ((1, 0), (3, -1), (12, 0), (4, 9), (5, 1), (6, -5),
             (7, -6), (8, -7), (9, -8), (10, -9), (13, 8)),
        )
        self.assertEqual((self.value(49), self.value(50)), (1, 8))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "littlefs-init-target.o"
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
