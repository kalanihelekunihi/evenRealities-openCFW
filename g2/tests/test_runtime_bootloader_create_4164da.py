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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_create_4164da_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_create_4164da.c"


class BootloaderRuntimeCreate4164DATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-create.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        word = ctypes.c_size_t

        class Config(ctypes.Structure):
            _fields_ = [
                ("handle", word), ("reserved", word),
                ("storage", word), ("storage_size", word),
            ]

        cls.Config = Config
        cls.lib.open_cfw_test_create_reset.argtypes = [word, word, word]
        cls.lib.open_cfw_bootloader_runtime_create_4164da.argtypes = [ctypes.POINTER(Config)]
        cls.lib.open_cfw_bootloader_runtime_create_4164da.restype = word
        for name in ("static_calls", "dynamic_calls", "storage"):
            getattr(cls.lib, f"open_cfw_test_create_{name}").restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_caller(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x64DA:0x652E]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (84, "d2c1ca8cb76c2a512d9e0c4cd0575b7f83a787b4309ac5962328749877134890"),
        )
        self.assertEqual(image[0x1E25A:0x1E25E].hex(), "e8f73ef9")

    def test_critical_context_returns_null_without_backend(self) -> None:
        self.lib.open_cfw_test_create_reset(1, 0x11, 0x22)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_create_4164da(None), 0)
        self.assertEqual(self.lib.open_cfw_test_create_static_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_create_dynamic_calls(), 0)

    def test_null_and_empty_config_use_dynamic_backend(self) -> None:
        for config in (None, self.Config(9, 8, 0, 0)):
            with self.subTest(config=config):
                self.lib.open_cfw_test_create_reset(0, 0x11, 0x2233)
                pointer = None if config is None else ctypes.byref(config)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_create_4164da(pointer),
                    0x2233,
                )
                self.assertEqual(self.lib.open_cfw_test_create_static_calls(), 0)
                self.assertEqual(self.lib.open_cfw_test_create_dynamic_calls(), 1)

    def test_sufficient_caller_storage_uses_static_backend(self) -> None:
        storage = (ctypes.c_uint8 * 32)()
        address = ctypes.addressof(storage)
        config = self.Config(0, 0, address, 32)
        self.lib.open_cfw_test_create_reset(0, 0x4455, 0x22)
        self.assertEqual(
            self.lib.open_cfw_bootloader_runtime_create_4164da(ctypes.byref(config)),
            0x4455,
        )
        self.assertEqual(self.lib.open_cfw_test_create_static_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_create_dynamic_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_create_storage(), address)

    def test_mixed_or_undersized_storage_config_is_rejected(self) -> None:
        for config in (
            self.Config(0, 0, 1, 31),
            self.Config(0, 0, 0, 1),
        ):
            with self.subTest(config=config):
                self.lib.open_cfw_test_create_reset(0, 0x11, 0x22)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_create_4164da(ctypes.byref(config)),
                    0,
                )
                self.assertEqual(self.lib.open_cfw_test_create_static_calls(), 0)
                self.assertEqual(self.lib.open_cfw_test_create_dynamic_calls(), 0)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-create.o"
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
