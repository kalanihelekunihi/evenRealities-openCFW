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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_handle_host.c"
SOURCES = [
    ROOT / "components/bootloader/core_overlay/runtime_handle_acquire_4166aa.c",
    ROOT / "components/bootloader/core_overlay/runtime_handle_release_416710.c",
]


class BootloaderRuntimeHandleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-handle.{suffix}"
        command = [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        subprocess.run(command + ["-o", str(cls.library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library)); word = ctypes.c_size_t
        cls.lib.open_cfw_test_handle_reset.argtypes = [word, word, word]
        cls.lib.open_cfw_bootloader_runtime_handle_acquire_4166aa.argtypes = [word, word]
        cls.lib.open_cfw_bootloader_runtime_handle_acquire_4166aa.restype = word
        cls.lib.open_cfw_bootloader_runtime_handle_release_416710.argtypes = [word]
        cls.lib.open_cfw_bootloader_runtime_handle_release_416710.restype = word
        for name in ("tagged_calls", "plain_calls", "object", "timeout", "zero_arguments"):
            getattr(cls.lib, f"open_cfw_test_handle_{name}").restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def error(value: int) -> int:
        return value & ((1 << (ctypes.sizeof(ctypes.c_size_t) * 8)) - 1)

    def test_authenticated_stock_bodies_and_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        bodies = ((0x66AA, 0x6710, "7e01992bf56a87f76d3d358be2ee1a493519767165cb5cfc739e9957a869e3f5"), (0x6710, 0x6762, "73668052c9d6843302d6c1db4095d2c87ce56ab770499a25c4d55fb0912292d3"))
        for start, end, digest in bodies:
            self.assertEqual(hashlib.sha256(image[start:end]).hexdigest(), digest)
        acquire = (0x540E, 0x5452, 0x54A0, 0x54EE, 0x553A, 0x5564, 0xA66C, 0xFEAE, 0x1E726)
        release = (0x5430, 0x546C, 0x54BE, 0x551A, 0x5550, 0x5578, 0xA67E, 0xFEE2, 0x1E7D4)
        self.assertEqual([image[o:o + 4].hex() for o in acquire], ["01f04cf9", "01f02af9", "01f003f9", "01f0dcf8", "01f0b6f8", "01f0a1f8", "fcf71df8", "f6f7fcfb", "e7f7c0ff"])
        self.assertEqual([image[o:o + 4].hex() for o in release], ["01f06ef9", "01f050f9", "01f027f9", "01f0f9f8", "01f0def8", "01f0caf8", "fcf747f8", "f6f715fc", "e7f79cff"])

    def test_acquire_rejects_critical_and_null_handles(self) -> None:
        for critical, handle, expected in ((1, 0x100, -6), (0, 1, -4)):
            self.lib.open_cfw_test_handle_reset(critical, 1, 1)
            self.assertEqual(self.lib.open_cfw_bootloader_runtime_handle_acquire_4166aa(handle, 9), self.error(expected))
            self.assertEqual(self.lib.open_cfw_test_handle_tagged_calls() + self.lib.open_cfw_test_handle_plain_calls(), 0)

    def test_acquire_selects_tagged_and_plain_backends(self) -> None:
        for handle, tagged in ((0x101, True), (0x100, False)):
            self.lib.open_cfw_test_handle_reset(0, 1, 1)
            self.assertEqual(self.lib.open_cfw_bootloader_runtime_handle_acquire_4166aa(handle, 7), 0)
            self.assertEqual(self.lib.open_cfw_test_handle_object(), 0x100)
            self.assertEqual(self.lib.open_cfw_test_handle_timeout(), 7)
            self.assertEqual(self.lib.open_cfw_test_handle_tagged_calls(), int(tagged))
            self.assertEqual(self.lib.open_cfw_test_handle_plain_calls(), int(not tagged))

    def test_acquire_maps_backend_failure_by_timeout(self) -> None:
        for timeout, expected in ((0, -3), (5, -2)):
            self.lib.open_cfw_test_handle_reset(0, 0, 0)
            self.assertEqual(self.lib.open_cfw_bootloader_runtime_handle_acquire_4166aa(0x100, timeout), self.error(expected))

    def test_release_contract_and_backend_selection(self) -> None:
        for handle, tagged in ((0x101, True), (0x100, False)):
            self.lib.open_cfw_test_handle_reset(0, 1, 1)
            self.assertEqual(self.lib.open_cfw_bootloader_runtime_handle_release_416710(handle), 0)
            self.assertEqual(self.lib.open_cfw_test_handle_object(), 0x100)
            self.assertEqual(self.lib.open_cfw_test_handle_tagged_calls(), int(tagged))
            self.assertEqual(self.lib.open_cfw_test_handle_plain_calls(), int(not tagged))
            self.assertEqual(self.lib.open_cfw_test_handle_zero_arguments(), 0)
        for critical, handle, expected in ((1, 0x100, -6), (0, 1, -4)):
            self.lib.open_cfw_test_handle_reset(critical, 1, 1)
            self.assertEqual(self.lib.open_cfw_bootloader_runtime_handle_release_416710(handle), self.error(expected))

    def test_release_maps_backend_failure(self) -> None:
        self.lib.open_cfw_test_handle_reset(0, 0, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_handle_release_416710(0x101), self.error(-3))

    def test_freestanding_targets_compile(self) -> None:
        for source in SOURCES:
            output = Path(self.temporary.name) / (source.stem + ".o")
            subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(output)], check=True, capture_output=True, text=True)


if __name__ == "__main__": unittest.main()
