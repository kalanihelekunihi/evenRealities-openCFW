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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_config_latch_secondary_422f4c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_config_latch_secondary_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareSecondaryConfigLatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hw-latch-secondary.dylib" if sys.platform == "darwin" else "hw-latch-secondary.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.latch = cls.lib.open_cfw_bootloader_hw_config_latch_secondary_422f4c
        cls.latch.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(ctypes.c_uint8)]
        cls.latch.restype = ctypes.c_uint32
        cls.token = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcls_host_token")
        cls.enter_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcls_host_enter_count")
        cls.restore_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcls_host_restore_count")
        cls.restored_token = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcls_host_restored_token")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.token.value = 0xA5A55A5A
        self.enter_count.value = self.restore_count.value = self.restored_token.value = 0

    @staticmethod
    def instance() -> Instance:
        value = Instance()
        value.bytes[:] = bytes([0xCC]) * 0x11C
        value.bytes[0x11A] = 0
        return value

    @staticmethod
    def configuration() -> ctypes.Array[ctypes.c_uint8]:
        value = (ctypes.c_uint8 * 0x35)()
        for index in range(0x35):
            value[index] = (index * 17 + 3) & 0xFF
        return value

    def test_authenticated_body_caller_pool_provider_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x12F4C:0x12FA2]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (86, "99c1945b3def3fccc0f8f5abc12e6233e33ef41ed6121b2e4fe5f465bfe99bb2"))
        self.assertEqual(blob[0x1350C:0x13510].hex(), "fff71efD".lower())
        self.assertEqual(int.from_bytes(blob[0x13854:0x13858], "little"), 0x08000005)
        self.assertEqual(hashlib.sha256(blob[0xB8EC:0xB8FA]).hexdigest(), "3fa74f07fb3e8bc8acc716c8bb6150450a752fceed439b6bd5a0c9a82c603e2f")
        self.assertEqual(blob[0x12FA2:0x12FAA].hex(), "7cb504000025f8f7")

    def test_first_latch_copies_exact_payload_and_resets_runtime_word(self) -> None:
        instance = self.instance()
        configuration = self.configuration()
        before = bytes(instance.bytes)
        self.assertEqual(self.latch(ctypes.byref(instance), configuration), 0)
        self.assertEqual(instance.bytes[0x11A], 1)
        self.assertEqual(instance.bytes[0x98], configuration[0x34])
        self.assertEqual(bytes(instance.bytes[0x64:0x80]), bytes(configuration[0:0x1C]))
        self.assertEqual(bytes(instance.bytes[0x9C:0xA0]), b"\0\0\0\0")
        changed = set(range(0x64, 0x80)) | {0x98, 0x9C, 0x9D, 0x9E, 0x9F, 0x11A}
        for index, byte in enumerate(instance.bytes):
            if index not in changed:
                self.assertEqual(byte, before[index])

    def test_duplicate_latch_returns_busy_without_mutation(self) -> None:
        instance = self.instance()
        configuration = self.configuration()
        instance.bytes[0x11A] = 2
        before = bytes(instance.bytes)
        self.assertEqual(self.latch(ctypes.byref(instance), configuration), 0x08000005)
        self.assertEqual(bytes(instance.bytes), before)

    def test_critical_token_is_restored_on_both_paths(self) -> None:
        for occupied in (0, 1):
            instance = self.instance()
            instance.bytes[0x11A] = occupied
            self.token.value = 0x12340000 | occupied
            self.enter_count.value = self.restore_count.value = 0
            self.latch(ctypes.byref(instance), self.configuration())
            self.assertEqual((self.enter_count.value, self.restore_count.value), (1, 1))
            self.assertEqual(self.restored_token.value, self.token.value)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwcls.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
