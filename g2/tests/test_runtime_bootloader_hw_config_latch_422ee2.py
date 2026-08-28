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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_config_latch_422ee2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_config_latch_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareConfigLatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / (
            "hw-latch.dylib" if sys.platform == "darwin" else "hw-latch.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
                "-Wall", "-Wextra", "-Werror", str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(output),
            ],
            check=True,
            capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.latch = cls.lib.open_cfw_bootloader_hw_config_latch_422ee2
        cls.latch.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(ctypes.c_uint8)]
        cls.latch.restype = ctypes.c_uint32
        cls.token = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcl_host_token")
        cls.enter_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcl_host_enter_count")
        cls.restore_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcl_host_restore_count")
        cls.restored_token = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcl_host_restored_token")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.token.value = 0xA5A55A5A
        self.enter_count.value = 0
        self.restore_count.value = 0
        self.restored_token.value = 0

    @staticmethod
    def instance() -> Instance:
        value = Instance()
        value.bytes[:] = bytes([0xCC]) * 0x11C
        value.bytes[0x119] = 0
        return value

    @staticmethod
    def configuration() -> ctypes.Array[ctypes.c_uint8]:
        value = (ctypes.c_uint8 * 0x35)()
        for index in range(0x35):
            value[index] = (index * 13 + 7) & 0xFF
        return value

    def test_authenticated_body_caller_pool_provider_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x12EE2:0x12F4C]
        self.assertEqual(len(body), 106)
        self.assertEqual(hashlib.sha256(body).hexdigest(), "c29518455fcc8058de0a0c6be773227f0aa9eda462085fa39707f8708d6ce5b0")
        self.assertEqual(blob[0x134E8:0x134EC].hex(), "fff7fbfc")
        self.assertEqual(blob[0x12EEA:0x12EEE].hex(), "f8f7fffc")
        self.assertEqual(int.from_bytes(blob[0x13850:0x13854], "little"), 0x08000004)
        self.assertEqual(blob[0x12F4C:0x12F54].hex(), "7cb504000e000025")
        self.assertEqual(hashlib.sha256(blob[0xB8EC:0xB8FA]).hexdigest(), "3fa74f07fb3e8bc8acc716c8bb6150450a752fceed439b6bd5a0c9a82c603e2f")

    def test_first_latch_copies_exact_payload_and_resets_runtime_fields(self) -> None:
        instance = self.instance()
        configuration = self.configuration()
        before = bytes(instance.bytes)
        self.assertEqual(self.latch(ctypes.byref(instance), configuration), 0)
        self.assertEqual(instance.bytes[0x119], 1)
        self.assertEqual(instance.bytes[0xD4], configuration[0x34])
        self.assertEqual(bytes(instance.bytes[0xA0:0xBC]), bytes(configuration[0:0x1C]))
        self.assertEqual(bytes(instance.bytes[0xD8:0xDC]), b"\0\0\0\0")
        self.assertEqual(instance.bytes[0xDE], 0)
        changed = set(range(0xA0, 0xBC)) | {0xD4, 0xD8, 0xD9, 0xDA, 0xDB, 0xDE, 0x119}
        for index, byte in enumerate(instance.bytes):
            if index not in changed:
                self.assertEqual(byte, before[index])

    def test_duplicate_latch_returns_busy_without_mutating_payload(self) -> None:
        instance = self.instance()
        configuration = self.configuration()
        instance.bytes[0x119] = 2
        before = bytes(instance.bytes)
        self.assertEqual(self.latch(ctypes.byref(instance), configuration), 0x08000004)
        self.assertEqual(bytes(instance.bytes), before)

    def test_critical_token_is_restored_on_both_paths(self) -> None:
        for occupied in (0, 1):
            instance = self.instance()
            instance.bytes[0x119] = occupied
            configuration = self.configuration()
            self.token.value = 0x12340000 | occupied
            self.enter_count.value = 0
            self.restore_count.value = 0
            self.latch(ctypes.byref(instance), configuration)
            self.assertEqual((self.enter_count.value, self.restore_count.value), (1, 1))
            self.assertEqual(self.restored_token.value, self.token.value)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [
                        compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                        "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                        "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra",
                        "-Werror", "-fno-ident", "-c", str(SOURCE), "-o",
                        str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwcl.o")),
                    ],
                    check=True,
                    capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
