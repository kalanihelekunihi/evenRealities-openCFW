import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_context_claim_42c4c6.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x410000
A = 0x42C4C6
Z = 0x42C538
FN = "open_cfw_bootloader_hw_context_claim_42c4c6"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402

FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
)
PROFILES = (
    ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
    Path("/opt/homebrew/opt/llvm@22/bin/clang"),
)


class HardwareContextClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        library = Path(cls.tmp.name) / "claim.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        dll = ctypes.CDLL(str(library))
        cls.claim = dll.open_cfw_bootloader_hw_context_claim_42c4c6_portable
        cls.claim.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
        ]
        cls.claim.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_validation_precedes_state_access(self):
        self.assertEqual(self.claim(8, 1, None, None, 0, None), 5)
        self.assertEqual(self.claim(0, 0, None, None, 0, None), 6)

    def test_already_claimed_is_rejected_without_mutation(self):
        control = ctypes.c_uint32(0xA9123456)
        instance = ctypes.c_uint32(99)
        output = ctypes.c_size_t(0xDEADBEEF)
        self.assertEqual(self.claim(3, 1, ctypes.byref(control),
                                    ctypes.byref(instance), 0x2001455C,
                                    ctypes.byref(output)), 7)
        self.assertEqual((control.value, instance.value, output.value),
                         (0xA9123456, 99, 0xDEADBEEF))

    def test_claim_stamps_magic_flags_index_and_stride(self):
        control = ctypes.c_uint32(0xAA654321)
        instance = ctypes.c_uint32()
        output = ctypes.c_size_t()
        self.assertEqual(self.claim(3, 1, ctypes.byref(control),
                                    ctypes.byref(instance), 0x2001455C,
                                    ctypes.byref(output)), 0)
        self.assertEqual(control.value, 0xA9123456)
        self.assertEqual(instance.value, 3)
        self.assertEqual(output.value, 0x2001455C + 3 * 0x8A8)

    def test_dual_toolchain_exact_and_relocation_free(self):
        stock = BOOT.read_bytes()[A - BASE:Z - BASE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(),
                         "9727ea0e7e8786ddfab4618f79b101d91192e7291034937b15da4a9246d17db2")
        with tempfile.TemporaryDirectory() as temp:
            for profile, compiler in enumerate(PROFILES):
                obj = Path(temp) / f"{profile}.o"
                subprocess.run([str(compiler), *FLAGS, "-c", str(SOURCE),
                                "-o", str(obj)], check=True,
                               capture_output=True, text=True)
                body, report = apollo_overlay.extract_in_place_function_section(
                    obj, FN, runtime_address=A, relocation_configs=[],
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(body, stock)
                self.assertEqual(report["relocation_count"], 0)

    def test_reviewable_source(self):
        text = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", text)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
