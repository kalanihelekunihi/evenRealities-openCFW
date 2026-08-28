from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_instance_init_422ad4.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_instance_init_host.c"
INSTANCE_SIZE = 0x11C


class BootloaderHardwareInstanceInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / (
            "hw-instance.dylib" if sys.platform == "darwin" else "hw-instance.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(output),
            ],
            check=True,
            capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.init = cls.lib.open_cfw_bootloader_hw_instance_init_422ad4
        cls.init.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)]
        cls.init.restype = ctypes.c_uint32
        cls.reset = cls.lib.open_cfw_hw_host_reset
        cls.reset.argtypes = [ctypes.c_uint8]
        cls.bytes_for = cls.lib.open_cfw_hw_host_instance_bytes
        cls.bytes_for.argtypes = [ctypes.c_uint32]
        cls.bytes_for.restype = ctypes.POINTER(ctypes.c_uint8)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def read32(raw, offset):
        return int.from_bytes(bytes(raw[offset:offset + 4]), "little")

    def test_authenticated_body_callsite_pool_and_boundaries(self):
        blob = OFFICIAL.read_bytes()
        body = blob[0x12AD4:0x12BA8]
        self.assertEqual(len(body), 212)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "e9be5104b2affd8296338018098cf8b3f634e45617cff59c745d52983c3c6f65",
        )
        self.assertEqual(blob[0x12AD2:0x12AD4], b"\x00\x00")
        self.assertEqual(blob[0x0F744:0x0F748].hex(), "03f0c6f9")
        self.assertEqual(blob[0x133E0:0x133E4], (0x01EA9E06).to_bytes(4, "little"))
        self.assertEqual(blob[0x133E4:0x133E8], (0x20024400).to_bytes(4, "little"))
        self.assertEqual(blob[0x13430:0x13434], (0x00EA9E06).to_bytes(4, "little"))
        self.assertEqual(blob[0x12BA8:0x12BAC].hex(), "f8b50400")

    def test_invalid_index_and_null_output(self):
        sentinel = ctypes.c_void_p(0x1234)
        self.assertEqual(self.init(4, ctypes.byref(sentinel)), 5)
        self.assertEqual(sentinel.value, 0x1234)
        self.assertEqual(self.init(0, None), 6)

    def test_initializes_each_slot_and_only_authenticated_fields(self):
        for index in range(4):
            self.reset(0xA5)
            output = ctypes.c_void_p()
            self.assertEqual(self.init(index, ctypes.byref(output)), 0)
            raw = self.bytes_for(index)
            self.assertEqual(output.value, ctypes.addressof(raw.contents))
            self.assertEqual(self.read32(raw, 0), 0xA5EA9E06)
            self.assertEqual(self.read32(raw, 0x28), index)
            self.assertEqual(raw[4], 0)
            self.assertEqual(self.read32(raw, 0x30), 0)
            self.assertEqual(self.read32(raw, 0x9C), 0)
            self.assertEqual(self.read32(raw, 0xD8), 0)
            self.assertEqual((raw[0xDC], raw[0xDD], raw[0xDE]), (0, 0, 1))
            self.assertEqual((raw[0x119], raw[0x11A]), (0, 0))
            self.assertEqual(raw[5], 0xA5)
            for other in range(4):
                if other != index:
                    self.assertEqual(bytes(self.bytes_for(other)[:INSTANCE_SIZE]), b"\xA5" * INSTANCE_SIZE)

    def test_compatible_handle_is_rejected_and_incompatible_handle_is_replaced(self):
        compatible = (ctypes.c_uint8 * INSTANCE_SIZE)()
        compatible[:4] = (0x01EA9E06).to_bytes(4, "little")
        output = ctypes.c_void_p(ctypes.addressof(compatible))
        self.assertEqual(self.init(2, ctypes.byref(output)), 7)
        self.assertEqual(output.value, ctypes.addressof(compatible))

        incompatible = (ctypes.c_uint8 * INSTANCE_SIZE)()
        incompatible[:4] = (0x00EA9E05).to_bytes(4, "little")
        output = ctypes.c_void_p(ctypes.addressof(incompatible))
        self.reset(0x5A)
        self.assertEqual(self.init(2, ctypes.byref(output)), 0)
        self.assertEqual(output.value, ctypes.addressof(self.bytes_for(2).contents))

    def test_source_cross_compiles(self):
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [
                        compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                        "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                        "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE),
                        "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hw-instance.o")),
                    ],
                    check=True,
                    capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
