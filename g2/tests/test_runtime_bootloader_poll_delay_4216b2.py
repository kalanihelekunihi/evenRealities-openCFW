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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_poll_delay_4216b2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_poll_delay_host.c"


class BootloaderPollDelayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "poll-delay.dylib" if sys.platform == "darwin" else "poll-delay.so"
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
        cls.poll = cls.lib.open_cfw_bootloader_poll_delay_4216b2
        cls.poll.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint32)]
        cls.poll.restype = None
        cls.lib.open_cfw_poll_fixture_reset.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
        ]
        cls.lib.open_cfw_poll_fixture_calls_get.restype = ctypes.c_uint32
        cls.lib.open_cfw_poll_fixture_last_duration_get.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_poll(self, active: int, remaining: int, clear_after: int = 0) -> tuple[int, int, int, int]:
        flag = ctypes.c_uint8(active)
        counter = ctypes.c_uint32(remaining)
        self.lib.open_cfw_poll_fixture_reset(ctypes.byref(flag), clear_after)
        self.poll(ctypes.byref(flag), ctypes.byref(counter))
        return (
            flag.value,
            counter.value,
            self.lib.open_cfw_poll_fixture_calls_get(),
            self.lib.open_cfw_poll_fixture_last_duration_get(),
        )

    def test_authenticated_complete_body_callers_and_delay_target(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x116B2:0x116D4]
        self.assertEqual(len(body), 34)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "eb69fa2933ef30723f342fbc330927d681c6ca5d2ac077b77bf5e7ed1689a795",
        )
        self.assertEqual(blob[0x116BC:0x116C0].hex(), "fbf780fd")
        self.assertEqual(blob[0x116D4:0x116D6].hex(), "f8b5")

    def test_zero_counter_or_inactive_flag_short_circuits(self) -> None:
        self.assertEqual(self.run_poll(1, 0), (1, 0, 0, 0))
        self.assertEqual(self.run_poll(0, 9), (0, 9, 0, 0))

    def test_active_poll_delays_ten_and_exhausts_counter(self) -> None:
        self.assertEqual(self.run_poll(1, 4), (1, 0, 4, 10))

    def test_flag_change_after_delay_still_consumes_current_iteration(self) -> None:
        self.assertEqual(self.run_poll(1, 7, clear_after=3), (0, 4, 3, 10))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).is_file():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-poll-delay.o")
            subprocess.run(
                [
                    compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(output),
                ],
                check=True, capture_output=True,
            )
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
