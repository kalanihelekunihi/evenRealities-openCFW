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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_config_release_secondary_422fa2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_config_release_secondary_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareSecondaryConfigReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hw-release-secondary.dylib" if sys.platform == "darwin" else "hw-release-secondary.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ), "-o", str(output)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.release = cls.lib.open_cfw_bootloader_hw_config_release_secondary_422fa2
        cls.release.argtypes = [ctypes.POINTER(Instance)]
        cls.release.restype = ctypes.c_uint32
        cls.token = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcrs_host_token")
        cls.enter_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcrs_host_enter_count")
        cls.restore_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcrs_host_restore_count")
        cls.restored_token = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcrs_host_restored_token")
        cls.memset_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcrs_host_memset_count")
        cls.memset_length = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcrs_host_memset_length")
        cls.memset_value = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwcrs_host_memset_value")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.token.value = 0xA5A55A5A
        self.enter_count.value = self.restore_count.value = self.restored_token.value = 0
        self.memset_count.value = self.memset_length.value = self.memset_value.value = 0

    @staticmethod
    def instance(state: int) -> Instance:
        value = Instance()
        value.bytes[:] = bytes([0xCC]) * 0x11C
        value.bytes[0x11A] = state
        return value

    def test_authenticated_body_caller_providers_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x12FA2:0x12FDE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (60, "9779bb01d8332c3219ab8dec41d5d6fc39a33ab7dda97cd14a61257fffb965f6"))
        self.assertEqual(blob[0x13062:0x13066].hex(), "fff79eff")
        self.assertEqual(hashlib.sha256(blob[0xB8EC:0xB8FA]).hexdigest(), "3fa74f07fb3e8bc8acc716c8bb6150450a752fceed439b6bd5a0c9a82c603e2f")
        self.assertEqual(hashlib.sha256(blob[0x560C:0x5650]).hexdigest(), "a1582337d1f09d5431278a57ef921759bf40c5f79bc4c8cc0c7a37b8b4d85731")
        self.assertEqual(blob[0x12FDE:0x12FE6].hex(), "2de9f0410400a046")

    def test_active_release_clears_exact_secondary_runtime_span(self) -> None:
        instance = self.instance(1)
        before = bytes(instance.bytes)
        self.assertEqual(self.release(ctypes.byref(instance)), 0)
        self.assertEqual(instance.bytes[0x11A], 0)
        self.assertEqual(bytes(instance.bytes[0x64:0xA0]), bytes(0x3C))
        self.assertEqual((self.memset_count.value, self.memset_length.value, self.memset_value.value), (1, 0x38, 0))
        changed = set(range(0x64, 0xA0)) | {0x11A}
        for index, byte in enumerate(instance.bytes):
            if index not in changed:
                self.assertEqual(byte, before[index])

    def test_inactive_or_noncanonical_state_returns_seven_without_mutation(self) -> None:
        for state in (0, 2, 0xFF):
            instance = self.instance(state)
            before = bytes(instance.bytes)
            self.assertEqual(self.release(ctypes.byref(instance)), 7)
            self.assertEqual(bytes(instance.bytes), before)
            self.assertEqual(self.memset_count.value, 0)

    def test_critical_token_is_restored_on_success_and_failure(self) -> None:
        for state in (1, 0):
            instance = self.instance(state)
            self.token.value = 0x12340000 | state
            self.enter_count.value = self.restore_count.value = 0
            self.release(ctypes.byref(instance))
            self.assertEqual((self.enter_count.value, self.restore_count.value), (1, 1))
            self.assertEqual(self.restored_token.value, self.token.value)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwcrs.o"))], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
