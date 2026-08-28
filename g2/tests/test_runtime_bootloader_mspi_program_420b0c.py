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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_program_420b0c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_program_host.c"


class MspiProgramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "program.dylib" if sys.platform == "darwin" else "program.so"
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
        cls.lib.open_cfw_program_fixture_config.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_program_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_program_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_program_420b0c.argtypes = [
            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32
        ]
        cls.lib.open_cfw_bootloader_mspi_program_420b0c.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_program_fixture_reset()
        self.buffer = (ctypes.c_uint8 * 1024)()

    def configure_failure(self, stage: int, call: int, status: int) -> None:
        self.lib.open_cfw_program_fixture_config(1, stage)
        self.lib.open_cfw_program_fixture_config(2, call)
        self.lib.open_cfw_program_fixture_config(3, status)

    def value(self, field: int) -> int:
        return self.lib.open_cfw_program_fixture_value(field)

    def events(self) -> tuple[int, ...]:
        return tuple(self.value(128 + i) for i in range(self.value(32)))

    def call(self, address: int, length: int, offset: int = 0) -> int:
        pointer = ctypes.cast(ctypes.byref(self.buffer, offset), ctypes.c_void_p)
        return self.lib.open_cfw_bootloader_mspi_program_420b0c(address, pointer, length)

    def test_authenticated_stock_body_pool_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10B0C:0x10C14]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (264, "dcaf2a13af5fb811c228b4845363682411abf1acab703507368f6d1e4463b15e"),
        )
        pool = blob[0x10ADA:0x10B0C]
        self.assertEqual(
            (len(pool), hashlib.sha256(pool).hexdigest()),
            (50, "619fd98be5ccc3286a0a39c06f1c556503edee5868456a01e8e15c67b2fb5ed2"),
        )
        successor_pool = blob[0x10C14:0x10C5C]
        self.assertEqual(
            (len(successor_pool), hashlib.sha256(successor_pool).hexdigest()),
            (72, "cfc3cdfaf2523ca39c957109635e3427aa5dca5f88993d6b841bc3ebc21b760f"),
        )
        self.assertEqual(blob[0x11326:0x1132A].hex(), "fff7f1fb")

    def test_validation_short_circuits_and_diagnostics(self) -> None:
        self.lib.open_cfw_program_fixture_config(0, 0)
        self.assertEqual(self.call(0, 1), 6)
        self.assertEqual((self.value(12), self.value(13), self.value(15)), (0x4326A8, 0, 1))
        self.assertEqual(self.events(), ())

        self.setUp()
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_program_420b0c(0, None, 1), 6)
        self.assertEqual((self.value(12), self.value(14), self.value(15)), (0x4326A8, 0, 1))

        self.setUp()
        self.assertEqual(self.call(0, 0), 6)
        self.assertEqual((self.value(12), self.value(15)), (0x4326A8, 0))

        self.setUp()
        self.assertEqual(self.call(0x02000000, 1), 5)
        self.assertEqual((self.value(12), self.value(13), self.value(14)),
                         (0x4326D4, 0x02000000, 0x02000000))
        self.assertEqual(self.events(), ())

    def test_page_splitting_transfer_tuple_and_success(self) -> None:
        self.assertEqual(self.call(0x1230F0, 0x220, 7), 0)
        self.assertEqual(self.value(33), 4)
        self.assertEqual(tuple(self.value(256 + i) for i in range(4)),
                         (0x1230F0, 0x123100, 0x123200, 0x123300))
        self.assertEqual(tuple(self.value(320 + i) for i in range(4)),
                         (0x10, 0x100, 0x100, 0x10))
        base = ctypes.addressof(self.buffer) + 7
        self.assertEqual(tuple(self.value(384 + i) for i in range(4)),
                         tuple((base + n) & 0xFFFFFFFF for n in (0, 0x10, 0x110, 0x210)))
        self.assertEqual((self.value(8), self.value(9), self.value(10)), (2, 1, 10))
        self.assertEqual(
            self.events(),
            (1, 2) + (5, 6, 7, 8, 9) * 4 + (3, 4),
        )
        self.assertEqual(self.value(11), 0)

    def test_each_failure_stage_stops_and_cleans_up(self) -> None:
        cases = (
            (1, 4, 0x431AF0, (1, 2, 5, 3, 4)),
            (2, 7, 0x431F0C, (1, 2, 5, 6, 3, 4)),
            (3, 7, 0x432208, (1, 2, 5, 6, 7, 3, 4)),
            (4, 4, 0x431B28, (1, 2, 5, 6, 7, 8, 3, 4)),
            (5, 7, 0x431B60, (1, 2, 5, 6, 7, 8, 9, 3, 4)),
        )
        for stage, expected_status, expected_format, expected_events in cases:
            with self.subTest(stage=stage):
                self.setUp()
                self.configure_failure(stage, 1, 7 if stage not in (1, 4) else 1)
                self.assertEqual(self.call(0x1230F0, 0x20), expected_status)
                self.assertEqual(self.value(12), expected_format)
                self.assertEqual((self.value(13), self.value(14)), (0x1230F0, 0x10))
                if stage in (2, 3, 5):
                    self.assertEqual(self.value(15), 7)
                self.assertEqual(self.events(), expected_events)

    def test_later_page_failure_uses_advanced_address_buffer_and_chunk(self) -> None:
        self.configure_failure(3, 2, 11)
        self.assertEqual(self.call(0x1230F0, 0x120, 5), 11)
        self.assertEqual((self.value(12), self.value(13), self.value(14), self.value(15)),
                         (0x432208, 0x123100, 0x100, 11))
        self.assertEqual(self.value(33), 2)
        self.assertEqual(self.events(),
                         (1, 2, 5, 6, 7, 8, 9, 5, 6, 7, 3, 4))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "program-target.o"
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
