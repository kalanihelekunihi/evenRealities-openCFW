import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_alignment_dispatch_42e4f4.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
FUNCTION = "open_cfw_bootloader_alignment_dispatch_42e4f4"
START = 0x0042E4F4
SIZE = 26
BODY_SHA = "b53569c4e9b718913c54a8e7137c6e1c91a6b6efd7374a4c043d8103fe4f423e"
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
CALLBACK = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p)


class BootloaderAlignmentDispatch42e4f4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "alignment_dispatch.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        cls.dispatch = ctypes.CDLL(
            str(library)).open_cfw_bootloader_alignment_dispatch_42e4f4_portable
        cls.dispatch.argtypes = [ctypes.c_uint32] * 4 + [CALLBACK, ctypes.c_void_p]
        cls.dispatch.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_portable_alignment_gate(self):
        calls = []

        @CALLBACK
        def provider(first, second, length, destination, _context):
            calls.append((first, second, length, destination)); return 0x12345678

        self.assertEqual(self.dispatch(1, 2, 32, 0x20000000, provider, None),
                         0x12345678)
        self.assertEqual(calls, [(1, 2, 32, 0x20000000)])
        for length_low in range(16):
            for destination_low in range(4):
                if length_low == 0 and destination_low == 0:
                    continue
                self.assertEqual(
                    self.dispatch(1, 2, 0x100 + length_low,
                                  0x20000000 + destination_low, provider, None),
                    0x08000140,
                )
        self.assertEqual(len(calls), 1)

    def test_dual_toolchain_and_main_bodies_are_exact(self):
        boot = BOOT.read_bytes(); main = MAIN.read_bytes()
        stock = boot[START - BOOT_BASE:START - BOOT_BASE + SIZE]
        analogue = main[0x004D0A2C - MAIN_BASE:0x004D0A2C - MAIN_BASE + SIZE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(), BODY_SHA)
        self.assertEqual(stock, analogue)
        relocations = [{"offset": 0x14, "type": "R_ARM_THM_CALL",
                        "symbol": "open_cfw_bootloader_aligned_provider_42e4a0",
                        "symbol_type": "STT_NOTYPE", "target_address": 0x0042E4A0}]
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, FUNCTION, runtime_address=START,
                    relocation_configs=relocations,
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(report["relocation_count"], 1)

    def test_source_is_reviewable_mit_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        self.assertIn(FUNCTION, body)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
