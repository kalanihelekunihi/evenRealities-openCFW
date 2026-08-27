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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_flags_create_416610_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_flags_create_416610.c"


class BootloaderRuntimeFlagsCreate416610Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-flags-create.{suffix}"
        command = [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        word = ctypes.c_size_t

        class Config(ctypes.Structure):
            _fields_ = [("name", word), ("attributes", word), ("storage", word), ("storage_size", word)]

        cls.Config = Config
        cls.lib.open_cfw_test_flags_create_reset.argtypes = [word, word, word]
        cls.lib.open_cfw_bootloader_runtime_flags_create_416610.argtypes = [ctypes.POINTER(Config)]
        cls.lib.open_cfw_bootloader_runtime_flags_create_416610.restype = word
        for name in ("static_calls", "dynamic_calls", "kind", "storage"):
            getattr(cls.lib, f"open_cfw_test_flags_create_{name}").restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes(); body = image[0x6610:0x66AA]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (154, "b41ac55ec65b009015e3839d778bf3b9ea73e9280457e348428591bb7ccea77d"))
        self.assertEqual(
            [image[offset:offset + 4].hex() for offset in (0x5596, 0x55A0, 0xA654, 0xFE72, 0x1E5C8, 0x205A8)],
            ["01f03bf8", "01f036f8", "fbf7dcff", "f6f7cdfb", "e8f722f8", "e6f732f8"],
        )

    def test_critical_context_returns_null_without_backend(self) -> None:
        self.lib.open_cfw_test_flags_create_reset(1, 0x10, 0x20)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_flags_create_416610(None), 0)
        self.assertEqual(self.lib.open_cfw_test_flags_create_static_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_flags_create_dynamic_calls(), 0)

    def test_null_and_empty_config_use_dynamic_kind_one(self) -> None:
        for config in (None, self.Config(7, 0, 0, 0)):
            with self.subTest(config=config):
                self.lib.open_cfw_test_flags_create_reset(0, 0x10, 0x2222)
                pointer = None if config is None else ctypes.byref(config)
                self.assertEqual(self.lib.open_cfw_bootloader_runtime_flags_create_416610(pointer), 0x2222)
                self.assertEqual(self.lib.open_cfw_test_flags_create_dynamic_calls(), 1)
                self.assertEqual(self.lib.open_cfw_test_flags_create_kind(), 1)

    def test_tag_attribute_selects_kind_four_and_tags_nonnull_result(self) -> None:
        config = self.Config(0, 1, 0, 0)
        self.lib.open_cfw_test_flags_create_reset(0, 0, 0x2200)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_flags_create_416610(ctypes.byref(config)), 0x2201)
        self.assertEqual(self.lib.open_cfw_test_flags_create_kind(), 4)

    def test_static_storage_threshold_and_kind_are_preserved(self) -> None:
        storage = (ctypes.c_uint8 * 80)(); address = ctypes.addressof(storage)
        for attributes, kind, result in ((0, 1, 0x4400), (1, 4, 0x4400)):
            with self.subTest(attributes=attributes):
                config = self.Config(0, attributes, address, 80)
                self.lib.open_cfw_test_flags_create_reset(0, result, 0)
                expected = result | (attributes & 1)
                self.assertEqual(self.lib.open_cfw_bootloader_runtime_flags_create_416610(ctypes.byref(config)), expected)
                self.assertEqual(self.lib.open_cfw_test_flags_create_static_calls(), 1)
                self.assertEqual(self.lib.open_cfw_test_flags_create_kind(), kind)
                self.assertEqual(self.lib.open_cfw_test_flags_create_storage(), address)

    def test_attribute_bit_three_and_invalid_storage_contract_are_rejected(self) -> None:
        for config in (self.Config(0, 8, 0, 0), self.Config(0, 0, 1, 79), self.Config(0, 0, 0, 1)):
            with self.subTest(config=config):
                self.lib.open_cfw_test_flags_create_reset(0, 1, 1)
                self.assertEqual(self.lib.open_cfw_bootloader_runtime_flags_create_416610(ctypes.byref(config)), 0)
                self.assertEqual(self.lib.open_cfw_test_flags_create_static_calls(), 0)
                self.assertEqual(self.lib.open_cfw_test_flags_create_dynamic_calls(), 0)

    def test_null_tagged_backend_result_remains_null(self) -> None:
        config = self.Config(0, 1, 0, 0)
        self.lib.open_cfw_test_flags_create_reset(0, 0, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_flags_create_416610(ctypes.byref(config)), 0)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-flags-create.o"
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True, text=True)


if __name__ == "__main__": unittest.main()
