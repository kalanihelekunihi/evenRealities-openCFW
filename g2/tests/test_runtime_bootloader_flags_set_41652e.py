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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_flags_set_41652e_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_flags_set_41652e.c"


class BootloaderRuntimeFlagsSet41652ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-flags-set.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        word = ctypes.c_size_t
        cls.lib.open_cfw_test_flags_reset.argtypes = [word, word, word, word, word]
        cls.lib.open_cfw_bootloader_runtime_flags_set_41652e.argtypes = [word, word]
        cls.lib.open_cfw_bootloader_runtime_flags_set_41652e.restype = word
        for name in (
            "context_calls", "isr_set_calls", "isr_get_calls", "task_calls",
            "pendsv_calls", "object", "flags",
        ):
            getattr(cls.lib, f"open_cfw_test_flags_{name}").restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_callers_and_pendsv_literal(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x652E:0x658C]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (94, "46e258aaf8b560d3617e4570d332ac2d274eb0aa1f1a4b40d4dd2756ff0cf005"),
        )
        self.assertEqual(image[0x1E43E:0x1E442].hex(), "e8f776f8")
        self.assertEqual(image[0x1E452:0x1E456].hex(), "e8f76cf8")
        self.assertEqual(image[0x699C:0x69A0].hex(), "04ed00e0")

    def test_invalid_object_or_reserved_flag_byte_short_circuits(self) -> None:
        for object_value, flags in ((0, 1), (1, 0x01000000), (1, 0xFF000000)):
            with self.subTest(object=object_value, flags=flags):
                self.lib.open_cfw_test_flags_reset(0, 1, 0, 0, 0)
                observed = self.lib.open_cfw_bootloader_runtime_flags_set_41652e(
                    object_value, flags
                )
                self.assertEqual(observed, ctypes.c_size_t(-4).value)
                self.assertEqual(self.lib.open_cfw_test_flags_context_calls(), 0)

    def test_task_context_forwards_backend_result(self) -> None:
        self.lib.open_cfw_test_flags_reset(0, 1, 0, 0x123456, 0)
        self.assertEqual(
            self.lib.open_cfw_bootloader_runtime_flags_set_41652e(0x22, 0x3456),
            0x123456,
        )
        self.assertEqual(self.lib.open_cfw_test_flags_task_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_flags_isr_set_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_flags_object(), 0x22)
        self.assertEqual(self.lib.open_cfw_test_flags_flags(), 0x3456)

    def test_isr_backend_failure_maps_to_minus_three(self) -> None:
        self.lib.open_cfw_test_flags_reset(1, 0, 0x40, 0, 1)
        self.assertEqual(
            self.lib.open_cfw_bootloader_runtime_flags_set_41652e(1, 2),
            ctypes.c_size_t(-3).value,
        )
        self.assertEqual(self.lib.open_cfw_test_flags_isr_set_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_flags_isr_get_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_flags_pendsv_calls(), 0)

    def test_isr_success_returns_combined_bits_and_requests_pendsv_when_woken(self) -> None:
        for wake, expected_pendsv in ((0, 0), (1, 1), (7, 1)):
            with self.subTest(wake=wake):
                self.lib.open_cfw_test_flags_reset(1, 1, 0x40, 0, wake)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_flags_set_41652e(0x11, 0x05),
                    0x45,
                )
                self.assertEqual(self.lib.open_cfw_test_flags_isr_set_calls(), 1)
                self.assertEqual(self.lib.open_cfw_test_flags_isr_get_calls(), 1)
                self.assertEqual(
                    self.lib.open_cfw_test_flags_pendsv_calls(), expected_pendsv
                )

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-flags-set.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True, text=True,
        )


if __name__ == "__main__":
    unittest.main()
