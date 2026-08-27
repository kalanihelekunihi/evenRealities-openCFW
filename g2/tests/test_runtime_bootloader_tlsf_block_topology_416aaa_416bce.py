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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_tlsf_block_topology_416aaa.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_tlsf_block_topology_host.c"

STOCK = (
    (0x6AAA, 0x6AD0, "6fd6ed8bd46b2ecfbd8cc973877b3890271e11f14aebbf7321d7d3201c161091"),
    (0x6AD0, 0x6B14, "dbe9a6e4cb835b979496fcc507e4a276ef3f89ccbd1086693db2d2e853b92e3d"),
    (0x6B14, 0x6B22, "da86edb0d105eafbb01fad13392207fbf1f0b8abe8fce47c74411d02e72e5168"),
    (0x6B22, 0x6B38, "99842e01e59e4953343b72098d01895f7d536a10f8585de238f80e1027086d01"),
    (0x6B38, 0x6B4E, "4c7189391619fd4de37aedf9f461611f47430852ee191b0ffe78f6c7b786beb5"),
    (0x6B4E, 0x6B7A, "fac0ce5b23840ee0f6982a90567918eff59f4267da923c737d9961de6c002e20"),
    (0x6B7A, 0x6BA4, "e099350b2959fe169f223ed5f271e2437f39c5c032a765ec544b6a9b0dbe9472"),
    (0x6BA4, 0x6BCE, "1f611bdbe93fe15137f38274ba907a6de6e4f0a2055e63dfcfb56cf0b16b1f94"),
)


class Block(ctypes.Structure):
    _fields_ = [
        ("previous_physical_block", ctypes.c_void_p),
        ("size", ctypes.c_uint32),
        ("next_free", ctypes.c_uint32),
        ("previous_free", ctypes.c_uint32),
    ]


class BootloaderTlsfBlockTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / (
            "tlsf_topology.dylib" if sys.platform == "darwin" else "tlsf_topology.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        pointer = ctypes.POINTER(Block)
        cls.prev = cls.lib.open_cfw_bootloader_tlsf_block_prev_416aaa
        cls.prev.argtypes = [pointer]
        cls.prev.restype = ctypes.c_void_p
        cls.next = cls.lib.open_cfw_bootloader_tlsf_block_next_416ad0
        cls.next.argtypes = [pointer]
        cls.next.restype = ctypes.c_void_p
        cls.link = cls.lib.open_cfw_bootloader_tlsf_block_link_next_416b14
        cls.link.argtypes = [pointer]
        cls.link.restype = ctypes.c_void_p
        cls.mark_free = cls.lib.open_cfw_bootloader_tlsf_block_mark_as_free_416b22
        cls.mark_free.argtypes = [pointer]
        cls.mark_used = cls.lib.open_cfw_bootloader_tlsf_block_mark_as_used_416b38
        cls.mark_used.argtypes = [pointer]
        cls.align_up = cls.lib.open_cfw_bootloader_tlsf_align_up_416b4e
        cls.align_up.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
        cls.align_up.restype = ctypes.c_size_t
        cls.align_down = cls.lib.open_cfw_bootloader_tlsf_align_down_416b7a
        cls.align_down.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
        cls.align_down.restype = ctypes.c_size_t
        cls.align_pointer = cls.lib.open_cfw_bootloader_tlsf_align_pointer_416ba4
        cls.align_pointer.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        cls.align_pointer.restype = ctypes.c_void_p
        cls.reset_assert = cls.lib.open_cfw_test_tlsf_topology_reset_assert
        cls.assert_count = cls.lib.open_cfw_test_tlsf_topology_assert_count
        cls.assert_line = cls.lib.open_cfw_test_tlsf_topology_assert_line
        cls.assert_expression = cls.lib.open_cfw_test_tlsf_topology_assert_expression
        cls.assert_expression.restype = ctypes.c_size_t
        cls.assert_file = cls.lib.open_cfw_test_tlsf_topology_assert_file
        cls.assert_file.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.reset_assert()

    def test_authenticated_complete_stock_entries_and_callers(self):
        image = OFFICIAL.read_bytes()
        for start, end, expected_hash in STOCK:
            body = image[start:end]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
        text = SOURCE.read_text()
        for address in ("0x00431A04U", "0x0043188CU", "0x004319C8U", "0x00433A84U", "0x00415735U"):
            self.assertIn(address, text)

    def test_physical_neighbor_link_and_state_contracts(self):
        storage = (ctypes.c_ubyte * 128)()
        base = ctypes.addressof(storage)
        current = Block.from_buffer(storage, 0)
        following = Block.from_buffer(storage, 32)
        current.size = 24
        following.size = 0
        self.assertEqual(self.next(ctypes.byref(current)), base + 32)
        self.assertEqual(self.link(ctypes.byref(current)), base + 32)
        self.assertEqual(following.previous_physical_block, base)

        self.mark_free(ctypes.byref(current))
        self.assertEqual(current.size & 1, 1)
        self.assertEqual(following.size & 2, 2)
        self.mark_used(ctypes.byref(current))
        self.assertEqual(current.size & 1, 0)
        self.assertEqual(following.size & 2, 0)
        self.assertEqual(self.assert_count(), 0)

    def test_previous_block_and_assert_contracts(self):
        previous = Block(size=16)
        current = Block(
            previous_physical_block=ctypes.addressof(previous),
            size=18,
        )
        self.assertEqual(self.prev(ctypes.byref(current)), ctypes.addressof(previous))
        self.assertEqual(self.assert_count(), 0)
        current.size &= ~2
        self.assertEqual(self.prev(ctypes.byref(current)), ctypes.addressof(previous))
        self.assertEqual(self.assert_count(), 1)
        self.assertEqual(self.assert_line(), 433)
        self.assertEqual(self.assert_expression(), 0x004319C8)
        self.assertEqual(self.assert_file(), 0x00431A04)

    def test_alignment_and_invalid_alignment_asserts(self):
        self.assertEqual(self.align_up(0x101, 8), 0x108)
        self.assertEqual(self.align_down(0x10F, 8), 0x108)
        self.assertEqual(self.align_pointer(0x1003, 16), 0x1010)
        self.assertEqual(self.assert_count(), 0)
        self.assertEqual(self.align_up(10, 3), 12)
        self.assertEqual(self.assert_count(), 1)
        self.assertEqual(self.assert_line(), 471)
        self.assertEqual(self.assert_expression(), 0x0043188C)

    def test_freestanding_target_compiles(self):
        output = Path(self.temporary.name) / "topology.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
