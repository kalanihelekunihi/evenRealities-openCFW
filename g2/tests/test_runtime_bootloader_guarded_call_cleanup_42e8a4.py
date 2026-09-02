import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_guarded_call_cleanup_42e8a4.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
FUNCTION = "open_cfw_bootloader_guarded_call_cleanup_42e8a4"
START = 0x0042E8A4
SIZE = 30
BODY_SHA = "c4d87e8f170f723eedb93c2fd52d09e6f176b9d41d75a0dba72b894fd9a42275"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
)
PROFILES = {
    "apple-clang": ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
    "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang"),
}
CALLBACK = ctypes.CFUNCTYPE(ctypes.c_uint32, *([ctypes.c_uint32] * 5),
                            ctypes.c_void_p)


class State(ctypes.Structure):
    _fields_ = [("control", ctypes.c_uint32), ("status", ctypes.c_uint32),
                ("write_count", ctypes.c_uint32),
                ("write_offsets", ctypes.c_uint32 * 3),
                ("write_values", ctypes.c_uint32 * 3)]


class BootloaderGuardedCallCleanup42e8a4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "guarded_call.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        cls.call = ctypes.CDLL(
            str(library)).open_cfw_bootloader_guarded_call_cleanup_42e8a4_portable
        cls.call.argtypes = [*([ctypes.c_uint32] * 5), CALLBACK,
                             ctypes.c_void_p, ctypes.POINTER(State)]
        cls.call.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_portable_argument_forwarding_and_ordered_cleanup(self):
        observed = []

        @CALLBACK
        def provider(first, second, third, fourth, fifth, _context):
            observed.append((first, second, third, fourth, fifth))
            return 0xA5A55A5A

        state = State(control=9, status=8)
        result = self.call(1, 2, 3, 4, 5, provider, None,
                           ctypes.byref(state))
        self.assertEqual(result, 0xA5A55A5A)
        self.assertEqual(observed, [(1, 2, 3, 4, 5)])
        self.assertEqual((state.control, state.status, state.write_count),
                         (0, 0, 3))
        self.assertEqual(list(state.write_offsets), [0, 0x1C, 0])
        self.assertEqual(list(state.write_values), [0xC3, 0, 0])

    def test_dual_toolchain_and_main_bodies_are_exact(self):
        boot = BOOT.read_bytes(); main = MAIN.read_bytes()
        stock = boot[START - BOOT_BASE:START - BOOT_BASE + SIZE]
        analogue = main[0x00541B7C - MAIN_BASE:0x00541B7C - MAIN_BASE + SIZE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(), BODY_SHA)
        self.assertEqual(stock, analogue)
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, FUNCTION, runtime_address=START,
                    relocation_configs=[], strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(report["relocation_count"], 0)

    def test_source_is_reviewable_mit_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        self.assertIn(FUNCTION, body)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
