import ctypes
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_noop_callbacks_42dd98.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
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
FUNCTIONS = (
    ("open_cfw_bootloader_noop_callback_42dd98", 0x0042DD98),
    ("open_cfw_bootloader_noop_callback_42e276", 0x0042E276),
    ("open_cfw_bootloader_noop_callback_42e39a", 0x0042E39A),
)


class BootloaderNoopCallbacks42dd98Tests(unittest.TestCase):
    def test_portable_callbacks_return_without_side_effects(self):
        with tempfile.TemporaryDirectory() as temporary:
            library = Path(temporary) / "noop_callbacks.so"
            compiler = shutil.which("cc") or shutil.which("clang")
            subprocess.run(
                [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
                 "-o", str(library)], check=True, capture_output=True, text=True,
            )
            dll = ctypes.CDLL(str(library))
            for function, _address in FUNCTIONS:
                callback = getattr(dll, function)
                callback.argtypes = []
                callback.restype = None
                callback()

    def test_dual_toolchain_entries_are_exact_bx_lr(self):
        boot = BOOT.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                for function, address in FUNCTIONS:
                    stock = boot[address - BOOT_BASE:address - BOOT_BASE + 2]
                    self.assertEqual(stock, bytes.fromhex("7047"))
                    linked, report = apollo_overlay.extract_in_place_function_section(
                        output, function, runtime_address=address,
                        relocation_configs=[], strict_relocation_contract=True,
                        allow_discarded_alloc_sections=True,
                    )
                    self.assertEqual(linked, stock, (profile, function))
                    self.assertEqual(report["relocation_count"], 0)

    def test_source_is_reviewable_mit_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        for function, _address in FUNCTIONS:
            self.assertIn(function, body)
        for token in (".byte", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
