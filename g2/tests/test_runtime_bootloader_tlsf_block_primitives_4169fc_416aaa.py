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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_tlsf_block_primitives_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_tlsf_block_primitives_4169fc.c"


class Block(ctypes.Structure):
    _fields_ = [
        ("previous_physical_block", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("next_free", ctypes.c_uint32),
        ("previous_free", ctypes.c_uint32),
    ]


STOCK = (
    (0x69FC, 0x6A10, "a67ca544ed43f3f6ea1b7b24e80378d770f84d2ed2f1af429108e1f782d0db38"),
    (0x6A10, 0x6A2C, "6d72ee9fe96d9cb2f7844cf09d9bd3731d4edad0aeaa85b46170327b89cf9b3c"),
    (0x6A2C, 0x6A40, "7a70a168cf1945bce79b61d349e7396a775e154b8baccc531ffd31727fe84581"),
    (0x6A40, 0x6A4C, "1f486b8f137891b916d28e06788f972bbaa6b6661c9456858680268524363d4e"),
    (0x6A4C, 0x6A5A, "909bbd0a882387f0ab2827ed452bb0573b0bc7bcf7e0f5e52bfbbad02993a040"),
    (0x6A5A, 0x6A68, "766e7c84437ffdbede3de95b842ee8a0ce886eb376b5b9bfa477d1457dfd045d"),
    (0x6A68, 0x6A74, "c534389c7a22af4d799f057fdf101d445a14bcccb4a6c32da17199c9623e402d"),
    (0x6A74, 0x6A82, "188a5913a72e61f591be862cd88dade35ae450fe221aa83ff04da332c23ad7c8"),
    (0x6A82, 0x6A90, "552a382a3d0ddb065512a1319dd0b70798a7c9a97812e24f9d7692c1af143698"),
    (0x6A90, 0x6A9C, "57d962b39925dd352f2fc680fe7bc0dc5ef6dc36602a0c5132530c964951cc3a"),
    (0x6A9C, 0x6AA6, "9d79408f1b43af81c23896d683ed2a63dc2120e2b5b2aa97c0ac00e039f4687c"),
    (0x6AA6, 0x6AAA, "29bce3401f67ec00955f0c63f4b66a81ff9e2df5270c73c9747d202ad1b63434"),
)


class BootloaderTlsfBlockPrimitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "tlsf_block.dylib" if sys.platform == "darwin" else "tlsf_block.so"
        )
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
            *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ),
            "-o", str(library),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.block_pointer = ctypes.POINTER(Block)
        cls.size = cls.library.open_cfw_bootloader_tlsf_block_size_4169fc
        cls.size.argtypes = [cls.block_pointer]
        cls.size.restype = ctypes.c_uint32
        cls.set_size = cls.library.open_cfw_bootloader_tlsf_block_set_size_416a10
        cls.set_size.argtypes = [cls.block_pointer, ctypes.c_uint32]
        cls.is_last = cls.library.open_cfw_bootloader_tlsf_block_is_last_416a2c
        cls.is_last.argtypes = [cls.block_pointer]
        cls.is_last.restype = ctypes.c_int
        cls.is_free = cls.library.open_cfw_bootloader_tlsf_block_is_free_416a40
        cls.is_free.argtypes = [cls.block_pointer]
        cls.is_free.restype = ctypes.c_int
        cls.set_free = cls.library.open_cfw_bootloader_tlsf_block_set_free_416a4c
        cls.set_free.argtypes = [cls.block_pointer]
        cls.set_used = cls.library.open_cfw_bootloader_tlsf_block_set_used_416a5a
        cls.set_used.argtypes = [cls.block_pointer]
        cls.is_previous_free = cls.library.open_cfw_bootloader_tlsf_block_is_previous_free_416a68
        cls.is_previous_free.argtypes = [cls.block_pointer]
        cls.is_previous_free.restype = ctypes.c_int
        cls.set_previous_free = cls.library.open_cfw_bootloader_tlsf_block_set_previous_free_416a74
        cls.set_previous_free.argtypes = [cls.block_pointer]
        cls.set_previous_used = cls.library.open_cfw_bootloader_tlsf_block_set_previous_used_416a82
        cls.set_previous_used.argtypes = [cls.block_pointer]
        cls.from_pointer = cls.library.open_cfw_bootloader_tlsf_block_from_pointer_416a90
        cls.from_pointer.argtypes = [ctypes.c_void_p]
        cls.from_pointer.restype = ctypes.c_void_p
        cls.to_pointer = cls.library.open_cfw_bootloader_tlsf_block_to_pointer_416a9c
        cls.to_pointer.argtypes = [cls.block_pointer]
        cls.to_pointer.restype = ctypes.c_void_p
        cls.offset = cls.library.open_cfw_bootloader_tlsf_offset_to_block_416aa6
        cls.offset.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        cls.offset.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entries(self):
        image = OFFICIAL.read_bytes()
        for start, end, expected_hash in STOCK:
            body = image[start:end]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)

    def test_size_status_and_mutation_contracts(self):
        block = Block(size=0x1237)
        self.assertEqual(self.size(ctypes.byref(block)), 0x1234)
        self.assertEqual(self.is_last(ctypes.byref(block)), 0)
        self.assertEqual(self.is_free(ctypes.byref(block)), 1)
        self.assertEqual(self.is_previous_free(ctypes.byref(block)), 2)
        self.set_size(ctypes.byref(block), 0x80)
        self.assertEqual(block.size, 0x83)
        self.set_used(ctypes.byref(block))
        self.assertEqual(block.size, 0x82)
        self.set_previous_used(ctypes.byref(block))
        self.assertEqual(block.size, 0x80)
        self.set_free(ctypes.byref(block))
        self.set_previous_free(ctypes.byref(block))
        self.assertEqual(block.size, 0x83)
        self.set_size(ctypes.byref(block), 0)
        self.assertEqual(block.size, 3)
        self.assertEqual(self.size(ctypes.byref(block)), 0)
        self.assertEqual(self.is_last(ctypes.byref(block)), 1)

    def test_pointer_conversion_and_offset_contracts(self):
        storage = (ctypes.c_uint8 * 64)()
        base = ctypes.addressof(storage)
        block = ctypes.cast(base + 12, self.block_pointer)
        user = self.to_pointer(block)
        self.assertEqual(user, base + 20)
        self.assertEqual(self.from_pointer(user), base + 12)
        self.assertEqual(self.offset(base + 7, 29), base + 36)

    def test_freestanding_target_compiles(self):
        output = Path(self.temporary.name) / "tlsf_block.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
