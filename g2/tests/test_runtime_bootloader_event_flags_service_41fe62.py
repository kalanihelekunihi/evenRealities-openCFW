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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_event_flags_service_41fe62.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_event_flags_service_host.c"
BASE = 0x00410000


def thumb_bl_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first = int.from_bytes(blob[offset : offset + 2], "little")
    second = int.from_bytes(blob[offset + 2 : offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    delta = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x3FF) << 12)
        | ((second & 0x7FF) << 1)
    )
    if delta & (1 << 24):
        delta -= 1 << 25
    return address + 4 + delta


class EventFlagsServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fixture.dylib" if sys.platform == "darwin" else "fixture.so"
        cls.library_path = Path(cls.temporary.name) / suffix
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o",
                str(cls.library_path),
            ],
            check=True,
        )
        cls.library = ctypes.CDLL(str(cls.library_path))
        word = ctypes.c_size_t
        cls.library.open_cfw_event_flags_fixture_reset.argtypes = [
            word,
            word,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.library.open_cfw_event_flags_fixture_handle.restype = word
        cls.library.open_cfw_event_flags_fixture_count.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_event_flags_fixture_count.restype = ctypes.c_uint32
        cls.library.open_cfw_event_flags_fixture_observed.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_event_flags_fixture_observed.restype = word
        cls.library.open_cfw_event_flags_fixture_log.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_event_flags_fixture_log.restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, handle: int, created: int, acquire: int, release: int) -> None:
        self.library.open_cfw_event_flags_fixture_reset(
            handle, created, acquire, release
        )

    def counts(self) -> tuple[int, int, int, int]:
        return tuple(
            self.library.open_cfw_event_flags_fixture_count(index)
            for index in range(4)
        )

    def log(self) -> list[int]:
        return [
            self.library.open_cfw_event_flags_fixture_log(index)
            for index in range(6)
        ]

    def test_authenticated_stock_functions_and_callers(self) -> None:
        blob = OFFICIAL.read_bytes()
        spans = (
            (0x0041FE62, 0x0041FE9C, "b5dbeb76a423f8cea25297e99a8287c96fd07ff2734beaa0551aefb3d4842c8c", (0x0042051C,)),
            (0x0041FE9C, 0x0041FED4, "29b06ffce120996862a184169a3fb2f17e46787672085d79977eaa979500244c", (0x0041FF0A,)),
            (0x0041FED4, 0x0041FF08, "9a3c0274be0fd350c7090add8b8adcccec4dea0fdb2a9c93a7733c1fd965e681", (0x0041FF2E,)),
        )
        for start, end, expected_hash, expected_callers in spans:
            body = blob[start - BASE : end - BASE]
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
            callers = tuple(
                address
                for address in range(BASE, BASE + len(blob) - 3, 2)
                if thumb_bl_target(blob, address) == start
            )
            self.assertEqual(callers, expected_callers)

    def test_initializer_is_idempotent_and_publishes_created_handle(self) -> None:
        self.reset(0x1111, 0x2222, 0, 0)
        self.library.open_cfw_bootloader_event_flags_init_41fe62()
        self.assertEqual(self.counts(), (0, 0, 0, 0))
        self.assertEqual(self.library.open_cfw_event_flags_fixture_handle(), 0x1111)

        self.reset(0, 0x2222, 0, 0)
        self.library.open_cfw_bootloader_event_flags_init_41fe62()
        self.assertEqual(self.counts(), (1, 0, 0, 0))
        self.assertEqual(self.library.open_cfw_event_flags_fixture_handle(), 0x2222)

    def test_initializer_logs_exact_record_only_when_creation_fails(self) -> None:
        self.reset(0, 0, 0, 0)
        self.library.open_cfw_bootloader_event_flags_init_41fe62()
        self.assertEqual(self.counts(), (1, 0, 0, 1))
        self.assertEqual(
            self.log(),
            [1, 0x00433CD8, 0x00431540, 0x0043376C, 0xBA, 0x004329FC],
        )

    def test_acquire_is_guarded_and_uses_wait_forever(self) -> None:
        self.reset(0, 0, 7, 0)
        self.library.open_cfw_bootloader_event_flags_acquire_41fe9c()
        self.assertEqual(self.counts(), (0, 0, 0, 0))

        self.reset(0x2222, 0, 0, 0)
        self.library.open_cfw_bootloader_event_flags_acquire_41fe9c()
        self.assertEqual(self.counts(), (0, 1, 0, 0))
        self.assertEqual(
            [
                self.library.open_cfw_event_flags_fixture_observed(0),
                self.library.open_cfw_event_flags_fixture_observed(1),
            ],
            [0x2222, 0xFFFFFFFF],
        )

        self.reset(0x3333, 0, 7, 0)
        self.library.open_cfw_bootloader_event_flags_acquire_41fe9c()
        self.assertEqual(self.counts(), (0, 1, 0, 1))
        self.assertEqual(
            self.log(),
            [1, 0x00433CD8, 0x00431540, 0x00433784, 0xC3, 0x00432CA0],
        )

    def test_release_is_guarded_and_logs_failures(self) -> None:
        self.reset(0, 0, 0, 7)
        self.library.open_cfw_bootloader_event_flags_release_41fed4()
        self.assertEqual(self.counts(), (0, 0, 0, 0))

        self.reset(0x4444, 0, 0, 0)
        self.library.open_cfw_bootloader_event_flags_release_41fed4()
        self.assertEqual(self.counts(), (0, 0, 1, 0))
        self.assertEqual(
            self.library.open_cfw_event_flags_fixture_observed(2), 0x4444
        )

        self.reset(0x5555, 0, 0, 9)
        self.library.open_cfw_bootloader_event_flags_release_41fed4()
        self.assertEqual(self.counts(), (0, 0, 1, 1))
        self.assertEqual(
            self.log(),
            [1, 0x00433CD8, 0x00431540, 0x0043379C, 0xCC, 0x00432A24],
        )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "event-flags.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target",
                "arm-none-eabi",
                "-mcpu=cortex-m55",
                "-mthumb",
                "-std=c11",
                "-Oz",
                "-ffreestanding",
                "-fno-builtin",
                "-ffunction-sections",
                "-fdata-sections",
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-fropi",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-c",
                str(SOURCE),
                "-o",
                str(output),
            ],
            check=True,
            capture_output=True,
        )


if __name__ == "__main__":
    unittest.main()
