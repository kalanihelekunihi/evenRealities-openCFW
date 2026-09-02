import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_descriptor_publish_42c45a.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x410000
A = 0x42C45A
Z = 0x42C4C6
FN = "open_cfw_bootloader_hw_descriptor_publish_42c45a"
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


class HardwareDescriptorPublishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        library = Path(cls.tmp.name) / "descriptor.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        dll = ctypes.CDLL(str(library))
        cls.publish = dll.open_cfw_bootloader_hw_descriptor_publish_42c45a_portable
        cls.publish.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ]
        cls.publish.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_selects_successor_and_maps_register_fields(self):
        entries = (ctypes.c_uint32 * 24)(*range(100, 124))
        registers = (ctypes.c_uint32 * 6)()
        self.assertEqual(self.publish(0, 3, entries, registers), 1)
        self.assertEqual(list(registers), [108, 109, 112, 110, 111, 113])

    def test_ring_selection_wraps(self):
        entries = (ctypes.c_uint32 * 16)(*range(200, 216))
        registers = (ctypes.c_uint32 * 6)()
        self.assertEqual(self.publish(1, 2, entries, registers), 0)
        self.assertEqual(list(registers), [200, 201, 204, 202, 203, 205])

    def test_dual_toolchain_exact_and_relocation_free(self):
        stock = BOOT.read_bytes()[A - BASE:Z - BASE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "0deea2026365cb9c3471cdd81a7644c3fa519db2239154f3456da25ab88c5525",
        )
        with tempfile.TemporaryDirectory() as temp:
            for profile, compiler in enumerate(PROFILES):
                obj = Path(temp) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(obj)],
                    check=True, capture_output=True, text=True,
                )
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
