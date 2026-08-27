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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_submit_41649a_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_submit_41649a.c"


class BootloaderRuntimeSubmit41649ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-submit.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        word = ctypes.c_size_t
        cls.lib.open_cfw_test_submit_reset.argtypes = [word, word]
        cls.lib.open_cfw_bootloader_runtime_submit_41649a.argtypes = [word, word]
        cls.lib.open_cfw_bootloader_runtime_submit_41649a.restype = ctypes.c_int
        for name in (
            "call_count", "owner", "kind", "argument", "option", "reserved"
        ):
            getattr(cls.lib, f"open_cfw_test_submit_{name}").restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_caller(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x649A:0x64DA]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (64, "3da32489b13b78370fde01b22ef77515363ac2866a8baa24e444d03ae87ec0e9"),
        )
        self.assertEqual(image[0x1E80C:0x1E810].hex(), "e7f745fe")

    def test_critical_context_short_circuits(self) -> None:
        self.lib.open_cfw_test_submit_reset(1, 1)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_submit_41649a(1, 2), -6)
        self.assertEqual(self.lib.open_cfw_test_submit_call_count(), 0)

    def test_null_arguments_are_rejected_without_backend_call(self) -> None:
        self.lib.open_cfw_test_submit_reset(0, 1)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_submit_41649a(0, 2), -4)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_submit_41649a(1, 0), -4)
        self.assertEqual(self.lib.open_cfw_test_submit_call_count(), 0)

    def test_success_forwards_the_recovered_five_argument_contract(self) -> None:
        self.lib.open_cfw_test_submit_reset(0, 1)
        self.assertEqual(
            self.lib.open_cfw_bootloader_runtime_submit_41649a(0x1122, 0x3344),
            0,
        )
        self.assertEqual(self.lib.open_cfw_test_submit_call_count(), 1)
        self.assertEqual(self.lib.open_cfw_test_submit_owner(), 0x1122)
        self.assertEqual(self.lib.open_cfw_test_submit_kind(), 4)
        self.assertEqual(self.lib.open_cfw_test_submit_argument(), 0x3344)
        self.assertEqual(self.lib.open_cfw_test_submit_option(), 0)
        self.assertEqual(self.lib.open_cfw_test_submit_reserved(), 0)

    def test_non_success_backend_status_maps_to_minus_three(self) -> None:
        for result in (0, 2, 0xFFFFFFFF):
            with self.subTest(result=result):
                self.lib.open_cfw_test_submit_reset(0, result)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_submit_41649a(1, 2),
                    -3,
                )
                self.assertEqual(self.lib.open_cfw_test_submit_call_count(), 1)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-submit.o"
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
