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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_register_4163b2_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_register_4163b2.c"


class Config(ctypes.Structure):
    _fields_ = [
        ("handle", ctypes.c_size_t),
        ("reserved", ctypes.c_size_t),
        ("storage", ctypes.c_size_t),
        ("storage_size", ctypes.c_size_t),
    ]


class BootloaderRuntimeRegister4163b2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-register.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        word = ctypes.c_size_t
        cls.lib.open_cfw_test_register_reset.argtypes = [word, word, word, word]
        cls.lib.open_cfw_bootloader_runtime_register_4163b2.argtypes = [word, word, word, ctypes.POINTER(Config)]
        cls.lib.open_cfw_bootloader_runtime_register_4163b2.restype = word
        for name in ("allocation_calls", "free_calls", "dynamic_calls", "static_calls"):
            getattr(cls.lib, f"open_cfw_test_register_{name}").restype = ctypes.c_uint
        cls.lib.open_cfw_test_register_allocated_address.restype = word
        cls.lib.open_cfw_test_register_free_address.restype = word
        cls.lib.open_cfw_test_register_backend_arg.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_register_backend_arg.restype = word
        cls.lib.open_cfw_test_register_record_word.argtypes = [word, ctypes.c_uint]
        cls.lib.open_cfw_test_register_record_word.restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self, context=0, allocation_ok=1, dynamic=0, static=0) -> None:
        self.lib.open_cfw_test_register_reset(context, allocation_ok, dynamic, static)

    def test_authenticated_complete_stock_entry_and_caller(self) -> None:
        image = OFFICIAL.read_bytes(); body = image[0x63B2:0x649A]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (232, "3d816e28d9db37c7ac113ab48791bf1b0d790e7b6d04e3dc0eaef95b37a601f1"),
        )
        self.assertEqual(image[0x1E590:0x1E594].hex(), "e7f70fff")

    def test_critical_null_owner_and_allocation_failure_short_circuit(self) -> None:
        self.reset(context=1)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_register_4163b2(1, 0, 2, None), 0)
        self.assertEqual(self.lib.open_cfw_test_register_allocation_calls(), 0)
        self.reset()
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_register_4163b2(0, 0, 2, None), 0)
        self.assertEqual(self.lib.open_cfw_test_register_allocation_calls(), 0)
        self.reset(allocation_ok=0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_register_4163b2(1, 0, 2, None), 0)
        self.assertEqual(self.lib.open_cfw_test_register_allocation_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_register_dynamic_calls(), 0)

    def test_dynamic_registration_tags_record_and_frees_only_on_failure(self) -> None:
        for result in (0, 0x55):
            with self.subTest(result=result):
                self.reset(dynamic=result)
                observed = self.lib.open_cfw_bootloader_runtime_register_4163b2(0x11, 0x100, 0x22, None)
                address = self.lib.open_cfw_test_register_allocated_address()
                self.assertEqual(observed, result)
                self.assertEqual(self.lib.open_cfw_test_register_dynamic_calls(), 1)
                self.assertEqual(self.lib.open_cfw_test_register_backend_arg(0), 0)
                self.assertEqual(self.lib.open_cfw_test_register_backend_arg(1), 1)
                self.assertEqual(self.lib.open_cfw_test_register_backend_arg(2), 0)
                self.assertEqual(self.lib.open_cfw_test_register_backend_arg(3), address | 1)
                self.assertEqual(self.lib.open_cfw_test_register_backend_arg(4), 0x0041639B)
                self.assertEqual(self.lib.open_cfw_test_register_record_word(address, 0), 0x11)
                self.assertEqual(self.lib.open_cfw_test_register_record_word(address, 1), 0x22)
                self.assertEqual(self.lib.open_cfw_test_register_free_calls(), 1 if result == 0 else 0)
                if result == 0:
                    self.assertEqual(self.lib.open_cfw_test_register_free_address(), address)

    def test_embedded_static_registration_uses_storage_plus_44(self) -> None:
        storage = ctypes.create_string_buffer(96)
        config = Config(0x33, 0, ctypes.addressof(storage), 52)
        self.reset(static=0x77)
        observed = self.lib.open_cfw_bootloader_runtime_register_4163b2(0x44, 1, 0x55, ctypes.byref(config))
        record = ctypes.addressof(storage) + 44
        self.assertEqual(observed, 0x77)
        self.assertEqual(self.lib.open_cfw_test_register_allocation_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_register_static_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_register_backend_arg(0), 0x33)
        self.assertEqual(self.lib.open_cfw_test_register_backend_arg(2), 1)
        self.assertEqual(self.lib.open_cfw_test_register_backend_arg(3), record)
        self.assertEqual(self.lib.open_cfw_test_register_backend_arg(5), ctypes.addressof(storage))
        self.assertEqual(self.lib.open_cfw_test_register_record_word(record, 0), 0x44)
        self.assertEqual(self.lib.open_cfw_test_register_record_word(record, 1), 0x55)

    def test_invalid_config_allocates_then_releases_without_registration(self) -> None:
        storage = ctypes.create_string_buffer(32)
        config = Config(9, 0, ctypes.addressof(storage), 12)
        self.reset()
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_register_4163b2(1, 1, 2, ctypes.byref(config)), 0)
        self.assertEqual(self.lib.open_cfw_test_register_dynamic_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_register_static_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_register_free_calls(), 1)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-register.o"
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
